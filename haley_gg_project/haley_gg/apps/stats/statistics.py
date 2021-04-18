from abc import ABCMeta
from abc import abstractmethod

from django.db.models import F
from django.db.models import Count
from django.db.models import Avg
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast


class WinAndLoseByRaceData(dict):
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

    def run(self):
        # self.select_related_on_queryset()
        self.distinct_results_queryset()
        self.convert_results_queryset_to_dictionary()

    def distinct_results_queryset(self):
        self.queryset = self.queryset.order_by(
            'league_id', 'title', 'round'
        ).distinct(
            'league_id', 'title', 'round'
        )

    def convert_results_queryset_to_dictionary(self):
        self.queryset = self.queryset.values(
            'league__name',
            'title',
            'round',
            'is_win',
            'winner_race',
            'loser_race',
            'map__name'
        )

    def get_result(self):
        return self.queryset


class BaseWinAndLoseByRaceCalculator(metaclass=ABCMeta):
    def __init__(self, queryset):
        self.queryset = queryset
        self.deduplicate_queryset()
        self.calculated_data = {}
        self.calculate()

    def deduplicate_queryset(self):
        self.deduplicator = ResultsQuerysetDeduplicator(self.queryset)
        self.deduplicator.run()
        self.queryset = self.deduplicator.get_result()

    @abstractmethod
    def calculate(self):
        pass

    def get_result(self):
        return self.calculated_data


class PlayerWinAndLoseByRaceCalculator(BaseWinAndLoseByRaceCalculator):

    def __init__(self, queryset):
        super().__init__(queryset)
        self.player_race = ''
        self.opponent_race = ''

    def calculate(self):
        """
        Set result variable to WinAndLoseByRace object.
        Because, this object only count player results.
        So result is not categorize with keys
        such as league name, map name etc.
        """
        self.calculated_data = WinAndLoseByRaceData()
        for result in self.queryset:
            self.set_races(result)

            self.calculated_data.count_only_winner(
                self.player_race, self.opponent_race
            )

    def set_races(self, result):
        """
        In this calculator, fix up winner as player.
        """
        # Suppose player were won.
        self.player_race = result['winner_race']
        self.opponent_race = result['loser_race']

        # But player lose, swap both race.
        if not result['is_win']:
            self.player_race, self.opponent_race = \
                self.opponent_race, self.player_race


class TotalLeagueWinAndLoseByRaceCalculator(
    BaseWinAndLoseByRaceCalculator
):

    def __init__(self, queryset):
        super().__init__(queryset)
        self.league = ''

    def calculate(self):
        for result in self.queryset:
            self.add_new_item_if_no_key_exists_in_calculated_data(result)

            self.calculated_data[self.league].count(
                result['winner_race'], result['loser_race']
            )

    def add_new_item_if_no_key_exists_in_calculated_data(self, result):
        self.set_league_key(result)

        if not self.is_league_key_exists_in_calculated_data():
            self.create_value_with_league_key_in_calculated_data()

    def set_league_key(self, result):
        self.league = result['league__name']

    def is_league_key_exists_in_calculated_data(self):
        return self.league in self.calculated_data

    def create_value_with_league_key_in_calculated_data(self):
        self.calculated_data[self.league] = WinAndLoseByRaceData()


class TotalMapWinAndLoseByRaceCalculator(
    BaseWinAndLoseByRaceCalculator
):

    def __init__(self, queryset):
        super().__init__(queryset)
        self.map = ''
        self.league = ''

    def calculate(self):
        for result in self.queryset:
            self.add_new_item_if_no_key_exists_in_calculated_data(result)

            self.calculated_data[self.map][self.league].count(
                result['winner_race'], result['loser_race']
            )

    def add_new_item_if_no_key_exists_in_calculated_data(self, result):
        # First, check map key is exists.
        self.set_map_key(result)
        if not self.is_map_key_exists_in_calculated_data():
            self.create_dictionary_with_map_key_in_calculated_data()

        # Secondary, check league key is exists with map key.
        self.set_league_key(result)
        if not self.is_league_key_exists_in_calculated_data_of_map():
            self.create_value_with_league_key_in_calculated_data_of_map()

    def set_map_key(self, result):
        self.map = result['map__name']

    def is_map_key_exists_in_calculated_data(self):
        return self.map in self.calculated_data

    def create_dictionary_with_map_key_in_calculated_data(self):
        self.calculated_data[self.map] = {}

    def set_league_key(self, result):
        self.league = result['league__name']

    def is_league_key_exists_in_calculated_data_of_map(self):
        return self.league in self.calculated_data[self.map]

    def create_value_with_league_key_in_calculated_data_of_map(self):
        self.calculated_data[self.map][self.league] = WinAndLoseByRaceData()


class BaseRankManager(metaclass=ABCMeta):
    """
    Ranks on result queryset with given expressions from RankCategory classes.
    After you inherit this class, you must add RankCategory classes to it.
    """
    """
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
