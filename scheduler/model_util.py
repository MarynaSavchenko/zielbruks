"""Utilities for working with model elements"""
from scheduler.models import Professor, Auditorium, Group


def get_professor(name: str, surname: str) -> Professor:
    """Gets professor from database or creates a new object and returns it"""
    professor, _created = Professor.objects.get_or_create(name=name, surname=surname)
    return professor


def get_auditorium(number: str) -> Auditorium:
    """Gets auditorium from database or creates a new object and returns it"""
    auditorium, _created = Auditorium.objects.get_or_create(number=number)
    return auditorium


def get_group(number: int) -> Group:
    """Gets group from database or creates a new object and returns it"""
    group, _created = Group.objects.get_or_create(number=number)
    return group
