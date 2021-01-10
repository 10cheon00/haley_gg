from django.shortcuts import render
from django.views.generic import ListView, CreateView

from haley_gg.apps.stats.models import Result
from haley_gg.apps.stats.forms import ResultForm


class ResultListView(ListView):
    template_name = 'stats/results_list.html'
    model = Result


class CreateResultView(CreateView):
    template_name = 'stats/create.html'
    form_class = ResultForm
