import datetime
from typing import Union, List

from django.db.models import QuerySet

from scheduler.models import Lesson


def get_start_date(lessons : Union[QuerySet, List[Lesson]]):
    """Returns the date which should be displayed as first in calendar as string"""
    lessons.order_by('start_time')
    start_date = datetime.datetime.now()
    for d in lessons:
        if (d.start_time > start_date):
            start_date = d.start_time
    return start_date.strftime("%Y-%m-%dT%H:%M:%S")