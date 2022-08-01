from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'username', 'email', 'password1', 'password2')


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['participants', 'host']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar', 'name', 'username', 'email', 'bio')