from django.shortcuts import render
from django.http import HttpResponseRedirect

from .Apps.haley_gg.models import User
from .Apps.haley_gg.forms import SearchUserForm


def main_page(request):
    form = SearchUserForm(request.GET or None)

    if form.is_valid():
        user = User.objects.get(name__iexact=form.cleaned_data['user_name'])
        return HttpResponseRedirect(user.get_absolute_url())
    context = {
        'search_form': form
    }
    return render(request, "main-page.html", context)
