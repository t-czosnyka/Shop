from django import forms
from .models import UserData
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class ResetForm(forms.Form):
    email = forms.EmailField()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        fields = ("username", "password1", "password2", "email", "first_name", "last_name")
        model = User


class UserChangeForm(forms.ModelForm):
    class Meta:
        fields = ("email", "first_name", "last_name")
        model = User

class UserDataForm(forms.ModelForm):

    class Meta:
        model = UserData
        exclude = ['user', 'is_active']

