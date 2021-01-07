from django.urls import path

from haley_gg.apps.stats import views


app_name = 'stats'

urlpatterns = [
    path('sample/', views.SampleView, name='sample_view'),
]
