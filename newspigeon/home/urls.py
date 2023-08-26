from django.urls import path
from .views import HomeListView
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path("", login_required(HomeListView.as_view()), name="home-home"),
    path('process_rating/', views.process_rating, name='process_rating'),
    ]
