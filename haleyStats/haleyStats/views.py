from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from .Apps.haley_gg.Models.users import User


def main_page(request):
    # if request.method == 'GET':
    #     user_name = request.GET.get('search-user')
    #     if user_name:
    #         user = get_object_or_404(User, name__iexact=user_name)
    #         if user:
    #             return redirect('haley_gg:users_detail', user.name)
    return render(request, "main_page.html", {})
