"""Defines available url paths and views handling them"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('show_calendar/', views.show_calendar, name='show_calendar'),
]

if settings.STATIC_URL is not None:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
