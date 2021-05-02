from abc import ABCMeta, abstractmethod

from django.shortcuts import get_object_or_404

from haley_gg.apps.stats.models import Player
from haley_gg.apps.stats.models import League
from haley_gg.apps.stats.models import Map
from haley_gg.apps.stats.utils import remove_space


class BaseStatisticMixin(metaclass=ABCMeta):
    """
    To use this mixin,
    specify model what have statistic classmethod,
    and specify queryset to use in statistic method.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 아마 밀리데이터는 항상 통계를 내주고 상황에 따라서 팀플데이터를 넣기로 한 것 같다.
        context['statistics'] = self.get_statistics()
        return context

    @abstractmethod
    def get_statistics(self):
        pass


class ProleagueStatisticMixin(BaseStatisticMixin):
    def get_statistics(self):
        return League.get_proleague_statistics()


class StarleagueStatisticMixin(BaseStatisticMixin):
    def get_statistics(self):
        return League.get_starleague_statistics()


class MapStatisticMixin(BaseStatisticMixin):
    def get_statistics(self):
        return Map.get_total_map_statistics()


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
