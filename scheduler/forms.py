"""Forms"""

from django import forms
from django.utils import timezone
from django.forms.widgets import SplitDateTimeWidget

from .models import Auditorium, Professor, Group


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


class SelectGroupForm(forms.ModelForm):
    """ form to choose group to show its schedule"""
    group = forms.ModelChoiceField(queryset=Group.objects.all(), to_field_name='id')

    class Meta:
        model = Group
        fields: list = []


class EditForm(forms.Form):
    """ popup form to edit lessons"""
    # id is empty when creating new lesson
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'size': '30', 'class': 'inputText'}))
    start_time = forms.SplitDateTimeField(initial=timezone.now().replace(second=0),
                                          widget=SplitDateTimeWidget(date_attrs={'type': 'date'},
                                                                     time_attrs={'type': 'time'}))
    end_time = forms.SplitDateTimeField(initial=timezone.now().replace(second=0),
                                        widget=SplitDateTimeWidget(date_attrs={'type': 'date'},
                                                                   time_attrs={'type': 'time'}))
    auditorium = forms.CharField(max_length=100)
    group = forms.IntegerField()
    professor = forms.CharField(max_length=100)

    def clean(self):
        start = self.cleaned_data['start_time']
        end = self.cleaned_data['end_time']
        if end < start:
            self.add_error('end_time', 'End date before start date!')
        if end == start:
            self.add_error('end_time', 'End date equals start date!')
        return self.cleaned_data
