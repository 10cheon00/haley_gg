from django.shortcuts import reverse, render
from django.views.generic import (
    View,
    UpdateView,
    CreateView
)

from ..Models.stats import Match
from ..forms import MatchForm


# Show all matches.
class MatchListView(View):
    template_name = "Stats/list.html"

    def get(self, request, *args, **kwargs):
        matches_by_date = Match.objects.all()
        context = {
            'matches': matches_by_date,
        }
        return render(request, self.template_name, context)


# Create a match model.
class CreateMatchView(CreateView):
    form_class = MatchForm
    model = Match
    template_name = 'Pattern/create.html'

    def get_absolute_url(self):
        return reverse('haley_gg:match_list')


# Update a match model.
class UpdateMatchView(UpdateView):
    model = Match
    form_class = MatchForm
    template_name = "Pattern/update.html"
