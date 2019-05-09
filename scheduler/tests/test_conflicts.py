"""Tests module for testing logic of finding conflicts"""

import datetime

from django.test import TestCase

from scheduler.models import Lesson, Professor, Group, Auditorium
from scheduler.conflicts_checker import db_conflicts, ConflictType

class NoConflictsTestCase(TestCase):
    """Class testing finding conflicts in database that does not have them"""
    def test_clean_database(self):
        """Test on a clean database"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts, [])

    def test_database_with_no_conflicts(self):
        """Test on a database with two lessons that are not overlapping"""
        auditorium = Auditorium.objects.create(number="1.11a")
        professor = Professor.objects.create(name="John", surname="Doe")
        group = Group.objects.create(number=1)
        Lesson.objects.create(
            name="Lesson1",
            professor=professor,
            auditorium=auditorium,
            group=group,
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        Lesson.objects.create(
            name="Lesson2",
            professor=professor,
            auditorium=auditorium,
            group=group,
            start_time=datetime.datetime(2019, 5, 11, 14, 00),
            end_time=datetime.datetime(2019, 5, 11, 16, 30)
        )
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts, [])

class OverlappingLessonsConflictsTestCase(TestCase):
    """Class testing conflicts for the times the lessons overlap"""
    def setUp(self):
        self.professor = Professor.objects.create(name="John", surname="Doe")
        self.first_lesson = Lesson.objects.create(
            name="First lesson",
            professor=self.professor,
            auditorium=Auditorium.objects.create(number="1.11a"),
            group=Group.objects.create(number=1),
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        self.middle_lesson = Lesson.objects.create(
            name="Middle lesson",
            professor=self.professor,
            auditorium=Auditorium.objects.create(number="1.11b"),
            group=Group.objects.create(number=2),
            start_time=datetime.datetime(2019, 5, 11, 13, 00),
            end_time=datetime.datetime(2019, 5, 11, 17, 00)
        )
        self.last_lesson = Lesson.objects.create(
            name="Last lesson",
            professor=self.professor,
            auditorium=Auditorium.objects.create(number="1.11c"),
            group=Group.objects.create(number=3),
            start_time=datetime.datetime(2019, 5, 11, 15, 00),
            end_time=datetime.datetime(2019, 5, 11, 16, 30)
        )

    def test_not_overlapping_lessons(self):
        """Test when times of lessons do not overlap"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts
                         .__contains__((ConflictType.PROFESSOR, self.first_lesson,
                                        self.last_lesson, self.professor)), False)

    def test_lesson_starts_and_ends_during_another(self):
        """Test when one lesson starts and ends during another"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts
                         .__contains__((ConflictType.PROFESSOR, self.middle_lesson,
                                        self.last_lesson, self.professor)), True)

    def test_lesson_overlaps_another(self):
        """Test when one lesson starts before another and then overlaps at it"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts
                         .__contains__((ConflictType.PROFESSOR, self.first_lesson,
                                        self.middle_lesson, self.professor)), True)

class OverlappingConflictsTypeTestCase(TestCase):
    """Class testing conflicts for the conflict types that are listed"""
    def setUp(self):
        self.professor = Professor.objects.create(name="John", surname="Doe")
        self.auditorium = Auditorium.objects.create(number="1.11a")
        self.group = Group.objects.create(number=1)
        self.first_lesson = Lesson.objects.create(
            name="First lesson",
            professor=self.professor,
            auditorium=self.auditorium,
            group=self.group,
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        self.second_lesson = Lesson.objects.create(
            name="Second lesson",
            professor=self.professor,
            auditorium=self.auditorium,
            group=self.group,
            start_time=datetime.datetime(2019, 5, 11, 13, 00),
            end_time=datetime.datetime(2019, 5, 11, 15, 00)
        )

    def test_overlapping_professor(self):
        """Test when conflict is for professor"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts
                         .__contains__((ConflictType.PROFESSOR, self.first_lesson,
                                        self.second_lesson, self.professor)), True)

    def test_overlapping_auditorium(self):
        """Test when conflict is for auditorium"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts
                         .__contains__((ConflictType.AUDITORIUM, self.first_lesson,
                                        self.second_lesson, self.auditorium)), True)

    def test_overlapping_group(self):
        """Test when conflict is for group"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts
                         .__contains__((ConflictType.GROUP, self.first_lesson,
                                        self.second_lesson, self.group)), True)

class CorrectnessOfAmountOfIncorrectDataListedTestCase(TestCase):
    """Class testing if the amount of conflicts is correct"""
    def setUp(self):
        self.professor = Professor.objects.create(name="John", surname="Doe")
        self.first_lesson = Lesson.objects.create(
            name="First lesson",
            professor=self.professor,
            auditorium=Auditorium.objects.create(number="1.11a"),
            group=Group.objects.create(number=1),
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        self.second_lesson = Lesson.objects.create(
            name="Second lesson",
            professor=self.professor,
            auditorium=Auditorium.objects.create(number="1.11b"),
            group=Group.objects.create(number=2),
            start_time=datetime.datetime(2019, 5, 11, 13, 00),
            end_time=datetime.datetime(2019, 5, 11, 15, 00)
        )

    def test_duplication_of_conflicts(self):
        """Test if the conflicts are not duplicated when found"""
        list_of_conflicts = db_conflicts()
        self.assertEqual(list_of_conflicts, ([(ConflictType.PROFESSOR, self.first_lesson,
                                               self.second_lesson, self.professor)]))
