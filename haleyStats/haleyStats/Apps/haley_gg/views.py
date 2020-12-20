# haley_gg/views.py
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import FormView
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.db.models import Count

from .models import User
from .models import Player
from .models import Map
from .models import Match
from .forms import CreateMapForm
from .forms import UpdateMapForm
from .forms import CreateUserForm
from .forms import UpdateUserForm
from .forms import MatchSheetForm
from .forms import CompareForm
from .utils import get_spreadsheet


# Select a map object with a name keyword.
class SelectMapMixin(object):
    def get_object(self):
        map = get_object_or_404(Map, name__iexact=self.kwargs['name'])
        return map


# Show all map objects.
class MapListView(ListView):
    template_name = 'Maps/list.html'
    model = Map
    paginated_by = 9
    context_object_name = 'maps'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['maps'] = Map.get_match_count().order_by('-count')
        return context


# Create a map object.
class CreateMapView(CreateView):
    template_name = 'Pattern/create.html'
    model = Map
    form_class = CreateMapForm


# Show details of a map object.
class DetailMapView(SelectMapMixin, DetailView):
    template_name = 'Maps/detail.html'
    model = Map
    context_object_name = 'map'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailMapView, self).get_context_data(*args, **kwargs)
        # only works on melee maps
        context['match_count'] = Map.get_match_count().filter(
            name__iexact=self.kwargs['name']
        ).values_list('count')[0]
        context['winning_rate_dict'] = self.object.get_statistics_on_winning_rate()
        return context


# Update a map object.
class UpdateMapView(SelectMapMixin, UpdateView):
    template_name = 'Pattern/update.html'
    model = Map
    form_class = UpdateMapForm


# Delete a map object.
class DeleteMapView(SelectMapMixin, DeleteView):
    template_name = "Pattern/delete.html"
    model = Map

    def get_success_url(self):
        return reverse('haley_gg:maps_list')


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
        context['match_queryset'] = self.object.get_user_melee_data()
        context['winning_rate'] = self.object.get_winning_rate()
        context['winning_rate_by_race'] = self.object.get_winning_rate_by_race()
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
    queryset = Match.melee.prefetch_related(
        'player_set',
        'player_set__user' # holy!
    ).select_related(
        'league', 'map'
    )


class MatchLoadSheetView(FormView):
    template_name = "Stats/load_sheet.html"
    form_class = MatchSheetForm

    def get_success_url(self):
        return reverse('haley_gg:match_list')

    def form_valid(self, form):
        document_url = form.cleaned_data['document_url']
        Match.create_data_from_sheet(get_spreadsheet(document_url))
        return super().form_valid(form)


class CompareView(View):
    template_name = 'Compare/compare.html'

    def get(self, request, *args, **kwargs):
        form = CompareForm(request.GET or None)
        context = {
            'compare_form': form
        }
        if form.is_valid():
            user_1 = form.cleaned_data['user_1']
            user_2 = form.cleaned_data['user_2']
            # map_name = form.cleaned_data['map_name']
            context.update(
                User.objects.get(name__iexact=user_1).versus(user_2)
            )
        return render(request, self.template_name, context)


class RankView(TemplateView):
    template_name = 'Rank/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(User.get_rank_data())
        return context
