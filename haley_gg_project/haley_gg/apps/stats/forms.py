from django import forms
from django.forms import modelformset_factory

from haley_gg.apps.stats.views import Result


class ResultFormSet(forms.BaseFormSet):
    def clean(self):
        pass


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = [
            'date',
            'league',
            'match_name',
            'map',
            'type',
            'player',
            'race',
            'win_state'
        ]
        widgets = {
            'date': forms.NumberInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }),
            'league': forms.Select(attrs={'class': 'form-control'}),
            'match_name': forms.TextInput(attrs={'class': 'form-control'}),
            'map': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'player': forms.Select(attrs={'class': 'form-control'}),
            'race': forms.Select(attrs={'class': 'form-control'}),
            'win_state': forms.CheckboxInput(
                attrs={
                    'type': 'checkbox',
                    'class': 'fasdfafsdafs',
                    'data-toggle': 'toggle',
                    'data-size': 'md',
                    'data-on': '승',
                    'data-off': '패',
                    'data-onstyle': 'primary',
                    'data-offstyle': 'danger'
                }),
        }
