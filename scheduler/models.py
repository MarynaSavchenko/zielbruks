"""Models gathering point"""
from random import randint

from django.db import models

palette = ["C5C5C6", "FFFFFF", "FFBFC9", "DAE3ED", "C2AB93", "D4D4D5", "FFD0D7", "E4EAF1", "D2C1B0",
           "E4E4E5", "FFE1E6", "EEF2F6", "E3D8CD", "F4F4F4", "FFF3F5", "F8F9FB", "F3EFEB"]


def random_color():
    return palette[randint(0, len(palette) - 1)]


class Professor(models.Model):
    """Person lecturing in a Lesson"""
    name = models.CharField("Professor name", max_length=100)
    surname = models.CharField("Professor surname", max_length=100)
    # blank=not required
    email = models.EmailField("Professor email", max_length=100, null=True, blank=True, unique=True)

    def save(self, *args, **kwargs):
        """Overriding save to run overridden clean()"""
        self.full_clean()
        return super(Professor, self).save(*args, **kwargs)

    def clean(self):
        """Clean up blank fields to null.
        Unless we give email, it will become ""
        and we aren't allowed to have more then one because of uniq
        """
        if self.email == "":
            self.email = None

    def __str__(self):
        return self.name + " " + self.surname


class Auditorium(models.Model):
    """Place at which a Lesson is given"""
    number = models.CharField("Auditorium number", max_length=30, unique=True)
    color = models.CharField(max_length=10, default=random_color)

    def __str__(self):
        return str(self.number)


class Group(models.Model):
    """Group of Students attending the same courses"""
    number = models.IntegerField("Group number", unique=True)
    color = models.CharField(max_length=10, default=random_color)

    def __str__(self):
        return str(self.number)


class Lesson(models.Model):
    """A university class having specific time and place"""

    # If you want to get a list of lessons from Foreign Tables, you should use related_name
    name = models.CharField("Lesson name", max_length=100)
    professor = models.ForeignKey(Professor, related_name='lessons', on_delete=models.CASCADE)
    auditorium = models.ForeignKey(Auditorium, related_name='lessons', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='lessons', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        unique_together = ('name', 'professor', 'auditorium', 'group', 'start_time', 'end_time',)

    def __str__(self):
        return self.name


class Student(models.Model):
    """Student particiapting in Lessons"""

    name = models.CharField("Student name", max_length=100)
    surname = models.CharField("Student surname", max_length=100)
    group = models.ForeignKey(Group, related_name='students', on_delete=models.SET_NULL, null=True)
    email = models.EmailField("Student email", max_length=100, null=True, blank=True, unique=True)
    index = models.CharField(max_length=30, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Student, self).save(*args, **kwargs)

    def clean(self):
        """Clean up blank fields to null"""
        if self.email == "":
            self.email = None

    def __str__(self):
        return self.name + " " + self.surname
