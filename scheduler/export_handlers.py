"""Data export functions"""
from tempfile import NamedTemporaryFile

import pandas as pd

from scheduler.models import Lesson, Group, Auditorium


def export_to_csv(start_time, end_time):
    data_frame = get_lessons(start_time, end_time, True)
    temp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    data_frame.to_csv(temp_file.name, index=False)
    return temp_file


def export_to_excel(start_time, end_time):
    data_frame = get_lessons(start_time, end_time, False)
    temp_file = NamedTemporaryFile(suffix='.xlsx', delete=False)
    data_frame.to_excel(temp_file.name, index=False)
    return temp_file


def get_lessons(start_time, end_time, iscsv):
    """returns list of lessons in given time period"""
    lessons_query = Lesson.objects.filter(start_time__range=[start_time, end_time],
                                          end_time__range=[start_time, end_time])
    lessons = [(q.start_time.strftime("%d-%m-%y" if iscsv else "%Y-%m-%d"),
                q.start_time.strftime("%H:%M" if iscsv else "%H:%M:%S"),
                q.end_time.strftime("%H:%M" if iscsv else "%H:%M:%S"),
                q.name,
                (q.professor.name + " " + q.professor.surname),
                Group.objects.filter(id=q.group_id)[:1].get().name,
                Auditorium.objects.filter(id=q.auditorium_id)[:1].get().number,)
               for q in lessons_query]
    return pd.DataFrame(lessons,
                        columns=['Date', 'Start time', 'End time', 'Lesson', 'Professor', 'Group',
                                 'Room'])
