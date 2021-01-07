from django.shortcuts import render


def SampleView(request):
    render(request, 'main_page.html', {})
