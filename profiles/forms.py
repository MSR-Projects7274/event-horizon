from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    """Form for updating basic account details."""

    class Meta:
        model = User
        fields = ['email']


class RegistrationForm(UserCreationForm):
    """Form for creating a new user account."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']