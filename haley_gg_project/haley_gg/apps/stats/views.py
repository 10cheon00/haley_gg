from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView, View, ListView, DetailView

from haley_gg.apps.stats.models import Result, League, Player
from haley_gg.apps.stats.forms import get_pvp_data_formset
from haley_gg.apps.stats.forms import ResultForm
from haley_gg.apps.stats.utils import remove_space


class GroupedResultMixin(object):
    def get_grouped_results(self, queryset):
        # Group result data by result name.
        grouped_result_dict = {}
        for result in queryset:
            name = result.match_name()
            if name not in grouped_result_dict:
                grouped_result_dict[name] = []
            grouped_result_dict[name].append(result)
        return grouped_result_dict


class ResultListView(GroupedResultMixin, ListView):
    template_name = 'stats/results/list.html'
    model = Result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Result.objects.select_related(
            'map',
            'league',
            'player'
        )
        context['result_list'] = self.get_grouped_results(queryset)
        return context


class ResultCreateView(View):
    template_name = 'stats/results/create.html'

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
    template_name = 'stats/leagues/proleague.html'

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


class PlayerDetailView(GroupedResultMixin, DetailView):
    model = Player
    template_name = 'stats/players/detail.html'

    def get_object(self):
        return get_object_or_404(
            Player,
            name__iexact=remove_space(self.kwargs['name'])
        )

    """
    get_context_data sequence.

    1. View requests object to model with queryset.
       Queryset is specified in view or custom get_object function.
    2. View contain object to context dictionary.
       If view has context_object_name, replace key to it.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Result.objects.select_related(
            'map',
            'league',
            'player'
        )
        result_dict = self.get_grouped_results(queryset)
        for key, results in result_dict.items():
            # If grouped_result_list not contain this player, remove it.
            pass
        return context
