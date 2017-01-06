import django_filters
from customuser.models import User


class UserFilter(django_filters.FilterSet):

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "phd_to_rate", "phd_update_date"]