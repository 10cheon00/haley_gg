from abc import ABCMeta, abstractmethod

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


class Match(list):
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


class BaseDataDict(dict, metaclass=ABCMeta):
    """
    객체 내에 해당하는 key가 없을 경우 미리 정의된 객체를 생성한다.
    """

    @abstractmethod
    def save(self):
        pass

    def get_or_create(self, key):
        return self.setdefault(key, self.create_data_class())

    def create_data_class(self):
        return self.data_class()


class MatchDict(BaseDataDict):
    """
    match name을 기준으로 Match들을 관리한다.
    """
    data_class = Match

    def save(self, result):
        match = self.get_or_create(result.get_match_name())
        match.add_result(result)


class LeagueMatchDict(BaseDataDict):
    """
    league name을 기준으로 MatchDict들을 관리한다.
    """

    data_class = MatchDict

    def save(self, result):
        match_dict = self.get_or_create(result.league.name)
        match_dict.save(result)


class LeagueMatchClassifier:
    def __init__(self, queryset):
        self.__result_queryset = queryset
        self.__league_match_dict = LeagueMatchDict()

    def classify(self):
        for result in self.__result_queryset:
            self.__league_match_dict.save(result)
        return self.__league_match_dict


class PlayerMatchClassifier:
    def __init__(self, queryset):
        self.__result_queryset = queryset
        self.__match_dict = MatchDict()

    def classify(self):
        for result in self.__result_queryset:
            self.__match_dict.save(result)
        return self.__match_dict


def stringify_streak_count(streak_count):
    streak_string = '연패'

    if streak_count > 0:
        streak_string = '연승'

    streak_count = abs(streak_count)
    return f'{streak_count}{streak_string}'
