from registration.forms import RegistrationForm
from django import forms
from customuser.models import User


class CustomUserForm(RegistrationForm):
    """
    Registration for, using, username and email (password is automaticaly add)
    """
    class Meta:
        model = User
        fields = ["username", "email"]


class CustomUserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", "first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
                  "job_title", "sciences"]
