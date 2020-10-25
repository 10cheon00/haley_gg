from django import forms
# from django.utils.translation import ugettext_lazy as _

from .Models.maps import Map
from .Models.stats import Match
from .Models.users import User
from .Models.stats import Player


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'name',
            'joined_date',
            'most_race'
        ]


class UserUpdateForm(UserCreateForm):
    class Meta(UserCreateForm.Meta):
        # Show all field in User model.
        fields = [
            'name',
            'joined_date',
            'most_race',
            'career'
        ]


class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ('name', 'file', 'image')

    def __init__(self, *args, **kwargs):
        super(MapForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = True
        self.fields['image'].required = True


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'date',
            'league_name',
            'name',
            'set',
            'map',
        ]

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        self.fields['player_1'] = forms.ModelChoiceField(
            queryset=User.objects.all(), empty_label=None)
        self.fields['player_2'] = forms.ModelChoiceField(
            queryset=User.objects.all(), empty_label=None)
        self.fields['is_player_1_winner'] = forms.BooleanField(required=False)

    def save(self, commit=True):
        data = super(MatchForm, self).save(commit=False)
        if commit:
            data.save()

        p1 = Player.objects.create(
            user=self.cleaned_data['player_1'],
            match=data)
        p2 = Player.objects.create(
            user=self.cleaned_data['player_2'],
            match=data)

        if self.cleaned_data['is_player_1_winner']:
            p1.is_win = True
            p1.save()
        else:
            p2.is_win = True
            p2.save()

        return data

    def clean(self):
        super(MatchForm, self).clean()
        # 1. Check reduplication on rounds and set.
        data = self.cleaned_data
        if Match.objects.filter(name=data['name'], set=data['set']).exists():
            error_msg = u"Already exist match. Check match name or set."
            self.add_error('set', error_msg)
            # raise forms.ValidationError(_("Already exist match."))

        # 2. Check same user on fields.
        if data['player_1'] == data['player_2']:
            error_msg = u"Players should not same."
            self.add_error('player_1', error_msg)
            # raise forms.ValidationError(_("Players should not same."))
        return data
