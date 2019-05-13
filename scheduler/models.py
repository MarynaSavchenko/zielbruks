"""Models gathering point"""
from random import randint

from django.db import models

# generated with http://tools.medialab.sciences-po.fr/iwanthue/
palette = ["#be7349", "#7977ec", "#73e36e", "#dd50b4", "#59ac2e", "#ab70e1", "#b1e160",
           "#cf6ad6", "#9fb528", "#5d85e7", "#d8bd2d", "#4398df", "#dedb54", "#e73f8a",
           "#5be3a2", "#e53d56", "#46a654", "#e84675", "#71e4cf", "#ea4c39", "#47cde5",
           "#ea6642", "#3c98c2", "#ea9e2f", "#5e7bb7", "#af9a23", "#9b83cd", "#6c8d21",
           "#c9579a", "#a5e093", "#f072a8", "#99b656", "#bd73b6", "#d3d67a", "#e5a9ef",
           "#6e8e3b", "#8ea1de", "#da702a", "#7abdf3", "#bd822a", "#32a79f", "#e86266",
           "#47a178", "#d56480", "#649b61", "#de96c5", "#9d8e30", "#b86990", "#e4ba58",
           "#eb92a2", "#738c4e", "#ce5f46", "#a0b87a", "#c36c6a", "#969448", "#f29278",
           "#89834d", "#e2c988", "#a68347", "#dea573"]

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
