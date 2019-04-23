"""Views gathering point"""
import datetime
import os.path
from typing import List, Tuple

import pandas as pd
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader

import scheduler.conflicts as conflicts
import scheduler.import_handlers as imp
from scheduler.calendar_util import get_start_date
from scheduler.models import Auditorium, Lesson, Group, Professor
from .forms import SelectAuditoriumForm, SelectProfessorForm, SelectGroupForm


def index(_request: HttpRequest) -> HttpResponse:
    """Render the main page"""
    return render(_request, 'index.html')


def upload(request: HttpRequest) -> HttpResponse:
    """Render file upload page"""
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        if isinstance(myfile.name, str):
            ext = os.path.splitext(myfile.name)[1]
            if ext == '.csv':
                filename = default_storage.save(myfile.name, myfile)
                data = pd.read_csv(myfile.name)
                default_storage.delete(filename)
            elif ext == '.xlsx':
                filename = default_storage.save(myfile.name, myfile)
                data = pd.read_excel(myfile.name)
                default_storage.delete(filename)
            else:
                return render(request, "upload.html", {'error': "Extension not supported"})
            added_lessons, incorrect, duplicate = imp.parse_data(data, ext)
            data_html = data.to_html(classes=["table-bordered", "table-striped", "table-hover"],
                                     justify='center')
            context = {'loaded_data': data_html, 'added': added_lessons,
                       'incorrect': incorrect, 'duplicate': duplicate}
            return render(request, "upload.html", context)
    return render(request, "upload.html")


def show_conflicts(request: HttpRequest) -> HttpResponse:
    """Render the conflicts page"""
    template = loader.get_template('conflicts.html')
    conflicts_list = conflicts.db_conflicts()
    color = ''
    context = {
        'conflicts': conflicts_list,
        'color': color,
    }
    return HttpResponse(template.render(context, request))


def show_rooms_schedule(request: HttpRequest) -> HttpResponse:
    """Render the auditorium schedule page"""
    if request.method == 'POST':
        form = SelectAuditoriumForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data['auditorium']
            room_number = room.number
            auditorium_lessons_query = Lesson.objects.filter(auditorium=room)
            auditorium_lessons_list = [(q.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        q.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        Professor.objects.filter(id=q.professor_id)[:1].get(),
                                        room_number,
                                        Group.objects.filter(id=q.group_id)[:1].get().number)
                                       for q in auditorium_lessons_query]
            context = {
                'form': form,
                'chosen_flag': True,
                'events_flag': bool(auditorium_lessons_list),
                'room_no': room_number,
                'events': auditorium_lessons_list,
                'start_date': get_start_date(auditorium_lessons_query)
            }
            return render(request, "room_schedule.html", context)
        return HttpResponse("AN ERROR OCCURRED")
    return render(request, "room_schedule.html", context={'form': SelectAuditoriumForm()})


def show_professors_schedule(request: HttpRequest) -> HttpResponse:
    """Render the professor schedule page"""
    if request.method == 'POST':
        form = SelectProfessorForm(request.POST)
        if form.is_valid():
            professor = form.cleaned_data['professor']
            professors_lessons_query = Lesson.objects.filter(professor=professor)
            professors_lessons_list = [(q.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        q.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        q.name,
                                        Auditorium.objects.filter(id=q.auditorium_id)[:1]
                                        .get().number,
                                        Group.objects.filter(id=q.group_id)[:1].get().number)
                                       for q in professors_lessons_query]
            context = {
                'form': form,
                'chosen_flag': True,
                'events_flag': bool(professors_lessons_list),
                'events': professors_lessons_list,
                'professor': professor,
                'lessons': Lesson.objects.all(),
                'start_date': get_start_date(professors_lessons_query)
            }
            return render(request, "professors_scheduler.html", context)
        return HttpResponse("AN ERROR OCCURRED")
    return render(request, "professors_scheduler.html", context={'form': SelectProfessorForm()})


def show_groups_schedule(request: HttpRequest) -> HttpResponse:
    """Render the group schedule page"""
    if request.method == 'POST':
        form = SelectGroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            groups_lessons_query = Lesson.objects.filter(group=group)
            groups_lessons_list = [(q.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    q.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                    q.name,
                                    Auditorium.objects.filter(id=q.auditorium_id)[:1].get().number,
                                    (q.professor.name + " " + q.professor.surname))
                                   for q in groups_lessons_query]
            context = {
                'form': form,
                'chosen_flag': True,
                'events_flag': bool(groups_lessons_list),
                'events': groups_lessons_list,
                'group': group,
                'lessons': Lesson.objects.all(),
                'start_date': get_start_date(groups_lessons_query)
            }
            return render(request, "groups_scheduler.html", context)
        return HttpResponse("AN ERROR OCCURRED")
    return render(request, "groups_scheduler.html", context={'form': SelectGroupForm()})
