from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import reverse
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
from haley_gg.apps.stats.forms import CompareUserForm
from haley_gg.apps.stats.forms import UpdatePlayerForm
from haley_gg.apps.stats.forms import UpdateMapForm
from haley_gg.apps.stats.utils import ResultsGroupManager
from haley_gg.apps.stats.mixins import LeagueStatisticMixin
from haley_gg.apps.stats.mixins import PlayerSelectMixin
from haley_gg.apps.stats.mixins import MapSelectMixin


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
        context['result_dict'] = ResultsGroupManager(queryset)
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
    melee_queryset = Result.melee.filter(league__type='proleague')


class StarleagueView(LeagueStatisticMixin, TemplateView):
    template_name = 'stats/leagues/starleague.html'
    melee_queryset = Result.melee.filter(league__type='starleague')


class PlayerDetailView(PlayerSelectMixin, DetailView):
    model = Player
    template_name = 'stats/players/detail.html'
    queryset = Result.objects.select_related(
        'map',
        'league',
        'player'
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
        manager = ResultsGroupManager(self.queryset)
        context['results_groups'] = \
            manager.get_results_groups_which_having_player(self.object.name)
        context.update(self.object.get_statistics())
        context.update(self.object.get_career_and_titles())
        return context


class PlayerUpdateView(PlayerSelectMixin, UpdateView):
    model = Player
    template_name = 'stats/players/update.html'
    form_class = UpdatePlayerForm


class MapListView(ListView):
    model = Map
    template_name = 'stats/maps/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maps'] = context['object_list'].annotate(
            result_count=Count('results')/2  #  occured exception on teamplay.
        ).order_by('-result_count', 'name')
        # 맵리스트 표시, 형식은 자유
        # 맵마다 경기 수 표시
        return context


class MapDetailView(MapSelectMixin, DetailView):
    model = Map
    template_name = 'stats/maps/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.object.get_statistics())
        return context


class MapUpdateView(MapSelectMixin, UpdateView):
    model = Map
    template_name = 'stats/maps/update.html'
    form_class = UpdateMapForm


class CompareUserView(View):
    template_name = 'stats/compare/compare.html'
    form_class = CompareUserForm

    def get(self, request):
        form = CompareUserForm(request.GET or None)
        context = {
            'compare_user_form': form
        }
        if form.is_valid():
            # get data from form.
            # process comparing.
            player = Player.objects.get(
                name=form.cleaned_data.get('player')
            )
            opponent = Player.objects.get(
                name=form.cleaned_data.get('opponent')
            )
            context['compare'] = {
                'player': player,
                'opponent': opponent,
                'data': player.versus(opponent),
            }
        return render(request, self.template_name, context)
