from django.db import models
from django.utils import timezone
from django.urls import reverse
# Create your models here.


class User(models.Model):
    class Meta:
        ordering = ['-joined_date']

    user_name = models.CharField(max_length=30, default="")
    joined_date = models.DateField(default=timezone.now)
    career = models.TextField(default="추가 바람.")
    most_race = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.user_name

    def get_Absolute_Url(self):
        return reverse("users:detail", kwargs={"name": self.user_name})
