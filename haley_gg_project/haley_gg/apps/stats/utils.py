from django.db.models import Avg
from django.db.models import IntegerField
from django.db.models.functions import Cast


def remove_space(text):
    return text.replace(' ', '')


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


def get_deduplicated_result_queryset(queryset):
    """
    Process distinct on queryset.
    Return values are available for both melee and teamplay statistic manager.
    """
    field_list = [
        'league__name',
        'title',
        'round',
        'winner_race',
        'loser_race'
    ]
    return queryset.order_by(*field_list).distinct(*field_list)


class ResultGroup(list):
    """
    같은 경기 이름을 가진 result들을 모아놓는 자료구조.
    """

    def __init__(self):
        self.winner = []
        self.loser = []

    def add_result(self, result):
        self.append(result)
        self.winner.append(result.winner)
        self.loser.append(result.loser)

    def get_first_result(self):
        return self[0]

    def get_winners(self):
        return self.winner

    def get_losers(self):
        return self.loser


class BaseDataClassifier(dict):
    """
    객체 내에 해당하는 key가 없을 경우 미리 정의된 객체를 생성한다.
    """

    def __init__(self):
        self.data_structure = dict

    def get_or_create(self, key):
        return self.setdefault(key, self.data_structure())


class ResultGroupDataClassifier(BaseDataClassifier):
    """
    match name을 기준으로 ResultGroup들을 관리한다.
    """

    def __init__(self):
        self.data_structure = ResultGroup


class LeagueDataClassifier(BaseDataClassifier):
    """
    league name을 기준으로 ResultGroupDataClassifier들을 관리한다.
    """

    def __init__(self):
        self.data_structure = ResultGroupDataClassifier


class ResultGroupManager(ResultGroupDataClassifier):
    def __init__(self, result_queryset):
        super().__init__()
        self.__result_queryset = result_queryset

    def groups(self):
        for result in self.__result_queryset:
            result_group = self.get_result_group(result)
            result_group.add_result(result)
        return self

    def get_result_group(self, result):
        result_group = self.get_or_create(result.get_match_name())
        return result_group


class LeagueResultGroupManager(LeagueDataClassifier):
    """
    리그를 기준으로 ResultGroup들을 관리한다.
    결과값은 시간순으로 정렬되어 있는 result_group들이어야 한다.
    """

    def __init__(self, result_queryset):
        """
        Convert all result queryset to results group.
        """
        super().__init__()
        self.__result_queryset = result_queryset

    def groups(self):
        for result in self.__result_queryset:
            result_group = self.get_result_group(result)
            result_group.add_result(result)
        return self

    def get_result_group(self, result):
        league_result_group_list = self.get_or_create(result.league.name)
        result_group = league_result_group_list.get_or_create(result.get_match_name())
        return result_group


def stringify_streak_count(streak_count):
    streak_string = '연패'

    if streak_count > 0:
        streak_string = '연승'

    streak_count = abs(streak_count)
    return f'{streak_count}{streak_string}'
