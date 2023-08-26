from django.urls import path
from .views import PrefListView
from .views import update_category_ratings
from .views import updateUserObject
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", login_required(PrefListView.as_view()), name="prefs-home"),
    path("update-category-ratings/", update_category_ratings,
         name="update-categoryratings"),
    path("update-picked-user/", updateUserObject, name="update-picked-user"),
]
