"""Views gathering point"""
import os.path
from datetime import datetime
from wsgiref.util import FileWrapper

import pandas as pd
from django.contrib.auth import authenticate, login as log
from django.core.files.storage import default_storage
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.utils.datastructures import MultiValueDictKeyError
from xlrd import XLRDError

import scheduler.import_handlers as imp
from scheduler.calendar_util import get_start_date, generate_conflicts_context, \
    generate_full_schedule_context, generate_full_index_context_with_date, get_group_colors, \
    get_auditoriums_colors, generate_full_index_context, generate_context_for_conflicts_report
from scheduler.conflicts_checker import db_conflicts
from scheduler.export_handlers import export_to_csv, export_to_excel
from scheduler.model_util import get_professor, get_auditorium, get_group
from scheduler.models import Auditorium, Lesson, Group, Conflict, Professor
from zielbruks.settings import LOGIN_REDIRECT_URL
from .forms import SelectAuditoriumForm, SelectProfessorForm, SelectGroupForm, \
    EditForm, MassEditForm, LoginForm, ExportForm


def login(request: HttpRequest) -> HttpResponse:
    """Render the login page"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    log(request, user)
                    # Redirect to a success page.
                    return HttpResponseRedirect(LOGIN_REDIRECT_URL)
            context = {'error': "Incorrect login or password", 'form': form}
            return render(request, 'login.html', context)
        return render(request, 'login.html', context={"form": form})
    context = {'form': LoginForm()}
    return render(request, 'login.html', context)


def index(request: HttpRequest) -> HttpResponse:
    """Render the main page"""
    context: dict = {}
    context.update(generate_conflicts_context())
    context.update(generate_full_schedule_context())
    context['form'] = MassEditForm()
    return render(request, 'index.html', context)


def index_specific(_request: HttpRequest, date: str) -> HttpResponse:
    """Render the main page with given date"""
    date_as_datetime = datetime.strptime(date, '%Y-%m-%d')
    context = generate_full_index_context_with_date(date_as_datetime)
    form = MassEditForm()
    context.update({'form': form})
    return render(_request, 'index.html', context)


def upload_schedule(request: HttpRequest) -> HttpResponse:
    """Render schedule upload page"""
    filename = None
    context: dict = {}
    try:
        if request.method == 'POST' and request.FILES['uploaded_file']:
            file = request.FILES['uploaded_file']
            if isinstance(file.name, str):
                filename = default_storage.save(file.name, file)

                ext = os.path.splitext(file.name)[1]
                if ext == '.csv':
                    data = pd.read_csv(file.name)
                elif ext == '.xlsx':
                    data = pd.read_excel(file.name)
                else:
                    return render(request, "upload_schedule.html",
                                  {'error': "Error: Extension not supported"})
                added_lessons, incorrect, duplicate = imp.parse_data(data, ext)
                data_html = data.style \
                    .set_table_attributes('class="table table-striped table-hover table-bordered"')\
                    .apply(lambda x: [('background: lightcoral' if x.name in incorrect else
                                       ('background: lightblue' if x.name in duplicate else ''))
                                      for _ in x], axis=1) \
                    .render()
                db_conflicts()
                context = {'loaded_data': data_html, 'added': added_lessons}
    except MultiValueDictKeyError:
        context = {'error': "Error: You didn't select a file"}
    except XLRDError:
        context = {'error': "Error: Corrupted file"}
    except UnicodeDecodeError:
        context = {'error': "Error: File contains weird symbols"}
    except imp.ImportSizeException:
        context = {'error': "Error: Incorrect number of columns"}
    finally:
        if filename:
            default_storage.delete(filename)
    return render(request, "upload_schedule.html", context)


def upload_students(request: HttpRequest) -> HttpResponse:
    """Render students upload page"""
    filename = None
    context: dict = {}
    try:
        if request.method == 'POST' and request.FILES['uploaded_file']:
            file = request.FILES['uploaded_file']
            if isinstance(file.name, str):
                filename = default_storage.save(file.name, file)

                ext = os.path.splitext(file.name)[1]
                if ext == '.csv':
                    data = pd.read_csv(file.name)
                elif ext == '.xlsx':
                    data = pd.read_excel(file.name)
                else:
                    return render(request, "upload_students.html",
                                  {'error': "Error: Extension not supported"})
                added_lessons, incorrect, duplicate = imp.import_students(data)
                data_html = data.style \
                    .set_table_attributes('class="table table-striped table-hover table-bordered"')\
                    .apply(lambda x: [('background: lightcoral' if x.name in incorrect else
                                       ('background: lightblue' if x.name in duplicate else ''))
                                      for _ in x], axis=1) \
                    .render()
                db_conflicts()
                context = {'loaded_data': data_html, 'added': added_lessons}
    except MultiValueDictKeyError:
        context = {'error': "Error: You didn't select a file"}
    except XLRDError:
        context = {'error': "Error: Corrupted file"}
    except UnicodeDecodeError:
        context = {'error': "Error: File contains weird symbols"}
    except imp.ImportSizeException:
        context = {'error': "Error: Incorrect number of columns"}
    finally:
        if filename:
            default_storage.delete(filename)
    return render(request, "upload_students.html", context)


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
                                        Group.objects.filter(id=q.group_id)[:1].get().name,
                                        room_number,
                                        (q.professor.name + " " + q.professor.surname),
                                        q.auditorium_color,
                                        q.group_color,
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
                'start_date': get_start_date(auditorium_lessons_query),
                "groups_colors": get_group_colors(),
                "auditoriums_colors": get_auditoriums_colors(),
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
                                        Group.objects.filter(id=q.group_id)[:1].get().name,
                                        Auditorium.objects.filter(id=q.auditorium_id)[:1]
                                        .get().number,
                                        (q.professor.name + " " + q.professor.surname),
                                        q.auditorium_color,
                                        q.group_color,
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
                'start_date': get_start_date(professors_lessons_query),
                "groups_colors": get_group_colors(),
                "auditoriums_colors": get_auditoriums_colors(),
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
                                    q.auditorium_color,
                                    q.group_color,
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
                'start_date': get_start_date(groups_lessons_query),
                "groups_colors": get_group_colors(),
                "auditoriums_colors": get_auditoriums_colors(),
            }
            return render(request, "groups_scheduler.html", context)
        return HttpResponse("AN ERROR OCCURRED")
    return render(request, "groups_scheduler.html", context={'form': SelectGroupForm()})


def show_schedule(request: HttpRequest) -> HttpResponse:
    """Render the schedule page"""
    context = generate_full_schedule_context()
    return render(request, "full_schedule.html", context)


def edit(request: HttpRequest, lesson_id) -> HttpResponse:
    """Render the edit page"""
    if request.META.get('HTTP_REFERER') is None:
        return redirect('/calendar/')
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            if is_ajax(request):
                return render(request, 'edit.html', context={"form": form})

            past_conflicts = list(Conflict.objects.all())
            lesson = Lesson.objects.get(id=form.cleaned_data['id'])
            lesson.name = form.cleaned_data['name']
            professor = form.cleaned_data['professor'].strip().split()
            lesson.professor = get_professor(professor[0], professor[1])
            lesson.auditorium = get_auditorium(form.cleaned_data['auditorium'])
            lesson.group = get_group(form.cleaned_data['group'])
            lesson.start_time = form.cleaned_data['start_time']
            lesson.end_time = form.cleaned_data['end_time']
            lesson.save()
            db_conflicts()
            context = generate_full_index_context_with_date(form.cleaned_data['start_time'])
            current_conflicts = list(context['conflicts'])
            context.update(generate_context_for_conflicts_report(past_conflicts, current_conflicts))
            return render(request, 'index.html', context=context)
        return render(request, 'edit.html', context={"form": form})
    lesson = Lesson.objects.get(id=lesson_id)
    form = EditForm(
        initial={'id': lesson.id, 'name': lesson.name, 'professor': lesson.professor,
                 'auditorium': lesson.auditorium, 'group': lesson.group,
                 'start_time': lesson.start_time, 'end_time': lesson.end_time})
    return render(request, 'edit.html', context={"form": form})


def create(request: HttpRequest) -> HttpResponse:
    """Render the create page"""
    if request.META.get('HTTP_REFERER') is None:
        return redirect('/calendar/')
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            if is_ajax(request):
                return render(request, 'edit.html', context={"form": form})

            past_conflicts = list(Conflict.objects.all())
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
            db_conflicts()
            context = generate_full_index_context_with_date(form.cleaned_data['start_time'])
            current_conflicts = list(context['conflicts'])
            context.update(generate_context_for_conflicts_report(past_conflicts, current_conflicts))
            return render(request, 'index.html', context=context)
        return render(request, 'edit.html', context={"form": form})
    return render(request, 'edit.html', context={"form": EditForm()})


def remove(request: HttpRequest, lesson_id) -> HttpResponse:
    """Remove event and redirect to index page"""
    try:
        if request.method == 'POST':
            past_conflicts = list(Conflict.objects.all())
            lesson = Lesson.objects.get(id=lesson_id)
            lesson.delete()
            db_conflicts()
            context = generate_full_index_context()
            current_conflicts = list(context['conflicts'])
            context.update(generate_context_for_conflicts_report(past_conflicts, current_conflicts))
            return render(request, 'index.html', context=context)
        return redirect('/calendar/')
    except Lesson.DoesNotExist:
        return redirect('/calendar/')


def is_ajax(request: HttpRequest) -> bool:
    return request.META.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest'


def delete_lessons(request: HttpRequest) -> HttpResponse:
    """Logic for mass delete of conflicts"""
    if request.method == 'POST':
        past_conflicts = list(Conflict.objects.all())
        checks = request.POST.getlist('checks[]')
        Lesson.objects.filter(id__in=checks).delete()
        db_conflicts()
        context = generate_full_index_context()
        current_conflicts = list(context['conflicts'])
        context.update(generate_context_for_conflicts_report(past_conflicts, current_conflicts))
        return render(request, 'index.html', context=context)
    context = generate_full_index_context()
    return render(request, 'index.html', context=context)


def edit_lessons(request: HttpRequest) -> HttpResponse:
    """Logic for mass edit of conflicts"""
    if request.method == 'POST':
        form = MassEditForm(request.POST)
        if form.is_valid():
            changes = {}
            past_conflicts = list(Conflict.objects.all())
            if form.cleaned_data['lesson_name']:
                changes['name'] = form.cleaned_data['lesson_name']
            if form.cleaned_data['professor']:
                professor = form.cleaned_data['professor'].strip().split()
                changes['professor'] = get_professor(professor[0], professor[1])
            if form.cleaned_data['auditorium']:
                changes['auditorium'] = get_auditorium(form.cleaned_data['auditorium'])
            if form.cleaned_data['group']:
                changes['group'] = get_group(form.cleaned_data['group'])
            if form.cleaned_data['start_time']:
                changes['start_time'] = form.cleaned_data['start_time']
            if form.cleaned_data['end_time']:
                changes['end_time'] = form.cleaned_data['end_time']

            checks = request.POST.getlist('checks[]')
            if changes != {}:
                lessons = Lesson.objects.filter(id__in=checks)
                lessons.update(**changes)

            db_conflicts()
            context_after_edit = generate_full_index_context()
            current_conflicts = list(context_after_edit['conflicts'])
            context_after_edit.update(
                generate_context_for_conflicts_report(past_conflicts, current_conflicts))
            return render(request, 'index.html', context=context_after_edit)
        context: dict = {}
        context.update(generate_conflicts_context())
        context.update(generate_full_schedule_context())
        context.update({'form': form})
        return render(request, 'index.html', context=context)
    return index(request)


def professors(request: HttpRequest) -> HttpResponse:
    """Render the professors page"""
    professors_list = Professor.objects.all()
    context = {'professors': professors_list, 'form': SelectProfessorForm()}
    if request.method == 'POST':
        if 'choose' in request.POST:
            form = SelectProfessorForm(request.POST)
            if form.is_valid():
                professor = form.cleaned_data['professor']
                email = professor.email
                if not email:
                    email = "Noemail"
                context = {'professors': professors_list, 'form': form, 'email': email}
        elif 'save' in request.POST:
            form = SelectProfessorForm(request.POST)
            if form.is_valid():
                email = request.POST.get('email')
                professor = form.cleaned_data['professor']
                try:
                    professor_with_email = Professor.objects.get(email=email)
                    if professor != professor_with_email:
                        context = {'professors': professors_list, 'form': form, 'email': email,
                                   'inform': "This email is already in use"}
                    else:
                        professor.email = email
                        professor.save()
                        context = {'professors': professors_list, 'form': SelectProfessorForm()}
                except Professor.DoesNotExist:
                    professor.email = email
                    professor.save()
                    context = {'professors': professors_list, 'form': SelectProfessorForm()}

        else:
            return HttpResponse("AN ERROR OCCURRED")
    return render(request, "professors.html", context)


def export(request: HttpRequest) -> HttpResponse:
    """Render the export page"""
    if request.META.get('HTTP_REFERER') is None:
        return redirect('/calendar/')
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            if is_ajax(request):
                return render(request, 'export.html', context={"form": form})
            if form.cleaned_data["start_time"] and form.cleaned_data["end_time"] and \
                    form.cleaned_data["file_format"] == "csv":
                temp_file = export_to_csv(form.cleaned_data["start_time"],
                                          form.cleaned_data["end_time"])
                file_name = 'schedule.csv'
            elif form.cleaned_data["start_time"] and form.cleaned_data["end_time"] and \
                    form.cleaned_data["file_format"] == "excel":
                temp_file = export_to_excel(form.cleaned_data["start_time"],
                                            form.cleaned_data["end_time"])
                file_name = 'schedule.xlsx'
            else:
                return render(request, 'export.html', context={"form": form})
            wrapper = FileWrapper(temp_file)
            response = HttpResponse(wrapper, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=' + file_name
            return response
        return render(request, 'export.html', context={"form": form})
    form = ExportForm()
    return render(request, 'export.html', context={"form": form})
