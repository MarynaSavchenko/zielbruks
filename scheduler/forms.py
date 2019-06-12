"""Forms"""

from django import forms
from django.utils import timezone
from django.forms.widgets import SplitDateTimeWidget

from .models import Room, Professor, Group


class SelectRoomForm(forms.ModelForm):
    """ form to choose room to show"""
    room = forms.ModelChoiceField(queryset=Room.objects.all(), to_field_name='number')

    class Meta:
        model = Room
        fields: list = []


class LoginForm(forms.Form):
    """ form to render on login page """
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


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
    room = forms.CharField(max_length=100)
    group = forms.IntegerField(min_value=1)
    professor = forms.CharField(max_length=100)

    def clean(self):
        try:
            start = self.cleaned_data['start_time']
            end = self.cleaned_data['end_time']
            professor = self.cleaned_data['professor']
            if end < start:
                self.add_error('end_time', 'End date before start date.')
            if end == start:
                self.add_error('end_time', 'End date equals start date.')
            if len(professor.strip().split()) != 2:
                self.add_error('professor', 'Pass name and surname (separated by space).')
        except KeyError:
            raise forms.ValidationError("Fill all the fields!")
        return self.cleaned_data


class MassEditForm(forms.Form):
    """ form to mass edit lessons"""
    lesson_name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'size': '30', 'class': 'inputText'}), required=False)
    professor = forms.CharField(max_length=100, required=False)
    room = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'size': '5'}), required=False)
    group = forms.IntegerField(min_value=1, max_value=9999, required=False)
    start_time = forms.SplitDateTimeField(widget=SplitDateTimeWidget(date_attrs={'type': 'date'},
                                                                     time_attrs={'type': 'time'}),
                                          required=False)
    end_time = forms.SplitDateTimeField(widget=SplitDateTimeWidget(date_attrs={'type': 'date'},
                                                                   time_attrs={'type': 'time'}),
                                        required=False)

    def clean(self):
        professor = self.cleaned_data['professor']
        if professor:
            if len(professor.strip().split()) != 2:
                self.add_error('professor', 'Pass name and surname (separated by space).')

        start = self.cleaned_data.get('start_time', 0)
        end = self.cleaned_data.get('end_time', 0)

        if end != 0 and start != 0:
            if end and start:
                if end < start:
                    self.add_error('end_time', 'End date before start date.')
                if end == start:
                    self.add_error('end_time', 'End date equals start date.')

        return self.cleaned_data
