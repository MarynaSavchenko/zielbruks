"""Utilities for displaying calendars"""
import datetime

from django.db.models import QuerySet

from scheduler import conflicts_checker, models
from scheduler.models import Lesson, Auditorium, Group


def get_start_date(lessons: QuerySet):
    """Returns the date which should be displayed as first in calendar as string"""
    lessons.order_by('start_time')
    start_date = datetime.datetime.now()
    for lesson in lessons:
        if lesson.start_time > start_date:
            start_date = lesson.start_time
            return start_date.isoformat(timespec='seconds')
    return start_date.isoformat(timespec='seconds')


def generate_full_schedule_context():
    """Returns context dict for full schedule"""
    lessons_query = Lesson.objects.all()
    lessons_list = [(q.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                     q.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                     q.name,
                     Group.objects.filter(id=q.group_id)[:1].get().number,
                     Auditorium.objects.filter(id=q.auditorium_id)[:1].get().number,
                     (q.professor.name + " " + q.professor.surname),
                     models.palette[q.auditorium_id % len(models.palette)],
                     models.palette[q.group_id % len(models.palette)],
                     q.id)
                    for q in lessons_query]
    context = {
        'events': lessons_list,
        'lessons': Lesson.objects.all(),
        'start_date': get_start_date(lessons_query),
        'chosen_flag': True,
        'events_flag': bool(lessons_list),
        'type': 'all',
        'name': 'lessons'
    }
    return context


def generate_conflicts_context():
    """Returns context dict for conflicts"""
    conflicts_list = conflicts_checker.db_conflicts()
    color = ''
    context = {
        'conflicts': conflicts_list,
        'conflicts_color': color,
        'conflicts_flag': bool(conflicts_list)
    }
    return context


def get_full_context_with_date(start_time):
    """Returns full context dict and """
    context: dict = {}
    context.update(generate_conflicts_context())
    context.update(generate_full_schedule_context())
    context['start_date'] = start_time.isoformat(timespec='seconds')
    return context
