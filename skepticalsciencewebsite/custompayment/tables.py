from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables
from django_tables2.utils import A
from custompayment.models import Order, Payment, Address


class OrderTable(tables.Table):
    """
    a table to represent a list of publication
    """
    # temporary use the futur view of the publication
    link = tables.LinkColumn("detail_order", text="order", kwargs={"token" : A('token')}, orderable=False)

    class Meta:
        model = Order
        fields = ["status", "creation_date", "item"]
        attrs = {"class": "table table-responsive paleblue"}