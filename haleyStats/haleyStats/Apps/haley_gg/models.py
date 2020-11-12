# haley_gg/models.py

from django.db import models
from django.utils import timezone
from django.urls import reverse

race_list = (
    ('T', 'Terran'),
    ('P', 'Protoss'),
    ('Z', 'Zerg'),
    ('R', 'Random')
)


class User(models.Model):
    # name that same as Starcraft Nickname
    name = models.CharField(
        max_length=30,
        default="")

    # joined date
    joined_date = models.DateField(
        default=timezone.now)

    # User's career
    career = models.TextField(
        default="아직 잠재력이 드러나지 않았습니다...")

    # User's race
    most_race = models.CharField(
        max_length=10,
        choices=race_list)

    class Meta:
        ordering = ['-joined_date', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("haley_gg:users_detail", kwargs={"name": self.name})

    # Get win rate no matter of player's race.
    def get_winning_rate(self, queryset):
        if queryset:
            match_count = queryset.count()
            match_win_count = queryset.filter(is_win=True).count()
            try:
                win_rate = round(match_win_count / match_count * 100, 2)
            except ZeroDivisionError:
                return 0
            return win_rate
        return 0

    # Get winning_rate by race
    def get_winning_rate_by_race(self, melee_match_list):
        rates = {
            'T': 0,
            'P': 0,
            'Z': 0,
        }
        if melee_match_list:
            victory_count_dict = {
                'T': 0,
                'P': 0,
                'Z': 0,
            }
            match_count_dict = {
                'T': 0,
                'P': 0,
                'Z': 0,
            }
            # rates of victory by races.
            # 플레이어와 연관된 매치리스트를 돌면서 연결된 상대의 종족을 읽는다.
            for match in melee_match_list:
                # This function works only when match type is melee.
                if match.match_type != 'melee':
                    continue

                for player in match.player_set.all():
                    if player.user != self:
                        # count by opponent race.
                        match_count_dict[player.race] += 1
                        # if player wins, count by opponent race.
                        if not player.is_win:
                            victory_count_dict[player.race] += 1
            for key in rates.keys():
                try:
                    # Get player_s race vs Z,P winning_rate.
                    rates[key] = round(
                        victory_count_dict[key] / match_count_dict[key] * 100,
                        2)
                except ZeroDivisionError:
                    rates[key] = 0
        return rates


class Map(models.Model):
    # map name
    name = models.CharField(
        max_length=30,
        default="")

    # map files(ex: .scx, .scm, or zip files)
    file = models.FileField(
        upload_to="Maps/files/")

    # map images
    image = models.ImageField(
        upload_to="Maps/images/",
        default="Maps/images/default.jpg")

    # match count on this map
    match_count = models.PositiveIntegerField(
        default=0)

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
    type_name = models.CharField(
        max_length=10,
        default="")

    # map list
    map_list = models.ManyToManyField(
        Map)

    class Meta:
        ordering = ['type_name']


class League(models.Model):
    # league name that indicate a league name such as Proleague, Starleague, etc...
    name = models.CharField(
        max_length=20,
        default="")

    # to distinguish league, this model has a league_type field
    type = models.CharField(
        max_length=20,
        choices=(
            ("proleague", "프로리그"),
            ("starleague", "스타리그"),
        ),
        default="")

    class Meta:
        ordering = [
            'name'
        ]


# All one on one match stored this type.
class Match(models.Model):
    # league
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE)

    # Round, dual tournament or something like that. Seems like game title
    # ex. Round 1, 16강 A조 ... etc
    name = models.CharField(
        max_length=30,
        default="",
        blank=True)

    # additional description such as set, ace match, winner's match etc ...
    description = models.CharField(
        max_length=50,
        default="",
        blank=True)

    # match date
    date = models.DateField(
        default=timezone.now,
        blank=True)

    # map used in match
    map = models.ForeignKey(
        Map,
        on_delete=models.CASCADE,
        blank=True)

    # remake for this match
    remark = models.CharField(
        max_length=50,
        default="",
        blank=True)

    # Below fields are not shown to user.
    # is one-on-one match or top and bottom?
    match_type = models.CharField(
        max_length=20,
        choices=(
            ('one-on-one', '1대1'),
            ('top-and-bottom', '팀플'),
        ),
        default="")

    class Meta:
        ordering = [
            '-date',
            '-name',
            '-description',
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
        string.append(str(self.description))
        return string

    def get_absolute_url(self, **kwargs):
        return reverse('haley_gg:match_list')


class Player(models.Model):
    # cannot comment this member. too hard to describe...
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE)

    # is win?
    is_win = models.BooleanField(
        default=False)

    # player who in game
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)

    # race in this match
    race = models.CharField(
        default="",
        max_length=10,
        choices=race_list[:-1])

    class Meta:
        ordering = ['match']

    def __str__(self):
        string = []
        string.append(self.match.__str__())
        string.append(' ')
        string.append(str(self.user))
        return ''.join(string)
