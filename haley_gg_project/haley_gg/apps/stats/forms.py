from django import forms
from django.forms import formset_factory
from haley_gg.apps.stats.models import Player, Map, Result



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


class PlayerVersusPlayerDataForm(forms.Form):
    race_list = [
        ('T', 'Terran'),
        ('P', 'Protoss'),
        ('Z', 'Zerg'),
    ]
    # set or winner's match, etc ...
    # this field is combined into match_name field in ResultForm.
    description = forms.CharField(
        max_length=100,
        required=False
    )
    type = forms.ChoiceField(
        choices=[
            ('melee', '밀리'),
            ('top_and_bottom', '팀플')
        ]
    )
    winner = forms.ModelChoiceField(
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    winner_race = forms.ChoiceField(choices=race_list)
    map = forms.ModelChoiceField(queryset=Map.objects.all())
    loser = forms.ModelChoiceField(queryset=Player.objects.all())
    loser_race = forms.ChoiceField(choices=race_list)

    def clean(self):
        cleaned_data = super().clean()

        # Check that winner is same as loser.
        winner = cleaned_data['winner']
        loser = cleaned_data['loser']
        if winner.name == loser.name:
            error_msg = '선택한 플레이어 이름이 같습니다.'
            self.add_error('winner', error_msg)
            self.add_error('loser', error_msg)

        return cleaned_data


class PlayerVersusPlayerDataFormSet(forms.BaseFormSet):
    def clean(self):
        super().clean()

        # When grouped by descriptions, Check that types are same.
        type_dict = {}
        for form in self.forms:
            type = form.cleaned_data['type']
            description = form.cleaned_data['description']
            if description not in type_dict.keys():
                type_dict[description] = type
            else:
                if type_dict[description] != type:
                    error_msg = '한 경기 내의 경기 타입이 서로 다릅니다.'
                    form.add_error('type', error_msg)


def get_player_versus_player_data_formset():
    return formset_factory(
        form=PlayerVersusPlayerDataForm,
        extra=2,
    )


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = [
            'date',
            'league',
            'match_name',
        ]
        widgets = {
            'date': forms.NumberInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'league': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'match_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }
        labels = {
            'date': '날짜',
            'league': '리그',
            'match_name': '게임이름',
            # form row를 사용할 때는 col-form-label로 class를 지정해주어야 한다.
            # label_tag() 인자로 attrs 옵션을 줄 수 있는데, init에서 하려고 하니까 안된다.
            # 당장은 중요한게 아니니까 보류.
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # save with formset data.
    def save(self, formset):
        pass
