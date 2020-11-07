from django.shortcuts import render, redirect
from django.views.generic import (
    View,
    UpdateView,
)
from django.core.paginator import Paginator

from ..Models.stats import Match
from ..Forms.stats import (
    CreateStarLeagueMatchForm,
    get_playerformset_factory
)


# Show all matches.
class MatchListView(View):
    template_name = "Stats/match-list.html"

    def get(self, request, *args, **kwargs):
        matches = Match.objects.all()
        paginator = Paginator(matches, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, self.template_name, context)


class CreateStarLeagueMatchView(View):
    template_name = "Stats/create-starleague-match.html"

    def get(self, request, *args, **kwargs):
        match_form = CreateStarLeagueMatchForm()
        player_formset_factory = get_playerformset_factory(extra=2)
        player_formset = player_formset_factory()
        context = {
            'match_form': match_form,
            'player_formset': player_formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        match_form = CreateStarLeagueMatchForm(request.POST)
        player_formset_factory = get_playerformset_factory(extra=2)
        player_formset = player_formset_factory(request.POST)
        if match_form.is_valid() and player_formset.is_valid():
            # save match data.
            match = match_form.save(commit=False)
            match.match_type = "one_on_one"
            match.save()
            player_formset.instance = match
            player_formset.save()
            return redirect('/match/')
        context = {
            'match_form': match_form,
            'player_formset': player_formset,
        }
        return render(request, self.template_name, context)


class CreateProLeagueMatchView(View):
    template_name = "Stats/create-proleague-match.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
