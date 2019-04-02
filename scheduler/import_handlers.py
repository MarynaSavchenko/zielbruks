"""Data import functions"""
import datetime
import pandas as pd
from scheduler.models import Professor, Auditorium, Group, Lesson


def parse_data(data: pd.DataFrame, ext: str) -> int:
    """
    Parse basic info, process extension and pass to designated function
    :param data: DataFrame with lessons
        Accepted format: date | start_time | end_time | Subject | Professor | Group | Auditorium
    :param ext: File extension: .csv or .xlsx
    :return: number of lessons added
    """
    if len(data.columns) == 7 and not data.isnull().values.any():
        if ext == '.csv':
            return import_csv(data)
        if ext == '.xlsx':
            return import_excel(data)
    return 0


def import_csv(data: pd.DataFrame) -> int:
    """
    Parse csv data from DataFrame and add to database
    :param data: consists of simple types (str or int)
        Date: DD-MM-YY  Time: HH:MM
    :return: number of lessons added
    """
    added_columns = 0
    for row in data.itertuples(index=False):
        date = [int(val) for val in row[0].split("-")]
        start_time = [int(val) for val in row[1].split(":")]
        end_time = [int(val) for val in row[2].split(":")]
        professor = row[4].split(" ")
        if len(date) == 3 and len(start_time) == 2 and len(end_time) == 2 and len(professor) == 2:
            date[2] += 2000
            start_date = datetime.datetime(date[2], date[1], date[0], start_time[0], start_time[1])
            end_date = datetime.datetime(date[2], date[1], date[0], end_time[0], end_time[1])
            parameters = (row[3], professor[1], professor[0], row[6], row[5], start_date, end_date)
            if save_into_database(parameters):
                added_columns += 1
    return added_columns


def import_excel(data: pd.DataFrame) -> int:
    """
    Parse excel data from DataFrame and add to database
    :param data: consists of complex types for date etc.
        Date: YYYY-MM-DD  Time: HH:MM:SS
    :return: number of lessons added
    """
    added_columns = 0
    for row in data.itertuples(index=False):
        professor = row[4].split(" ")
        if isinstance(row[0], pd.Timestamp) and isinstance(row[1], datetime.time) and \
                isinstance(row[2], datetime.time) and len(professor) == 2:
            start_time = datetime.timedelta(hours=row[1].hour, minutes=row[1].minute)
            end_time = datetime.timedelta(hours=row[2].hour, minutes=row[2].minute)
            start_date = row[0].to_pydatetime() + start_time
            end_date = row[0].to_pydatetime() + end_time
            parameters = (row[3], professor[1], professor[0], row[6], row[5], start_date, end_date)
            if save_into_database(parameters):
                added_columns += 1
    return added_columns


def save_into_database(parameters: tuple) -> bool:
    """
    Save a lesson (and other model if necessary) objects into database
    :param parameters: tuple of formatted data needed for database:
                (lesson_name, prof_name, prof_surname, auditorium, group, start_date, end_date)
    :return: whether given lesson already existed or not
    """
    print(parameters)
    professor, _created = Professor.objects.get_or_create(
        name=parameters[1],
        surname=parameters[2]
    )
    auditorium, _created = Auditorium.objects.get_or_create(
        number=parameters[3]
    )
    group, _created = Group.objects.get_or_create(
        number=parameters[4]
    )
    _lesson, created = Lesson.objects.get_or_create(
        name=parameters[0],
        professor=professor,
        auditorium=auditorium,
        group=group,
        start_time=parameters[5],
        end_time=parameters[6]
    )
    return created
