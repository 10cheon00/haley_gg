from django.db import models
from django.utils import timezone
from django.shortcuts import reverse

from ..Models.users import User
from ..Models.maps import Map

league_type_list = (
    ('starleague', '개인리그'),
    ('proleague', '프로리그'),
)

match_type_list = (
    ('one_on_one', '1대1'),
    ('top_and_bottom', '팀플'),
)

race_list = (
    ('T', 'Terran'),
    ('P', 'Protoss'),
    ('Z', 'Zerg'),
)


# All one on one match stored this type.
class Match(models.Model):
    # league name that indicate a league name such as Proleague, Starleague, etc...
    league_name = models.CharField(max_length=20, default="", null=False)

    # Round, dual tournament or something like that. Seems like game title
    # ex. Round 1, 16강 A조 ... etc
    name = models.CharField(max_length=50, default="", null=False)

    # set in match
    set = models.PositiveSmallIntegerField(default=1, null=False)

    # match date
    date = models.DateField(default=timezone.now, null=False)

    # map used in game
    map = models.ForeignKey(Map, on_delete=models.CASCADE, null=False)

    # remake for this match
    remark = models.CharField(max_length=50, default="", blank=True)

    #
    # to distinguish league, this model has a league_type field
    league_type = models.CharField(
        choices=league_type_list,
        default="",
        max_length=20)

    # is one-on-one match or top and bottom?
    match_type = models.CharField(
        choices=match_type_list,
        default="",
        max_length=20)

    class Meta:
        ordering = [
            '-league_name',
            '-date',
            '-name',
            '-set',
        ]

    def __str__(self):
        str = self.get_name()
        return ''.join(str)

    # Return match name in list type.
    def get_name(self):
        string = []
        string.append(str(self.date))
        string.append(' l ')
        string.append(str(self.league_name))
        string.append(' ')
        string.append(str(self.name))
        string.append(' ')
        string.append(str(self.set))
        return string

    def get_absolute_url(self, **kwargs):
        return reverse('haley_gg:match_list')


class Player(models.Model):
    # cannot comment this member. too hard to describe...
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=False)

    # is win?
    is_win = models.BooleanField(default=False)

    # player who in game
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False)

    # race in this match
    race = models.CharField(
        default="",
        max_length=10,
        choices=race_list,
        null=False)

    class Meta:
        ordering = ['match']

    def __str__(self):
        string = []
        string.append(self.match.__str__())
        string.append(' ')
        string.append(str(self.user))
        return ''.join(string)
