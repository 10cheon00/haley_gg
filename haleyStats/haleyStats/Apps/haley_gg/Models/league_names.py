from django.db import models


class LeagueName(models.Model):
    name = models.CharField(max_length=50, default="", unique=True)
