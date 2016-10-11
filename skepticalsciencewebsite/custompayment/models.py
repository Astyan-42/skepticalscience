from django.db import models
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment
from custompayment.constants import *
from customuser.models import User

# to complete Order and Payment
# to add Billing address and Discount code


class Order(models.Model):

    order_id = models.CharField(verbose_name=_("OrderID"), max_length=50, unique=True)
    status = models.CharField(_('order status'), max_length=32, choices=ORDER_CHOICES, default=NEW)
    creation_date = models.DateTimeField(_('created'), auto_now_add=True)
    last_status_change = models.DateTimeField(_('last status change'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('buyer'))
    # billing_address = models.ForeignKey(Address)


class Payment(BasePayment):
    order = models.ForeignKey(Order, related_name='payments')

    def get_failure_url(self):
        return 'http://example.com/failure/'

    def get_success_url(self):
        return 'http://example.com/success/'

    def get_purchased_items(self):
        # you'll probably want to retrieve these from an associated order
        # either scientific account or posting a publication
        yield PurchasedItem(name='The Hound of the Baskervilles', sku='BSKV',
                            quantity=9, price=Decimal(10), currency='USD')