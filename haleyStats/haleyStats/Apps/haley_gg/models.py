# haley_gg/models.py

import datetime

from django.db import models
from django.utils import timezone
from django.urls import reverse

from .manager import MeleeMatchManager
from .manager import TeamMatchManager

race_list = (
    ('T', 'Terran'),
    ('P', 'Protoss'),
    ('Z', 'Zerg'),
    ('R', 'Random')
)


class User(models.Model):
    # name that same as Starcraft Nickname
    name = models.CharField(
        max_length=30,
        default="")

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

    # Return winning_rate by race
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
            if player.is_win:
                count += 1
            else:
                count -= 1

        string = [str(abs(count)), '']
        if count > 0:
            string[1] = '연승'
        else:
            string[1] = '연패'
        return ''.join(string)


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
    # statistics on victory to be calculated.
    # - T vsZ, P
    # - Z vsP, (T)
    # - P vs(T, Z)
    # () is already calculated.
    # Only works when match_type is melee.
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
        # loop per matches related this map.
        for match in self.match_set.all():
            winner_race = ''
            loser_race = ''
            for player in match.player_set.all():
                if player.is_win:
                    winner_race = player.race
                else:
                    loser_race = player.race
            # If winner's race same as loser's race, just add.
            # Same race match just have number of matches.
            winning_rate_dict[winner_race][loser_race][0] += 1
        # So, winning_rate_dict has all data who win or lose.
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
            ("proleague", "프로리그"),
            ("starleague", "스타리그"),
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
        max_length=50,
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

    objects = models.Manager()
    melee = MeleeMatchManager()
    team = TeamMatchManager()

    class Meta:
        ordering = [
            '-date',
            '-name',
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
    def create_data_from_sheet(self, doc):
        # Google Spreadsheet warn you 'read requests per user per 100 seconds'
        # So i bring all data at once.
        melee_sheet = doc.worksheet('개인전적Data')
        match_result_list = melee_sheet.get_all_values()
        match_length = len(match_result_list)

        # loops from last of exist data to last of new data.
        for i in range(Match.objects.all().count() * 2 + 1, match_length, 2):
            match_result = match_result_list[i]

            # if match_result's item is empty data,
            # fill it with 'Unknown Data'.
            for index, value in enumerate(match_result):
                if value == '':
                    match_result[index] = "Unknown data."

            # match date
            date = match_result[0]
            date = date.split('.')
            if len(date[0]) < 4:
                date[0] = f'20{date[0]}'
            date = '-'.join(date)
            date = datetime.datetime.strptime(date, '%Y-%m-%d')

            # League
            name = match_result[1]
            index = name.find('HSL')
            if index < 0:
                index = name.find('HPL')
                league_type = "proleague"
            else:
                league_type = "starleague"
            league, created = League.objects.get_or_create(
                name__iexact=name[0:index+6],
                defaults={
                    'name': name[0:index+6],
                    'type': league_type,
                })

            # name
            name = name[index+7:]

            # map
            map, created = Map.objects.get_or_create(
                name=match_result[6],
                defaults={
                })

            # remark
            remark = ""
            try:
                # if match is abstention...
                remark = match_result[13] or match_result[12]
            except IndexError:
                remark = ""

            if "기권" in remark:
                remark = "기권 경기"
            elif "몰수" in remark:
                remark = "몰수 경기"
            elif "에이스" in remark:
                remark = "에이스 결정전"
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
            player_1_race = match_result[3].upper()
            player_2_race = match_result[5].upper()
            player_1, created = User.objects.get_or_create(
                name__iexact=match_result[2],
                defaults={
                    'name': match_result[2],
                    'most_race': player_1_race,
                })
            player_2, created = User.objects.get_or_create(
                name__iexact=match_result[4],
                defaults={
                    'name': match_result[4],
                    'most_race': player_2_race,
                })

            Player.objects.create(
                match=match,
                user=player_1,
                is_win=(match_result[2].lower() == match_result[7].lower()),
                race=player_1_race)
            Player.objects.create(
                match=match,
                user=player_2,
                is_win=(match_result[4].lower() == match_result[7].lower()),
                race=player_2_race)


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
