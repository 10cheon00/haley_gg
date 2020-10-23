from django.shortcuts import reverse, render, redirect
from django.views.generic import (
    View,
)

from ..Models.stats import Match, Player
from ..forms import MatchForm


class MatchListView(View):
    """
    Get matches by date.
    """
    template_name = "Stats/list.html"

    def get(self, request, *args, **kwargs):
        # request.GET['time-option']
        # First, get all matches in a day which gave html.
        matches_by_date = Match.objects.all() # filter(date__exact='2020-10-22')
        # Second, get all player in a match each mathces.
        # player_in_match_list = []
        # for match in matches_by_date:
        #     player_in_match_list.append(
        #         Player.objects.filter(match__exact=match))
        context = {
            'matches': matches_by_date,
        }
        return render(request, self.template_name, context)


class CreateMeleeView(View):
    template_name = 'Pattern/create.html'

    def get(self, request, *args, **kwargs):
        form = MatchForm()
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('haley_gg:match_list'))
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

#     def form_valid(self, form):
#         return super(CreateMeleeView, self).form_valid(form)

#     def form_invalid(self, form):
#         return super(CreateMeleeView, self).form_invalid(form)

    def get_absolute_url(self):
        return reverse('haley_gg:match_list')
