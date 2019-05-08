"""Defines available url paths and views handling them"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('conflicts/', views.show_conflicts, name='conflicts'),
    path('upload/', views.upload, name='upload'),
    path('show_room_schedule/', views.show_rooms_schedule, name='show_room_schedule'),
    path('show_professors_schedule/', views.show_professors_schedule,
         name='show_professors_schedule'),
    path('show_groups_schedule/', views.show_groups_schedule, name='show_groups_schedule'),
    path('show_schedule/', views.show_schedule, name='show_schedule'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('edit/<int:lesson_id>/', views.edit, name='edit'),
    path('create/', views.create, name='create'),
]

if settings.STATIC_URL is not None:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
