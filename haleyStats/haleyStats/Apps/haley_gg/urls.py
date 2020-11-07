from django.urls import path

from .Views import maps
from .Views import users
from .Views import stats


app_name = 'haley_gg'

urlpatterns = []

# maps.urls
urlpatterns += [
    path('map/',
         maps.MapListView.as_view(),
         name="maps_list"),
    path('map/new/',
         maps.MapCreateView.as_view(),
         name="maps_create"),
    path('map/<str:name>/',
         maps.MapDetailView.as_view(),
         name="maps_detail"),
    path('map/<str:name>/delete/',
         maps.MapDeleteView.as_view(),
         name="maps_delete"),
    path('map/<str:name>/update/',
         maps.MapUpdateView.as_view(),
         name="maps_update"),
]

# users.urls
urlpatterns += [
    path('user/new/',
         users.UserCreateView.as_view(),
         name="users_create"),
    path('user/<str:name>/',
         users.UserDetailView.as_view(),
         name="users_detail"),
    path('user/<str:name>/delete/',
         users.UserDeleteView.as_view(),
         name="users_delete"),
    path('user/<str:name>/update/',
         users.UserUpdateView.as_view(),
         name="users_update"),
]

# stats.urls
urlpatterns += [
    path('match/',
         stats.MatchListView.as_view(),
         name="match_list"),
    path('match/new-starleague',
         stats.CreateStarLeagueMatchView.as_view(),
         name="match_create"),
    path('match/new-proleague',
         stats.CreateProLeagueMatchView.as_view(),
         name="match_create"),
    # path('match/<int:id>/update/',
    #      stats.UpdateMatchView.as_view(),
    #      name="match_update"),
]
