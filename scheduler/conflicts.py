"""module responsible for finding conflicts in database"""
from typing import List, Tuple
from enum import Enum
from scheduler.models import Lesson, Professor, Auditorium, Group

class ConflictType(Enum):
    PROFESSOR = 1
    AUDITORIUM = 2
    GROUP = 3

def are_overlapping(lesson1: Lesson, lesson2: Lesson) -> bool:
    """
    Check if one lesson started or ended during other
    :param lesson1, lesson2: Lesson object retreived from database
    :return: bool if lessons are conflicting
    """
    if lesson1.start_time <= lesson2.start_time and lesson1.end_time > lesson2.start_time:
        return True
    if lesson1.end_time >= lesson2.end_time and lesson1.start_time < lesson2.end_time:
        return True
    if lesson1.start_time >= lesson2.start_time and lesson1.end_time <= lesson2.end_time:
        return True
    return False

def check_lesson(lesson: Lesson) -> List[Tuple[ConflictType, Lesson, Lesson, object]]:
    """
    This function searches db for other lessons sharing the same professor, auditorium and group
    And then checks if they are conflcting with eachother using are_overlapping
    :param lesson: Lesson for which we are chcecking possible conflicts
    :return: List of tuples holding information about conflict.
             Tuple[ConflictType, Lesson1, Lesson1, object]
             ConflictType helps to differentiate which conflict it is
             Lesson1 and Lesson2 are Lesson that are currently in conflict
             object is Model object responsible for conflict (Professor,Auditorium,Group)
    """
    confs: List[Tuple[ConflictType, Lesson, Lesson, object]] = []
    for lesson_2 in Lesson.objects.filter(professor=lesson.professor):
        if lesson != lesson_2:
            if are_overlapping(lesson, lesson_2):
                new_conflict = (ConflictType.PROFESSOR, lesson, lesson_2, lesson.professor)
                confs.append(new_conflict)
    for lesson_2 in Lesson.objects.filter(auditorium=lesson.auditorium):
        if lesson != lesson_2:
            if are_overlapping(lesson, lesson_2):
                new_conflict = (ConflictType.AUDITORIUM, lesson, lesson_2, lesson.auditorium)
                confs.append(new_conflict)
    for lesson_2 in Lesson.objects.filter(group=lesson.group):
        if lesson != lesson_2:
            if are_overlapping(lesson, lesson_2):
                new_conflict = (ConflictType.GROUP, lesson, lesson_2, lesson.group)
                confs.append(new_conflict)
    return confs

def db_conflicts() -> List[Tuple[ConflictType, Lesson, Lesson, object]]:
    """
    This function finds conflicts for every lesson in database by using check_lesson
    :return: List of tuples holding information about conflict.
             Tuple[ConflictType, Lesson1, Lesson1, object]
             ConflictType helps to differentiate which conflict it is
             Lesson1 and Lesson2 are Lesson that are currently in conflict
             object is Model object responsible for conflict (Professor,Auditorium,Group)
    """
    les = Lesson.objects.all()
    confs: List[Tuple[ConflictType, Lesson, Lesson, object]] = []
    for lesson in les:
        lesson_conflicts = check_lesson(lesson)
        for conflict in lesson_conflicts:
            if (conflict[0], conflict[2], conflict[1], conflict[3]) not in confs:
                confs.append(conflict)
    return confs
