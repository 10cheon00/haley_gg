from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.views import View
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

    def form_valid(self, form):
        return super(UserCreateView, self).form_valid(form)


class UserDetailView(View):
    template_name = 'Users/detail.html'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, user_name=kwargs['user_name'])
        context = {
            'object': user
        }
        return render(request, self.template_name, context)
