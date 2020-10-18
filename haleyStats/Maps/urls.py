from django.urls import path

from . import views

app_name = 'maps'

urlpatterns = [
    path('',
         views.MapListView.as_view(),
         name="list"),
    path('new/',
         views.MapCreateView.as_view(),
         name="create"),
    path('<str:name>/',
         views.MapDetailView.as_view(),
         name="detail"),
    path('<str:name>/delete/',
         views.MapDeleteView.as_view(),
         name="delete"),
    path('<str:name>/update/',
         views.MapUpdateView.as_view(),
         name="update"),
]
