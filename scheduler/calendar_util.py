"""Utilities for displaying calendars"""
import datetime

from django.db.models import QuerySet


def get_start_date(lessons: QuerySet):
    """Returns the date which should be displayed as first in calendar as string"""
    lessons.order_by('start_time')
    start_date = datetime.datetime.now()
    for lesson in lessons:
        if lesson.start_time > start_date:
            start_date = lesson.start_time
            return start_date.strftime("%Y-%m-%dT%H:%M:%S")
    return start_date
