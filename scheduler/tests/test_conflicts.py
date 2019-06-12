"""Tests module for testing logic of finding conflicts"""

import datetime

from django.test import TestCase

from scheduler.models import Lesson, Professor, Group, Room, Conflict
from scheduler.conflicts_checker import db_conflicts

class NoConflictsTestCase(TestCase):
    """Class testing finding conflicts in database that does not have them"""
    def test_clean_database(self):
        """Test on a clean database"""
        db_conflicts()
        self.assertQuerysetEqual(Conflict.objects.all(), Conflict.objects.none())

    def test_database_with_no_conflicts(self):
        """Test on a database with two lessons that are not overlapping"""
        room = Room.objects.create(number="1.11a")
        professor = Professor.objects.create(name="John", surname="Doe")
        group = Group.objects.create(name="1")
        Lesson.objects.create(
            name="Lesson1",
            professor=professor,
            room=room,
            group=group,
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        Lesson.objects.create(
            name="Lesson2",
            professor=professor,
            room=room,
            group=group,
            start_time=datetime.datetime(2019, 5, 11, 14, 00),
            end_time=datetime.datetime(2019, 5, 11, 16, 30)
        )
        db_conflicts()
        self.assertQuerysetEqual(Conflict.objects.all(), Conflict.objects.none())

class OverlappingLessonsConflictsTestCase(TestCase):
    """Class testing conflicts for the times the lessons overlap"""
    def setUp(self):
        self.professor = Professor.objects.create(name="John", surname="Doe")
        self.first_lesson = Lesson.objects.create(
            name="First lesson",
            professor=self.professor,
            room=Room.objects.create(number="1.11a"),
            group=Group.objects.create(name="1"),
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        self.middle_lesson = Lesson.objects.create(
            name="Middle lesson",
            professor=self.professor,
            room=Room.objects.create(number="1.11b"),
            group=Group.objects.create(name="2"),
            start_time=datetime.datetime(2019, 5, 11, 13, 00),
            end_time=datetime.datetime(2019, 5, 11, 17, 00)
        )
        self.last_lesson = Lesson.objects.create(
            name="Last lesson",
            professor=self.professor,
            room=Room.objects.create(number="1.11c"),
            group=Group.objects.create(name="3"),
            start_time=datetime.datetime(2019, 5, 11, 15, 00),
            end_time=datetime.datetime(2019, 5, 11, 16, 30)
        )

    def test_not_overlapping_lessons(self):
        """Test when times of lessons do not overlap"""
        db_conflicts()
        self.assertQuerysetEqual(Conflict.objects.filter(first_lesson=self.first_lesson,
                                                         second_lesson=self.last_lesson,
                                                         conflict_type='PROFESSOR',
                                                         object_id=self.professor.id),
                                 Conflict.objects.none())

    def test_lesson_starts_and_ends_during_another(self):
        """Test when one lesson starts and ends during another"""
        db_conflicts()
        self.assertEqual(len(Conflict.objects.filter(first_lesson=self.middle_lesson,
                                                     second_lesson=self.last_lesson,
                                                     conflict_type='PROFESSOR',
                                                     object_id=self.professor.id)),
                         1)

    def test_lesson_overlaps_another(self):
        """Test when one lesson starts before another and then overlaps at it"""
        db_conflicts()
        self.assertEqual(len(Conflict.objects.filter(first_lesson=self.first_lesson,
                                                     second_lesson=self.middle_lesson,
                                                     conflict_type='PROFESSOR',
                                                     object_id=self.professor.id)),
                         1)

class OverlappingConflictsTypeTestCase(TestCase):
    """Class testing conflicts for the conflict types that are listed"""
    def setUp(self):
        self.professor = Professor.objects.create(name="John", surname="Doe")
        self.room = Room.objects.create(number="1.11a")
        self.group = Group.objects.create(name="1")
        self.first_lesson = Lesson.objects.create(
            name="First lesson",
            professor=self.professor,
            room=self.room,
            group=self.group,
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        self.second_lesson = Lesson.objects.create(
            name="Second lesson",
            professor=self.professor,
            room=self.room,
            group=self.group,
            start_time=datetime.datetime(2019, 5, 11, 13, 00),
            end_time=datetime.datetime(2019, 5, 11, 15, 00)
        )

    def test_overlapping_professor(self):
        """Test when conflict is for professor"""
        db_conflicts()
        self.assertEqual(len(Conflict.objects.filter(first_lesson=self.first_lesson,
                                                     second_lesson=self.second_lesson,
                                                     conflict_type='PROFESSOR',
                                                     object_id=self.professor.id)),
                         1)

    def test_overlapping_room(self):
        """Test when conflict is for room"""
        db_conflicts()
        self.assertEqual(len(Conflict.objects.filter(first_lesson=self.first_lesson,
                                                     second_lesson=self.second_lesson,
                                                     conflict_type='ROOM',
                                                     object_id=self.room.id)),
                         1)

    def test_overlapping_group(self):
        """Test when conflict is for group"""
        db_conflicts()
        self.assertEqual(len(Conflict.objects.filter(first_lesson=self.first_lesson,
                                                     second_lesson=self.second_lesson,
                                                     conflict_type='GROUP',
                                                     object_id=self.group.id)),
                         1)

class CorrectnessOfAmountOfIncorrectDataListedTestCase(TestCase):
    """Class testing if the amount of conflicts is correct"""
    def setUp(self):
        self.professor = Professor.objects.create(name="John", surname="Doe")
        self.first_lesson = Lesson.objects.create(
            name="First lesson",
            professor=self.professor,
            room=Room.objects.create(number="1.11a"),
            group=Group.objects.create(name="1"),
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )
        self.second_lesson = Lesson.objects.create(
            name="Second lesson",
            professor=self.professor,
            room=Room.objects.create(number="1.11b"),
            group=Group.objects.create(name="2"),
            start_time=datetime.datetime(2019, 5, 11, 13, 00),
            end_time=datetime.datetime(2019, 5, 11, 15, 00)
        )

    def test_duplication_of_conflicts(self):
        """Test if the conflicts are not duplicated when found"""
        db_conflicts()
        self.assertEqual(len(Conflict.objects.filter(first_lesson=self.first_lesson,
                                                     second_lesson=self.second_lesson,
                                                     conflict_type='PROFESSOR',
                                                     object_id=self.professor.id))
                         +
                         len(Conflict.objects.filter(first_lesson=self.second_lesson,
                                                     second_lesson=self.first_lesson,
                                                     conflict_type='PROFESSOR',
                                                     object_id=self.professor.id))
                         ,
                         1)
