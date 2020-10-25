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
# Create your views here.


class SelectUserMixin(object):
    def get_object(self):
        return get_object_or_404(User, name=self.kwargs['name'])


class UserCreateView(CreateView):
    model = User
    template_name = 'Pattern/create.html'
    form_class = UserCreateForm


class UserDetailView(SelectUserMixin, View):
    template_name = 'Users/detail.html'

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        match_list = Player.objects.filter(user__exact=user)  # need ordering.
        # match_list = Match.objects.filter(date__exact=datetime(2020, 10, 23))
        context = {
            'user': user,
            'match_list': match_list
        }
        return render(request, self.template_name, context)


class UserUpdateView(SelectUserMixin, UpdateView):
    model = User
    template_name = 'Pattern/update.html'
    form_class = UserUpdateForm


class UserDeleteView(SelectUserMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        # Can't sure properly select redirect url. I will think this later.
        return reverse('main_page')
