"""Views gathering point"""
import os.path
import pandas as pd
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import default_storage
from django.template import loader
import scheduler.import_handlers as imp
from scheduler.models import Auditorium, Lesson
import scheduler.conflicts as conflicts

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


def show_calendar(request: HttpRequest) -> HttpResponse:
    """ to do """
    times = pd.date_range('2019-12-02T08:00:00.000Z', '2019-12-02T22:00:00.000Z', freq='15T')
    rooms = Auditorium.objects.all()
    context = {
        'times': [d.strftime('%H:%M') for d in times],
        'rooms': rooms,
        'range': range(len(rooms)),
        'lessons': Lesson.objects.all()
    }
    return render(request, "calendar.html", context)

def confs(request: HttpRequest) -> HttpResponse:
    """Render the conflicts page"""
    template = loader.get_template('conflicts.html')
    conflicts_list = conflicts.db_conflicts()
    color = 'success'
    context = {
        'conflicts': conflicts_list,
        'color': color,
    }
    return HttpResponse(template.render(context, request))
