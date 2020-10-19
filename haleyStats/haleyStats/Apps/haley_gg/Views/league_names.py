from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView
)

from ..Models.league_names import LeagueName


class SelectLeagueNameMixin(object):
    def get_object(self):
        return get_object_or_404(LeagueName, name=self.kwargs['name'])


class LeagueNameCreateView(CreateView):
    model = LeagueName
    template_name = 'Pattern/create.html'
    fields = [
        'name',
    ]

    def form_valid(self, form):
        return super(LeagueNameCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(LeagueNameCreateView, self).form_invalid(form)


class LeagueNameDetailView(SelectLeagueNameMixin, DetailView):
    template_name = 'LeagueNames/detail.html'


class LeagueNameUpdateView(SelectLeagueNameMixin, UpdateView):
    model = LeagueName
    template_name = 'Pattern/update.html'
    fields = [
        'name',
    ]


class LeagueNameDeleteView(SelectLeagueNameMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        return reverse('haley_gg:stats')
