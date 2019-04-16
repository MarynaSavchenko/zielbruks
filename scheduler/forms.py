"""Forms"""
from django import forms

from .models import Lesson, Student, Auditorium, Professor, Group


class SelectAuditoriumForm(forms.ModelForm):
    """ form to choose auditorium to show"""
    auditorium = forms.ModelChoiceField(queryset=Auditorium.objects.all(), to_field_name='number')

    class Meta:
        model = Auditorium
        fields: list = []


class SelectProfessorForm(forms.ModelForm):
    """ form to choose professor to show their schedule"""
    professor = forms.ModelChoiceField(queryset=Professor.objects.all(), to_field_name='id')

    class Meta:
        model = Professor
        fields: list = []
