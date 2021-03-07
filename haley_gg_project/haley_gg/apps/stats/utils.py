from django.db.models import Avg
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Case
from django.db.models import When
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


def get_win_rate(results):
    """
    Get rate from result queryset with is_win field.
    """
    return results.annotate(
        win_rate=Avg(
            Cast('is_win', output_field=IntegerField()) * 100
        )
    )


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

    def __init__(self, result_queryset):
        """
        convert result queryset to results group.
        """
        for result in result_queryset:
            match_name = result.match_name()
            results_group = self.find_results_group(match_name)
            if results_group is None:
                results_group = self.add_results_group(ResultsGroup(match_name))
            results_group.add_result(result)

    def add_results_group(self, results_group):
        self.append(results_group)
        return results_group

    def get_results_groups(self):
        return self

    def find_results_group(self, match_name):
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


class WinAndResultCountByRace(dict):
    player_race = ''
    opponent_race = ''

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
        self[self.player_race][self.opponent_race][0] += 1

    def add_one_result(self):
        self[self.player_race][self.opponent_race][1] += 1

    def is_result_related_with_player(self, result, player_name):
        return player_name in [
            result['player_a__name'], result['player_b__name']
        ]


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


def get_results_group_by_player_name(results):
    """
    Get results what grouped by player name.
    """
    return results.values('player__name').order_by('player__name')


def get_players_result_count(results):
    """
    Get player's result count that grouped by its name.
    """
    return get_results_group_by_player_name(results).annotate(
        # Add criteria for same rate player.
        result_count=Count('id')
    )


def get_players_of_win_rate(results):
    """
    Get all player's win rate.
    """
    return get_win_rate(
        get_players_result_count(results)
    ).order_by(
        '-win_rate', '-result_count'
    ).values(
        'player__name', 'win_rate', 'result_count'
    )


def get_players_of_result_count(results):
    """
    Get all player's result count.
    """
    return get_players_result_count(
        results
    ).order_by('-result_count').values('player__name', 'result_count')


def get_win_and_lose_count(results):
    """
    Get win and lose count of results.
    """
    return get_results_group_by_player_name(
        results
    ).annotate(
        win_count=Sum(
            Cast('is_win', output_field=IntegerField())
        ),
        lose_count=Sum(
            Case(
                When(
                    is_win=False, then=1
                ),
                default=0, output_field=IntegerField()
            )
        )
    ).values('player__name', 'win_count', 'lose_count')


def get_top_n_players(results, player_number):
    """
    Get top n players of each category.
    """
    win_and_lose_count = get_win_and_lose_count(results)
    win_and_lose_streak = get_win_and_lose_streak(results)
    return {
        'win_count':
        win_and_lose_count.order_by('-win_count')[:player_number],
        'lose_count':
        win_and_lose_count.order_by('-lose_count')[:player_number],
        'win_rate':
        get_players_of_win_rate(results)[:player_number],
        'result_count':
        get_players_of_result_count(results)[:player_number],
        'win_streak':
        win_and_lose_streak['win_streaks'][:player_number],
        'lose_streak':
        win_and_lose_streak['lose_streaks'][:player_number],
    }

