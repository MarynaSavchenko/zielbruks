"""Models gathering point"""
from random import randint

from django.db import models

palette = ['#66BD63', '#006837', '#92C5DE', '#1A9850', '#D6604D', '#B2182B', '#4D9221', '#7FBC41',
           '#2166AC', '#C51B7D', '#276419', '#F1B6DA', '#FDDBC7', '#D73027', '#F46D43', '#F4A582',
           '#A50026', '#053061', '#DE77AE', '#A6D96A', '#F7F7F7', '#B8E186', '#FEE08B', '#67001F',
           '#D1E5F0', '#FDAE61', '#FFFFBF', '#E6F5D0', '#D9EF8B', '#8E0152', '#4393C3', '#FDE0EF']

def color_from_id(numeric_id):
    return palette[numeric_id % len(palette)]

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


    def __eq__(self, other):
        if not isinstance(other, models.Model):
            return False
        if self._meta.concrete_model != other._meta.concrete_model:
            return False
        my_pk = self.pk
        return my_pk == other.pk and self.name == other.name and self.surname == other.surname \
               and self.email == other.email


class Auditorium(models.Model):
    """Place at which a Lesson is given"""
    number = models.CharField("Auditorium number", max_length=30, unique=True)

    def __str__(self):
        return str(self.number)


    def __eq__(self, other):
        if not isinstance(other, models.Model):
            return False
        if self._meta.concrete_model != other._meta.concrete_model:
            return False
        my_pk = self.pk
        return my_pk == other.pk and self.number == other.number


class Group(models.Model):
    """Group of Students attending the same courses"""
    number = models.IntegerField("Group number", unique=True)

    def __str__(self):
        return str(self.number)

    def __eq__(self, other):
        if not isinstance(other, models.Model):
            return False
        if self._meta.concrete_model != other._meta.concrete_model:
            return False
        my_pk = self.pk
        return my_pk == other.pk and self.number == other.number


class Lesson(models.Model):
    """A university class having specific time and place"""

    # If you want to get a list of lessons from Foreign Tables, you should use related_name
    name = models.CharField("Lesson name", max_length=100)
    professor = models.ForeignKey(Professor, related_name='lessons', on_delete=models.CASCADE)
    auditorium = models.ForeignKey(Auditorium, related_name='lessons', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='lessons', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    group_color = property(lambda self: color_from_id(self.group_id))
    auditorium_color = property(lambda self: color_from_id(self.auditorium_id))

    class Meta:
        unique_together = ('name', 'professor', 'auditorium', 'group', 'start_time', 'end_time',)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, models.Model):
            return False
        if self._meta.concrete_model != other._meta.concrete_model:
            return False
        my_pk = self.pk
        if my_pk == other.pk and self.name == other.name and self.start_time == other.start_time \
                and self.end_time == other.end_time:
            if self.professor == other.professor and self.auditorium == other.auditorium \
                    and self.group == other.group:
                return True
        return False


class Student(models.Model):
    """Student participating in Lessons"""

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


class Conflict(models.Model):
    """Conflict generated by Lessons"""
    first_lesson = models.ForeignKey(Lesson, related_name='first_lesson',
                                     on_delete=models.CASCADE, null=False)
    second_lesson = models.ForeignKey(Lesson, related_name='second_lesson',
                                      on_delete=models.CASCADE, null=False)
    CONFLICT_TYPE = (
        ('AUDITORIUM', 'AUDITORIUM'),
        ('PROFESSOR', 'PROFESSOR'),
        ('GROUP', 'GROUP')
    )
    conflict_type = models.CharField(choices=CONFLICT_TYPE, max_length=20)
    object_id = models.IntegerField()

    def __str__(self):
        return str(self.first_lesson) + " and " + str(self.second_lesson) + " " \
               + self.conflict_type + " " + str(self.object_id)

    def __eq__(self, other):
        if not isinstance(other, models.Model):
            return False
        if self._meta.concrete_model != other._meta.concrete_model:
            return False
        if self.conflict_type == other.conflict_type and self.object_id == other.object_id:
            if self.first_lesson == other.first_lesson \
                    and self.second_lesson == other.second_lesson:
                return True
            if self.first_lesson == other.second_lesson \
                    and self.second_lesson == other.first_lesson:
                return True
        return False
