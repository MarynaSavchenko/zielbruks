"""Views gathering point"""
from django.shortcuts import render
from django.http import HttpResponse

def index(_request):
    return HttpResponse("Hello, world. Tu będzie strona głowna schedulera")
