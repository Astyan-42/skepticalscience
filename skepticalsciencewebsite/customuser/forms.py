from django import forms
from registration.forms import RegistrationForm
from customuser.models import User
from django_select2.forms import Select2MultipleWidget


class CustomUserForm(RegistrationForm):
    """
    Registration for, using, username and email (password is automaticaly add)
    """
    class Meta:
        model = User
        fields = ["username", "email"]


class CustomUserUpdateForm(forms.ModelForm):
    """
    create an user form with restricted field (the field could be directly in the view, used the for
    """
    class Meta:
        model = User
        fields = ["email", "first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
                  "job_title", "sciences"]
        widgets = {'sciences': Select2MultipleWidget(attrs={'class': 'form-control'})}
