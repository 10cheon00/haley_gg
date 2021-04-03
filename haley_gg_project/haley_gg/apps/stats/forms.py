from django import forms
from django.forms import formset_factory
from django.db.models import Q

from haley_gg.apps.stats.models import Player
from haley_gg.apps.stats.models import Map
from haley_gg.apps.stats.models import Result
from haley_gg.apps.stats.models import League
from haley_gg.apps.stats.models import ProleagueTeam
from haley_gg.apps.stats.utils import remove_space


class SearchPlayerForm(forms.Form):
    name = forms.CharField(
        label='Player',
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control'
            }
        )
    )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        name = remove_space(name)
        return name


class UpdatePlayerForm(forms.ModelForm):
    tier_list = [
        ('major', '메이저'),
        ('minor', '마이너'),
        ('rookie', '루키')
    ]

    class Meta:
        model = Player
        fields = [
            'name',
            'joined_date',
            'most_race',
            'career',
            'tier',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'joined_date': forms.NumberInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'most_race': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'career': forms.Textarea(
                attrs={'class': 'form-control'}
            ),
            'tier': forms.Select(
                attrs={'class': 'form-control'}
            )
        }


class UpdateMapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = (
            'name',
            'type',
        )
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                }
            ),
            'type': forms.Select(
                attrs={'class': 'form-control'}
            )
        }


class ResultForm(forms.Form):
    date = forms.DateField(
        label='날짜',
        widget=forms.NumberInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
    )
    league = forms.ModelChoiceField(
        label='리그',
        queryset=League.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    title = forms.CharField(
        label='게임 이름',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
    )


class PVPDataForm(forms.Form):
    race_list = [
        ('T', 'Terran'),
        ('P', 'Protoss'),
        ('Z', 'Zerg'),
    ]
    # set or winner's match, etc ...
    # this field is combined into title field in ResultForm.
    round = forms.CharField(
        label="라운드",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
    )
    type = forms.ChoiceField(
        label="게임 타입",
        choices=[
            ('melee', '밀리'),
            ('teamplay', '팀플')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            },
        ),
    )
    winner = forms.ModelChoiceField(
        label="승자",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    winner_race = forms.ChoiceField(
        label="승자 종족",
        choices=race_list,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    map = forms.ModelChoiceField(
        label='맵',
        queryset=Map.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    loser = forms.ModelChoiceField(
        label="패자",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    loser_race = forms.ChoiceField(
        label="패자 종족",
        choices=race_list,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    remark = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '특이사항 ex)기권승'
            }
        ),
        required=False
    )

    def clean(self):
        # Check that winner is same as loser.

        cleaned_data = super().clean()
        if not self.errors:
            winner = cleaned_data.get('winner')
            loser = cleaned_data.get('loser')
            if winner.name == loser.name:
                error_msg = '선택한 플레이어 이름이 같습니다.'
                self.add_error('winner', error_msg)
                self.add_error('loser', error_msg)
        return cleaned_data


class PVPDataFormSet(forms.BaseFormSet):
    MELEE_PLAYER_LIMIT = 2

    def is_valid_with(self, resultForm):
        # Get resultForm data to check that data what formset have already exists.
        self.resultForm = resultForm
        return super().is_valid()

    def clean(self):
        """
        1. Group results by round data.
        1.1 If current result already exists, pass.
        2. If result's type is teamplay, check grouped teamplay data are validate.
        """

        super().clean()

        # If formset have errors, pass cross form validation.
        if self.total_error_count() > 0:
            return

        # Group by round
        grouped_form = {}
        for form in self.forms:
            round = form.cleaned_data.get('round')
            # Check that data already exists with resultForm data given.
            if Result.objects.filter(
                date=self.resultForm.cleaned_data.get('date'),
                league=self.resultForm.cleaned_data.get('league'),
                title=self.resultForm.cleaned_data.get('title'),
                round=round
            ).exists():
                error_msg = '같은 경기 결과가 이미 존재합니다.'
                form.add_error('round', error_msg)
                continue

            if round not in grouped_form:
                grouped_form[round] = []
            grouped_form[round].append(form)

        # Iterate forms that grouped by round.
        for form_list in grouped_form.values():
            # Only run below validation sequence when result type is teamplay.
            # Melee data already validated in PVPDataForm.
            if len(form_list) < 2:
                continue

            # Check that all map are equal.
            maps = [form.cleaned_data.get('map') for form in form_list]
            map_error_msg = ''
            if len(maps) != len(set(maps)):
                map_error_msg = '같은 맵이 아닙니다.'

            # Check that all players are distinct.
            players = [form.cleaned_data.get('winner') for form in form_list]
            players.extend([form.cleaned_data.get('loser') for form in form_list])
            duplicate_players = set([x for x in players if players.count(x) > 1])
            duplicate_error_msg = '플레이어가 중복됩니다.'

            # Check that all type are equal.
            error_msg = '팀플 타입이 아닙니다.'
            for form in form_list:
                if form.cleaned_data.get('type') != 'teamplay':
                    form.add_error('type', error_msg)
                if len(map_error_msg) == 0:
                    form.add_error('map', map_error_msg)
                if form.cleaned_data.get('winner') in duplicate_players:
                    form.add_error('winner', duplicate_error_msg)
                if form.cleaned_data.get('loser') in duplicate_players:
                    form.add_error('loser', duplicate_error_msg)

    def save_with(self, ResultForm):
        """
        To create result data, I use form, not modelform.
        Q: Why don't you use ModelForm?
        A: Because modelform can't satisfy my result model.
        This form have field that winner and loser,
        but Result model only has one player.
        And it doesn't care who is winner. Just it has win_status.
        So I create two result data related winner and loser,
        but modelform only create one data. So, I use form, not modelform.
        """

        # It works fine, but using modelform is standardly recommand.
        date = ResultForm.cleaned_data.get('date')
        league = ResultForm.cleaned_data.get('league')
        title = ResultForm.cleaned_data.get('title')

        result_list = []
        for form in self.forms:
            cleaned_data = form.cleaned_data
            result_list.extend([
                Result(
                    date=date,
                    league=league,
                    title=title,
                    round=cleaned_data.get('round'),
                    map=cleaned_data.get('map'),
                    type=cleaned_data.get('type'),
                    player=cleaned_data.get('winner'),
                    race=cleaned_data.get('winner_race'),
                    player_a=cleaned_data.get('winner'),
                    player_b=cleaned_data.get('loser'),
                    player_a_race=cleaned_data.get('winner_race'),
                    player_b_race=cleaned_data.get('loser_race'),
                    is_win=True
                ),
                Result(
                    date=date,
                    league=league,
                    title=title,
                    round=cleaned_data.get('round'),
                    map=cleaned_data.get('map'),
                    type=cleaned_data.get('type'),
                    player=cleaned_data.get('loser'),
                    race=cleaned_data.get('loser_race'),
                    player_a=cleaned_data.get('winner'),
                    player_b=cleaned_data.get('loser'),
                    player_a_race=cleaned_data.get('winner_race'),
                    player_b_race=cleaned_data.get('loser_race'),
                    is_win=False
                )]
            )
        Result.objects.bulk_create(result_list)

        saved_result_list = []
        for result in result_list:
            # Calculate team status.

            """
            1. Get a league in resultForm.
            2. If it is not proleague, continue to other result.
            3. Get team associated player in result.
            4. Save current result to team.
            """
            if league.type != 'proleague':
                continue

            team = ProleagueTeam.objects.filter(
                Q(league=league) &
                Q(players__in=[result.player])
            ).first()

            if team:
                # To save win/lose result, check that result counts in list.
                # If it lower than MELEE_PLAYER_LIMIT, append result.
                if saved_result_list.count(
                    result.round
                ) < self.MELEE_PLAYER_LIMIT:
                    team.save_result(result)
                    saved_result_list.append(result.round)


class CompareUserForm(forms.Form):
    player = forms.ModelChoiceField(
        label="플레이어",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    opponent = forms.ModelChoiceField(
        label="상대",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    def clean(self):
        # Check that player is same as opponent.

        cleaned_data = super().clean()
        if not self.errors:
            player = cleaned_data.get('player')
            opponent = cleaned_data.get('opponent')
            if player.id is opponent.id:
                error_msg = '선택한 플레이어 이름이 같습니다.'
                self.add_error('player', error_msg)
                self.add_error('opponent', error_msg)
        return cleaned_data


def get_pvp_data_formset():
    return formset_factory(
        form=PVPDataForm,
        formset=PVPDataFormSet,
        extra=2,
    )
