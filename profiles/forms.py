from django import forms
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    """Form for updating basic account details."""

    class Meta:
        model = User
        fields = ['email']