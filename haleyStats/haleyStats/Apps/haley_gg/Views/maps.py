from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    View, ListView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse

from ..Models.maps import Map
from ..forms import UploadFileForm
# Create your views here.


class SelectMapMixin(object):
    def get_object(self):
        return get_object_or_404(Map, name=self.kwargs['name'])


class MapListView(ListView):
    model = Map
    template_name = 'Maps/list.html'

    context_object_name = 'Maps'


class MapCreateView(View):
    template_name = 'Maps/create.html'

    def get(self, request, *args, **kwargs):
        form = UploadFileForm()
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('haley_gg:maps_list'))
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    # def form_valid(self, form):
    #     return super(MapCreateView, self).form_valid(form)

    # def form_invalid(self, form):
    #     return super(MapCreateView, self).form_invalid(form)


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
        return reverse('haley_gg:maps_list')
