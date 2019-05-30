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

def color_from_id(numeric_id, shuffle=False):
    """Selects color by entity id"""
    if shuffle:
        colors = palette[len(palette) // 2:] + palette[:len(palette) // 2]
    else:
        colors = palette
    return colors[numeric_id % len(colors)]

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

    group_color = property(lambda self: color_from_id(self.group_id, True))
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
            try:
                if self.first_lesson == other.first_lesson \
                        and self.second_lesson == other.second_lesson:
                    return True
                if self.first_lesson == other.second_lesson \
                        and self.second_lesson == other.first_lesson:
                    return True
            except Lesson.DoesNotExist:
                return False
        return False
