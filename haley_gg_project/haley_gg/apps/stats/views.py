from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import DetailView
from django.db.models import Count

from haley_gg.apps.stats.models import Result
from haley_gg.apps.stats.models import League
from haley_gg.apps.stats.models import Map
from haley_gg.apps.stats.models import Player
from haley_gg.apps.stats.forms import get_pvp_data_formset
from haley_gg.apps.stats.forms import ResultForm
from haley_gg.apps.stats.utils import remove_space
from haley_gg.apps.stats.utils import get_grouped_results_with_match_name
from haley_gg.apps.stats.utils import get_grouped_results_that_has_player


class ResultListView(ListView):
    template_name = 'stats/results/list.html'
    model = Result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Result.objects.select_related(
            'map',
            'league',
            'player'
        )
        context['result_dict'] = get_grouped_results_with_match_name(queryset)
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
        leagues = League.objects.filter(
            type='proleague'
        ).prefetch_related(
            'teams',
            'results',
            'results__map',
            'results__player',
        )
        league_list = []
        for league in leagues:
            league_list.append(
                (league, get_grouped_results_with_match_name(league.results.all()))
            )
        context['leagues'] = leagues
        context['league_list'] = league_list
        return context


class PlayerDetailView(DetailView):
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
        grouped_results_dict = get_grouped_results_that_has_player(
            get_grouped_results_with_match_name(queryset), self.object.name
        )
        context['result_dict'] = grouped_results_dict
        context.update(self.object.get_statistics())
        return context


class MapListView(ListView):
    model = Map
    template_name = 'stats/maps/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calculated_map = context['object_list'].annotate(
            result_count=Count('results')/2
        ).order_by('-result_count', 'name')
        context['maps'] = calculated_map
        # 맵리스트 표시, 형식은 자유
        # 맵마다 경기 수 표시
        return context


class MapDetailView(DetailView):
    model = Map
    template_name = 'stats/maps/detail.html'

    def get_object(self):
        return get_object_or_404(
            Map,
            name__iexact=remove_space(self.kwargs['name'])
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.object.get_statistics())
        return context
