from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Avg
from django.db.models.functions import Cast
from django.utils import timezone
from django.shortcuts import reverse

from haley_gg.apps.stats.managers import MeleeManager
from haley_gg.apps.stats.utils import slugify
from haley_gg.apps.stats.utils import remove_space
# from haley_gg.apps.stats.utils import calculate_percentage
from haley_gg.apps.stats.utils import get_win_rate
from haley_gg.apps.stats.utils import ResultsGroupManager
from haley_gg.apps.stats.utils import WinAndResultCountByRace
from haley_gg.apps.stats.utils import get_results_group_by_player_name
from haley_gg.apps.stats.utils import get_player_streak
from haley_gg.apps.stats.utils import MeleeRankManager


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

    career = models.TextField(default="아직 잠재력이 드러나지 않았습니다...")

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
        win_and_result_count_by_race = WinAndResultCountByRace()
        win_and_result_count_by_race.save_all_result_only_related_with_player(
            Result.melee.all(),
            self.name
        )
        return {
            'win_rate': get_win_rate(
                get_results_group_by_player_name(self.results)
            ).first()['win_rate'],
            'win_rate_by_race_dict': win_and_result_count_by_race,
            'streak': get_player_streak(self.results.all()),
        }

    def get_career_and_titles(self):
        import re
        career_titles = re.findall(r'\[(.*?)\]', self.career)
        stars = 0
        badges = []
        for title in career_titles:
            color = ''
            if '준우승' in title:
                stars += 1
                color = 'info'
            elif '우승' in title:
                color = 'success'
            else:
                color = 'secondary'

            badges.append(
                f'<div class="badge badge-{color}">{title}</div>'
            )
        return {
            'career': {
                'stars': range(stars),
                'badges': badges,
                'converted_career':
                self.career.replace('[', '').replace(']', '')
            }
        }

    def versus(self, opponent):
        """
        1. 연관된 전적 조회
        2. 승, 패 조회
        3. 그 외 Elo, 랭킹들 조회
        """
        results = Result.objects.filter(
            Q(type='melee') &
            (Q(player_a=self.id) & Q(player_b=opponent.id)) |
            (Q(player_a=opponent.id) & Q(player_b=self.id))
        ).select_related('league', 'map', 'player')
        context = {
            'results': ResultsGroupManager(results),
            'statistics': results.filter(player=self.id).aggregate(
                win_count=Sum(
                    Cast('is_win', output_field=models.IntegerField())
                ),
                win_rate=Avg(
                    Cast('is_win', output_field=models.IntegerField()) * 100
                )
            ),
        }
        return context


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

    @classmethod
    def get_league_statistics(cls, leagues):
        league_list = []
        for league in leagues:
            league_list.append(league.get_statistics())
        return {
            'leagues': leagues,
            'league_list': league_list,
        }

    def get_statistics(self):
        # it must be get melee results, but this code isn't!
        results = self.results.all()
        melee_results = self.results.filter(type="melee")
        win_and_result_count_by_race = WinAndResultCountByRace()
        win_and_result_count_by_race.save_all_result(melee_results)
        rank_manager = MeleeRankManager(melee_results)
        return {
            'league_name': self.slugify_str(),
            'grouped_league_results': ResultsGroupManager(results),
            'race_relative_count': win_and_result_count_by_race,
            'top_players': rank_manager.get_top_players()
        }


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

        melee_results = self.results.filter(type="melee")

        # Get top 5 players of statistic items.
        win_and_result_count_by_race = WinAndResultCountByRace()
        win_and_result_count_by_race.save_all_result(melee_results)
        rank_manager = MeleeRankManager(melee_results)
        return {
            'win_rate_by_race': win_and_result_count_by_race,
            'top_players': rank_manager.get_top_players()
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
            '):',
            str(self.is_win),
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
