from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse

from .models import User
# Create your views here.


class SelectUserMixin(object):
    def get_object(self):
        return get_object_or_404(User, user_name=self.kwargs['user_name'])


class UserCreateView(CreateView):
    model = User
    template_name = 'Users/create.html'
    fields = [
        'user_name',
        'joined_date',
        'most_race'
    ]

    def form_valid(self, form):
        return super(UserCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(UserCreateView, self).form_invalid(form)


class UserDetailView(SelectUserMixin, DetailView):
    template_name = 'Users/detail.html'


class UserUpdateView(SelectUserMixin, UpdateView):
    model = User
    template_name = 'Users/update.html'
    fields = [
        'user_name',
        'joined_date',
        'most_race',
        'career'
    ]


class UserDeleteView(SelectUserMixin, DeleteView):
    template_name = "Users/delete.html"

    def get_success_url(self):
        return reverse('main_page')
