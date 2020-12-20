# haley_gg/models.py
from django.db import models
from django.db.models import (
    Count,
    Sum,
    Case,
    When,
    Max,
    F,
    Q,
    Subquery,
    OuterRef,
    Value,
)
from django.db.models.functions import Coalesce
from django.db.models import Window
from django.utils import timezone
from django.urls import reverse

from .manager import MeleeMatchManager
from .manager import TeamMatchManager
from .manager import MeleePlayerManager
from .utils import get_match_data_from_match_list
from .utils import get_streak_count

race_list = (
    ('T', 'Terran'),
    ('Z', 'Zerg'),
    ('P', 'Protoss'),
    ('R', 'Random')
)


class User(models.Model):
    # name that same as Starcraft Nickname
    name = models.CharField(
        max_length=30,
        default="",
        unique=True)

    # joined date
    joined_date = models.DateField(
        default=timezone.now)

    # User's career
    career = models.TextField(
        default="아직 잠재력이 드러나지 않았습니다...")

    # User's race
    most_race = models.CharField(
        max_length=10,
        choices=race_list)

    class Meta:
        ordering = ['-joined_date', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("haley_gg:users_detail", kwargs={"name": self.name})

    # Return win rate no matter of player's race.
    def get_winning_rate(self):
        queryset = self.player_set.all()
        match_count = queryset.count()
        victory_count = queryset.filter(is_win=True).count()
        try:
            win_rate = round(victory_count / match_count * 100, 2)
        except ZeroDivisionError:
            return 0
        return win_rate

    # Return winning_rate by race
    def get_winning_rate_by_race(self):
        rate_dict = {
            'T': [0,   # victory_count
                  0,   # matches_count
                  0],  # rate
            'Z': [0, 0, 0],
            'P': [0, 0, 0],
        }
        match_list = Player.melee.values(
            'match_id',
            'user_id',
            'is_win',
            'race',
        )

        # 1. 모든 매치에 연결된 플레이어의 데이터를 갖고오게 되었다.
        # 2. 해당 유저와 붙은 유저의 전적을 골라내야한다.
        #    전적 추가할 때 매치에 연결된 유저들은 붙어있기 때문에 인덱싱만 잘 조절하면 된다.
        for index, match_dict in enumerate(match_list):
            if match_dict['user_id'] != self.id:
                continue
            if match_list[index+1]['match_id'] == match_dict['match_id']:
                opponent_index = index + 1
            else:
                opponent_index = index - 1
            opponent_race = match_list[opponent_index]['race']

            if match_dict['is_win']:
                rate_dict[opponent_race][0] += 1
            rate_dict[opponent_race][1] += 1

        for key in rate_dict.keys():
            try:
                # Get player's race vs Z,P winning_rate.
                victories = rate_dict[key][0]
                matches = rate_dict[key][1]
                rate_dict[key][2] = round(
                    victories / matches * 100,
                    2)
            except ZeroDivisionError:
                rate_dict[key][2] = 0
        return rate_dict

    # Returns the winning status.
    def get_winning_status(self):
        count = 0
        last_status = True
        # stop loop when current status is different last status.
        for player in self.player_set.filter(match__type='one_on_one'):
            if count == 0:
                last_status = player.is_win
            else:
                if last_status is not player.is_win:
                    break
            count += 1 if player.is_win else -1

        string = [str(abs(count)), '']
        string[1] = '연승' if count > 0 else '연패'
        return ''.join(string)

    def get_user_melee_data(self, opponent_name=None):
        queryset = Player.melee.all()
        # defer로 원하는 field만 가져오도록 하는 방법이 있다.
        # 그런데 그렇게 하니까 더 딜레이가 걸린다.
        # 왜 그런지는 잘 모르겠다...만 loop최적화를 해야할 것 같다.
        # 어쩌면 player_set처럼 내부기능이 존재할 것 같다.
        id_list = []
        for index, data in enumerate(queryset):
            if data.user_id != self.id:
                continue
            # find opponent index
            if queryset[index+1].match_id == data.match_id:
                opponent_index = index + 1
            else:
                opponent_index = index - 1
            # if opponent name is given, check.
            if opponent_name is not None:
                if queryset[opponent_index].user.name.lower() != opponent_name.lower():
                    continue
            # append player index when match with opponent.
            id_list.append(data.id)
            id_list.append(queryset[opponent_index].id)
        return queryset.filter(
            id__in=id_list
        )

    def versus(self, opponent_name):
        queryset = self.get_user_melee_data(
            opponent_name=opponent_name)
        total_count = queryset.count()
        win_count = queryset.filter(
            Q(user_id=self.id),
            Q(is_win=True)
        ).count()
        lose_count = int(total_count / 2) - win_count

        compare_dict = {
            'player_queryset': queryset,
            'total_count': total_count,
            'win_count': win_count,
            'lose_count': lose_count,
        }
        return compare_dict

    @classmethod
    def get_rank_data(cls):
        # 1. player 중에 자신과 관련된 것.
        # 2. match_type이 one_on_one인 것.
        # Model.objects.filter()를 하면 모델 전체에게 명령을 내리는데,
        # 외부키로 연결된 오브젝트에 접근해서 갖고오게 된다. select_related를 해두면 더 좋을려나..
        # 해당 user에 related인 player들만 갖고 올 때 1v1인 경우만 갖고 와서
        # annotate로 player의 총 개수를 가지는 컬럼을 하나 만들고
        # values와 order_by로 최상위 5명의 이름과 총 개수만 반환하도록 했다.
        # https://docs.djangoproject.com/en/dev/topics/db/aggregation/#order-of-annotate-and-filter-clauses
        rank_data_dict = {}
        """
        보여줘야할 데이터들

        공식전
         L  다전,
         L  연승(개인+팀플)
         L  연승(개인)
         L  연패(개인+팀플)
         L  연패(개인)

        프로리그
         L  다전
         L  연승(개인+팀플)
         L  연승(개인)
         L  연승(팀플)
         L  에결연승
         L  연패(개인+팀플)
         L  연패(개인)
         L  연패(팀플)

        개인리그
         L  다전
         L  연승
         L  연패

        """
        # 각 user의 player의 개수를 세되, 여기선 1v1인 매치만 세었다.
        rank_data_dict['total_matches'] = cls.objects.filter(
            player__match__type__exact='one_on_one'
        ).annotate(
            total_matches=Count('player')
        ).values(
            'name',
            'total_matches',
        ).order_by('-total_matches')[:5]

        # 연승 찾는 방법
        # 1.  제일 최근에 진 row를 찾는다.
        #     제일 최근에 졌으므로 그 것보다 더 최근의 매치들은 다 이겼을 거다.
        # 2.  그 row보다 id값이 큰 것들의 count를 계산한다.

        # 여기선 그냥 밀리전적만 보므로, 필터링을 한 전적결과만 넣어주면
        # get_streak_count에서 결과를 반환해줄거다.
        # streak_queryset = Player.melee.annotate(
        #     last_defeat=Window(
        #         expression=Max(
        #             'id',
        #             filter=Q(is_win=False)
        #         ),
        #         partition_by=F('user'),
        #         order_by=[F('user').asc()]
        #     )
        # )
        # streak_queryset = Player.melee.annotate(
        #     is_streak=Subquery(
        #         streak_queryset.filter(user=OuterRef('user')).values('last_defeat')[:1]
        #         # 각 user별로 max_id값을 갖고오는데, Subquery에서는 어떻게 해야
        #         # 개별적으로 저장되는지...
        #     )
        # )
        # queryset = streak_queryset.values('user').annotate(
        #     streak_sum=Count(
        #         'is_streak', filter=Q(id__gt=F('is_streak'))
        #     )
        # ).order_by('-streak_sum')
        
        
        
        # last_defeat = Player.melee.values('user').annotate(
        #     max_id=Window(
        #         expression=Max(
        #             'id',
        #             filter=Q(is_win=False)
        #         ),
        #         partition_by=F('user'),
        #         order_by=F('user').asc(),
        #         output_field=models.IntegerField()
        #     )
        # )
        # q = Player.melee.annotate(
        #     streak=Case(
        #         When(
        #             id__gt=last_defeat.filter(
        #                 user=OuterRef('user')
        #             ).values('max_id')[:1],
        #             then=1
        #         ),
        #         default=0,
        #         output_field=models.IntegerField()
        #     )
        # )
        # queryset = Player.melee.values('user').annotate(
        #     count=Subquery(
        #         q.filter(user=OuterRef('user')).annotate(
        #             count=Sum('streak')
        #         ).values('count')[:1]
        #     )
        # ).values('user', 'count')

        player_queryset = Player.melee.all()
        streak_rank = {}
        for user in User.objects.all():
            user_queryset = player_queryset.filter(user=user)
            count = get_streak_count(user_queryset)
            if count > 0:
                streak_rank[user] = count
        rank_data_dict['q'] = streak_rank
        # 뭔 짓을 해도 3초이상 걸린다 왜그럴까..
        # filtered_id = Player.melee.filter(
        #     Q(user=OuterRef('user')) &
        #     Q(is_win=False)
        # ).order_by('-id')
        # queryset = User.objects.prefetch_related('player_set').annotate(
        #     streak_sum=Count(
        #         'player__id',
        #         filter=Q(player__id__gt=filtered_id.values('id')[:1]) & Q(player__is_win=False),
        #         output_field=models.IntegerField()
        #     )
        # )
        # 제일 마지막으로 진 값 위로는 1이 저장되어 있음
        # group by는 열들을 모아서 집계를 한다. 하지만 partition by는 열을 모으지 않고
        # 집계값만 각 열에 넣어준다.

        # rank_data_dict['queryset'] = queryset[300:600]
        # rank_data_dict['streak_queryset'] = last_defeat_queryset[:100]
        # rank_data_dict['streak_queryset'] = streak_queryset[:100]
        return rank_data_dict


class Map(models.Model):
    # map name
    name = models.CharField(
        max_length=30,
        default="")

    # map files(ex: .scx, .scm, or zip files)
    file = models.FileField(
        upload_to="Maps/files/",
        blank=True)

    # map images
    image = models.ImageField(
        upload_to="Maps/images/",
        default="Maps/images/default.jpg")

    # # match count on this map
    # match_count = models.PositiveIntegerField(
    #     default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('haley_gg:maps_detail', kwargs={"name": self.name})

    # Count matches related this map.
    # def update_match_count(self):
    #     self.match_count = self.match_set.all().count()
    #     self.save()
    @classmethod
    def get_match_count(cls):
        return cls.objects.prefetch_related('match').annotate(
            count=Count('match')
        )

    # Calculate statistics on victory by race.
    # Only works when type is melee.
    #
    # Too slow....
    #
    def get_statistics_on_winning_rate(self):
        winning_rate_dict = {
            'T': {
                # first element is number of wins.
                # second is winning rate.
                'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]
            },
            'Z': {
                'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]
            },
            'P': {
                'T': [0, 0], 'Z': [0, 0], 'P': [0, 0]
            },
        }

        # Only hit db once, get all data.
        match_result_list = Player.objects.select_related(
            'match',
            'map'
        ).values_list(
            'match__map_id',
            'match__type',
            'match_id',
            'is_win',
            'race',
        )
        match_dict = {}
        for match_result in match_result_list:
            if match_result[0] != self.id or match_result[1] != 'one_on_one':
                continue
            else:
                key = str(match_result[2])
                data = match_dict.get(key)
                if data is None:
                    data = []
                is_win = match_result[3]
                race = match_result[4]
                data.append((is_win, race))
                match_dict[key] = data

        for values in match_dict.values():
            winner_race = ''
            loser_race = ''
            if values[0][0] is True:
                winner_race = values[0][1]
            else:
                loser_race = values[0][1]
            if values[1][0] is True:
                winner_race = values[1][1]
            else:
                loser_race = values[1][1]
            winning_rate_dict[winner_race][loser_race][0] += 1

        race_list = ['T', 'P', 'Z']
        for winner in race_list:
            for loser in race_list:
                # if races are same, do not calculate.
                if winner == loser:
                    continue

                win_count = winning_rate_dict[winner][loser][0]
                loser_count = winning_rate_dict[loser][winner][0]
                match_count = win_count + loser_count
                try:
                    winning_rate_dict[winner][loser][1] = round(
                        win_count / match_count * 100, 2)
                except ZeroDivisionError:
                    winning_rate_dict[winner][loser][1] = 0
        return winning_rate_dict


class League(models.Model):
    # league name that indicate a league name
    # such as Proleague, Starleague, etc...
    name = models.CharField(
        max_length=20,
        default="")

    # to distinguish league, this model has a league_type field
    type = models.CharField(
        max_length=20,
        choices=(
            ("pro_league", "프로리그"),
            ("star_league", "스타리그"),
            ("event_league", "이벤트리그"),
        ),
        default="")

    class Meta:
        ordering = [
            'name'
        ]

    def __str__(self):
        return self.name


# All one on one match stored this type.
class Match(models.Model):
    # league
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        verbose_name="리그",
        related_name='match')

    # Round, dual tournament or something like that. Seems like game title
    # ex. Round 1, 16강 A조 ... etc
    name = models.CharField(
        max_length=100,
        default="",
        verbose_name="매치 제목")

    # Disabled.
    # # additional description such as set, ace match, winner's match etc ...
    # description = models.CharField(
    #     max_length=50,
    #     default="",
    #     verbose_name="매치 부제목")

    # match date
    date = models.DateField(
        default=timezone.now,
        verbose_name='경기 날짜')

    # map used in match
    map = models.ForeignKey(
        Map,
        on_delete=models.CASCADE,
        verbose_name='맵',
        related_name='match')

    # remake for this match
    remark = models.CharField(
        max_length=50,
        default="",
        blank=True,
        verbose_name="비고")

    # Below fields are not shown to user.
    # is one on one match or top and bottom?
    type = models.CharField(
        max_length=20,
        choices=(
            ('one_on_one', '1대1'),
            ('top_and_bottom', '팀플'),
        ),
        default="")

    # Managers
    objects = models.Manager()
    melee = MeleeMatchManager()
    team = TeamMatchManager()

    class Meta:
        ordering = [
            '-date',
            '-name',
            '-id',
        ]

    def __str__(self):
        str = self.get_name()
        return ''.join(str)

    def get_absolute_url(self, **kwargs):
        return reverse('haley_gg:match_list')

    # Return match name in list type.
    def get_name(self):
        string = []
        string.append(str(self.date))
        string.append(' l ')
        string.append(str(self.league.__str__()))
        string.append(' ')
        string.append(str(self.name))
        return string

    @classmethod
    def create_data_from_sheet(cls, doc):
        # Google Spreadsheet warn you 'read requests per user per 100 seconds'
        # So i bring all data at once.

        #
        # Managing melee data.
        #
        melee_sheet = doc.worksheet('개인전적Data')
        match_data_list = melee_sheet.get_all_values()
        match_length = len(match_data_list)
        # Loops from last of exist data to last of new data.
        # Only counts if match type isn't top and bottom.

        remark_dict = {
            '기권': '기권 경기',
            '몰수': '몰수 경기',
            '에이스': '에이스 결정전',
        }
        for i in range(
            Match.melee.count() * 2 + 1,
            match_length,
            2
        ):
            match_data = match_data_list[i]
            match_info_dict = get_match_data_from_match_list(match_data)

            # date
            date = match_info_dict['date']

            # League
            league_name = match_info_dict['league_name']
            league_type = match_info_dict['league_type']
            league, created = League.objects.get_or_create(
                name__iexact=league_name,
                defaults={
                    'name': league_name,
                    'type': league_type,
                })
            # name
            name = match_info_dict['name']

            # Map
            map, created = Map.objects.get_or_create(
                name=match_data[6],
                defaults={
                })

            # remark
            remark = ""
            try:
                # if match is abstention...
                remark = match_data[13] or match_data[12]
            except IndexError:
                remark = ""

            if remark in remark_dict:
                remark = remark_dict[remark]
            else:
                remark = ""

            # Create Match data.
            match = Match.objects.create(
                league=league,
                name=name,
                date=date,
                map=map,
                remark=remark,
                type='one_on_one')

            # Players
            player_1_name = match_data[2]
            player_1_race = match_data[3].upper()
            player_2_name = match_data[4]
            player_2_race = match_data[5].upper()
            player_1, created = User.objects.get_or_create(
                name__iexact=player_1_name,
                defaults={
                    'name': player_1_name,
                    'most_race': player_1_race,
                })
            player_2, created = User.objects.get_or_create(
                name__iexact=player_2_name,
                defaults={
                    'name': player_2_name,
                    'most_race': player_2_race,
                })
            if match_data[7].lower() == player_1_name.lower():
                target_data = [player_1,        # winner
                               player_1_race,
                               player_2,        # loser
                               player_2_race]
            else:
                target_data = [player_2,
                               player_2_race,
                               player_1,
                               player_1_race]
            is_win = True if match_data[8] == '승' else False

            Player.objects.create(
                match=match,
                user=target_data[0],
                is_win=is_win,
                race=target_data[1])
            Player.objects.create(
                match=match,
                user=target_data[2],
                is_win=False if is_win else True,
                race=target_data[3])

        #
        # Managing top and bottom data.
        #
        teamplay_sheet = doc.worksheet('팀플전적Data')
        match_result_list = teamplay_sheet.get_all_values()
        match_length = len(match_result_list)
        # Only counts if match type isn't top and bottom.
        for i in range(
            Match.team.count() * 6 + 1,
            match_length,
            6
        ):
            match_result = match_result_list[i]
            match_info_dict = get_match_data_from_match_list(match_result)

            # date
            date = match_info_dict['date']

            # League
            league_name = match_info_dict['league_name']
            league_type = match_info_dict['league_type']
            league, created = League.objects.get_or_create(
                name__iexact=league_name,
                defaults={
                    'name': league_name,
                    'type': league_type,
                })
            # name
            name = match_info_dict['name']

            # Map
            map, created = Map.objects.get_or_create(
                name=match_result[8],
                defaults={
                })

            # remark
            remark = ""
            try:
                # if match is abstention...
                remark = match_result[14]
            except IndexError:
                remark = ""

            if remark in remark_dict:
                remark = remark_dict[remark]
            else:
                remark = ""

            # Create Match data.
            match = Match.objects.create(
                league=league,
                name=name,
                date=date,
                map=map,
                remark=remark,
                type='top_and_bottom')

            # Players
            # race does not matter
            player_race = ''
            for i in range(2, 8):
                if i < 5:
                    is_win = True if match_result[9] in match_result[2:5] else False
                else:
                    is_win = True if match_result[9] in match_result[5:8] else False

                player, created = User.objects.get_or_create(
                    name__iexact=match_result[i],
                    defaults={
                        'name': match_result[i],
                        'most_race': player_race,
                    })

                Player.objects.create(
                    match=match,
                    user=player,
                    is_win=is_win,
                    race=player_race)


class Player(models.Model):
    # cannot comment this member. too hard to describe...
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        blank=True)

    # player who in game
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)

    # is win?
    is_win = models.BooleanField(
        default=False)

    # race in this match
    race = models.CharField(
        max_length=10,
        default="",
        choices=race_list[:-1])

    # Managers
    objects = models.Manager()
    melee = MeleePlayerManager()

    class Meta:
        ordering = ['match']

    def __str__(self):
        string = []
        string.append(self.match.__str__())
        string.append(' ')
        string.append(str(self.user))
        return ''.join(string)
