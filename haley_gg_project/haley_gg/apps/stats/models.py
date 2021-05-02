from django.shortcuts import reverse
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.db.models import F
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Avg
from django.db.models import Window
from django.db.models import OuterRef
from django.db.models.functions import RowNumber
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast

from haley_gg.apps.stats.managers import MeleeResultManager
from haley_gg.apps.stats.managers import ProleagueResultManager
from haley_gg.apps.stats.managers import StarleagueResultManager
from haley_gg.apps.stats.utils import remove_space
from haley_gg.apps.stats.utils import get_player_win_rate
from haley_gg.apps.stats.utils import get_deduplicated_result_queryset
from haley_gg.apps.stats.utils import PlayerMatchClassifier
from haley_gg.apps.stats.utils import LeagueMatchClassifier
from haley_gg.apps.stats.utils import stringify_streak_count
from haley_gg.apps.stats.statistics import LeagueMeleeRank
from haley_gg.apps.stats.statistics import PlayerRaceStatisticsCalculator
from haley_gg.apps.stats.statistics import LeagueRaceStatisticsCalculator
from haley_gg.apps.stats.statistics import MapRaceStatisticsCalculator


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

    def get_result_group(self):
        """
        TODO
        이 플레이어의 전적중에 팀플이 껴있는 경우
        연결된 다른 result도 갖고 와야한다.
        """
        player_of_match = PlayerMatchClassifier(
            Result.objects.filter(
                Q(winner_id=self.id) |
                Q(loser_id=self.id)
            ).select_related(
                'league', 'map', 'player', 'winner', 'loser'
            )
        )
        return {
            'match_list': player_of_match.classify()
        }

    def get_statistics(self):
        # If no results from player, below sequences are skipped.
        if not self.results.exists():
            return {}

        melee_results = self.results.filter(type='melee')
        win_and_lose_by_race_calculator = \
            PlayerRaceStatisticsCalculator(melee_results)

        streak_count = Result.get_player_streak_count(self.name)

        return {
            'win_rate':
            get_player_win_rate(self.results),
            'race_statistics':
            win_and_lose_by_race_calculator.calculate(),
            'streak':
            stringify_streak_count(streak_count),
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
        results = Result.melee.filter(
            (Q(winner=self.id) & Q(loser=opponent.id)) |
            (Q(winner=opponent.id) & Q(loser=self.id))
        ).select_related('league', 'map', 'player', 'winner', 'loser')

        player_of_match = PlayerMatchClassifier(results)

        context = {
            'results': player_of_match.classify(),
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

    @classmethod
    def get_proleague_statistics(cls):
        cls.league_list = League.objects.filter(type='proleague').only('name')
        cls.league_queryset = Result.proleague

        return cls.get_statistics()

    @classmethod
    def get_starleague_statistics(cls):
        cls.league_list = League.objects.filter(type='starleague').only('name')
        cls.league_queryset = Result.starleague

        return cls.get_statistics()

    @classmethod
    def get_statistics(cls):
        match_classifier = LeagueMatchClassifier(cls.league_queryset.all())
        cls.match_dict = match_classifier.classify()

        race_statistics_calculator = \
            LeagueRaceStatisticsCalculator(
                cls.league_queryset.get_melee_queryset()
            )
        cls.race_statistics_dict = \
            race_statistics_calculator.calculate()

        melee_rank = LeagueMeleeRank(cls.league_queryset.get_melee_queryset())
        cls.rank_data_dict = melee_rank.ranks()

        league_statistics = {}

        for league in cls.league_list:
            race_statistics = \
                cls.race_statistics_dict.get_or_create(league.name)
            matches = cls.match_dict.get_or_create(league.name)
            rank_data = cls.rank_data_dict.get_or_create(league.name)

            league_statistics[league.name] = {
                'race_statistics': race_statistics,
                'matches': matches,
                'rank': rank_data,
            }
        return league_statistics


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

    def get_result_count(self):
        if self.is_teamplay_map():
            return '팀플맵은 집계하지 않습니다.'
        return get_deduplicated_result_queryset(self.results).count()

    def is_teamplay_map(self):
        return self.type == 'teamplay'

    @classmethod
    def get_total_map_statistics(cls):
        race_statistics_calculator = \
            MapRaceStatisticsCalculator(Result.melee)
        race_statistics_dict = \
            race_statistics_calculator.calculate()

        map_statistics = {}
        for map in Map.objects.only('name', 'type'):
            if map.is_teamplay_map():
                map_statistics[map] = {}
                continue

            map_statistics[map] = race_statistics_dict.get(map.name)

        return map_statistics

    def get_statistics(self):
        context = {}
        context['statistics'] = self.get_race_statistics()
        return context

    def get_race_statistics(self):
        if self.is_teamplay_map():
            return {}

        race_statistics_calculator = \
            LeagueRaceStatisticsCalculator(self.results)
        race_statistics_dict = \
            race_statistics_calculator.calculate()

        map_race_statistics = {}
        for league in League.objects.only('name'):
            map_race_statistics[league.name] = \
                race_statistics_dict.get(league.name)

        return map_race_statistics


class ProleagueTeam(models.Model):
    """
    TODO
    form에서 전적을 저장할 때 연결된 팀에도 결과를 누적하도록 수정.
    """

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
    )

    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='results'
    )

    title = models.CharField(
        default='',
        max_length=100,
    )

    round = models.CharField(
        default='',
        max_length=100,
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
    winner = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='results_winner'
    )

    loser = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='results_loser'
    )

    winner_race = models.CharField(
        default='',
        max_length=10,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
        )
    )

    loser_race = models.CharField(
        default='',
        max_length=10,
        choices=(
            ('T', 'Terran'),
            ('P', 'Protoss'),
            ('Z', 'Zerg'),
        )
    )

    is_win = models.BooleanField(
        default=False,
    )

    remarks = models.CharField(
        default='',
        max_length=100,
        null=True,
        blank=True,
    )

    objects = models.Manager()
    melee = MeleeResultManager()
    proleague = ProleagueResultManager()
    starleague = StarleagueResultManager()

    class Meta:
        ordering = [
            F('date').desc(),
            F('title').desc(),
            F('round').desc(),
            F('is_win').desc(),
        ]

    def __str__(self):
        str_list = [
            str(self.date),
            ' | ',
            self.get_match_name(),
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

    def get_match_name(self):
        str_list = [
            self.league.__str__(),
            ' ',
            self.title,
            ' ',
            self.round,
        ]
        return ''.join(str_list)

    results_queryset = None
    numbered_queryset = None
    numbered_most_recent_win_and_lose_queryset = None
    streak_queryset = None

    @classmethod
    def get_all_player_streak_count(cls):
        """
        How to get player's streaks?

        1.  Give row numbers to all results.
            It sorted in ascending order by date,
            partitioned by player name.
        2.  Find a most recent win and lose result,
            annotates its row number to queryset.
        3.  Substract win result's row number to lose result's row number.
            It is streak!
        """
        cls.set_results_queryset_to_all_results_queryset()
        cls.calculate_streak_count()

        return cls.streak_queryset

    @classmethod
    def set_results_queryset_to_all_results_queryset(cls):
        cls.results_queryset = Result.objects.all()

    @classmethod
    def get_player_streak_count(cls, player_name):
        cls.filter_only_result_queryset_related_with_player(player_name)
        cls.calculate_streak_count()
        return cls.streak_queryset.first()['count']

    @classmethod
    def filter_only_result_queryset_related_with_player(cls, player_name):
        cls.results_queryset = Result.objects.filter(
            player__name__iexact=player_name
        )

    @classmethod
    def calculate_streak_count(cls):
        cls.numbering_on_results_queryset_partition_by_player()
        cls.find_most_recent_win_and_lose_row_number_queryset()
        cls.calculate_streak_count_with_win_and_lose_row_number_queryset()

    @classmethod
    def numbering_on_results_queryset_partition_by_player(cls):
        cls.numbered_queryset = cls.results_queryset.annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=F('player__name'),
                order_by=cls._meta.ordering
            )
        ).order_by(*cls._meta.ordering)

    @classmethod
    def find_most_recent_win_and_lose_row_number_queryset(cls):
        cls.numbered_most_recent_win_and_lose_queryset = \
            cls.numbered_queryset.filter(
                player__name=OuterRef('player__name')
            ).order_by(
                'is_win',
                *cls._meta.ordering
            ).distinct('is_win').values('row_number')

    @classmethod
    def calculate_streak_count_with_win_and_lose_row_number_queryset(cls):
        cls.streak_queryset = cls.numbered_queryset.annotate(
            win_row_number=cls.numbered_most_recent_win_and_lose_queryset[:1],
            lose_row_number=cls.numbered_most_recent_win_and_lose_queryset[1:2],
        ).annotate(
            count=Coalesce(
                F('win_row_number'),
                0
            ) - Coalesce(
                F('lose_row_number'),
                0
            )
        ).order_by(
            'player__name'
        ).distinct(
            'player__name'
        ).values(
            'player__name',
            'count'
        )
