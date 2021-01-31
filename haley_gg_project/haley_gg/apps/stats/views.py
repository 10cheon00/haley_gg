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
        resultform = ResultForm()
        formset = PVPDataFormSet()
        context = {
            'formset': formset,
            'form': resultform
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        PVPDataFormSet = get_pvp_data_formset()
        resultForm = ResultForm(request.POST)
        formset = PVPDataFormSet(request.POST)
        if resultForm.is_valid():
            if formset.is_valid_with(resultForm):
                formset.save_with(resultForm)
                return redirect(reverse('stats:result_list'))
        context = {
            'formset': formset,
            'form': resultForm
        }
        return render(request, self.template_name, context)


class ProleagueView(TemplateView):
    template_name = 'stats/proleague.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['league_list'] = League.objects.filter(
            type="proleague"
        ).prefetch_related(
            'team_list',
            'result_list',
            'result_list__map',
            'result_list__league',
            'result_list__player',
        )
        return context

