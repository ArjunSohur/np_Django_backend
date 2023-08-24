from django.urls import path
from .views import HomeListView
from . import views

urlpatterns = [
    path("", HomeListView.as_view(), name="home-home"),
    ]