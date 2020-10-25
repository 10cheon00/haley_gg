from django.db import models
from django.utils import timezone
from django.shortcuts import reverse

from ..Models.users import User
from ..Models.maps import Map


class Match(models.Model):
    # league name that indicated league such as Proleague, Starleague, etc...
    league_name = models.CharField(max_length=20, default="", null=False)
    # Round, dual tournament or something like that. Seems like game title
    name = models.CharField(max_length=50, default="", null=False)
    # set in match
    set = models.PositiveSmallIntegerField(default=1, null=False)
    # match date
    date = models.DateField(default=timezone.now, null=False)
    # map used in game
    map = models.ForeignKey(Map, on_delete=models.CASCADE, null=False)

    class Meta:
        ordering = [
            '-league_name',
            '-name',
            '-set',
            '-date',
        ]

    def __str__(self):
        str = self.get_name()
        return ''.join(str)

    # Return match name in list type.
    def get_name(self):
        string = []
        string.append(str(self.league_name))
        string.append(' ')
        string.append(str(self.name))
        string.append(' ')
        string.append(str(self.set))
        string.append('경기')
        return string

    def get_absolute_url(self, **kwargs):
        return reverse('haley_gg:match_list')


class Player(models.Model):
    # player who in game
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False)
    # cannot comment this member. too hard to describe...
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=False)
    # is win?
    is_win = models.BooleanField(default=False)

    class Meta:
        ordering = ['match']

    def __str__(self):
        string = []
        string.append(' ')
        string.append(str(self.user))
        return ''.join(string)
