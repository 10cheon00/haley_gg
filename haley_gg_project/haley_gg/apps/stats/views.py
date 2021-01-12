from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.forms import modelformset_factory

from haley_gg.apps.stats.models import Result


class ResultListView(ListView):
    template_name = 'stats/results_list.html'
    model = Result


class CreateResultView(View):
    template_name = 'stats/create.html'

    def get(self, request, *args, **kwargs):
        context = {
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        request.POST
        'form-TOTAL_FORMS': ['2'],
        'form-INITIAL_FORMS': ['0'],
        'form-MIN_NUM_FORMS': ['0'],
        'form-MAX_NUM_FORMS': ['1000'],
        """
        context = {
        }
        return render(request, self.template_name, context)
