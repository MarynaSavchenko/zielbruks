"""Utilities for working with model elements"""
from scheduler.models import Professor, Room, Group


def get_professor(name: str, surname: str) -> Professor:
    """Gets professor from database or creates a new object and returns it"""
    professor, _created = Professor.objects.get_or_create(name=name, surname=surname)
    return professor


def get_room(number: str) -> Room:
    """Gets room from database or creates a new object and returns it"""
    room, _created = Room.objects.get_or_create(number=number)
    return room


def get_group(name: str) -> Group:
    """Gets group from database or creates a new object and returns it"""
    group, _created = Group.objects.get_or_create(name=name)
    return group
