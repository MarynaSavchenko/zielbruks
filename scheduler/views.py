"""Views gathering point"""
import os.path

import pandas as pd
from django.core.files.storage import default_storage
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from xlrd import XLRDError

import scheduler.import_handlers as imp
from scheduler import models
from scheduler.calendar_util import get_start_date, generate_conflicts_context, \
    generate_full_schedule_context, get_full_context_with_date
from scheduler.model_util import get_professor, get_auditorium, get_group
from scheduler.models import Auditorium, Lesson, Group
from .forms import SelectAuditoriumForm, SelectProfessorForm, SelectGroupForm, EditForm


def index(_request: HttpRequest) -> HttpResponse:
    """Render the main page"""
    context: dict = {}
    context.update(generate_conflicts_context())
    context.update(generate_full_schedule_context())
    return render(_request, 'index.html', context)


def upload(request: HttpRequest) -> HttpResponse:
    """Render file upload page"""
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        if isinstance(myfile.name, str):
            filename = default_storage.save(myfile.name, myfile)
            try:
                ext = os.path.splitext(myfile.name)[1]
                if ext == '.csv':
                    data = pd.read_csv(myfile.name)
                elif ext == '.xlsx':
                    data = pd.read_excel(myfile.name)
                else:
                    return render(request, "upload.html",
                                  {'error': "Error: Extension not supported"})
                added_lessons, incorrect, duplicate = imp.parse_data(data, ext)
                data_html = data.style \
                    .set_table_attributes('class="table table-striped table-hover table-bordered"')\
                    .apply(lambda x: [('background: lightcoral' if x.name in incorrect else
                                       ('background: lightblue' if x.name in duplicate else ''))
                                      for i in x], axis=1) \
                    .render()
                return render(request, "upload.html",
                              {'loaded_data': data_html, 'added': added_lessons})
            except XLRDError:
                return render(request, "upload.html", {'error': "Error: Corrupted file"})
            finally:
                default_storage.delete(filename)
    return render(request, "upload.html")


def show_conflicts(request: HttpRequest) -> HttpResponse:
    """Render the conflicts page"""
    template = loader.get_template('conflicts.html')
    context = generate_conflicts_context()
    return HttpResponse(template.render(context, request))


def show_rooms_schedule(request: HttpRequest) -> HttpResponse:
    """Render the auditorium schedule page"""
    if request.method == 'POST':
        form = SelectAuditoriumForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data['auditorium']
            room_number = room.number
            auditorium_lessons_query = Lesson.objects.filter(auditorium=room)
            auditorium_lessons_list = [(q.start_time.isoformat(timespec='seconds'),
                                        q.end_time.isoformat(timespec='seconds'),
                                        q.name,
                                        Group.objects.filter(id=q.group_id)[:1].get().number,
                                        room_number,
                                        (q.professor.name + " " + q.professor.surname),
                                        models.palette[q.auditorium_id % len(models.palette)],
                                        models.palette[q.group_id % len(models.palette)],
                                        q.id,
                                        q.start_time.strftime("%H:%M") + "-"
                                        + q.end_time.strftime("%H:%M"))
                                       for q in auditorium_lessons_query]
            context = {
                'form': form,
                'chosen_flag': True,
                'events_flag': bool(auditorium_lessons_list),
                'type': 'auditorium',
                'name': room_number,
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
            professors_lessons_list = [(q.start_time.isoformat(timespec='seconds'),
                                        q.end_time.isoformat(timespec='seconds'),
                                        q.name,
                                        Group.objects.filter(id=q.group_id)[:1].get().number,
                                        Auditorium.objects.filter(id=q.auditorium_id)[:1]
                                        .get().number,
                                        (q.professor.name + " " + q.professor.surname),
                                        models.palette[q.auditorium_id % len(models.palette)],
                                        models.palette[q.group_id % len(models.palette)],
                                        q.id,
                                        q.start_time.strftime("%H:%M") + "-"
                                        + q.end_time.strftime("%H:%M"))
                                       for q in professors_lessons_query]
            context = {
                'form': form,
                'chosen_flag': True,
                'events_flag': bool(professors_lessons_list),
                'events': professors_lessons_list,
                'type': 'professor',
                'name': professor,
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
            groups_lessons_list = [(q.start_time.isoformat(timespec='seconds'),
                                    q.end_time.isoformat(timespec='seconds'),
                                    q.name,
                                    group,
                                    Auditorium.objects.filter(id=q.auditorium_id)[:1].get().number,
                                    (q.professor.name + " " + q.professor.surname),
                                    models.palette[q.auditorium_id % len(models.palette)],
                                    models.palette[q.group_id % len(models.palette)],
                                    q.id,
                                    q.start_time.strftime("%H:%M") + "-"
                                    + q.end_time.strftime("%H:%M"))
                                   for q in groups_lessons_query]
            context = {
                'form': form,
                'chosen_flag': True,
                'events_flag': bool(groups_lessons_list),
                'events': groups_lessons_list,
                'type': 'group',
                'name': group,
                'lessons': Lesson.objects.all(),
                'start_date': get_start_date(groups_lessons_query)
            }
            return render(request, "groups_scheduler.html", context)
        return HttpResponse("AN ERROR OCCURRED")
    return render(request, "groups_scheduler.html", context={'form': SelectGroupForm()})


def show_schedule(request: HttpRequest) -> HttpResponse:
    """Render the schedule page"""
    context = generate_full_schedule_context()
    return render(request, "full_schedule.html", context)


def sign_up(request: HttpRequest) -> HttpResponse:
    """Render the signup page"""
    return render(request, "still_working.html")


def log_in(request: HttpRequest) -> HttpResponse:
    """Render the login page"""
    return render(request, "still_working.html")


def edit(request: HttpRequest, lesson_id) -> HttpResponse:
    """Render the edit page"""
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            lesson = Lesson.objects.get(id=form.cleaned_data['id'])
            lesson.name = form.cleaned_data['name']
            professor = form.cleaned_data['professor'].strip().split()
            lesson.professor = get_professor(professor[0], professor[1])
            lesson.auditorium = get_auditorium(form.cleaned_data['auditorium'])
            lesson.group = get_group(form.cleaned_data['group'])
            lesson.start_time = form.cleaned_data['start_time']
            lesson.end_time = form.cleaned_data['end_time']
            lesson.save()
            context = get_full_context_with_date(form.cleaned_data['start_time'])
            return render(request, 'index.html', context=context)
        return render(request, 'edit.html', context={"form": form})
    lesson = Lesson.objects.get(id=lesson_id)
    form = EditForm(
        initial={'id': lesson.id, 'name': lesson.name, 'professor': lesson.professor,
                 'auditorium': lesson.auditorium, 'group': lesson.group,
                 'start_time': lesson.start_time, 'end_time': lesson.end_time})
    return render(request, 'edit.html', context={"form": form})


def create(request: HttpRequest) -> HttpResponse:
    """Render the edit page"""
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            professor = form.cleaned_data['professor'].strip().split()
            professor = get_professor(professor[0], professor[1])
            auditorium = get_auditorium(form.cleaned_data['auditorium'])
            group = get_group(form.cleaned_data['group'])
            Lesson.objects.get_or_create(
                name=form.cleaned_data['name'],
                professor=professor,
                auditorium=auditorium,
                group=group,
                start_time=form.cleaned_data['start_time'],
                end_time=form.cleaned_data['end_time']
            )
            context = get_full_context_with_date(form.cleaned_data['start_time'])
            return render(request, 'index.html', context=context)
        return render(request, 'edit.html', context={"form": form})
    return render(request, 'edit.html', context={"form": EditForm()})
