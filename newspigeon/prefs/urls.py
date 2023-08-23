from django.urls import path
from .views import PrefListView
from .views import update_category_ratings

urlpatterns = [
    path("", PrefListView.as_view(), name="prefs-home"),
    path("update-category-ratings/", update_category_ratings,
         name="update-categoryratings"),
]
