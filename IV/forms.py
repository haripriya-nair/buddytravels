from importlib.metadata import files
from django import forms
from .models import Package, Student, Agent,Photographer
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction


class DateInput(forms.DateInput):
    input_type = 'date'


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = '__all__'
        exclude = ['users', 'agent']

        widgets = {
            'ddate': DateInput()
        }


class UserSignUpForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ['username', 'email', 'phone', 'id_image', ]

    @transaction.atomic
    def save(self):
        student = super().save(commit=False)
        student.is_customer = True
        student.save()
        return student


class AgentSignUpForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ['username', 'email',]

    @transaction.atomic
    def save(self):
        student = super().save(commit=False)
        student.is_agent = True
        student.save()
        return student


class PhotographerSignUpForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ['username', 'email', ]

    @transaction.atomic
    def save(self):
        student = super().save(commit=False)
        student.is_photographer = True
        student.save()
        return student


class AgentDetailForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = '__all__'
        exclude = ['User', 'status',]


class PhotographerDetailForm(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = '__all__'
        exclude = []

