"""Admin panel configuration"""
from django.contrib import admin
from .models import Professor, Student, Group, Auditorium

# Register your models here.


admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Group)
admin.site.register(Auditorium)
