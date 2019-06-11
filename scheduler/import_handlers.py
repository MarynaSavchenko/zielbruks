"""Data import functions"""
import datetime as dt
from typing import List, Tuple
from numpy import nan
import pandas as pd

from scheduler.model_util import get_professor, get_auditorium, get_group
from scheduler.models import Lesson, Student


class ImportSizeException(Exception):
    pass


class ImportExtensionException(Exception):
    pass


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
        raise ImportExtensionException
    raise ImportSizeException


def import_csv(data: pd.DataFrame) -> Tuple[int, List[int], List[int]]:
    """
    Parse csv data from DataFrame and add to database
    :param data: consists of simple types (str or int)
        Date: DD-MM-YY or YYYY-MM-DD  Time: HH:MM(:SS)
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
            date = [val for val in row[1].split("-")]
            start_t = [val for val in row[2].split(":")]
            end_t = [val for val in row[3].split(":")]
            professor_data = row[5].strip().split()
            if len(date) == 3 and len(start_t) >= 2 and len(end_t) >= 2\
                    and len(professor_data) == 2:
                if not all((len(x) == 2 for x in date[1:2] + start_t + end_t)):
                    incorrect.append(row[0])
                    continue
                if len(date[0]) == 2:
                    start_date = dt.datetime(int(date[2]) + 2000, int(date[1]), int(date[0]),
                                             int(start_t[0]), int(start_t[1]))
                    end_date = dt.datetime(int(date[2]) + 2000, int(date[1]), int(date[0]),
                                           int(end_t[0]), int(end_t[1]))
                elif len(date[0]) == 4:
                    start_date = dt.datetime(int(date[0]), int(date[1]), int(date[2]),
                                             int(start_t[0]), int(start_t[1]))
                    end_date = dt.datetime(int(date[0]), int(date[1]), int(date[2]),
                                           int(end_t[0]), int(end_t[1]))
                else:
                    incorrect.append(row[0])
                    continue
                if start_date > end_date:
                    incorrect.append(row[0])
                    continue
                professor = get_professor(professor_data[0], professor_data[1])
                auditorium = get_auditorium(str(row[7]))
                group = get_group(str(row[6]))
                _lesson, created = Lesson.objects.get_or_create(
                    name=str(row[4]).strip(),
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
        except ValueError:
            incorrect.append(row[0])
            continue
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
        professor_data = row[5].strip().split()
        if len(professor_data) == 2:
            try:
                if isinstance(row[2], str):
                    tmp_time = dt.datetime.strptime(row[2], "%H:%M:%S")
                    start_time = dt.timedelta(hours=tmp_time.hour, minutes=tmp_time.minute)
                    tmp_time = dt.datetime.strptime(row[3], "%H:%M:%S")
                    end_time = dt.timedelta(hours=tmp_time.hour, minutes=tmp_time.minute)
                else:
                    start_time = dt.timedelta(hours=row[2].hour, minutes=row[2].minute)
                    end_time = dt.timedelta(hours=row[3].hour, minutes=row[3].minute)
                if isinstance(row[1], str):
                    date = dt.datetime.strptime(row[1], "%Y-%m-%d")
                    start_date = date + start_time
                    end_date = date + end_time
                else:
                    start_date = row[1].to_pydatetime() + start_time
                    end_date = row[1].to_pydatetime() + end_time
            except ValueError:
                incorrect.append(row[0])
                continue
            if start_date > end_date:
                incorrect.append(row[0])
                continue
            professor = get_professor(professor_data[0], professor_data[1])
            auditorium = get_auditorium(str(row[7]))
            group = get_group(str(row[6]))
            _lesson, created = Lesson.objects.get_or_create(
                name=str(row[4]).strip(),
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
    if not all((isinstance(x, str) for x in row[1:6])):
        return False
    if not isinstance(row[7], (str, int, float)):
        # 3.27, 3.27a and 137 should all be supported
        return False
    return True


def check_types_excel(row: tuple) -> bool:
    """Returns true if row from excel file has correct types"""
    if not isinstance(row[1], (pd.Timestamp, str)):
        return False
    if not ((isinstance(row[2], dt.time) and isinstance(row[3], dt.time)) or
            (isinstance(row[2], str) and isinstance(row[3], str))):
        return False
    if not all((isinstance(x, str) for x in row[4:5])):
        return False
    if not isinstance(row[6], (str, int)):
        return False
    if not isinstance(row[7], (str, int, float)):
        # 3.27, 3.27a and 137 should all be supported
        return False
    return True


def import_students(data: pd.DataFrame) -> Tuple[int, List[int], List[int]]:
    """
        Parse students data and add to database
        :param data: DataFrame with students data
            Accepted format: index_number | name_and_surname | group
        :return: number of students added
        """
    if len(data.columns) == 3:
        added_columns = 0
        incorrect = []
        duplicate = []
        for row in data.itertuples():
            if row.count(nan) != 0 or not students_check_types(row):
                incorrect.append(row[0])
                continue
            full_name = row[2].strip().split()
            if len(full_name) == 2:
                group = get_group(row[3])
                _student, created = Student.objects.get_or_create(
                    name=full_name[0],
                    surname=full_name[1],
                    group=group,
                    index=int(row[1])
                )
                if created:
                    added_columns += 1
                else:
                    duplicate.append(row[0])
            else:
                incorrect.append(row[0])
                continue
        return added_columns, incorrect, duplicate
    raise ImportSizeException


def students_check_types(row: tuple) -> bool:
    """Returns true if row containing students data has correct types"""
    try:
        index = int(row[1])
        if index < 100000 or index > 999999:
            return False
    except ValueError:
        return False
    if not isinstance(row[2], str):
        return False
    if not isinstance(row[3], (str, int)):
        return False
    return True
