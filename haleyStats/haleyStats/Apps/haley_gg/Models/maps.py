from django.db import models
from django.urls import reverse
# Create your models here.


class Map(models.Model):

    # map name
    name = models.CharField(max_length=30, default="")
    # counts of match in this map.
    match_counts = models.IntegerField(default=0)
    # map files(ex: .scx, .scm, or zip files)
    file = models.FileField(upload_to="Maps/files/", null=False)
    # map images
    image = models.ImageField(upload_to="Maps/images/",
                              default="Maps/images/default.jpg", null=False)

    class Meta:
        ordering = ['-match_counts']
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_map_name')
        ]

    def get_absolute_url(self):
        return reverse('haley_gg:maps_detail', kwargs={"name": self.name})

    def __str__(self):
        return self.name
