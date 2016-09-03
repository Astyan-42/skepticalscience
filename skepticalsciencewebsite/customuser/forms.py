from registration.forms import RegistrationForm
from customuser.models import User


class CustomUserForm(RegistrationForm):
    """
    Registration for, using, username and email (password is automaticaly add
    """
    class Meta:
        model = User
        fields = ["username", "email"]
