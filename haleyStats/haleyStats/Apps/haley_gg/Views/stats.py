from django.shortcuts import render, redirect
from django.views.generic import (
    View,
    UpdateView,
)

from ..Models.stats import Match
from ..forms import MatchForm, PlayerFormsetFactory


# Show all matches.
class MatchListView(View):
    template_name = "Stats/list.html"

    def get(self, request, *args, **kwargs):
        matches_by_date = Match.objects.all()
        context = {
            'matches': matches_by_date,
        }
        return render(request, self.template_name, context)


# # Create a match model.
# class CreateMatchView(CreateView):
#     form_class = MatchForm
#     model = Match
#     template_name = 'Pattern/create.html'

#     def get_absolute_url(self):
#         return reverse('haley_gg:match_list')


class CreateMatchView(View):
    template_name = "Stats/create.html"

    def get(self, request, *args, **kwargs):
        matchForm = MatchForm(prefix="matchForm")
        playerFormset = PlayerFormsetFactory()
        # playerForm = PlayerForm(prefix="playerForm")
        context = {
            'match_form': matchForm,
            'player_formset': playerFormset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        matchForm = MatchForm(request.POST)
        playerFormset = PlayerFormsetFactory(request.POST)
        if matchForm.is_valid():
            if playerFormset.is_valid():
                return redirect('/match/')
        context = {
            'match_form': matchForm,
            'player_formset': playerFormset,
        }
        return render(request, self.template_name, context)


# Update a match model.
class UpdateMatchView(UpdateView):
    model = Match
    form_class = MatchForm
    template_name = "Pattern/update.html"
