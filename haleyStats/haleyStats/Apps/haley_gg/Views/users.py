from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.urls import reverse

from ..Models.users import User
from ..Models.stats import Player
from ..forms import UserCreateForm, UserUpdateForm


# Select a user object with a name keyword.
class SelectUserMixin(object):
    def get_object(self):
        return get_object_or_404(User, name__iexact=self.kwargs['name'])


# Create a user object.
class UserCreateView(CreateView):
    model = User
    template_name = 'Pattern/create.html'
    form_class = UserCreateForm


# Show details of a user object.
class UserDetailView(SelectUserMixin, View):
    template_name = 'Users/detail.html'

    def get(self, request, *args, **kwargs):
        # select user object with name keyword.
        user = self.get_object()
        # get objects which same as selected user.
        # it must be pagination. i will manage it later.
        match_list = Player.objects.filter(user__exact=user)
        context = {
            'user': user,
            'match_list': match_list
        }
        return render(request, self.template_name, context)


# Update a user object.
class UserUpdateView(SelectUserMixin, UpdateView):
    model = User
    template_name = 'Pattern/update.html'
    form_class = UserUpdateForm


# Delete a user object.
class UserDeleteView(SelectUserMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        # Can't sure properly select redirect url. I will think this later.
        return reverse('main_page')
