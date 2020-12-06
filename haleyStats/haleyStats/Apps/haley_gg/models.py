# haley_gg/models.py
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse

from .manager import MeleeMatchManager
from .manager import TeamMatchManager
from .utils import get_match_data_from_match_list

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
        match_list = Player.melee().values(
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
        for player in self.player_set.all():
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
        queryset = Player.melee()

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

    # match count on this map
    match_count = models.PositiveIntegerField(
        default=0)

    class Meta:
        ordering = ['-match_count', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('haley_gg:maps_detail', kwargs={"name": self.name})

    # Count matches related this map.
    def update_match_count(self):
        self.match_count = self.match_set.all().count()
        self.save()

    # Calculate statistics on victory by race.
    # Only works when match_type is melee.
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
            'match__match_type',
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
        verbose_name="리그")

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
        verbose_name="경기 날짜")

    # map used in match
    map = models.ForeignKey(
        Map,
        on_delete=models.CASCADE,
        verbose_name="맵")

    # remake for this match
    remark = models.CharField(
        max_length=50,
        default="",
        blank=True,
        verbose_name="비고")

    # Below fields are not shown to user.
    # is one on one match or top and bottom?
    match_type = models.CharField(
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
                match_type='one_on_one')

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
                match_type='top_and_bottom')

            # Players
            for i in range(2, 8):
                # race does not matter
                player_race = ''
                if i < 5:
                    is_win = match_result[9] in match_result[2:5]
                else:
                    is_win = match_result[9] in match_result[5:8]

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

    # is win?
    is_win = models.BooleanField(
        default=False)

    # player who in game
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)

    # race in this match
    race = models.CharField(
        max_length=10,
        default="",
        choices=race_list[:-1])

    class Meta:
        ordering = ['match']

    def __str__(self):
        string = []
        string.append(self.match.__str__())
        string.append(' ')
        string.append(str(self.user))
        return ''.join(string)

    @classmethod
    def melee(cls):
        return cls.objects.select_related(
            'match',
            'user'
        ).filter(
            match__match_type='one_on_one'
        )
