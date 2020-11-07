from django import forms
from django.forms import inlineformset_factory

from ..Models.users import User
from ..Models.stats import Player
from ..Models.stats import Match
from ..utils import get_user_with_name


# Match form for StarLeague.
class CreateStarLeagueMatchForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = [
            'date',
            'league_name',
            'name',
            'set',
            'map',
            'remark',
        ]

    def clean(self):
        cleaned_data = super(CreateStarLeagueMatchForm, self).clean()
        if self.errors:
            return cleaned_data
        # Check reduplication on rounds and set.
        if Match.objects.filter(name=cleaned_data['name'],
                                set=cleaned_data['set']
                                ).exists():
            error_msg = u"Already exist match. Check match name or set."
            self.add_error('set', error_msg)
        return cleaned_data


# 어... formset을 이용해서 매치 7개를 다 등록하는 방향으로 가야 할 것 같다.
# 따로 폼을 써야할 필요성을 느끼진 못했지만 xlsx에서 봤었듯 리그명, 라운드, 경기날짜.. 그런건 한번만 입력해도 되니까...
# class CreateProleagueMatchForm(forms.ModelForm):


class PlayerForm(forms.ModelForm):
    player_name = forms.CharField(max_length=30)

    class Meta:
        model = Player
        fields = [
            'race',
            'is_win'
        ]

    def clean(self):
        super(PlayerForm, self).clean()
        user = get_user_with_name(self.cleaned_data['player_name'])
        if type(user) == 'str':
            self.add_error('player_name', user)  # it is error_msg
        return

    def save(self, commit=False):
        instance = super(PlayerForm, self).save(commit=False)

        instance.user = get_user_with_name(self.cleaned_data['player_name'])

        if commit:
            instance.save()


# If model has a foreign key, it is better to use inlineformset.
class PlayerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super(PlayerFormSet, self).clean()
        users = []
        # check name in player list.
        for form in self.forms:
            user = form.cleaned_data.get('player_name')
            print(user)
            if user in users:
                error_msg = u"Players should not same."
                form.add_error('player_name', error_msg)
            else:
                users.append(user)
        return


def get_playerformset_factory(extra):
    return inlineformset_factory(
        parent_model=Match,
        model=Player,
        fields=[
            'player_name',
            'race',
            'is_win',
        ],
        form=PlayerForm,
        formset=PlayerFormSet,
        extra=extra,  # maximum of forms
        can_delete=False)  # formset purpose is to delete item
