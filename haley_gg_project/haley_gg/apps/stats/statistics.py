from abc import ABCMeta
from abc import abstractmethod

from django.db.models import F
from django.db.models import Count
from django.db.models import Avg
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast

from haley_gg.apps.stats.utils import get_deduplicated_result_queryset
from haley_gg.apps.stats.utils import BaseDataClassifier


class WinAndLoseByRace(dict):
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


class LeagueWinAndLoseByRaceClassifier(BaseDataClassifier):
    def __init__(self):
        self.data_structure = WinAndLoseByRace


class BaseWinAndLoseByRaceCalculator(metaclass=ABCMeta):
    """
    Calculate win and lose count by each race on melee results.
    """

    @abstractmethod
    def calculate(self):
        pass

    def set_queryset(self, queryset):
        self._queryset = get_deduplicated_result_queryset(queryset)


class LeagueWinAndLoseByRaceCalculator(
    LeagueWinAndLoseByRaceClassifier,
    BaseWinAndLoseByRaceCalculator,
):
    """
    Calculate win and lose count by each race on melee results.
    """

    def __init__(self, queryset):
        super().__init__()
        self.set_queryset(queryset)

    def calculate(self):
        for result in self._queryset:
            league_win_and_lose_by_race = \
                self.get_or_create(result.league.name)
            league_win_and_lose_by_race.count(
                result.winner_race, result.loser_race
            )
        return self


class PlayerWinAndLoseByRaceCalculator(BaseWinAndLoseByRaceCalculator):
    def __init__(self, queryset):
        self.set_queryset(queryset)
        self.player_race = ''
        self.opponent_race = ''
        self.__calculated_data = WinAndLoseByRace()

    def calculate(self):
        """
        Set result variable to WinAndLoseByRace object.
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


class BaseRankManager(metaclass=ABCMeta):
    """
    Ranks on result queryset with given expressions from RankCategory classes.
    After you inherit this class, you must add RankCategory classes to it.
    """
    """
    TODO
    현재 매우 느림. 이유를 파악하자.
    """

    def __init__(self, queryset):
        self.queryset = queryset
        self.limit = 5
        self.rank_category_list = []
        self.ranked_results = {}

    def ranks_on_queryset(self):
        self.group_queryset_by_league__name_and_player__name()
        self.annotate_on_queryset_with_rank_category_list()
        self.order_queryset_each_rank_category()

    def group_queryset_by_league__name_and_player__name(self):
        self.queryset = self.queryset.values(
            'league__name',
            'player__name'
        ).order_by(
            'league__name',
            'player__name'
        )

    def annotate_on_queryset_with_rank_category_list(self):
        for rank_category in self.rank_category_list:
            self.queryset = rank_category.get_annotated_queryset(self.queryset)

    def order_queryset_each_rank_category(self):
        for rank_category in self.rank_category_list:
            category = rank_category.get_category_name()
            self.ranked_results.update({
                category: self.queryset.order_by(
                    'league__name',
                    F(category).desc(),
                    'player__name'
                ).values(
                    'league__name',
                    'player__name',
                    category
                )
            })

    def set_rank_category_list(self, *rank_category_list_args):
        self.rank_category_list = list(rank_category_list_args)

    def get_ranked_results(self):
        return self.ranked_results


class MeleeRankManager(BaseRankManager):
    def __init__(self, melee_result_queryset):
        super().__init__(melee_result_queryset)
        self.set_rank_category_list(
            WinCountRankCategory(),
            LoseCountRankCategory(),
            ResultCountRankCategory(),
            WinPercentageRankCategory(),
        )
        self.ranks_on_queryset()


class BaseRankCategory(metaclass=ABCMeta):
    def __init__(self, category_name):
        self.category_name = category_name

    @abstractmethod
    def get_annotated_queryset(self, queryset):
        pass

    def get_category_name(self):
        return self.category_name


class WinCountRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(category_name='win_count')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            win_count=Sum(
                Cast('is_win', output_field=IntegerField())
            )
        )


class LoseCountRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(category_name='lose_count')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            lose_count=Sum(
                1 - Cast('is_win', output_field=IntegerField())
            )
        )


class ResultCountRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(category_name='result_count')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            result_count=Count('id')
        )


class WinPercentageRankCategory(BaseRankCategory):
    def __init__(self):
        super().__init__(category_name='win_percentage')

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            win_percentage=Avg(
                Cast('is_win', output_field=IntegerField()) * 100
            )
        )
