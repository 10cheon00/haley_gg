from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    DetailView,
    CreateView
)
from django.urls import reverse

from ..Models.maps import Map
from ..forms import MapForm


# Select a map object with a name keyword.
class SelectMapMixin(object):
    def get_object(self):
        return get_object_or_404(Map, name__iexact=self.kwargs['name'])


# Show all map objects.
class MapListView(ListView):
    model = Map
    template_name = 'Maps/list.html'

    context_object_name = 'Maps'


# Create a map object.
class MapCreateView(CreateView):
    template_name = 'Pattern/create.html'
    model = Map
    form_class = MapForm


# Show details of a map object.
class MapDetailView(SelectMapMixin, DetailView):
    template_name = 'Maps/detail.html'


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
