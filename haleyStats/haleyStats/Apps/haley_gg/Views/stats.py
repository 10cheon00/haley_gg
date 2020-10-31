from django.shortcuts import render, redirect
from django.views.generic import (
    View,
    UpdateView,
)
from django.db import transaction

from ..Models.stats import Match
from ..forms import MatchForm, player_formset_factory


# Show all matches.
class MatchListView(View):
    template_name = "Stats/list.html"

    def get(self, request, *args, **kwargs):
        matches_by_date = Match.objects.all()
        context = {
            'matches': matches_by_date,
        }
        return render(request, self.template_name, context)


class CreateMatchView(View):
    template_name = "Stats/create.html"

    def get(self, request, *args, **kwargs):
        match_form = MatchForm()
        player_formset = player_formset_factory()
        context = {
            'match_form': match_form,
            'player_formset': player_formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        match_form = MatchForm(request.POST)
        player_formset = player_formset_factory(request.POST)
        if match_form.is_valid() and player_formset.is_valid():
            with transaction.atomic():
                # save match data.
                match = match_form.save()
                # Caution! For now, only two players are saved.
                # Extra players are excluded.
                player_formset.instance = match
                player_formset.save()
            return redirect('/match/')
        context = {
            'match_form': match_form,
            'player_formset': player_formset,
        }
        return render(request, self.template_name, context)


# Update a match model.
class UpdateMatchView(UpdateView):
    model = Match
    form_class = MatchForm
    template_name = "Pattern/update.html"
