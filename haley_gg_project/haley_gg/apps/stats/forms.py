from django import forms
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from django.db.models import Count

from haley_gg.apps.stats.models import Player, Map, Result, League



"""
form 페이지 구성을 생각해봐야겠다.
지금처럼 플레이어마다 모든 필드를 보여주는 방식은 별로 좋지 않다.
단순하게 하자.

[ 경, 기, 정, 보, 들, ... ],
승리 플레이어, 맵, 패배 플레이어만 필드로 둬도 되지 않을까?
Q) 그럼 팀플은 어떻게 해?
 -> 팀플도 똑같이 저장한다.
 -> 어차피 Result에는 누구한테 이겼다는게 별로 중요하지 않다. 승리여부만 중요하지.
 -> 데이터를 보여줄 때 그룹화가 중요한데, 해봐야 related_set보단 빠르겠지.
 -> 지금 사용하는 formset을 바꿔야겠다!

form + formset구조
form
    date
    league
    match_name

formset
    승리자
    승리자 종족
    맵
    패배자
    패배자 종족
    description
    type
"""


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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields

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

        name_dict = {}
        for form in self.forms:
            # Check that matches are already exist.
            if Result.objects.filter(
                date=form.cleaned_data.get('date'),
                league=form.cleaned_data.get('league'),
                match_name=form.cleaned_data.get('match_name')
            ).exists():
                error_msg = '이미 존재하는 경기 결과입니다.'
                form.add_error('match_name', error_msg)

            # Check that formset have duplicated match_name what form has.
            # If same match_name is exist in formset,
            # check that all type are top_and_bottom,
            # and check that all map are equal.
            description = form.cleaned_data.get('description')
            # If description is empty, skip further progress.
            if description:
                if description in name_dict.keys():
                    # This result already exists in formset.
                    if form.cleaned_data.get('type') == 'melee':
                        # This form's type is not top_and_bottom.
                        error_msg = '같은 이름을 가진 경기의 타입이 서로 다릅니다.'
                        form.add_error('type', error_msg)
                    if form.cleaned_data.get('map') != name_dict[description]:
                        # This form is teamplay result.
                        error_msg = '같은 이름을 가진 경기의 맵이 서로 다릅니다.'
                        form.add_error('map', error_msg)
                else:
                    # This form is not duplicated.
                    name_dict[description] = form.cleaned_data.get('map')


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # form row를 사용할 때는 col-form-label로 class를 지정해주어야 한다.
        # label_tag() 인자로 attrs 옵션을 줄 수 있는데, init에서 하려고 하니까 안된다.
        # 당장은 중요한게 아니니까 보류.

    # save with formset data.
    def save_with(self, PVPDataFormSet):
        # To create result data, we use form, not modelform.
        # Q: Why don't you use ModelForm?
        # A: Because modelform can't satisfy my result model.
        # This form have field that winner and loser,
        # but Result model only has one player.
        # And it doesn't care who is winner. Just it has win_status.
        # So we create two result data related winner and loser,
        # but modelform only create one data. So, I use form, not modelform.

        # It works fine, but using modelform is standardly recommand.
        for form in PVPDataFormSet:
            cleaned_data = form.cleaned_data
            date = self.cleaned_data.get('date')
            league = self.cleaned_data.get('league')
            title = self.cleaned_data.get('match_name')
            match_name = ''.join([title, cleaned_data.get('description')])

            Result.objects.create(
                date=date,
                league=league,
                match_name=match_name,
                map=cleaned_data.get('map'),
                type=cleaned_data.get('type'),
                player=cleaned_data.get('winner'),
                race=cleaned_data.get('winner_race'),
                win_state=True
            )
            Result.objects.create(
                date=date,
                league=league,
                match_name=match_name,
                map=cleaned_data.get('map'),
                type=cleaned_data.get('type'),
                player=cleaned_data.get('loser'),
                race=cleaned_data.get('loser_race'),
                win_state=False
            )


def get_pvp_data_formset():
    return formset_factory(
        form=PVPDataForm,
        formset=PVPDataFormSet,
        extra=2,
    )
