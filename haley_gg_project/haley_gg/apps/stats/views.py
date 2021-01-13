from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.forms import modelformset_factory

from haley_gg.apps.stats.models import Result
from haley_gg.apps.stats.forms import get_player_versus_player_data_formset
from haley_gg.apps.stats.forms import ResultForm


class ResultListView(ListView):
    template_name = 'stats/results_list.html'
    model = Result


class CreateResultView(View):
    template_name = 'stats/create.html'

    def get(self, request, *args, **kwargs):
        PlayerVersusPlayerDataFormSet = get_player_versus_player_data_formset()
        formset = PlayerVersusPlayerDataFormSet()
        form = ResultForm()
        context = {
            'formset': formset,
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        request.POST
        'form-TOTAL_FORMS': ['2'],
        'form-INITIAL_FORMS': ['0'],
        'form-MIN_NUM_FORMS': ['0'],
        'form-MAX_NUM_FORMS': ['1000'],
        """
        PlayerVersusPlayerDataFormSet = get_player_versus_player_data_formset()
        formset = PlayerVersusPlayerDataFormSet(request.POST)
        form = ResultForm(request.POST)
        if formset.is_valid() and form.is_valid():
            pass
        context = {
            'formset': formset,
            'form': form
        }
        return render(request, self.template_name, context)
