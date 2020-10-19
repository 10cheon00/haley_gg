from django.db import models
from django.utils import timezone

from ..Models.league_names import LeagueName
from ..Models.users import User
from ..Models.maps import Map


class Match(models.Model):
    class Meta:
        abstract = True

    league_name = models.ForeignKey(
        LeagueName, on_delete=models.CASCADE, null=False)
    match_name = models.CharField(max_length=50, default="", null=False)
    match_set = models.PositiveSmallIntegerField(default=1, null=False)
    match_date = models.TimeField(default=timezone.now, null=False)
    match_map = models.ForeignKey(Map, on_delete=models.CASCADE, null=False)


class Melee(Match):
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    winner_race = models.CharField(max_length=10, default="", null=False)
    loser = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    loser_race = models.CharField(max_length=10, default="", null=False)

    def __str__(self):
        return self.league_name + self.match_name + 'set ' + self.match_set
