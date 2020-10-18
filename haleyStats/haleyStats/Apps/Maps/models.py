from django.db import models
from django.urls import reverse
# Create your models here.


class Map(models.Model):
    name = models.CharField(max_length=30, default="", unique=True)
    match_count = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('maps:detail', kwargs={"name": self.name})

    def __str__(self):
        return self.name
