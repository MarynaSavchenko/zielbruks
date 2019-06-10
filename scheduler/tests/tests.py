"""First tests module"""
import datetime

from django.test import TestCase

import pandas as pd

from scheduler.import_handlers import parse_data, import_csv, import_excel
from scheduler.models import Lesson, Professor, Room, Group


class ImportHandlersTest(TestCase):
    """Class testing data parsing and importing into database"""

    @classmethod
    def setUpTestData(cls):
        Lesson.objects.create(
            name="Existing",
            professor=Professor.objects.create(name="John", surname="Doe"),
            room=Room.objects.create(number="1.11a"),
            group=Group.objects.create(number=1),
            start_time=datetime.datetime(2019, 5, 11, 12, 00),
            end_time=datetime.datetime(2019, 5, 11, 13, 30)
        )

    def test_parse_data_extension(self):
        """Unsupported extensions will not be processed"""
        res = parse_data(pd.DataFrame(), ".txt")
        self.assertEqual(res, (0, [], []))
        res = parse_data(pd.DataFrame(), ".md")
        self.assertEqual(res, (0, [], []))

    def test_parse_data_length(self):
        """Incorrect number of rows will not be processed"""
        too_long_data = pd.DataFrame(["1", "2", "3", "4", "5", "6", "7", "8"]).transpose()
        too_short_data = pd.DataFrame(["1", "2", "3", "4", "5", "6"]).transpose()
        res = parse_data(too_long_data, ".csv")
        self.assertEqual(res, (0, [], []))
        res = parse_data(too_short_data, ".csv")
        self.assertEqual(res, (0, [], []))

    def test_import_csv(self):
        """
        Uses data format from csv file
        Existing record is not added
        Duplicates are added only once
        Incorrect are not added at all
        Adds 2 records, 2 duplicate, 5 incorrect
        """
        data = pd.DataFrame(
            [["11-05-19", "12:00", "13:30", "Existing", "John Doe", "1", "1.11a"],
             ["12-05-19", "14:00", "15:30", "IncorrectName", "John", "3", "2.41"],
             ["10-05-19", "13:00", "14:00", "Duplicate", "Adam Smith", "1", "132"],
             ["31-05-19", "20:00", "22:00", "Correct", "John Doe", "2", "2.41"],
             ["10-05-19", "13:00", "14:00", "Duplicate", "Adam Smith", "1", "132"],
             ["01-04-19", "16:00", "15:30", "IncorrectTime", "Harry Potter", "3", "2.41"],
             ["02/04/19", "17:00", "18:30", "IncorrectDateFormat", "Harry Potter", "3", "2.41"],
             ["02-04-19", "17", "18:30", "IncorrectTimeFormat", "Harry Potter", "3", "2.41"],
             ["02-04-19", "17:00", "18:30", "IncorrectProfessorType", "1", "3", "2.41"]])
        added, incorrect, duplicate = import_csv(data)
        # checking function results
        self.assertEqual(added, 2)
        self.assertEqual(incorrect, [1, 5, 6, 7, 8])
        self.assertEqual(duplicate, [0, 4])
        # checking database contents
        self.assertEqual(Lesson.objects.filter(name="Existing").count(), 1)
        self.assertEqual(Lesson.objects.filter(name="Duplicate").count(), 1)
        self.assertEqual(Lesson.objects.filter(name="Correct").count(), 1)
        self.assertEqual(Lesson.objects.filter(name="IncorrectName").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectTime").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectDateFormat").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectTimeFormat").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectProfessorType").count(), 0)

    def test_import_excel(self):
        """
        Uses data format from xlsx file
        Existing record is not added
        Duplicates are added only once
        Incorrect are not added at all
        Adds 2 records, 2 duplicate, 5 incorrect
        """
        data = pd.DataFrame(
            [[pd.Timestamp(2019, 5, 11), datetime.time(12, 00), datetime.time(13, 30),
              "Existing", "John Doe", 1, "1.11a"],
             [pd.Timestamp(2019, 5, 12), datetime.time(14, 00), datetime.time(15, 30),
              "IncorrectName", "John", "3", 2.41],
             [pd.Timestamp(2019, 5, 10), datetime.time(13, 00), datetime.time(14, 00),
              "Duplicate", "Adam Smith", "1", 132],
             [pd.Timestamp(2019, 5, 31), datetime.time(20, 00), datetime.time(22, 00),
              "Correct", "John Doe", "2", 2.41],
             [pd.Timestamp(2019, 5, 10), datetime.time(13, 00), datetime.time(14, 00),
              "Duplicate", "Adam Smith", "1", "132"],
             [pd.Timestamp(2019, 4, 1), datetime.time(16, 00), datetime.time(15, 30),
              "IncorrectTime", "Harry Potter", "3", "2.41"],
             ["02-04-19", datetime.time(17, 00), datetime.time(18, 30),
              "IncorrectDateType", "Harry Potter", "3", 2.41],
             [pd.Timestamp(2019, 4, 2), "17:00", datetime.time(18, 30),
              "IncorrectTimeType", "Harry Potter", "3", 2.41],
             [pd.Timestamp(2019, 4, 2), datetime.time(17, 00), datetime.time(18, 30),
              "IncorrectProfessorType", "1", "3", 2.41]])
        added, incorrect, duplicate = import_excel(data)
        # checking function results
        self.assertEqual(added, 2)
        self.assertEqual(incorrect, [1, 5, 6, 7, 8])
        self.assertEqual(duplicate, [0, 4])
        # checking database contents
        self.assertEqual(Lesson.objects.filter(name="Existing").count(), 1)
        self.assertEqual(Lesson.objects.filter(name="Duplicate").count(), 1)
        self.assertEqual(Lesson.objects.filter(name="Correct").count(), 1)
        self.assertEqual(Lesson.objects.filter(name="IncorrectName").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectTime").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectDateType").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectTimeType").count(), 0)
        self.assertEqual(Lesson.objects.filter(name="IncorrectProfessorType").count(), 0)
