from abc import ABCMeta
from abc import abstractmethod

from django.db.models import F
from django.db.models import Count
from django.db.models import Avg
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast

from haley_gg.apps.stats.utils import get_deduplicated_result_queryset
from haley_gg.apps.stats.utils import BaseDataDict


class RaceStatistics(dict):
    WIN_INDEX = 0
    LOSE_INDEX = 1

    def __init__(self):
        """
        각 종족마다 상대 종족에 대한 승, 패 수를 갖고 있다.
        """
        self.update({
            'T': {'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]},
            'Z': {'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]},
            'P': {'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]}
        })

    def count(self, winner_race, loser_race):
        self[winner_race][loser_race][self.WIN_INDEX] += 1
        self[loser_race][winner_race][self.LOSE_INDEX] += 1

    def count_only_winner(self, winner_race, loser_race):
        self[winner_race][loser_race][self.WIN_INDEX] += 1


class BaseRaceStatisticsCalculator(metaclass=ABCMeta):
    """
    Calculate win and lose count by each race on melee results.
    """

    def __init__(self, queryset):
        self.deduplicate_queryset(queryset)

    def deduplicate_queryset(self, queryset):
        self._queryset = get_deduplicated_result_queryset(queryset)

    @abstractmethod
    def calculate(self):
        pass


class LeagueOfRaceStatisticsCalculator(BaseRaceStatisticsCalculator):
    """
    Calculate win and lose count by each race on melee results.
    """

    """
    TODO
    구조 개선 필요.
    """

    class RaceStatisticsClassifier(BaseDataDict):
        data_class = RaceStatistics

        def classify(self, result):
            race_statistics = self.get_or_create(result.league.name)
            race_statistics.count(result.winner_race, result.loser_race)

    def __init__(self, queryset):
        super().__init__(queryset)
        self.race_statistics_classifier = self.RaceStatisticsClassifier()

    def calculate(self):
        for result in self._queryset:
            self.race_statistics_classifier.classify(result)
        return self.race_statistics_classifier


class PlayerOfRaceStatisticsCalculator(BaseRaceStatisticsCalculator):
    def __init__(self, queryset):
        super().__init__(queryset)
        self.player_race = ''
        self.opponent_race = ''
        self.__calculated_data = RaceStatistics()

    def calculate(self):
        """
        Set result variable to RaceStatistics object.
        Because, this object only count player results.
        So result is not categorize with keys
        such as league name, map name etc.
        """
        for result in self._queryset:
            self.__set_races(result)

            self.__calculated_data.count_only_winner(
                self.player_race, self.opponent_race
            )
        return self.__calculated_data

    def __set_races(self, result):
        """
        In this calculator, fix up winner as player.
        """
        # Suppose player were won.
        self.player_race = result.winner_race
        self.opponent_race = result.loser_race

        # But player lose, swap both race.
        if not result.is_win:
            self.player_race, self.opponent_race = \
                self.opponent_race, self.player_race


class RankData:
    def __init__(self, league_name, player_name, category, value):
        self.league_name = league_name
        self.player_name = player_name
        self.category = category
        self.value = value


class RankDataList(list):
    def add_data(self, rank_data):
        self.append(rank_data)


class RankDataClassifier(BaseDataDict):
    data_class = RankDataList

    def save(self, rank_data):
        rank_data_list = self.get_or_create(rank_data.category)
        rank_data_list.add_data(rank_data)


class LeagueRankDataClassifier(BaseDataDict):
    data_class = RankDataClassifier

    def save(self, rank_data):
        rank_data_classifier = self.get_or_create(rank_data.league_name)
        rank_data_classifier.save(rank_data)


class BaseRankCalculator(metaclass=ABCMeta):
    """
    Ranks on result queryset with given expressions from RankCategory classes.
    After you inherit this class, you must add RankCategory classes to it.
    """
    """
    TODO
    현재 매우 느림. 이유를 파악하자.
    그리고 클래스가 많고 구조가 많이 복잡하다.
    동작은 하지만 개선이 필요하다.
    """

    def __init__(self, queryset):
        self.queryset = queryset
        self.limit = 5
        self.rank_category_list = []

    def ranks(self):
        self.group_queryset_by_league_name_and_player_name()
        self.annotate_on_queryset_with_rank_category_list()

    def group_queryset_by_league_name_and_player_name(self):
        self.queryset = self.queryset.values(
            'league__name', 'player__name'
        ).order_by(
            'league__name', 'player__name'
        )

    def annotate_on_queryset_with_rank_category_list(self):
        for rank_category in self.rank_category_list:
            self.queryset = rank_category.get_annotated_queryset(self.queryset)

    def set_rank_category_list(self, *rank_category_list_args):
        self.rank_category_list = list(rank_category_list_args)

    def get_ranked_queryset(self):
        return self.queryset

    def get_rank_category_name_list(self):
        name_list = []
        for rank_category in self.rank_category_list:
            name_list.append(rank_category.get_name())
        return name_list


class MeleeRankCalculator(BaseRankCalculator):
    def __init__(self, melee_result_queryset):
        super().__init__(melee_result_queryset)
        self.set_rank_category_list(
            WinCountRankCategory(),
            LoseCountRankCategory(),
            ResultCountRankCategory(),
            WinPercentageRankCategory(),
        )
        super().ranks()


class LeagueMeleeRank(MeleeRankCalculator):
    def __init__(self, melee_result_queryset):
        super().__init__(melee_result_queryset)
        self.__league_rank_data_classifier = LeagueRankDataClassifier()

    def ranks(self):
        for rank_category in self.rank_category_list:
            self.category_name = rank_category.get_name()
            self.order_queryset_by_category()
            self.convert_ordered_queryset_to_RankData()
            for rank_data in self.converted_rank_data_list:
                self.__league_rank_data_classifier.save(rank_data)

        return self.__league_rank_data_classifier

    def order_queryset_by_category(self):
        self.ordered_queryset = self.get_ranked_queryset().order_by(
            'league__name', F(self.category_name).desc(), 'player__name'
        )

    def convert_ordered_queryset_to_RankData(self):
        self.converted_rank_data_list = RankDataList()
        for row in self.ordered_queryset:
            self.converted_rank_data_list.add_data(
                RankData(
                    row.get('league__name'),
                    row.get('player__name'),
                    self.category_name,
                    row.get(self.category_name),
                )
            )


class BaseRankCategory(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_annotated_queryset(self, queryset):
        pass

    def get_name(self):
        return self.name


class WinCountRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(name='win_count')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            win_count=Sum(
                Cast('is_win', output_field=IntegerField())
            )
        )


class LoseCountRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(name='lose_count')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            lose_count=Sum(
                1 - Cast('is_win', output_field=IntegerField())
            )
        )


class ResultCountRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(name='result_count')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            result_count=Count('id')
        )


class WinPercentageRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(name='win_percentage')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            win_percentage=Avg(
                Cast('is_win', output_field=IntegerField()) * 100
            )
        )
