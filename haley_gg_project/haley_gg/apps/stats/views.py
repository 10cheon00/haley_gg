from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django.db.models import Count

from haley_gg.apps.stats.models import Result
from haley_gg.apps.stats.models import League
from haley_gg.apps.stats.models import Map
from haley_gg.apps.stats.models import Player
from haley_gg.apps.stats.forms import get_pvp_data_formset
from haley_gg.apps.stats.forms import ResultForm
from haley_gg.apps.stats.forms import UpdatePlayerForm
from haley_gg.apps.stats.utils import remove_space
from haley_gg.apps.stats.utils import get_grouped_results_by_match_name
from haley_gg.apps.stats.utils import get_grouped_results_that_has_player
from haley_gg.apps.stats.mixins import LeagueStatisticMixin
from haley_gg.apps.stats.mixins import PlayerSelectMixin


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
        context['result_dict'] = get_grouped_results_by_match_name(queryset)
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


class ProleagueView(LeagueStatisticMixin, TemplateView):
    template_name = 'stats/leagues/proleague.html'
    queryset = League.objects.filter(
        type='proleague'
    ).prefetch_related(
        'teams',
        'results',
        'results__map',
        'results__player',
    )


class StarleagueView(LeagueStatisticMixin, TemplateView):
    template_name = 'stats/leagues/starleague.html'
    queryset = League.objects.filter(
        type='starleague'
    ).prefetch_related(
        'results',
        'results__map',
        'results__player',
    )


class PlayerDetailView(PlayerSelectMixin, DetailView):
    model = Player
    template_name = 'stats/players/detail.html'

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
            get_grouped_results_by_match_name(queryset), self.object.name
        )
        context['result_dict'] = grouped_results_dict
        context.update(self.object.get_statistics())
        context.update(self.object.get_career_and_badge())
        return context


class PlayerUpdateView(PlayerSelectMixin, UpdateView):
    model = Player
    template_name = 'stats/players/update.html'
    form_class = UpdatePlayerForm
    """
    339 커리어 데이터
    [★1]HPL 시즌1 "불독이 멍멍"팀 우승(개인 5승3패/팀플 6승0패)
    HPL 시즌3 "Run"팀장
    HPL 시즌1 팀플다승3위(6승0패)
    HPL 시즌1 통합다승3위(10승3패)
    """


class MapListView(ListView):
    model = Map
    template_name = 'stats/maps/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps'] = context['object_list'].annotate(
            result_count=Count('results')/2
        ).order_by('-result_count', 'name')
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
