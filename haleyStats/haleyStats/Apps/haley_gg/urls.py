from django.urls import path

from .Views import maps
from .Views import users


app_name = 'haley_gg'

urlpatterns = [
    path('maps/',
         maps.MapListView.as_view(),
         name="maps_list"),
    path('maps/new/',
         maps.MapCreateView.as_view(),
         name="maps_create"),
    path('maps/<str:name>/',
         maps.MapDetailView.as_view(),
         name="maps_detail"),
    path('maps/<str:name>/delete/',
         maps.MapDeleteView.as_view(),
         name="maps_delete"),
    path('maps/<str:name>/update/',
         maps.MapUpdateView.as_view(),
         name="maps_update"),

    path('users/new/',
         users.UserCreateView.as_view(),
         name="users_create"),
    path('users/<str:name>/',
         users.UserDetailView.as_view(),
         name="users_detail"),
    path('users/<str:name>/delete/',
         users.UserDeleteView.as_view(),
         name="users_delete"),
    path('users/<str:name>/update/',
         users.UserUpdateView.as_view(),
         name="users_update"),
]

