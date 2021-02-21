from django.db.models import Avg
from django.db.models.functions import Cast
from django.db.models import IntegerField

from haley_gg.apps.stats.utils_object import GroupedResults
from haley_gg.apps.stats.utils_object import RaceAndWinState
from haley_gg.apps.stats.utils_object import WinAndResultCountByRace


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
    """
    Remove space character in text what given.
    """
    return text.replace(' ', '')


def get_grouped_results_with_match_name(results):
    """
    Groups result data by match name.
    """
    grouped_results_dict = {}
    for result in results:
        name = result.match_name()
        if name not in grouped_results_dict:
            grouped_results_dict[name] = GroupedResults()
        grouped_results_dict[name].add_result(result)
    return grouped_results_dict


def get_grouped_results_that_has_player(grouped_results_dict, player):
    """
    Do filtering grouped result data.
    Deletes all result data from grouped result data without a given player.
    """
    for key in list(grouped_results_dict.keys()):
        # If grouped_result_list not contain this player, remove it.
        if not grouped_results_dict[key].has_player(player):
            del grouped_results_dict[key]
    return grouped_results_dict


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
    Get rate from result model with is_win field.
    """
    print(results.annotate(
        win_rate=Avg(
            Cast('is_win', output_field=IntegerField()) * 100
        )
    ))
    return results.annotate(
        win_rate=Avg(
            Cast('is_win', output_field=IntegerField()) * 100
        )
    )


def get_grouped_RaceAndWinState(results):
    """
    results을 RaceAndWinState형태로 전환한다.
    전환한 RaceAndWinState를 player name을 따라 분류한다.
    결과값으로 player name에 따라,
    RaceAndWinState형태로 전환된 result들을 분류한 dictionary를 반환한다.
    """
    total_grouped_RaceAndWinState_objects = {}
    results_values = results.values(
        'player__name',
        'player_a_race',
        'player_b_race',
        'is_win'
    )

    for result in results_values:
        player_name = result['player__name']
        if player_name not in total_grouped_RaceAndWinState_objects:
            total_grouped_RaceAndWinState_objects[player_name] = []

        total_grouped_RaceAndWinState_objects[player_name].append(
            convert_result_to_RaceAndWinState(result)
        )

    return total_grouped_RaceAndWinState_objects


def convert_result_to_RaceAndWinState(result):
    """
    convert result to RaceAndWinState object.

    RaceAndWinState
    |-- player_race
    |-- opponent_race
    `-- win_state
    """
    player_a_race = result['player_a_race']
    player_b_race = result['player_b_race']
    if not result['is_win']:
        player_a_race, player_b_race = player_b_race, player_a_race

    return RaceAndWinState(
        player_a_race,
        player_b_race,
        result['is_win']
    )


def convert_RaceAndWinStates_to_WinAndResultCountByRace_object(
    RaceAndWinState_object
):
    """
    Convert RaceAndWinState to WinAndResultCountByRace object.
    This function returns number of wins, results by relative race.
    """

    WinAndResultCountByRace_object = WinAndResultCountByRace()
    player_race = RaceAndWinState_object.player_race
    opponent_race = RaceAndWinState_object.opponent_race

    if RaceAndWinState_object.is_win:
        WinAndResultCountByRace_object[player_race][opponent_race][0] += 1
    WinAndResultCountByRace_object[player_race][opponent_race][1] += 1
    return WinAndResultCountByRace_object


def get_sum_of_RaceAndWinStates(grouped_RaceAndWinState_objects):
    """
    Add all WinAndResultCountByRace objects in grouped RaceAndWinState_objects.
    """
    sum_of_WinAndResultCountByRace_object = WinAndResultCountByRace()
    for RaceAndWinState_object in grouped_RaceAndWinState_objects:
        converted_data = \
            convert_RaceAndWinStates_to_WinAndResultCountByRace_object(
                RaceAndWinState_object
            )
        sum_of_WinAndResultCountByRace_object += converted_data
    return sum_of_WinAndResultCountByRace_object


def get_total_sum_of_RaceAndWinStates(results):
    """
    Calculate number of win, result counts in all results by relative race.
    Firstly, groups results by player name.
    Secondly, add all RaceAndWinState in grouped results.
    Lastly, returns added data in WinAndResultCountByRace type.
    """
    total_of_WinAndResultCountByRace_object = WinAndResultCountByRace()
    grouped_RaceAndWinState = get_grouped_RaceAndWinState(results)

    for grouped_RaceAndWinState_object in grouped_RaceAndWinState.values():
        total_of_WinAndResultCountByRace_object += get_sum_of_RaceAndWinStates(
            grouped_RaceAndWinState_object
        )

    return total_of_WinAndResultCountByRace_object
