from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    View,
    UpdateView,
    DeleteView,
    CreateView
)
from django.urls import reverse

from ..Models.maps import Map
from ..Forms.maps import MapForm


# Select a map object with a name keyword.
class SelectMapMixin(object):
    def get_object(self):
        map = get_object_or_404(Map, name__iexact=self.kwargs['name'])
        map.update_match_count()
        return map


# Show all map objects.
class MapListView(View):
    model = Map
    template_name = 'Maps/list.html'

    def get(self, request, *args, **kwargs):
        # Must be pagination.
        maps = Map.objects.all()
        for map in maps:
            map.update_match_count()
        context = {
            'maps': maps,
        }
        return render(request, self.template_name, context)


# Create a map object.
class MapCreateView(CreateView):
    template_name = 'Pattern/create.html'
    model = Map
    form_class = MapForm


# Show details of a map object.
class MapDetailView(SelectMapMixin, View):
    template_name = 'Maps/detail.html'

    def get(self, request, *args, **kwargs):
        map = self.get_object()
        # get statistic data.
        winning_rate_dict = map.get_statistics_on_winning_rate()
        context = {
            'map': map,
            'winning_rate_dict': winning_rate_dict,
        }
        return render(request, self.template_name, context)


# Update a map object.
class MapUpdateView(SelectMapMixin, UpdateView):
    model = Map
    template_name = 'Pattern/update.html'
    form_class = MapForm


# Delete a map object.
class MapDeleteView(SelectMapMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        return reverse('haley_gg:maps_list')

# MapTypeViews should be write below.
