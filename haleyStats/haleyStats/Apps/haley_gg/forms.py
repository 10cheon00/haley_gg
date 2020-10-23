from django import forms

from .Models.maps import Map
from .Models.stats import Match
from .Models.users import User
from .Models.stats import Player


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ('name', 'file', 'image')

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
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
        self.fields['is_player_1_winner'] = forms.BooleanField()

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
