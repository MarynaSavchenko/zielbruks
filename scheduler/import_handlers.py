"""Data import functions"""
import datetime
from typing import List, Tuple
from numpy import nan
import pandas as pd

from scheduler.model_util import get_professor, get_auditorium, get_group
from scheduler.models import Lesson


def parse_data(data: pd.DataFrame, ext: str) -> Tuple[int, List[int], List[int]]:
    """
    Parse basic info, process extension and pass to designated function
    :param data: DataFrame with lessons
        Accepted format: date | start_time | end_time | Subject | Professor | Group | Auditorium
    :param ext: File extension: .csv or .xlsx
    :return: number of lessons added
    """
    if len(data.columns) == 7:
        if ext == '.csv':
            return import_csv(data)
        if ext == '.xlsx':
            return import_excel(data)
    return 0, [], []


def import_csv(data: pd.DataFrame) -> Tuple[int, List[int], List[int]]:
    """
    Parse csv data from DataFrame and add to database
    :param data: consists of simple types (str or int)
        Date: DD-MM-YY  Time: HH:MM
    :return: number of lessons added
    """
    added_columns = 0
    incorrect = []
    duplicate = []
    for row in data.itertuples():
        if row.count(nan) != 0 or not check_types_csv(row):
            incorrect.append(row[0])
            continue
        try:
            date = [int(val) for val in row[1].split("-")]
            start_t = [int(val) for val in row[2].split(":")]
            end_t = [int(val) for val in row[3].split(":")]
        except ValueError:
            incorrect.append(row[0])
            continue
        professor_data = row[5].strip().split()
        if len(date) == 3 and len(start_t) == 2 and len(end_t) == 2 and len(professor_data) == 2:
            date[2] += 2000
            start_date = datetime.datetime(date[2], date[1], date[0], start_t[0], start_t[1])
            end_date = datetime.datetime(date[2], date[1], date[0], end_t[0], end_t[1])
            if start_date > end_date:
                incorrect.append(row[0])
                continue
            professor = get_professor(professor_data[0], professor_data[1])
            auditorium = get_auditorium(str(row[7]))
            group = get_group(row[6])
            _lesson, created = Lesson.objects.get_or_create(
                name=row[4],
                professor=professor,
                auditorium=auditorium,
                group=group,
                start_time=start_date,
                end_time=end_date
            )
            if created:
                added_columns += 1
            else:
                duplicate.append(row[0])
        else:
            incorrect.append(row[0])
    return added_columns, incorrect, duplicate


def import_excel(data: pd.DataFrame) -> Tuple[int, List[int], List[int]]:
    """
    Parse excel data from DataFrame and add to database
    :param data: consists of complex types for date etc.
        Date: YYYY-MM-DD  Time: HH:MM:SS
    :return: number of lessons added
    """
    added_columns = 0
    incorrect = []
    duplicate = []
    for row in data.itertuples():
        if row.count(nan) != 0 or not check_types_excel(row):
            incorrect.append(row[0])
            continue
        professor_data = row[5].strip.split()
        if len(professor_data) == 2:
            start_time = datetime.timedelta(hours=row[2].hour, minutes=row[2].minute)
            end_time = datetime.timedelta(hours=row[3].hour, minutes=row[3].minute)
            start_date = row[1].to_pydatetime() + start_time
            end_date = row[1].to_pydatetime() + end_time
            if start_date > end_date:
                incorrect.append(row[0])
                continue
            professor = get_professor(professor_data[0], professor_data[1])
            auditorium = get_auditorium(str(row[7]))
            group = get_group(row[6])
            _lesson, created = Lesson.objects.get_or_create(
                name=row[4],
                professor=professor,
                auditorium=auditorium,
                group=group,
                start_time=start_date,
                end_time=end_date
            )
            if created:
                added_columns += 1
            else:
                duplicate.append(row[0])
        else:
            incorrect.append(row[0])
    return added_columns, incorrect, duplicate


def check_types_csv(row: tuple) -> bool:
    """Returns true if row from csv file has correct types"""
    if not all((isinstance(x, str) for x in row[1:5])):
        return False
    try:
        int(row[6])
    except ValueError:
        return False
    if not isinstance(row[7], (str, int, float)):
        # 3.27, 3.27a and 137 should all be supported
        return False
    return True


def check_types_excel(row: tuple) -> bool:
    """Returns true if row from excel file has correct types"""
    if not isinstance(row[1], pd.Timestamp):
        return False
    if not (isinstance(row[2], datetime.time) and isinstance(row[3], datetime.time)):
        return False
    if not (isinstance(row[4], str) and isinstance(row[5], str)):
        return False
    try:
        int(row[6])
    except ValueError:
        return False
    if not isinstance(row[7], (str, int, float)):
        # 3.27, 3.27a and 137 should all be supported
        return False
    return True
