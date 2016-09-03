from registration.forms import RegistrationForm
from customuser.models import User


class CustomUserForm(RegistrationForm):
    class Meta:
        model = User
        fields = ["username", "email"]
