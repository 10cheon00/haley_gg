from django.shortcuts import render
from django.views.generic import CreateView, DetailView

from .models import User
# Create your views here.


class UserCreateView(CreateView):
    model = User
    template_name = 'Users/create.html'
    fields = [
        'user_name',
        'joined_date',
        'most_race'
    ]


class UserDetailView(DetailView):
    model = User
    template_name = 'Users/detail.html'
