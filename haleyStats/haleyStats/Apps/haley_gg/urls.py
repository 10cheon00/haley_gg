from django.urls import path

from . import views


app_name = 'haley_gg'

urlpatterns = []

# maps.urls
urlpatterns += [
    path('map/',
         views.MapListView.as_view(),
         name="maps_list"),
    path('map/new-map/',
         views.MapCreateView.as_view(),
         name="maps_create"),
    path('map/new-map-type/',
         views.MapCreateView.as_view(),
         name="maps_create"),
    path('map/<str:name>/',
         views.MapDetailView.as_view(),
         name="maps_detail"),
    path('map/<str:name>/delete/',
         views.MapDeleteView.as_view(),
         name="maps_delete"),
    path('map/<str:name>/update/',
         views.MapUpdateView.as_view(),
         name="maps_update"),
]

# users.urls
urlpatterns += [
    path('user/new/',
         views.UserCreateView.as_view(),
         name="users_create"),
    path('user/<str:name>/',
         views.UserDetailView.as_view(),
         name="users_detail"),
    path('user/<str:name>/delete/',
         views.UserDeleteView.as_view(),
         name="users_delete"),
    path('user/<str:name>/update/',
         views.UserUpdateView.as_view(),
         name="users_update"),
]

# stats.urls
urlpatterns += [
    path('match/',
         views.MatchListView.as_view(),
         name="match_list"),
    path('match/new-starleague',
         views.CreateStarLeagueMatchView.as_view(),
         name="match_create"),
    path('match/new-proleague',
         views.CreateProLeagueMatchView.as_view(),
         name="match_create"),
    # path('match/<int:id>/update/',
    #      stats.UpdateMatchView.as_view(),
    #      name="match_update"),
]
