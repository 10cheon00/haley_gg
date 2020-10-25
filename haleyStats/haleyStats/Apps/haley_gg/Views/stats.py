from django.shortcuts import reverse, render, redirect
from django.views.generic import (
    View,
    UpdateView,
    CreateView
)

from ..Models.stats import Match
from ..forms import MatchForm


class MatchListView(View):
    template_name = "Stats/list.html"

    def get(self, request, *args, **kwargs):
        matches_by_date = Match.objects.all()
        context = {
            'matches': matches_by_date,
        }
        return render(request, self.template_name, context)


class CreateMatchView(CreateView):
    form_class = MatchForm
    model = Match
    template_name = 'Pattern/create.html'
#     def get(self, request, *args, **kwargs):
#         form = MatchForm()
#         context = {
#             'form': form
#         }
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         form = MatchForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse('haley_gg:match_list'))
#         context = {
#             'form': form
#         }
#         return render(request, self.template_name, context)

#     def form_valid(self, form):
#         return super(CreateMeleeView, self).form_valid(form)

#     def form_invalid(self, form):
#         return super(CreateMeleeView, self).form_invalid(form)

    def get_absolute_url(self):
        return reverse('haley_gg:match_list')


class UpdateMatchView(UpdateView):
    model = Match
    form_class = MatchForm
    template_name = "Pattern/update.html"