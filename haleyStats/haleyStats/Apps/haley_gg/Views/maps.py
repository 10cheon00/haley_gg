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
# Create your views here.


class SelectMapMixin(object):
    def get_object(self):
        return get_object_or_404(Map, name=self.kwargs['name'])


class MapListView(ListView):
    model = Map
    template_name = 'Maps/list.html'

    context_object_name = 'Maps'


class MapCreateView(CreateView):
    template_name = 'Pattern/create.html'
    model = Map
    form_class = MapForm


class MapDetailView(SelectMapMixin, DetailView):
    template_name = 'Maps/detail.html'


class MapUpdateView(SelectMapMixin, UpdateView):
    model = Map
    template_name = 'Pattern/update.html'
    form_class = MapForm


class MapDeleteView(SelectMapMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        return reverse('haley_gg:maps_list')
