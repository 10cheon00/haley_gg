from django.db import models
from django.urls import reverse
# Create your models here.


class Map(models.Model):
    # Must change unique to UniqueConstraint.
    # And add Case-Insensitive to UniqueConstraint.condition.
    name = models.CharField(max_length=30, default="", unique=True)
    match_counts = models.IntegerField(default=0)
    file = models.FileField(upload_to="Maps/files/", null=True)
    image = models.ImageField(upload_to="Maps/images/",
                              default="Maps/images/default.jpg",
                              null=False)

    def get_absolute_url(self):
        return reverse('haley_gg:maps_detail', kwargs={"name": self.name})

    def __str__(self):
        return self.name
