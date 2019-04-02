"""Views gathering point"""
import os.path
import pandas as pd
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import FileSystemStorage
import scheduler.import_handlers as imp


def index(_request: HttpRequest) -> HttpResponse:
    """Render the main page"""
    return render(_request, 'index.html')


def upload(request: HttpRequest) -> HttpResponse:
    """Render file upload page"""
    if request.method == 'POST' and request.FILES['myfile']:
        print(request.POST)
        myfile = request.FILES['myfile']
        storage = FileSystemStorage()
        ext = os.path.splitext(myfile.name)[1]
        if ext == '.csv':
            storage.save(myfile.name, myfile)
            data = pd.read_csv(myfile.name)
            storage.delete(myfile.name)
        elif ext == '.xlsx':
            storage.save(myfile.name, myfile)
            data = pd.read_excel(myfile.name)
            storage.delete(myfile.name)
        else:
            return render(request, "upload.html", {'error': "Extension not supported"})
        added_lessons = imp.import_data(data)
        data_html = data.to_html(classes=["table-bordered", "table-striped", "table-hover"],
                                 justify='center')
        return render(request, "upload.html", {'loaded_data': data_html, 'added': added_lessons})
    return render(request, "upload.html")
