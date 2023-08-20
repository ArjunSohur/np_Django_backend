from django.urls import path
from .views import PrefListView, update_preferences

urlpatterns = [
    path("", PrefListView.as_view(), name="prefs-home"),
    path("update_preferences/", update_preferences, name="update_preferences"),
]