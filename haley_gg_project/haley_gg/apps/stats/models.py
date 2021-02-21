from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import reverse


from haley_gg.apps.stats.managers import MeleeManager
from haley_gg.apps.stats.utils import slugify
from haley_gg.apps.stats.utils import remove_space
# from haley_gg.apps.stats.utils import calculate_percentage
from haley_gg.apps.stats.utils import get_win_rate
from haley_gg.apps.stats.utils import get_grouped_RaceAndWinState
from haley_gg.apps.stats.utils import get_sum_of_RaceAndWinStates
from haley_gg.apps.stats.utils import get_total_sum_of_RaceAndWinStates


class Player(models.Model):
    # When create or save player name,
    # remove blanks from name string.
    name = models.CharField(
        default='',
        max_length=50
    )

    most_race = models.CharField(
        default='',
        max_length=50,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
            ('R', 'Random'),
        )
    )

    joined_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    # Save name what removed spaces.
    def save(self, *args, **kwargs):
        self.name = remove_space(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stats:player', kwargs={'name': self.name})

    def get_statistics(self):
        """
        총 승률
        최근 10경기 승률
        종족별 승률
        """
        # If no results from player, below sequences are skipped.
        if not self.results.exists():
            return {}

        # Win rate of total results.
        win_rate = get_win_rate(
            Result.objects.values('player').order_by('player')
        ).filter(  # filter for this player.
            player=self
        ).first()['win_rate']

        count_dict = get_sum_of_RaceAndWinStates(
            get_grouped_RaceAndWinState(Result.melee.all())[self.name]
        )
        statistic_dict = {
            'win_rate': win_rate,
            'win_rate_by_race_dict': count_dict
        }
        return statistic_dict


class League(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )

    type = models.CharField(
        default='',
        max_length=50,
        choices=(
            ('proleague', '프로리그'),
            ('starleague', '스타리그'),
            ('otherleague', '그외 리그'),
        )
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def slugify_str(self):
        return slugify(self.name)


class Map(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stats:map', kwargs={'name': self.name})

    def get_statistics(self):
        # Get all rate by race
        # Need exception for teamplay map.

        results = self.results.all()

        # Get Top 5 player rate on this map.
        top_5_players = get_win_rate(
            self.results.values(
                'player__name'
            ).order_by(
                'player__name'
            ).annotate(
                # Add criteria for same rate player.
                result_count=Count('id')
            )
        ).order_by('-win_rate', '-result_count')[:5]

        return {
            'win_rate_by_race': get_total_sum_of_RaceAndWinStates(
                results
            ),
            'top_5_players': top_5_players
        }


class ProleagueTeam(models.Model):
    name = models.CharField(
        default='',
        max_length=100,
        unique=True
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'proleague'},
        related_name='teams'
    )
    players = models.ManyToManyField(
        Player
    )
    # This value is sum of set score.
    points = models.SmallIntegerField(
        default=0
    )
    melee_win = models.PositiveSmallIntegerField(
        default=0
    )
    melee_lose = models.PositiveSmallIntegerField(
        default=0
    )
    top_and_bottom_win = models.PositiveSmallIntegerField(
        default=0
    )
    top_and_bottom_lose = models.PositiveSmallIntegerField(
        default=0
    )

    class Meta:
        ordering = [
            '-points'
        ]

    def __str__(self):
        return self.name

    # update counts.
    def save_result(self, result):
        if result.is_win:
            self.points += 1
        else:
            self.points -= 1

        if result.type == 'melee':
            if result.is_win:
                self.melee_win += 1
            else:
                self.melee_lose += 1
        else:
            if result.is_win:
                self.top_and_bottom_win += 1
            else:
                self.top_and_bottom_lose += 1
        self.save()

    def get_total_win(self):
        return self.melee_win + self.top_and_bottom_win

    def get_total_lose(self):
        return self.melee_lose + self.top_and_bottom_lose


class Result(models.Model):
    date = models.DateField(default=timezone.now)

    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='results'
    )

    title = models.CharField(
        default='',
        max_length=100
    )

    round = models.CharField(
        default='',
        max_length=100
    )

    map = models.ForeignKey(
        Map,
        related_name='results',
        on_delete=models.CASCADE)

    type = models.CharField(
        default='',
        max_length=20,
        choices=(
            ('melee', '밀리'),
            ('top_and_bottom', '팀플')
        )
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='results'
    )
    race = models.CharField(
        default='',
        max_length=10,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
        )
    )
    # for convinience.
    player_a = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='results_player_a'
    )

    player_b = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='results_player_b'
    )

    player_a_race = models.CharField(
        default='',
        max_length=10,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
        )
    )

    player_b_race = models.CharField(
        default='',
        max_length=10,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
        )
    )

    is_win = models.BooleanField(default=False)

    remarks = models.CharField(
        default='',
        max_length=100,
        null=True,
        blank=True,
    )

    objects = models.Manager()
    melee = MeleeManager()

    class Meta:
        ordering = [
            '-date',
            '-title',
            '-round',
            '-is_win',
        ]

    def __str__(self):
        str_list = [
            str(self.date),
            ' | ',
            self.match_name(),
            ' ',
            self.map.__str__(),
            ' | ',
            self.type,
            ' | ',
            self.player.__str__(),
            '(',
            self.race,
            ')',
        ]
        return ''.join(str_list)

    def match_name(self):
        str_list = [
            self.league.__str__(),
            ' ',
            self.title,
            ' ',
            self.round,
        ]
        return ''.join(str_list)
