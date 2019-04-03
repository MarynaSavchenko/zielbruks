"""Defines available url paths and views handling them"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('conflicts/', views.conflicts, name='conflicts'),
    path('upload/', views.upload, name='upload'),
]
