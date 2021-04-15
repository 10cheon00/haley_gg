from abc import ABCMeta
from abc import abstractmethod

from django.db.models import F
from django.db.models import Count
from django.db.models import Avg
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast


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


class ResultsQuerysetDeduplicator:
    def __init__(self, results_queryset):
        self.queryset = results_queryset
        self.run()

    def run(self):
        self.distinct_results_queryset()
        self.convert_results_queryset_to_dictionary()

    def distinct_results_queryset(self):
        self.queryset = self.queryset.order_by(
            'league_id', 'title', 'round'
        ).distinct(
            'league_id', 'title', 'round'
        )

    def get_result(self):
        return self.queryset

    def convert_results_queryset_to_dictionary(self):
        self.queryset = self.queryset.values()


class BaseWinAndLoseByRaceCalculator(metaclass=ABCMeta):
    result = None
    win_and_lose_by_race = None

    def __init__(self, queryset):
        self.deduplicator = ResultsQuerysetDeduplicator(queryset)
        self.initialize_win_and_lose_by_race()
        self.calculate()

    @abstractmethod
    def initialize_win_and_lose_by_race(self):
        pass

    @abstractmethod
    def calculate(self):
        pass

    def get_result(self):
        return self.win_and_lose_by_race


class PlayerWinAndLoseByRaceCalculator(BaseWinAndLoseByRaceCalculator):
    def __init__(self, queryset):
        super().__init__(queryset)

    def initialize_win_and_lose_by_race(self):
        self.win_and_lose_by_race = WinAndLoseByRace()

    def calculate(self):
        """
        여기선 WinAndLoseByRace의 Winner 항목이 플레이어가 된다.
        그래서 winner를 player로 항상 설정해야한다.
        """
        for result in self.deduplicator.get_result():
            # Suppose player were won.
            player_race = result['winner_race']
            opponent_race = result['loser_race']

            # But player lose, swap both race.
            if not result['is_win']:
                player_race, opponent_race = opponent_race, player_race

            self.win_and_lose_by_race.count_only_winner(
                player_race, opponent_race
            )


class TotalLeagueWinAndLoseByRaceCalculator(
    BaseWinAndLoseByRaceCalculator
):
    def __init__(self, queryset):
        super().__init__(queryset)

    def initialize_win_and_lose_by_race(self):
        self.win_and_lose_by_race_dict = {}

    def calculate(self):
        for result in self.deduplicator.get_result():
            # If league's WinAndLoseByRace doesn't exist, create it.
            if not self.is_exists_WinAndLoseByRace_related(
                result['league_id']
            ):
                self.win_and_lose_by_race_dict[result['league_id']] = \
                    WinAndLoseByRace()

            self.win_and_lose_by_race_dict[result['league_id']].count(
                result['winner_race'],
                result['loser_race']
            )

    def is_exists_WinAndLoseByRace_related(self, league_id):
        return league_id in self.win_and_lose_by_race_dict

    # override to return all of league data.
    def get_result(self):
        return self.win_and_lose_by_race_dict


class TotalMapWinAndLoseByRaceCalculator(
    BaseWinAndLoseByRaceCalculator
):
    """
    TODO
    특정 맵이 아닌 모든 맵으로 바꿀 생각이다.
    맵A
    |-- 리그1에서 승패
    `-- 리그2에서 승패
    맵B
    |-- ...
    `-- ...
    맵C
    |--
    `--
    모든 맵의 정보를 갖고 있어야 하고, 맵마다 리그별 정보를 갖고 있어야 한다.
    """


class BaseRankManager(metaclass=ABCMeta):
    """
    Ranks on result queryset with given expressions from RankCategory classes.
    After you inherit this class, you must add RankCategory classes to it.
    """
    """
    """
    queryset = None
    limit = 5
    rank_category_list = []
    ranked_results = {}

    def __init__(self, queryset):
        self.queryset = queryset

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
    category_name = ''

    @abstractmethod
    def get_annotated_queryset(self, queryset):
        pass

    def get_category_name(self):
        return self.category_name


class WinCountRankCategory(BaseRankCategory):
    category_name = 'win_count'

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            win_count=Sum(
                Cast('is_win', output_field=IntegerField())
            )
        )


class LoseCountRankCategory(BaseRankCategory):
    category_name = 'lose_count'

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            lose_count=Sum(
                1 - Cast('is_win', output_field=IntegerField())
            )
        )


class ResultCountRankCategory(BaseRankCategory):
    category_name = 'result_count'

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            result_count=Count('id')
        )


class WinPercentageRankCategory(BaseRankCategory):
    category_name = 'win_percentage'

    def get_annotated_queryset(self, queryset):
        return queryset.annotate(
            win_percentage=Avg(
                Cast('is_win', output_field=IntegerField()) * 100
            )
        )