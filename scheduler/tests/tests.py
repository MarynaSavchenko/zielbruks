"""First tests module"""

from django.test import TestCase


class SampleTestClass(TestCase):
    """Class doing nothing useful to showcase test running"""

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)
