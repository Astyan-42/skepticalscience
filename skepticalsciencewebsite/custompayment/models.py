from uuid import uuid4
from django.db import models
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment
from simple_history.models import HistoricalRecords
from custompayment.constants import *
from customuser.models import User

# to complete Order and Payment
# to add Billing address and Discount code


class Item(models.Model):

    name = models.CharField(_('item name'), max_length=32, choices=ITEM_CHOICES)
    sku = models.IntegerField(_('SKU'))  # used for the pk of the publication or the pk of the user


class Order(models.Model):

    token = models.CharField(_('token'), max_length=36, unique=True, null=True, blank=True)
    status = models.CharField(_('order status'), max_length=32, choices=ORDER_CHOICES, default=NEW)
    creation_date = models.DateTimeField(_('created'), auto_now_add=True)
    last_status_change = models.DateTimeField(_('last status change'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('buyer'))
    # billing_address = models.ForeignKey(Address)
    item = models.OneToOneField(Item, verbose_name=_('item'))
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid4())
            return super(Order, self).save(*args, **kwargs)

    def change_status(self, status):
        if status != self.status:
            self.status = status
            self.save()


class Payment(BasePayment):
    order = models.ForeignKey(Order, related_name='payments')

    def get_failure_url(self):
        return 'http://example.com/failure/'

    def get_success_url(self):
        return 'http://example.com/success/'

    def get_purchased_items(self):
        # you'll probably want to retrieve these from an associated order
        # either scientific account or posting a publication
        item = self.order.item
        default_price = PRODUCTS_PRICES[item.name]
        # adjusted_price = depend of country + (user quality if for publication) + promotion
        yield PurchasedItem(name=item.name, sku=str(item.sku),
                            quantity=1, price=Decimal(default_price), currency='USD')
