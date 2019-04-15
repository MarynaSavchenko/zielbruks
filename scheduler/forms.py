from django import forms

from .models import Lesson, Student, Auditorium, Professor, Group


class SelectAuditoriumForm(forms.ModelForm):
    """ form to choose auditorium to show"""
    auditorium = forms.ModelChoiceField(queryset=Auditorium.objects.all(), to_field_name='number')

    class Meta:
        model = Auditorium
        fields: list = []
