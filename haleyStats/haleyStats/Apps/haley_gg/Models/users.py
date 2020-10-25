from django.db import models
from django.utils import timezone
from django.urls import reverse

import math

race_list = (
    ('T', 'Terran'),
    ('P', 'Protoss'),
    ('Z', 'Zerg'),
    ('R', 'Random')
)


class User(models.Model):
    # name that same as Starcraft Nickname
    name = models.CharField(max_length=30, default="", null=False)
    # joined date
    joined_date = models.DateField(default=timezone.now, null=False)
    # User's career
    career = models.TextField(default="아직 잠재력이 드러나지 않았습니다...")
    # User's race
    most_race = models.CharField(max_length=10, choices=race_list, null=False)

    class Meta:
        ordering = ['-joined_date', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("haley_gg:users_detail", kwargs={"name": self.name})

    def get_win_rate(self, queryset):
        if queryset:
            try:
                match_counts = queryset.count()
                match_win_counts = queryset.filter(is_win=True).count()
                win_rate = math.floor(match_win_counts / match_counts * 100)
            except ZeroDivisionError:
                return 0
            return win_rate
        return 0
