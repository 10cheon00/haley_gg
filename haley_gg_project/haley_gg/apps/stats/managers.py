from django.db import models


class MeleeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='melee')
