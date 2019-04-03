"""Models gathering point"""
from django.db import models


# Create your models here.

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

    def __str__(self):
        return str(self.number)


class Group(models.Model):
    """Group of Students attending the same courses"""
    number = models.IntegerField("Group number", unique=True)

    def __str__(self):
        return str(self.number)


class Lesson(models.Model):
    """A university class having specific time and place"""

    # If you want to get a list of lessons from Foreign Tables, you should use related_name
    name = models.CharField("Lesson name", max_length=100, unique=True)
    professor = models.ForeignKey(Professor, related_name='lessons', on_delete=models.CASCADE)
    auditorium = models.ForeignKey(Auditorium, related_name='lessons', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='lessons', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

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
