
class RaceAndWinState:
    """
    Used in showing statistics for calculating win rate from result data.
    This object has player race, opponent race, win state.
    """

    def __init__(self, player_race, opponent_race, win_state):
        self.__player_race = player_race
        self.__opponent_race = opponent_race
        self.__win_state = win_state

    @property
    def player_race(self):
        return self.__player_race

    @property
    def opponent_race(self):
        return self.__opponent_race

    @property
    def is_win(self):
        return self.__win_state


class WinAndResultCountByRace(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
