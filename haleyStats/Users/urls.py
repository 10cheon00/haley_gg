from django.urls import path

from . import views

app_name='users'
urlpatterns = [
    path('new/',
         views.UserCreateView.as_view(),
         name="create"),
    path('<str:name>/',
         views.UserDetailView.as_view(),
         name="detail"),
]