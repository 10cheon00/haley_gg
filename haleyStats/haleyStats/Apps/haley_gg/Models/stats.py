from django.db import models
from django.utils import timezone
from django.shortcuts import reverse

from ..Models.users import User
from ..Models.maps import Map


class Match(models.Model):
    class Meta:
        ordering = [
            '-league_name',
            '-name',
            '-set',
            '-date',
        ]

    league_name = models.CharField(max_length=20, default="", null=False)
    name = models.CharField(max_length=50, default="", null=False)
    set = models.PositiveSmallIntegerField(default=1, null=False)
    date = models.DateField(default=timezone.now, null=False)
    map = models.ForeignKey(Map, on_delete=models.CASCADE, null=False)

    def __str__(self):
        str = self.get_name()
        return ''.join(str)

    def get_name(self):
        string = []
        string.append(str(self.league_name))
        string.append(' ')
        string.append(str(self.name))
        string.append(' ')
        string.append(str(self.set))
        string.append('경기')
        return string

    def get_match_of(self, date):
        return self.objects.filter(date__exact=date)

    def get_match_of_user(self, user):
        return self.objects.filter(user__exact=user)

    def get_absolute_url(self, **kwargs):
        return reverse('haley_gg:match_list')


class Player(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=False)
    is_win = models.BooleanField(default=False)

    def __str__(self):
        string = []
        string.append(' ')
        string.append(str(self.user))
        return ''.join(string)

# Post
#  - title, content, author, created_date
#
# Author
#  - name
#
# Comment
#  - Key to Post, Key to Author, content
# melee, team 모델에 관해 생각좀 해야겠다. 구조가 이게 맞는건지.. 외래키에서 막힌다.
# team은 여러 player들로 구성되어 있을텐데 승리한 팀과 패배한 팀을 어떻게 구성할건지...