from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, View, ListView

from haley_gg.apps.stats.models import Result, League
from haley_gg.apps.stats.forms import get_pvp_data_formset
from haley_gg.apps.stats.forms import ResultForm


class ResultListView(ListView):
    template_name = 'stats/results_list.html'
    model = Result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = Result.objects.select_related(
            'map',
            'league',
            'player')
        context['result_list'] = results
        return context


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


class ProleagueView(TemplateView):
    template_name = 'stats/proleague.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league_list'] = League.objects.filter(
            type="proleague"
        ).prefetch_related(
            'result_set',
            'result_set__map',
            'result_set__league',
            'result_set__player',
        )
        return context

