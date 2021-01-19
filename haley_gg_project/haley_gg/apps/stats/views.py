from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.forms import modelformset_factory

from haley_gg.apps.stats.models import Result
from haley_gg.apps.stats.forms import get_pvp_data_formset
from haley_gg.apps.stats.forms import ResultForm


class ResultListView(ListView):
    template_name = 'stats/results_list.html'
    model = Result


class CreateResultView(View):
    template_name = 'stats/create.html'

    def get(self, request, *args, **kwargs):
        PVPDataFormSet = get_pvp_data_formset()
        formset = PVPDataFormSet()
        resultform = ResultForm()
        context = {
            'formset': formset,
            'form': resultform
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        PVPDataFormSet = get_pvp_data_formset()
        formset = PVPDataFormSet(request.POST)
        resultform = ResultForm(request.POST)
        if formset.is_valid() and resultform.is_valid():
            formset.save_with(resultform)
            return redirect(reverse('stats:result_list'))
        context = {
            'formset': formset,
            'form': resultform
        }
        return render(request, self.template_name, context)
