"""Defines available url paths and views handling them"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('show_calendar/', views.show_calendar, name='show_calendar'),
]
