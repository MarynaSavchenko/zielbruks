"""Admin panel configuration"""
from django.contrib import admin
from .models import Professor, Student, Lesson, Group, Auditorium, Conflict

# Register your models here.


admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Lesson)
admin.site.register(Group)
admin.site.register(Auditorium)
admin.site.register(Conflict)
