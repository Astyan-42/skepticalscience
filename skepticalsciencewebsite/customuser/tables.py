from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables
from django_tables2.utils import A
from customuser.models import User


class UserTable(tables.Table):
    """
    a table to represent a list of publication
    """
    # temporary use the futur view of the publication
    link = tables.LinkColumn("view_profile", text="user", kwargs={"pk" : A('pk')}, orderable=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "phd_update_date"]
        order_by = 'phd_update_date'
        attrs = {"class": "table table-responsive paleblue"}