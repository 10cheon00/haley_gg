from django.db import models
from django.urls import reverse


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

    # Calculate statistics on victory by race.
    # statistics on victory to be calculated.
    # - T vsZ, P
    # - Z vsP, (T)
    # - P vs(T, Z)
    # () is already calculated.
    # Only works when match_type is melee.
    def get_statistics_on_winning_rate(self):
        winning_rate_dict = {
            'T': {
                # first element is number of wins.
                # second is winning rate.
                'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]
            },
            'Z': {
                'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]
            },
            'P': {
                'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]
            },
        }
        for match in self.match_set.all():
            winner_race = ''
            loser_race = ''
            for player in match.player_set.all():
                if player.is_win:
                    winner_race = player.race
                else:
                    loser_race = player.race
            # If winner's race same as loser's race, just add.
            # Same race match just have number of matches.
            winning_rate_dict[winner_race][loser_race][0] += 1
        # 이제 누가 어느 종족을 이겼는지 winning_rate_dict에 다 저장되어있다.
        # So, winning_rate_dict has all data who win or lose.
        race_list = ['T', 'P', 'Z']
        for winner in race_list:
            for loser in race_list:
                # if races are same, do not calculate.
                if winner == loser:
                    continue

                win_count = winning_rate_dict[winner][loser][0]
                loser_count = winning_rate_dict[loser][winner][0]
                match_count = win_count + loser_count
                try:
                    winning_rate_dict[winner][loser][1] = round(
                        win_count / match_count * 100, 2)
                except ZeroDivisionError:
                    winning_rate_dict[winner][loser][1] = 0
        return winning_rate_dict


# Map type for insert proleague results.
class MapType(models.Model):
    # map type name
    type_name = models.CharField(max_length=10, default="", null=False)
    # map list
    map_list = models.ManyToManyField(Map)

    class Meta:
        ordering = ['type_name']
