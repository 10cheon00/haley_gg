from django.urls import path

from haley_gg.apps.stats import views


app_name = 'stats'

urlpatterns = [
    path('new/', views.ResultCreateView.as_view(), name='create_result'),
    path('proleague/', views.ProleagueView.as_view(), name='proleague'),
    path('starleague/', views.StarleagueView.as_view(), name='starleague'),
    path('player/<name>/', views.PlayerDetailView.as_view(), name='player'),
    path('player/<name>/update', views.PlayerUpdateView.as_view(), name='update_player'),
    path('map/', views.MapView.as_view(), name='map_list'),
    path('compare/', views.CompareUserView.as_view(), name='compare')
]
