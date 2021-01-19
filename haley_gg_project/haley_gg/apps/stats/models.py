from django.db import models
from django.utils import timezone


class Player(models.Model):
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


class Map(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Result(models.Model):
    date = models.DateField(default=timezone.now)

    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE
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

    class Meta:
        ordering = [
            'date',
            'title',
            'round',
            'win_state',
        ]

    def __str__(self):
        str_list = [
            str(self.date),
            ' | ',
            self.league.__str__(),
            ' ',
            self.title,
            ' ',
            self.round,
            ' ',
            self.map.__str__(),
            ' | ',
            self.player.__str__(),
            '(',
            self.race,
            ')',
        ]
        return ''.join(str_list)
