from django.db import models
from django.urls import reverse

import math


class Map(models.Model):

    # map name
    name = models.CharField(max_length=30, default="")
    # map files(ex: .scx, .scm, or zip files)
    file = models.FileField(upload_to="Maps/files/", null=False)
    # map images
    image = models.ImageField(upload_to="Maps/images/",
                              default="Maps/images/default.jpg", null=False)
    # match count on this map
    match_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-match_count', 'name']

    def get_absolute_url(self):
        return reverse('haley_gg:maps_detail', kwargs={"name": self.name})

    def __str__(self):
        return self.name

    # Count matches related this map.
    def update_match_count(self):
        self.match_count = self.match_set.all().count()
        self.save()

    # Calculate odds by race.
    # Odds to be calculated.
    # - T vsZ, P
    # - Z vsP, (T)
    # - P vs(T, Z)
    # () is already calculated.
    # Only works when match_type is melee.
    def odds_dict_by_race(self):
        odds_dict_by_race = {
            'T': {'Z': 0, 'P': 0},
            'P': {'T': 0, 'Z': 0},
            'Z': {'T': 0, 'P': 0},
        }
        victory_count_dict = {
            'T': {'Z': 0, 'P': 0},
            'P': {'T': 0, 'Z': 0},
            'Z': {'T': 0, 'P': 0},
        }
        for match in self.match_set.all():
            win_race = ''
            lose_race = ''
            for player in match.player_set.all():
                if player.is_win:
                    win_race = player.race
                else:
                    lose_race = player.race
            if win_race != lose_race:
                victory_count_dict[win_race][lose_race] += 1
        # 이제 누가 어느 종족을 이겼는지 victory_count_dict에 다 저장되어있다.
        race_list = ['T', 'P', 'Z']
        for winner in race_list:
            for loser in race_list:
                # if races are same, do not calculate.
                if winner == loser:
                    continue

                win_count = victory_count_dict[winner][loser]
                loser_count = victory_count_dict[loser][winner]
                match_count = win_count + loser_count
                try:
                    odds_dict_by_race[winner][loser] = math.floor(
                        win_count / match_count * 100)
                except ZeroDivisionError:
                    odds_dict_by_race[winner][loser] = 0
        return odds_dict_by_race
