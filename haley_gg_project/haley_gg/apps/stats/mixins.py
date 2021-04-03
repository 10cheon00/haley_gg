from django.shortcuts import get_object_or_404

from haley_gg.apps.stats.models import League
from haley_gg.apps.stats.models import Player
from haley_gg.apps.stats.utils import remove_space


class LeagueStatisticMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics'] = League.get_league_statistics(self.queryset)
        return context


class PlayerSelectMixin(object):
    def get_object(self):
        return get_object_or_404(
            Player,
            name__iexact=remove_space(self.kwargs['name'])
        )


class MapSelectMixin(object):
    def get_object(self):
        return get_object_or_404(
            Map,
            name__iexact=remove_space(self.kwargs['name'])
        )
