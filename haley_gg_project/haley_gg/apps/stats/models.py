from django.shortcuts import reverse
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.db.models import Value
from django.db.models import F
from django.db.models import Sum
from django.db.models import Min
from django.db.models import Avg
from django.db.models import Window
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models.functions import RowNumber
from django.db.models.functions import Cast

from haley_gg.apps.stats.managers import MeleeManager
from haley_gg.apps.stats.utils import slugify
from haley_gg.apps.stats.utils import remove_space
# from haley_gg.apps.stats.utils import calculate_percentage
from haley_gg.apps.stats.utils import get_player_win_rate
from haley_gg.apps.stats.utils import ResultsGroupManager
from haley_gg.apps.stats.utils import WinAndResultCountByRace
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

    career = models.TextField(default='아직 잠재력이 드러나지 않았습니다...')

    tier = models.CharField(
        default='rookie',
        max_length=50,
        choices=(
            ('major', '메이저'),
            ('minor', '마이너'),
            ('rookie', '루키')
        )
    )

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
            'win_rate': get_player_win_rate(self.results),
            'win_rate_by_race_dict': win_and_result_count_by_race,
            'streak': Result.get_player_streak(self.name),
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


"""
True
True
False
False
True
...
"""
"""
TODO

1. Form에서 Result를 생성할 때 Elo도 같이 계산하도록 수정.
2. Result가 Elo를 외래키로 갖고 있어야 하는지에 대한 생각 정리.
    Result는 한 가지의 Elo를 갖는다. 즉 1대1 관계.
    외래키로 만들어봐야 비용만 낭비되는거 아닌가... OneonOneKey?
    개인 전적 페이지에서 Elo그래프를 보여주고, 전적 리스트에서도 보여줘야 한다.
    누구의 elo인지도 구분할 수 있어야 하고...
    Result에 elo값만 저장하는 필드만 만들고??

     -> 당장은 미룸. 어차피 Result에서 조회만 하기 때문에 나중가서 생각하기.
     -> 팀플레이때문에 Elo 필드는 null=True로 해야겠다.

3. Elo 계산식을 갖다 쓰되 K값 계산식 참고.

3-1. K값 계산식에 연승값이 참조되는데, 연승 및 연패는 어떻게 계산할지 생각 정리.


- 계산식
m = 연승/연패값 (절댓값)
k = 32 + 1.641^(m-1) - 1
w = 승리 여부 ( 승=1, 패=0 )
변동 Elo = myElo +
    k * (
        w - (
            1 /
            (
                1 + 10^((opElo-myElo)/400)
            )
        )
    )

ELO를 구현하기 위해 먼저 구현해야할 것
1. 연승식
2. 리그통계함수
3. 통계객체


"""


class Elo(models.Model):
    date = models.DateField(default=timezone.now)

    value = models.IntegerField(default=0)

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='elo_list'
    )

    class Meta:
        ordering = ['date']


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
        win_and_result_count_by_race.save_all_result(melee_results)  # makes simillar queries!
        rank_manager = MeleeRankManager(melee_results)
        return {
            'league_name': self.slugify_str(),
            'grouped_league_results': ResultsGroupManager(results),
            # 'race_relative_count': win_and_result_count_by_race,
            'top_players':
            rank_manager.get_ordered_annotated_result_dict_by_each_categories()  # makes simillar quries!
        }


class Map(models.Model):
    name = models.CharField(
        default='',
        max_length=50
    )

    type = models.CharField(
        default='melee',
        max_length=50,
        choices=(
            ('melee', '밀리맵'),
            ('teamplay', '팀플맵'),
        )
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
            'top_players': 
            rank_manager.get_ordered_annotated_result_dict_by_each_categories()
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
    teamplay_win = models.PositiveSmallIntegerField(
        default=0
    )
    teamplay_lose = models.PositiveSmallIntegerField(
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
                self.teamplay_win += 1
            else:
                self.teamplay_lose += 1
        self.save()

    def get_total_win(self):
        return self.melee_win + self.teamplay_win

    def get_total_lose(self):
        return self.melee_lose + self.teamplay_lose


class Result(models.Model):
    date = models.DateField(
        default=timezone.now,
        db_index=True
    )

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
            ('teamplay', '팀플')
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
            F('date').desc(),
            F('title').desc(),
            F('round').desc(),
            F('is_win').desc(),
        ]
        indexes = [
            models.Index(fields=['date', 'title', 'round', 'is_win'])
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

    @classmethod
    def get_numbering_results_partition_by_player(cls):
        queryset = cls.melee.annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=F('player__name'),
                order_by=cls._meta.ordering
            )
        ).order_by(*cls._meta.ordering)
        return queryset

    @classmethod
    def get_numbering_results_partition_by_player_with_player_name(
        cls,
        player_name
    ):
        queryset = cls.melee.filter(player__name=player_name).annotate(
            row_number=Window(
                expression=RowNumber(),
                order_by=cls._meta.ordering
            )
        ).order_by(*cls._meta.ordering)
        return queryset

    @classmethod
    def get_streak(cls):
        queryset = cls.get_numbering_results_partition_by_player()
        distinct_player_is_win = queryset.filter(
            player__name=OuterRef('player__name')
        ).order_by(
            'is_win',
            *cls._meta.ordering
        ).distinct('is_win').values('row_number')

        queryset = queryset.annotate(
            win_row_number=distinct_player_is_win[:1],
            lose_row_number=distinct_player_is_win[1:2],
        ).annotate(
            streak=F('win_row_number') - F('lose_row_number')
        ).order_by(
            'player__name'
        ).distinct(
            'player__name'
        ).values('player__name', 'streak')
        return queryset

    @classmethod
    def get_player_streak(cls, player_name):
        queryset = \
            cls.get_numbering_results_partition_by_player_with_player_name(
                player_name
            )

        distinct_player_is_win = queryset.filter(
            player__name=player_name
        ).order_by(
            'is_win',
            *cls._meta.ordering
        ).distinct('is_win').values('row_number')

        queryset = queryset.annotate(
            win_row_number=distinct_player_is_win[:1],
            lose_row_number=distinct_player_is_win[1:2],
        ).annotate(
            streak=F('win_row_number') - F('lose_row_number')
        ).order_by(
            'player__name'
        ).distinct(
            'player__name'
        ).values('player__name', 'streak')
        return queryset
