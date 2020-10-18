from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse

from .models import Map
# Create your views here.


class SelectMapMixin(object):
    def get_object(self):
        return get_object_or_404(Map, name=self.kwargs['name'])


class MapListView(ListView):
    model = Map
    template_name = 'Maps/list.html'

    context_object_name = 'Maps'


class MapCreateView(CreateView):
    model = Map
    template_name = 'Maps/create.html'
    fields = [
        'name',
    ]

    def form_valid(self, form):
        return super(MapCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(MapCreateView, self).form_invalid(form)


class MapDetailView(SelectMapMixin, DetailView):
    template_name = 'Maps/detail.html'


class MapUpdateView(SelectMapMixin, UpdateView):
    model = Map
    template_name = 'Maps/update.html'
    fields = [
        'name',
    ]


class MapDeleteView(SelectMapMixin, DeleteView):
    template_name = "Maps/delete.html"

    def get_success_url(self):
        return reverse('maps:list')
