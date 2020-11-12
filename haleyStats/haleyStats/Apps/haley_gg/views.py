# haley_gg/views.py
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    View,
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse

from .models import (
    User,
    Map,
    Match,
)
from .forms import (
    MapForm,
    CreateUserForm,
    UpdateUserForm,
    CreateMatchForm,
)


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
class MapCreateView(CreateView):
    template_name = 'Pattern/create.html'
    model = Map
    form_class = MapForm


# Show details of a map object.
class MapDetailView(SelectMapMixin, DetailView):
    template_name = 'Maps/detail.html'
    model = Map
    context_object_name = 'map'

    def get_context_data(self, *args, **kwargs):
        context = super(MapDetailView, self).get_context_data(*args, **kwargs)
        context['winning_rate_dict'] = self.object.get_statistics_on_winning_rate()
        return context


# Update a map object.
class MapUpdateView(SelectMapMixin, UpdateView):
    template_name = 'Pattern/update.html'
    model = Map
    form_class = MapForm


# Delete a map object.
class MapDeleteView(SelectMapMixin, DeleteView):
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
class UserCreateView(CreateView):
    model = User
    template_name = 'Pattern/create.html'
    form_class = CreateUserForm


# Show details of a user object.
class UserDetailView(SelectUserMixin, View):
    template_name = 'Users/detail.html'

    def get(self, request, *args, **kwargs):
        # select user object with name keyword.
        user = self.get_object()
        # get winning rate with player list.(it has foreign key with user model.)
        # so player_set.all() returns all player model relate with user.
        winning_rate = user.get_winning_rate(user.player_set.all())

        match_list = Match.objects.filter(
            player__user=user, match_type='one_on_one')
        get_winning_rate_by_race = user.get_winning_rate_by_race(match_list)
        context = {
            'user': user,
            'match_list': match_list,
            'winning_rate': winning_rate,
            'winning_rate_by_race': get_winning_rate_by_race,
        }
        return render(request, self.template_name, context)


# Update a user object.
class UserUpdateView(SelectUserMixin, UpdateView):
    model = User
    template_name = 'Pattern/update.html'
    form_class = UpdateUserForm


# Delete a user object.
class UserDeleteView(SelectUserMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        # Can't sure properly select redirect url. I will think this later.
        return reverse('main_page')


# Show all matches.
class MatchListView(ListView):
    template_name = "Stats/match-list.html"
    paginated_by = 10
    model = Match


class CreateStarLeagueMatchView(View):
    template_name = "Stats/create-starleague-match.html"
    league_type = "starleague"
    players_count = 2
    form_class = CreateMatchForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


class CreateProLeagueMatchView(View):
    template_name = "Stats/create-proleague-match.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


