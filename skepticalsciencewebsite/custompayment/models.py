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
# to add Billing address and Discount code => billing address https://chriskief.com/2015/01/19/create-or-update-with-a-django-modelform/


class Item(models.Model):

    name = models.CharField(_('item name'), max_length=32, choices=ITEM_CHOICES)
    sku = models.IntegerField(_('SKU'))  # used for the pk of the publication or the pk of the user


class Discount(models.Model):

    name = models.CharField(_('Name'), max_length=255)
    code = models.CharField(_('discount code'), max_length=32)
    discount_for = models.CharField(_('item'), max_length=32, choices=ITEM_CHOICES),
    discount_type = models.CharField(_('type'), max_length=32, choices=DISCOUNT_CHOICES)
    discount_value = models.FloatField(_('value'))
    starting_date = models.DateField(_('starting'))
    ending_date = models.DateField(_('ending'))


class Order(models.Model):

    token = models.CharField(_('token'), max_length=36, unique=True, null=True, blank=True)
    status = models.CharField(_('order status'), max_length=32, choices=ORDER_CHOICES, default=NEW)
    creation_date = models.DateTimeField(_('created'), auto_now_add=True)
    last_status_change = models.DateTimeField(_('last status change'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('buyer'))
    discount = models.OneToOneField(Discount, verbose_name=('discount'), null=True, blank=True)
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
        # either scientific account or posting a publication
        item = self.order.item
        default_price = PRODUCTS_PRICES[item.name]
        # adjusted_price = depend of country + (user quality if for publication) + promotion
        yield PurchasedItem(name=item.name, sku=str(item.sku),
                            quantity=1, price=Decimal(default_price), currency='USD')
