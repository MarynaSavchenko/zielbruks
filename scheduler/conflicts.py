"""module responsible fro finding conflicts in database"""
from typing import List, Tuple
from enum import Enum
from scheduler.models import Lesson, Professor, Auditorium, Group

class ConflictType(Enum):
    PROFESSOR = 1
    AUDITORIUM = 2
    GROUP = 3

def check_time_conflict(lesson1: Lesson, lesson2: Lesson) -> bool:
    """
    Check if lesson2 started or ended during lesson1.
    Lessons should have common factor like same professor, auditorium, group
    :param lesson1, lesson2: Lesson object retrived from database
    :return: bool if lessons are conflicting
    """
    if lesson1.start_time <= lesson2.start_time and lesson1.end_time > lesson2.start_time:
        return True
    if lesson1.end_time >= lesson2.end_time and lesson1.start_time < lesson2.end_time:
        return True
    return False

def check_lesson(lesson: Lesson) -> List[Tuple[ConflictType, Lesson, Lesson, object]]:
    """
    This function searches db for other lessons sharing the same professor, auditorium and group
    And then checks if they are conflcting with eachother using chceck_time_conflicts
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
            if (ConflictType.PROFESSOR, lesson_2, lesson, lesson.professor) not in confs:
                if check_time_conflict(lesson, lesson_2):
                    new_conflict = (ConflictType.PROFESSOR, lesson, lesson_2, lesson.professor)
                    confs.append(new_conflict)
    for lesson_2 in Lesson.objects.filter(auditorium=lesson.auditorium):
        if lesson != lesson_2:
            if (ConflictType.AUDITORIUM, lesson_2, lesson, lesson.auditorium) not in confs:
                if check_time_conflict(lesson, lesson_2):
                    new_conflict = (ConflictType.AUDITORIUM, lesson, lesson_2, lesson.auditorium)
                    confs.append(new_conflict)
    for lesson_2 in Lesson.objects.filter(group=lesson.group):
        if lesson != lesson_2:
            if (ConflictType.GROUP, lesson_2, lesson, lesson.group) not in confs:
                if check_time_conflict(lesson, lesson_2):
                    new_conflict = (ConflictType.GROUP, lesson, lesson_2, lesson.group)
                    confs.append(new_conflict)
    return confs

def db_conflicts() -> List[Tuple[ConflictType, Lesson, Lesson, object]]:
    """Render the main page"""
    les = Lesson.objects.all()
    confs: List[Tuple[ConflictType, Lesson, Lesson, object]] = []
    for lesson in les:
        confs = confs + check_lesson(lesson)
    return confs
