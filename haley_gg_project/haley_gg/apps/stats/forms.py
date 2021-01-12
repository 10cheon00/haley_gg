from django import forms
from django.core.exceptions import ValidationError

from haley_gg.apps.stats.models import Player, Map, Result


class PlayerResultDataFormSet(forms.BaseFormSet):
    # 여기서는 플레이어 이름이 겹치는지만 확인하면 된다.
    def clean(self):
        super().clean()
        for form in self.forms:
            pass

# basemodelformset에는 is_valid()가 없다.
# baseformset에 있는데, 각 form을 돌면서 is_valid()를 호출한다.

# form에서 is_valid()를 호출하면 full_clean()을 부른다는데 어디서 부르는지 못찾았다.
# full_clean()에서는 clean_field(), clean_form(), post_clean() 순으로 부른단다.
# 책이랑 설명이 다른데?

# formset에도 full_clean()이 있다.
# 각 form을 돌면서 달라진 점과 에러를 찾는다.
# validation의 범위를 벗어날 경우 ValidationError를 뿜고 끝낸다.
# 그렇지 않은 경우 clean()을 호출한다.
# clean()은 pass처리되어 있는데, 모든 form 내부에서 clean()이 호출된 뒤에
# hook한다는데, 의미를 잘 이해 못하겠다..

# ModelFormSet에서 clean() 쓰는 방법
# https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#overriding-clean-on-a-modelformset


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


class PlayerResultDataForm(forms.Form):
    race_list = [
        ('T', 'Terran'),
        ('P', 'Protoss'),
        ('Z', 'Zerg'),
    ]

    description = forms.CharField(max_length=100)
    type = forms.ChoiceField(choices=[
            ('melee', '밀리'),
            ('top_and_bottom', '팀플')
        ])
    winner = forms.ModelChoiceField(queryset=Player.objects.all())
    winner_race = forms.ChoiceField(choices=race_list)
    map = forms.ModelChoiceField(queryset=Map.objects.all())
    loser = forms.ModelChoiceField(queryset=Player.objects.all())
    loser_race = forms.ChoiceField(choices=race_list)


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
                }),
            'league': forms.Select(
                attrs={
                    'class': 'form-control'
                }),
            'match_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }),
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

    def clean(self):
        super().clean()
        pass

    # save with formset data.
    def save(self, formset):
        pass
