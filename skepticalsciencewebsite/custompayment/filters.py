import django_filters
from custompayment.models import Order


class OrderFilter(django_filters.FilterSet):

    class Meta:
        model = Order
        fields = ["status", "creation_date", "user"]