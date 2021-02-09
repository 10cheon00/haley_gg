from django.db import models
from django.utils import timezone
from django.shortcuts import reverse

from haley_gg.apps.stats.utils import slugify, remove_space


class Player(models.Model):
    # When create or save player name,
    # remove blanks from name string.
    name = models.CharField(
        default='',
        max_length=50
    )

    most_race = models.CharField(
        default='',
        max_length=50,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
            ('R', 'Random'),
        )
    )

    joined_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    # Save name what removed spaces.
    def save(self, *args, **kwargs):
        self.name = remove_space(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stats:player', kwargs={'name': self.name})


# Maybe, this model will be have op 8 players, or team.
class League(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )

    type = models.CharField(
        default='',
        max_length=50,
        choices=(
            ('proleague', '프로리그'),
            ('starleague', '스타리그'),
            ('otherleague', '그외 리그'),
        )
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def slugify_str(self):
        return slugify(self.name)


class Map(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class ProleagueTeam(models.Model):
    name = models.CharField(
        default='',
        max_length=100,
        unique=True
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'proleague'},
        related_name='team_list'
    )
    players = models.ManyToManyField(
        Player
    )
    # This value is sum of set score.
    points = models.SmallIntegerField(
        default=0
    )
    melee_win_counts = models.PositiveSmallIntegerField(
        default=0
    )
    melee_lose_counts = models.PositiveSmallIntegerField(
        default=0
    )
    top_and_bottom_win_counts = models.PositiveSmallIntegerField(
        default=0
    )
    top_and_bottom_lose_counts = models.PositiveSmallIntegerField(
        default=0
    )

    class Meta:
        ordering = [
            '-points'
        ]

    def __str__(self):
        return self.name

    # update counts.
    def save_result(self, result):
        if result.win_state:
            self.points += 1
        else:
            self.points -= 1

        if result.type == 'melee':
            if result.win_state:
                self.melee_win_counts += 1
            else:
                self.melee_lose_counts += 1
        else:
            if result.win_state:
                self.top_and_bottom_win_counts += 1
            else:
                self.top_and_bottom_lose_counts += 1
        self.save()

    def get_total_win(self):
        return self.melee_win_counts + self.top_and_bottom_win_counts

    def get_total_lose(self):
        return self.melee_lose_counts + self.top_and_bottom_lose_counts


class Result(models.Model):
    date = models.DateField(default=timezone.now)

    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='result_list'
    )

    title = models.CharField(
        default='',
        max_length=100
    )

    round = models.CharField(
        default='',
        max_length=100
    )

    map = models.ForeignKey(
        Map,
        on_delete=models.CASCADE)

    type = models.CharField(
        default='',
        max_length=20,
        choices=(
            ('melee', '밀리'),
            ('top_and_bottom', '팀플')
        )
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE
    )

    race = models.CharField(
        default='',
        max_length=10,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
        )
    )

    win_state = models.BooleanField(default=False)

    remarks = models.CharField(
        default='',
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            '-date',
            '-title',
            '-round',
            '-win_state',
        ]

    def __str__(self):
        str_list = [
            str(self.date),
            ' | ',
            self.match_name(),
            ' ',
            self.map.__str__(),
            ' | ',
            self.type,
            ' | ',
            self.player.__str__(),
            '(',
            self.race,
            ')',
        ]
        return ''.join(str_list)

    def match_name(self):
        str_list = [
            self.league.__str__(),
            ' ',
            self.title,
            ' ',
            self.round,
        ]
        return ''.join(str_list)
