from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404


def main_page(request):
    return render(request, "main-page.html", {})
