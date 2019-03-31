"""Views gathering point"""
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def index(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. Tu będzie strona głowna schedulera")
