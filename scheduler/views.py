"""Views gathering point"""
import os.path
import pandas as pd
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import default_storage
import scheduler.import_handlers as imp
from django.views import generic
import scheduler.conflicts as conflicts


class ConflictsView(generic.DetailView):
    template_name = 'conflicts.html'

    def get_context_data(self, **kwargs):
        context = super(ConflictsView, self).get_context_data(**kwargs)
        context['conflicts'] = conflicts.db_conflicts()
        return context


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
            added_lessons = imp.import_data(data)
            data_html = data.to_html(classes=["table-bordered", "table-striped", "table-hover"],
                                     justify='center')
            return render(request, "upload.html",
                          {'loaded_data': data_html, 'added': added_lessons})
    return render(request, "upload.html")


def conflicts(request: HttpRequest) -> HttpResponse:
    """Render the conflicts page"""
    return render(request, "conflicts.html")
