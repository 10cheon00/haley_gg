from django.db import models


class MeleeResultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'league', 'map', 'player', 'winner', 'loser'
        ).filter(type__exact='melee')


class ProleagueResultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'league', 'map', 'player', 'winner', 'loser'
        ).filter(league__type='proleague')

    def get_melee_queryset(self):
        return self.get_queryset().filter(type='melee')


class StarleagueResultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'league', 'map', 'player', 'winner', 'loser'
        ).filter(league__type='starleague')

    def get_melee_queryset(self):
        return self.get_queryset().filter(type='melee')
