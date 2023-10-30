from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Student
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    full_name = forms.CharField(max_length=100, label='ФИО')
    code = forms.CharField(max_length=6, label='Код')  # Поле для временного кода
    classroom = forms.IntegerField(required=False, label='Класс')
    classroom_letter = forms.CharField(max_length=1, required=False, label='Литера')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'user']


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']


class CreateCodeForm(forms.Form):
    expiration_hours = forms.IntegerField()


class MainMenuForm(forms.Form):
    num_paid = forms.IntegerField(label='Платное питание (кол-во)')
    num_discount = forms.IntegerField(label='Льготное питание(кол-во)')
    milk = forms.IntegerField(label='молоко(кол-во)')


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'passport_scan', 'registration_scan', 'birth_certificate_scan', 'class_number','class_letter']