from django.urls import path

from . import views

app_name = "stays"

urlpatterns = [
    path("", views.home, name="home"),
    path("escapes/", views.escape_list, name="list"),
    path("escapes/<slug:slug>/", views.escape_detail, name="escape"),
    path("destinations/<slug:slug>/", views.destination_detail, name="destination"),
    path("about/", views.about, name="about"),
    path("subscribe/", views.subscribe, name="subscribe"),
]
