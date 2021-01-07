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
            ('T', 'Random'),
        )
    )
    joined_date = models.DateField(
        default=timezone.now
    )


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


class Map(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )


class Result(models.Model):
    date = models.DateField(
        default=timezone.now
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE
    )
    match_name = models.CharField(
        default='',
        max_length=100
    )
    map = models.ForeignKey(
        Map,
        on_delete=models.CASCADE
    ),
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE
    )
    win_state = models.BooleanField(
        default=False
    )
