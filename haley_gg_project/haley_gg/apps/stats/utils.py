from abc import ABCMeta
from abc import abstractmethod

from django.db.models import Avg
from django.db.models import F
from django.db.models import Q
from django.db.models import Count
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast


def slugify(text):
    """
    Slugify a given text.
    """
    non_url_safe = [
        '"', '#', '$', '%', '&', '+',
        ',', '/', ':', ';', '=', '?',
        '@', '[', '\\', ']', '^', '`',
        '{', '|', '}', '~', "'", ' ', '-'
    ]
    return text.translate(text.maketrans('', '', u''.join(non_url_safe)))


def remove_space(text):
    return text.replace(' ', '')


def calculate_percentage(numerator, denominator):
    """
    Get rate. Round to 3 decimal places.
    """
    try:
        return round(numerator / denominator * 100, 2)
    except ZeroDivisionError:
        return 0


def get_player_win_rate(results):
    """
    Get rate from player's result queryset with is_win field.
    """
    win_rate = results.values(
        'player__name'
    ).aggregate(
        win_rate=Avg(
            Cast('is_win', output_field=IntegerField()) * 100
        )
    )['win_rate']
    rounded_win_rate = round(win_rate, 1)
    return rounded_win_rate


class ResultsGroup(list):
    """
    Groups result data to distinguish matches.
    This model used in template to show results by match.
    """

    def __init__(self, name):
        self.__match_name = name

    def add_result(self, result):
        self.append(result)

    def get_results(self):
        return self

    def has_player(self, player):
        return player in [result.player.name for result in self.get_results()]

    def get_first_result(self):
        return self[0]

    @property
    def match_name(self):
        return self.__match_name


class ResultsGroupManager(list):
    """
    This manager groups results into ResultGroup by match name.
    In template, result must shown by matches, so grouping results is needed.
    """

    def __init__(self, result_queryset):
        """
        convert result queryset to results group.
        """
        for result in result_queryset:
            match_name = result.match_name()
            if not self.is_result_group_exists(match_name):
                self.add_results_group(match_name)
            results_group = self.get_result_group_with_match_name(match_name)
            results_group.add_result(result)

    def is_result_group_exists(self, match_name):
        """
        Returns True if result group with match name is exists.
        """
        for results_group in self:
            if results_group.match_name == match_name:
                return True
        return False

    def get_result_group_with_match_name(self, match_name):
        for results_group in self:
            if results_group.match_name == match_name:
                return results_group
        return None

    def get_results_groups_which_having_player(self, player):
        results_group_copy = self[:]
        for results_group in results_group_copy:
            if not results_group.has_player(player):
                results_group_copy.remove(results_group)
        return results_group_copy

    def add_results_group(self, match_name):
        self.append(ResultsGroup(match_name))

    def get_results_groups(self):
        return self


class WinAndResultCountByRace(dict):
    """
    This class shows player win count by opponent race.
    This class can be operated with two functions.
    To count all result, use save_all_result function.
    To count related only specific player results,
    use save_all_result_only_related_with_player function.
    """
    player_race = ''
    opponent_race = ''
    WIN_COUNT_INDEX = 0
    RESULT_COUNT_INDEX = 1

    def __init__(self):
        super().__init__()
        self.update({
            'T': {  # Winner's race
                'T':  # Loser's race
                [0,  # win_count
                 0],  # Result_count
                'Z': [0, 0], 'P': [0, 0]},
            'Z': {'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]},
            'P': {'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]}
        })

    def __iadd__(self, other):
        for player, oppoent_race_dict in self.items():
            for opponent in oppoent_race_dict.keys():
                self_data_list = self[player][opponent]
                other_data_list = other[player][opponent]
                self[player][opponent] = [
                    x + y for x, y in zip(self_data_list, other_data_list)
                ]
        return self

    def save_all_result(self, result_queryset):
        result_queryset = result_queryset.values(
            'race',
            'player_a_race',
            'player_b_race',
            'is_win'
        )
        for result in result_queryset:
            self.save_one_result(result)

    def save_all_result_only_related_with_player(
        self,
        result_queryset,
        player_name
    ):
        result_queryset = result_queryset.values(
            'player_a__name',
            'player_b__name',
            'race',
            'player_a_race',
            'player_b_race',
            'is_win'
        )
        for result in result_queryset:
            if self.is_result_related_with_player(result, player_name):
                self.save_one_result(result)

    def save_one_result(self, result):
        self.get_players_races(result)
        if result['is_win']:
            self.add_one_win_result()
        self.add_one_result()

    def get_players_races(self, result):
        if result['race'] is result['player_a_race']:
            self.player_race = result['player_a_race']
            self.opponent_race = result['player_b_race']
        else:
            self.player_race = result['player_b_race']
            self.opponent_race = result['player_a_race']

    def add_one_win_result(self):
        self[self.player_race][self.opponent_race][self.WIN_COUNT_INDEX] += 1

    def add_one_result(self):
        self[self.player_race][self.opponent_race][self.RESULT_COUNT_INDEX] += 1

    def is_result_related_with_player(self, result, player_name):
        return player_name in [
            result['player_a__name'], result['player_b__name']
        ]


"""
TODO    아래의 Streak함수 RankExpression에서 사용할 수 있도록 바꾸기
"""


def get_win_and_lose_streak(results):
    """
    Get streak in results each player.
    """
    grouped_results_by_player = get_grouped_results_dict_by_player(results)

    win_streaks = []
    lose_streaks = []
    for player_name, player_results in grouped_results_by_player.items():
        streak = get_player_streak(player_results)
        if streak > 0:
            win_streaks.append((player_name, streak))
        else:
            lose_streaks.append((player_name, -1 * streak))

    return {
        'win_streaks': sorted(win_streaks, key=lambda x: x[1], reverse=True),
        'lose_streaks': sorted(lose_streaks, key=lambda x: x[1], reverse=True)
    }


def get_grouped_results_dict_by_player(results):
    """
    Get results group by player name, without using ORM.
    """
    results = results.select_related('player')
    grouped_results_by_player = {}
    for result in results:
        if result.player.name not in grouped_results_by_player:
            grouped_results_by_player[result.player.name] = []
        grouped_results_by_player[result.player.name].append(result)
    return grouped_results_by_player


def get_player_streak(player_results):
    """
    Get player's streak with its results.
    """
    streak = 0
    previous_win_state = player_results[0].is_win
    for result in player_results:
        if previous_win_state is not result.is_win:
            # If win state changed, break.
            break
        if result.is_win:
            streak += 1
        else:
            streak -= 1
        previous_win_state = result.is_win
    return streak


class BaseRankManager(metaclass=ABCMeta):
    """
    Ranks on result queryset with given annotations from RankExpression classes.
    After you inherit this class, you must add RankExpression classes to it.
    """

    result_queryset = None
    limit = 5
    rank_expression_dict = {}
    annotated_result_dict = {}

    def get_ordered_annotated_result_dict_by_each_categories(self):
        self.convert_ranked_result_queryset_to_annotated_result_dict()
        return self.sort_annotated_result_dict_by_categories()

    def convert_ranked_result_queryset_to_annotated_result_dict(self):
        self.set_annotated_result_dict(
            self.get_result_queryset_annotate_with_rank_expression_dict()
        )

    def sort_annotated_result_dict_by_categories(self):
        """
        각 카테고리별로 내림차순 정렬.
        그런데 queryset.values()가 순수 딕셔너리가 아니더라.
        """
        result_dict = {}
        for category in self.rank_expression_dict.keys():
            result_dict.update({
                category:
                self.get_ordered_annotated_result_dict_by_category(category)
            })

        return result_dict

    def get_result_queryset_annotate_with_rank_expression_dict(self):
        return self.result_queryset.values(
            'player__name'
        ).order_by(
            'player__name'
        ).annotate(
            **self.rank_expression_dict  # convert dictionary to expression
        )

    def get_ordered_annotated_result_dict_by_category(self, category):
        if self.is_category_in_rank_expression_dict(category):
            return self.get_annotated_result_dict(
            ).order_by(
                F(category).desc()
            ).values(
                'player__name',
                category
            )
        else:
            return self.get_annotated_result_dict()

    def set_rank_expression_dict(self, *rank_expression_dict_args):
        for rank_expression_dict in rank_expression_dict_args:
            self.rank_expression_dict.update(rank_expression_dict)

    def set_result_queryset(self, result_queryset):
        self.result_queryset = result_queryset

    def set_annotated_result_dict(self, dict):
        self.annotated_result_dict = dict

    def get_annotated_result_dict(self):
        return self.annotated_result_dict

    def is_category_in_rank_expression_dict(self, category):
        return category in self.rank_expression_dict.keys()


class MeleeRankManager(BaseRankManager):
    def __init__(self, result_queryset):
        self.set_result_queryset(result_queryset)
        self.set_rank_expression_dict(
            WinCountRankExpressionDict(),
            LoseCountRankExpressionDict(),
            ResultCountRankExpressionDict(),
            WinRateRankExpressionDict(),
        )


class BaseRankExpressionDict(dict, metaclass=ABCMeta):
    """
    This class was abstracted to have different expression by rank category.
    If you inherit this class and define expression by rank category,
    you can used it in rank manager class.
    """


class WinCountRankExpressionDict(BaseRankExpressionDict):
    def __init__(self):
        self.update({
            'win_count':
            Sum(
                Cast('is_win', output_field=IntegerField())
            )
        })


class LoseCountRankExpressionDict(BaseRankExpressionDict):
    def __init__(self):
        self.update({
            'lose_count':
            Sum(
                Case(
                    When(
                        is_win=False, then=1
                    ),
                    default=0, output_field=IntegerField()
                )
            )
        })


class ResultCountRankExpressionDict(BaseRankExpressionDict):
    def __init__(self):
        self.update({
            'result_count':
            Count('id')
        })


class WinRateRankExpressionDict(BaseRankExpressionDict):
    def __init__(self):
        self.update({
            'win_rate':
            Avg(
                Cast('is_win', output_field=IntegerField()) * 100
            )
        })
