"""module responsible for finding conflicts in database"""
import copy
from typing import List, Tuple
from enum import Enum

from django.db.models.query import QuerySet

from scheduler.models import Lesson, Professor, Room, Group, Conflict


def are_overlapping(lesson1: Lesson, lesson2: Lesson) -> bool:
    """
    Check if one lesson started or ended during other
    :param lesson1: Lesson object retrieved from database
    :param lesson2: Lesson object retrieved from database
    :return: bool if lessons are conflicting
    """
    if lesson1.start_time <= lesson2.start_time < lesson1.end_time:
        return True
    if lesson1.end_time >= lesson2.end_time > lesson1.start_time:
        return True
    if lesson1.start_time >= lesson2.start_time and lesson1.end_time <= lesson2.end_time:
        return True
    return False


def check_lesson(index: int, lesson_list: List[Lesson]) -> List[Tuple[str, Lesson, Lesson, int]]:
    """
    This function searches db for other lessons sharing the same professor, room and group
    And then checks if they are conflicting with each other using are_overlapping
    :param index: index of Lesson for which we are checking possible conflicts
    :param lesson_list: lessons list
    :return: List of tuples holding information about conflict.
             Tuple[str, Lesson1, Lesson2, int]
             str helps to differentiate which conflict it is
             Lesson1 and Lesson2 are Lesson that are currently in conflict
             int is Model object id responsible for conflict (Professor, Room, Group)
    """
    conflicts: List[Tuple[str, Lesson, Lesson, int]] = []
    lesson = lesson_list[index]
    for ind in range(index + 1, len(lesson_list)):
        lesson_2 = lesson_list[ind]
        if are_overlapping(lesson, lesson_2):
            if lesson_2.professor == lesson.professor:
                new_conflict = ("PROFESSOR", lesson, lesson_2, lesson.professor.id)
                conflicts.append(new_conflict)
            if lesson_2.room == lesson.room:
                new_conflict = ('ROOM', lesson, lesson_2, lesson.room.id)
                conflicts.append(new_conflict)
            if lesson_2.group == lesson.group:
                new_conflict = ("GROUP", lesson, lesson_2, lesson.group.id)
                conflicts.append(new_conflict)
    return conflicts


def db_conflicts():
    """
    This function finds conflicts for every lesson in database by using check_lesson
    :return: nothing
            Adds conflicts to database
    """
    Conflict.objects.all().delete()
    lessons = Lesson.objects.all()
    lessons_list = list(lessons)
    for index in range(len(lessons_list)):
        lesson_conflicts = check_lesson(index, lessons_list)
        for conflict in lesson_conflicts:
            c_type, f_lesson, s_lesson, o_id = conflict
            new_conflict = Conflict(conflict_type=c_type,
                                    first_lesson=f_lesson,
                                    second_lesson=s_lesson,
                                    object_id=o_id)
            new_conflict.save()


def conflicts_diff(past_conflicts: List[Conflict], current_conflicts: List[Conflict]) \
        -> Tuple[List[Conflict], List[Conflict]]:
    """
    :param past_conflicts: list of conflicts before change
    :param current_conflicts: list of conflicts after change
    :return:
    """
    removed_conflicts: List[Conflict] = []
    current_conflicts_copy = copy.deepcopy(current_conflicts)
    for conflict in past_conflicts:
        perfect_match = False
        for conflict2 in current_conflicts:
            if conflict.__eq__(conflict2):
                perfect_match = True
                current_conflicts_copy.remove(conflict2)
        if not perfect_match:
            removed_conflicts.append(conflict)
    return current_conflicts_copy, removed_conflicts
