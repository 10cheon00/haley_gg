from django.db import models


class MeleeMatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='one_on_one')


class TeamMatchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='top_and_bottom')


class MeleePlayerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'match',
            'user',
        ).filter(match__type='one_on_one')
