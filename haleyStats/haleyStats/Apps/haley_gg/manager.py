from django.db import models


class MeleeMatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(match_type='one_on_one')


class TeamMatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(match_type='top_and_bottom')
