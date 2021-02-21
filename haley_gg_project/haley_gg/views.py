from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect

from haley_gg.apps.stats.forms import SearchPlayerForm


def main_page(request):
    form = SearchPlayerForm(request.GET or None)
    if form.is_valid():
        # If there is no matched player... What to do?
        return HttpResponseRedirect(
            reverse(
                'stats:player',
                kwargs={'name': form.cleaned_data['name']}
            )
        )
    context = {
        'search_player_form': form
    }
    return render(request, "main-page.html", context)
