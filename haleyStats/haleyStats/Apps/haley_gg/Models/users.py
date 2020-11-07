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
    career = models.TextField(default="아직 잠재력이 드러나지 않았습니다...")
    # User's race
    most_race = models.CharField(max_length=10, choices=race_list, null=False)

    class Meta:
        ordering = ['-joined_date', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("haley_gg:users_detail", kwargs={"name": self.name})

    # Get win rate no matter of player's race.
    def get_winning_rate(self, queryset):
        if queryset:
            match_count = queryset.count()
            match_win_count = queryset.filter(is_win=True).count()
            try:
                win_rate = round(match_win_count / match_count * 100, 2)
            except ZeroDivisionError:
                return 0
            return win_rate
        return 0

    # Get winning_rate by race
    def get_winning_rate_by_race(self, melee_match_list):
        rates = {
            'T': 0,
            'P': 0,
            'Z': 0,
        }
        if melee_match_list:
            victory_count_dict = {
                'T': 0,
                'P': 0,
                'Z': 0,
            }
            match_count_dict = {
                'T': 0,
                'P': 0,
                'Z': 0,
            }
            # rates of victory by races.
            # 플레이어와 연관된 매치리스트를 돌면서 연결된 상대의 종족을 읽는다.
            for match in melee_match_list:
                # This function works only when match type is melee.
                if match.match_type != 'melee':
                    continue

                for player in match.player_set.all():
                    if player.user != self:
                        # count by opponent race.
                        match_count_dict[player.race] += 1
                        # if player wins, count by opponent race.
                        if not player.is_win:
                            victory_count_dict[player.race] += 1
            for key in rates.keys():
                try:
                    # Get player_s race vs Z,P winning_rate.
                    rates[key] = round(
                        victory_count_dict[key] / match_count_dict[key] * 100,
                        2)
                except ZeroDivisionError:
                    rates[key] = 0
        return rates
