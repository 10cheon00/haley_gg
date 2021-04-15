from django.db import models


class MeleeManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().filter(type__exact='melee')

    def get_proleague_results(self):
        return self.get_queryset().filter(league__type='proleague')

    def get_starleague_results(self):
        return self.get_queryset().filter(league__type='starleague')
