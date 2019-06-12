"""Defines available url paths and views handling them"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('calendar/', views.index, name='index'),
    path('calendar/<str:date>', views.index_specific, name='index_specific'),
    path('conflicts/', views.show_conflicts, name='conflicts'),
    path('upload_schedule/', views.upload_schedule, name='upload_schedule'),
    path('upload_students/', views.upload_students, name='upload_students'),
    path('show_room_schedule/', views.show_rooms_schedule, name='show_room_schedule'),
    path('show_professors_schedule/', views.show_professors_schedule,
         name='show_professors_schedule'),
    path('show_groups_schedule/', views.show_groups_schedule, name='show_groups_schedule'),
    path('show_schedule/', views.show_schedule, name='show_schedule'),
    path('edit/<int:lesson_id>/', views.edit, name='edit'),
    path('remove/<int:lesson_id>/', views.remove, name='remove'),
    path('create/', views.create, name='create'),
    path('professors/', views.professors, name='professors'),
    path('delete_lessons/', views.delete_lessons, name='delete_lessons'),
    path('edit_lessons/', views.edit_lessons, name='edit_lessons'),
    path('export/', views.export, name='export'),
]

if settings.STATIC_URL is not None:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
