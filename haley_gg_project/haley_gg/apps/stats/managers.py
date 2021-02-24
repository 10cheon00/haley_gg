from django.db import models


class MeleeManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().filter(type__exact='melee')
