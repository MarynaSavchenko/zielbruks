"""module responsible for finding conflicts in database"""
from typing import List, Tuple
from enum import Enum
from scheduler.models import Lesson, Professor, Auditorium, Group, Conflict


def are_overlapping(lesson1: Lesson, lesson2: Lesson) -> bool:
    """
    Check if one lesson started or ended during other
    :param lesson1, lesson2: Lesson object retrieved from database
    :return: bool if lessons are conflicting
    """
    if lesson1.start_time <= lesson2.start_time < lesson1.end_time:
        return True
    if lesson1.end_time >= lesson2.end_time > lesson1.start_time:
        return True
    if lesson1.start_time >= lesson2.start_time and lesson1.end_time <= lesson2.end_time:
        return True
    return False


def check_lesson(lesson: Lesson) -> List[Tuple[str, Lesson, Lesson, object]]:
    """
    This function searches db for other lessons sharing the same professor, auditorium and group
    And then checks if they are conflicting with each other using are_overlapping
    :param lesson: Lesson for which we are checking possible conflicts
    :return: List of tuples holding information about conflict.
             Tuple[ConflictType, Lesson1, Lesson2, object]
             ConflictType helps to differentiate which conflict it is
             Lesson1 and Lesson2 are Lesson that are currently in conflict
             object is Model object responsible for conflict (Professor,Auditorium,Group)
    """
    conflicts: List[Tuple[str, Lesson, Lesson, object]] = []
    for lesson_2 in Lesson.objects.filter(professor=lesson.professor):
        if lesson != lesson_2:
            if are_overlapping(lesson, lesson_2):
                new_conflict = ("PROFESSOR", lesson, lesson_2, lesson.professor.id)
                conflicts.append(new_conflict)
    for lesson_2 in Lesson.objects.filter(auditorium=lesson.auditorium):
        if lesson != lesson_2:
            if are_overlapping(lesson, lesson_2):
                new_conflict = ('AUDITORIUM', lesson, lesson_2, lesson.auditorium.id)
                conflicts.append(new_conflict)
    for lesson_2 in Lesson.objects.filter(group=lesson.group):
        if lesson != lesson_2:
            if are_overlapping(lesson, lesson_2):
                new_conflict = ("GROUP", lesson, lesson_2, lesson.group.id)
                conflicts.append(new_conflict)
    return conflicts


def conflict_already_in_db(c_type, f_lesson, o_id, s_lesson):
    return Conflict.objects.filter(conflict_type=c_type,
                                   first_lesson=s_lesson,
                                   second_lesson=f_lesson,
                                   object_id=o_id).exists()


def db_conflicts():
    """
    This function finds conflicts for every lesson in database by using check_lesson
    :return: List of tuples holding information about conflict.
             Tuple[ConflictType, Lesson1, Lesson1, object]
             ConflictType helps to differentiate which conflict it is
             Lesson1 and Lesson2 are Lesson that are currently in conflict
             object is Model object responsible for conflict (Professor,Auditorium,Group)
    """
    lessons = Lesson.objects.all()
    for lesson in lessons:
        lesson_conflicts = check_lesson(lesson)
        for conflict in lesson_conflicts:
            c_type, f_lesson, s_lesson, o_id = conflict
            if not conflict_already_in_db(c_type, s_lesson, o_id, f_lesson):
                if not conflict_already_in_db(c_type, f_lesson, o_id, s_lesson):
                    new_conflict = Conflict(conflict_type=c_type,
                                            first_lesson=f_lesson,
                                            second_lesson=s_lesson,
                                            object_id=o_id)
                    new_conflict.save()
