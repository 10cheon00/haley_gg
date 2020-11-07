from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.urls import reverse

from ..Models.users import User
from ..Models.stats import Player, Match
from ..Forms.users import CreateUserForm, UpdateUserForm


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
