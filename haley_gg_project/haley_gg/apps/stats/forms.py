from django import forms
from django.forms import formset_factory

from haley_gg.apps.stats.models import Player, Map, Result, League

class PVPDataForm(forms.Form):
    race_list = [
        ('T', 'Terran'),
        ('P', 'Protoss'),
        ('Z', 'Zerg'),
    ]
    # set or winner's match, etc ...
    # this field is combined into match_name field in ResultForm.
    description = forms.CharField(
        label="세트",
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
            ('top_and_bottom', '팀플')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            },
        ),
    )
    winner = forms.ModelChoiceField(
        label="승자",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    winner_race = forms.ChoiceField(
        label="승자 종족",
        choices=race_list,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    map = forms.ModelChoiceField(
        label='맵',
        queryset=Map.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    loser = forms.ModelChoiceField(
        label="패자",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    loser_race = forms.ChoiceField(
        label="패자 종족",
        choices=race_list,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        # Check that winner is same as loser.
        if not self.errors:
            winner = cleaned_data.get('winner')
            loser = cleaned_data.get('loser')
            if winner.name == loser.name:
                error_msg = '선택한 플레이어 이름이 같습니다.'
                self.add_error('winner', error_msg)
                self.add_error('loser', error_msg)
        return cleaned_data


class PVPDataFormSet(forms.BaseFormSet):
    def clean(self):
        super().clean()

        # If formset have errors, pass cross form validation.
        if self.total_error_count() > 0:
            return

        cleaned_data_dict = {}
        for form in self.forms:
            # Check that matches are already exist.
            if Result.objects.filter(
                date=form.cleaned_data.get('date'),
                league=form.cleaned_data.get('league'),
                match_name=form.cleaned_data.get('match_name') # is this currect?
            ).exists():
                error_msg = '이미 존재하는 경기 결과입니다.'
                form.add_error('match_name', error_msg)
                continue

            # Check that formset have duplicated match_name what form has.
            # If same match_name is exist in formset,
            # check that all type are top_and_bottom,
            # and check that all map are equal.
            description = form.cleaned_data.get('description')
            # If description is empty, skip further progress.
            if description:
                if description in cleaned_data_dict.keys():
                    # This result already exists in formset.
                    if form.cleaned_data.get('type') not in \
                    cleaned_data_dict[description]['type']:
                        # This form's type is not top_and_bottom.
                        error_msg = '같은 이름을 가진 경기의 타입이 서로 다릅니다.'
                        form.add_error('type', error_msg)
                    if form.cleaned_data.get('map') not in \
                    cleaned_data_dict[description]['map']:
                        # This form is teamplay result.
                        error_msg = '같은 이름을 가진 경기의 맵이 서로 다릅니다.'
                        form.add_error('map', error_msg)
                else:
                    # This form is not duplicated.
                    cleaned_data_dict[description] = {
                        'type': [form.cleaned_data.get('type')],
                        'map': [form.cleaned_data.get('map')]
                    }

    def save_with(self, ResultForm):
        # To create result data, we use form, not modelform.
        # Q: Why don't you use ModelForm?
        # A: Because modelform can't satisfy my result model.
        # This form have field that winner and loser,
        # but Result model only has one player.
        # And it doesn't care who is winner. Just it has win_status.
        # So we create two result data related winner and loser,
        # but modelform only create one data. So, I use form, not modelform.

        # It works fine, but using modelform is standardly recommand.
        date = ResultForm.cleaned_data.get('date')
        league = ResultForm.cleaned_data.get('league')
        title = ResultForm.cleaned_data.get('match_name')
        for form in self.forms:
            cleaned_data = form.cleaned_data
            match_name = ''.join([title, ' ', cleaned_data.get('description')])

            Result.objects.bulk_create([
                Result(
                    date=date,
                    league=league,
                    match_name=match_name,
                    map=cleaned_data.get('map'),
                    type=cleaned_data.get('type'),
                    player=cleaned_data.get('winner'),
                    race=cleaned_data.get('winner_race'),
                    win_state=True
                ),
                Result(
                    date=date,
                    league=league,
                    match_name=match_name,
                    map=cleaned_data.get('map'),
                    type=cleaned_data.get('type'),
                    player=cleaned_data.get('loser'),
                    race=cleaned_data.get('loser_race'),
                    win_state=False
                )
            ])


class ResultForm(forms.Form):
    date = forms.DateField(
        label='날짜',
        widget=forms.NumberInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
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
    match_name = forms.CharField(
        label='게임 이름',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
    )


def get_pvp_data_formset():
    return formset_factory(
        form=PVPDataForm,
        formset=PVPDataFormSet,
        extra=2,
    )
