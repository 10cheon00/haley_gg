from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect

from .Apps.haley_gg.forms import SearchUserForm


def main_page(request):
    form = SearchUserForm(request.GET or None)

    if form.is_valid():
        return HttpResponseRedirect(
            reverse(
                "haley_gg:users_detail",
                kwargs={"name": form.cleaned_data['user_name']}
            )
        )
    context = {
        'search_form': form
    }
    return render(request, "main-page.html", context)
