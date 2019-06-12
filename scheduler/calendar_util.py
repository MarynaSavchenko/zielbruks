"""Utilities for displaying calendars"""
import datetime

from django.db.models import QuerySet

from scheduler.conflicts_checker import conflicts_diff
from scheduler.forms import MassEditForm
from scheduler.models import Lesson, Room, Group, Conflict, color_from_id


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
                     Room.objects.filter(id=q.room_id)[:1].get().number,
                     (q.professor.name + " " + q.professor.surname),
                     q.room_color,
                     q.group_color,
                     q.id,
                     q.start_time.strftime("%H:%M") + "-" + q.end_time.strftime("%H:%M"))
                    for q in lessons_query]
    context = {
        'events': lessons_list,
        'lessons': Lesson.objects.all(),
        'start_date': get_start_date(lessons_query),
        'chosen_flag': True,
        'events_flag': bool(lessons_list),
        'type': 'all',
        'name': 'lessons',
        "groups_colors": get_group_colors(),
        "rooms_colors": get_rooms_colors(),
    }
    return context


def generate_conflicts_context():
    """Returns context dict for conflicts"""
    conflicts_list = Conflict.objects.all()
    color = ''
    context = {
        'conflicts': conflicts_list,
        'conflicts_color': color,
        'conflicts_flag': bool(conflicts_list)
    }
    return context


def generate_full_index_context_with_date(start_time):
    """Returns full context dict with date for index page"""
    context: dict = {}
    context.update(generate_conflicts_context())
    context.update(generate_full_schedule_context())
    context['start_date'] = start_time.isoformat(timespec='seconds')
    form = MassEditForm()
    context.update({'form': form})
    return context


def generate_full_index_context():
    """Returns full context dict for index page"""
    context: dict = {}
    context.update(generate_conflicts_context())
    context.update(generate_full_schedule_context())
    form = MassEditForm()
    context.update({'form': form})
    return context


def get_rooms_colors():
    """Returns list of tuples of rooms names and colors"""
    return [(a.number, color_from_id(a.id))
            for a in Room.objects.all()]


def get_group_colors():
    """Returns list of tuples of groups names and colors"""
    return [(g.number, color_from_id(g.id, True))
            for g in Group.objects.all()]


def generate_context_for_conflicts_report(past_conflicts, current_conflicts):
    """Returns context dict based on list of past conflicts and current conflicts"""
    new_conflicts, removed_conflicts = conflicts_diff(past_conflicts, current_conflicts)
    context = {'removed_conflicts': removed_conflicts,
               'removed_conflicts_number': len(removed_conflicts),
               'new_conflicts_number': len(new_conflicts),
               'new_conflicts': new_conflicts}
    return context
