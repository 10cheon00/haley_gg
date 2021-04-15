from django.db.models import Avg
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
    win_rate = results.aggregate(
        win_rate=Avg(
            Cast('is_win', output_field=IntegerField()) * 100
        )
    )['win_rate']
    return win_rate


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

    def has_player(self, player_name):
        return player_name in [result.player.name for result in self]

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
        convert all result queryset to results group.
        """
        for result in result_queryset:
            match_name = result.match_name()
            if not self.is_result_group_exists(match_name):
                self.add_results_group(match_name)
            results_group = self.get_result_group_with_match_name(match_name)
            results_group.add_result(result)

    def get_results_groups_which_having_player(self, player_name):
        results_group_copy = self[:]
        results_group_having_player = [
            result_group for result_group in results_group_copy
            if result_group.has_player(player_name)
        ]
        return results_group_having_player

    def is_result_group_exists(self, match_name):
        """
        Returns True if result group with match name is exists.
        """
        for results_group in self:
            if results_group.match_name == match_name:
                return True
        return False

    def add_results_group(self, match_name):
        self.append(ResultsGroup(match_name))

    def get_result_group_with_match_name(self, match_name):
        for results_group in self:
            if results_group.match_name == match_name:
                return results_group
        return None

    def get_results_groups(self):
        return self


def stringify_streak_count(streak_count):
    streak_string = '연패'

    if streak_count > 0:
        streak_string = '연승'

    streak_count = abs(streak_count)
    return f'{streak_count}{streak_string}'
