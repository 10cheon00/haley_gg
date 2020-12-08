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
         views.CreateMapView.as_view(),
         name="maps_create"),
    # path('map/new-map-type/',
    #      views.MapCreateView.as_view(),
    #      name="maps_create"),
    path('map/<str:name>/',
         views.DetailMapView.as_view(),
         name="maps_detail"),
    path('map/<str:name>/delete/',
         views.DeleteMapView.as_view(),
         name="maps_delete"),
    path('map/<str:name>/update/',
         views.UpdateMapView.as_view(),
         name="maps_update"),
]

# users.urls
urlpatterns += [
    path('user/new/',
         views.CreateUserView.as_view(),
         name="users_create"),
    path('user/<str:name>/',
         views.DetailUserView.as_view(),
         name="users_detail"),
    path('user/<str:name>/delete/',
         views.DeleteUserView.as_view(),
         name="users_delete"),
    path('user/<str:name>/update/',
         views.UpdateUserView.as_view(),
         name="users_update"),
]

# stats.urls
urlpatterns += [
    path('match/',
         views.MatchListView.as_view(),
         name="match_list"),
    path('match/load-sheet/',
         views.MatchLoadSheetView.as_view(),
         name="match_load_data"),
]

# compare.urls
urlpatterns += [
    path('compare/',
         views.CompareView.as_view(),
         name="compare"),
]

# ranks.urls
urlpatterns += [
    path('rank/',
         views.RankView.as_view(),
         name="ranks"),
]