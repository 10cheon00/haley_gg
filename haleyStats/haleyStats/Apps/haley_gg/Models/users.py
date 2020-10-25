from django.db import models
from django.utils import timezone
from django.urls import reverse

race_list = (
    ('T', 'Terran'),
    ('P', 'Protoss'),
    ('Z', 'Zerg'),
    ('R', 'Random')
)


class User(models.Model):
    # name that same as Starcraft Nickname
    name = models.CharField(max_length=30, default="", null=False)
    # joined date
    joined_date = models.DateField(default=timezone.now, null=False)
    # User's career
    career = models.TextField(default="추가 바람.")
    # User's race
    most_race = models.CharField(max_length=10, choices=race_list, null=False)

    class Meta:
        ordering = ['-joined_date', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name="unique_user_name")
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("haley_gg:users_detail", kwargs={"name": self.name})
