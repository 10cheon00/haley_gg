from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse

from ..Models.users import User
from ..Models.stats import Match
# Create your views here.


class SelectUserMixin(object):
    def get_object(self):
        return get_object_or_404(User, name=self.kwargs['name'])


class UserCreateView(CreateView):
    model = User
    template_name = 'Pattern/create.html'
    fields = [
        'name',
        'joined_date',
        'most_race'
    ]

    def form_valid(self, form):
        return super(UserCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(UserCreateView, self).form_invalid(form)


class UserDetailView(SelectUserMixin, View):
    template_name = 'Users/detail.html'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        match_list = '' # Melee().get_queryset_with_id(obj.id)
        context = {
            'object': obj,
            'match_list': match_list
        }
        return render(request, self.template_name, context)


class UserUpdateView(SelectUserMixin, UpdateView):
    model = User
    template_name = 'Pattern/update.html'
    fields = [
        'name',
        'joined_date',
        'most_race',
        'career'
    ]


class UserDeleteView(SelectUserMixin, DeleteView):
    template_name = "Pattern/delete.html"

    def get_success_url(self):
        return reverse('main_page')
