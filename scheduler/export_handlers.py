"""Data export functions"""
from tempfile import NamedTemporaryFile

import pandas as pd

from scheduler.models import Lesson, Group, Auditorium


def export_to_csv(start_time, end_time):
    data_frame = get_lessons(start_time, end_time)
    temp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    data_frame.to_csv(temp_file.name)
    return temp_file


def export_to_excel(start_time, end_time):
    data_frame = get_lessons(start_time, end_time)
    temp_file = NamedTemporaryFile(suffix='.xlsx', delete=False)
    data_frame.to_csv(temp_file.name)
    return temp_file


def get_lessons(start_time, end_time):
    """returns list of lessons in given time period"""
    lessons_query = Lesson.objects.filter(start_time__range=[start_time, end_time],
                                          end_time__range=[start_time, end_time])
    lessons = [(q.start_time,
                q.end_time,
                q.name,
                Group.objects.filter(id=q.group_id)[:1].get().number,
                Auditorium.objects.filter(id=q.auditorium_id)[:1].get().number,
                (q.professor.name + " " + q.professor.surname),)
               for q in lessons_query]
    return pd.DataFrame(lessons,
                        columns=['Start time', 'End time', 'Lesson', 'Group', 'Room', 'Professor'])
