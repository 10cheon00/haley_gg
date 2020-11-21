# haley_gg/views.py
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    FormView
)
from django.urls import reverse

from .models import User
from .models import Map
from .models import Match
from .forms import MapForm
from .forms import CreateUserForm
from .forms import UpdateUserForm
from .forms import MatchSheetForm
from .utils import get_spreadsheet


# Select a map object with a name keyword.
class SelectMapMixin(object):
    def get_object(self):
        map = get_object_or_404(Map, name__iexact=self.kwargs['name'])
        map.update_match_count()
        return map


# Show all map objects.
class MapListView(ListView):
    template_name = 'Maps/list.html'
    model = Map
    paginated_by = 9
    context_object_name = 'maps'

    def get_queryset(self):
        maps = Map.objects.all()
        for map in maps:
            map.update_match_count()
        return maps


# Create a map object.
class CreateMapView(CreateView):
    template_name = 'Pattern/create.html'
    model = Map
    form_class = MapForm


# Show details of a map object.
class DetailMapView(SelectMapMixin, DetailView):
    template_name = 'Maps/detail.html'
    model = Map
    context_object_name = 'map'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailMapView, self).get_context_data(*args, **kwargs)
        context['winning_rate_dict'] = self.object.get_statistics_on_winning_rate()
        return context


# Update a map object.
class UpdateMapView(SelectMapMixin, UpdateView):
    template_name = 'Pattern/update.html'
    model = Map
    form_class = MapForm


# Delete a map object.
class DeleteMapView(SelectMapMixin, DeleteView):
    template_name = "Pattern/delete.html"
    model = Map

    def get_success_url(self):
        return reverse('haley_gg:maps_list')

# MapTypeViews should be write below.


# Select a user object with a name keyword.
class SelectUserMixin(object):
    def get_object(self):
        return get_object_or_404(User, name__iexact=self.kwargs['name'])


# Create a user object.
class CreateUserView(CreateView):
    template_name = 'Pattern/create.html'
    model = User
    form_class = CreateUserForm


# Show details of a user object.
class DetailUserView(SelectUserMixin, DetailView):
    template_name = 'Users/detail.html'
    model = User
    context_object_name = 'user'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailUserView, self).get_context_data(*args, **kwargs)
        match_list = Match.objects.filter(
            player__user=self.object, match_type='one_on_one')
        context['match_list'] = match_list
        context['winning_rate'] = self.object.get_winning_rate(
            self.object.player_set.all())
        context['get_winning_rate_by_race'] = self.object.get_winning_rate_by_race(match_list)
        context['winning_status'] = self.object.get_winning_status()
        return context


# Update a user object.
class UpdateUserView(SelectUserMixin, UpdateView):
    model = User
    template_name = 'Pattern/update.html'
    form_class = UpdateUserForm


# Delete a user object.
class DeleteUserView(SelectUserMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        # Can't sure properly select redirect url. I will think this later.
        return reverse('main_page')


# Show all matches.
class MatchListView(ListView):
    template_name = "Stats/match-list.html"
    paginate_by = 10
    model = Match


class MatchLoadSheetView(FormView):
    template_name = "Stats/load_sheet.html"
    form_class = MatchSheetForm

    def get_success_url(self):
        return reverse('haley_gg:match_list')

    def form_valid(self, form):
        document_url = form.cleaned_data['document_url']
        Match.create_data_from_sheet(get_spreadsheet(document_url))
        return super().form_valid(form)
