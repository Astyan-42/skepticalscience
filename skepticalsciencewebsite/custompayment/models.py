from uuid import uuid4
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment
from simple_history.models import HistoricalRecords
from django_countries.fields import CountryField
from custompayment.constants import *
from customuser.models import User
from publications.models import Publication


class Address(models.Model):
    scientist = models.OneToOneField(User, verbose_name=_("Scientist"), null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    company_name = models.CharField(_('company or organization'), max_length=255, blank=True)
    street_address_1 = models.CharField(_('address'), max_length=255, blank=True)
    street_address_2 = models.CharField(_('address'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=255, blank=True)
    city_area = models.CharField(_('district'), max_length=127, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = CountryField(_('country'))
    country_area = models.CharField(_('state or province'), max_length=127, blank=True)
    phone = models.CharField(_('phone number'), max_length=30, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.first_name+" "+self.last_name


class Item(models.Model):

    name = models.CharField(_('item name'), max_length=32, choices=ITEM_CHOICES)
    sku = models.IntegerField(_('SKU'))  # used for the pk of the publication or the pk of the user

    def __str__(self):
        if self.name == SCIENTIST_ACCOUNT:
            return ITEM_CHOICES[SCIENTIST_ACCOUNT]
        else:
            return Publication.objects.get(pk=self.sku).__str__()


class Discount(models.Model):

    name = models.CharField(_('Name'), max_length=255)
    code = models.CharField(_('discount code'), primary_key=True, max_length=32)
    discount_for = models.CharField(_('item'), max_length=32, choices=ITEM_CHOICES)
    discount_type = models.CharField(_('type'), max_length=32, choices=DISCOUNT_CHOICES)
    discount_value = models.FloatField(_('value'))
    starting_date = models.DateField(_('starting'))
    ending_date = models.DateField(_('ending'))

    def __str__(self):
        return self.name+": "+str(self.code)


class Order(models.Model):

    token = models.CharField(_('token'), max_length=36, unique=True, null=True, blank=True)
    status = models.CharField(_('order status'), max_length=32, choices=ORDER_CHOICES, default=NEW)
    creation_date = models.DateTimeField(_('created'), auto_now_add=True)
    last_status_change = models.DateTimeField(_('last status change'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('buyer'))
    discount = models.ForeignKey(Discount, verbose_name=_('discount code'), null=True, blank=True)
    billing_address = models.ForeignKey(Address, verbose_name=_('billing address'), null=True, blank=True)
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

    def clean(self):
        if self.discount is not None:
            if self.discount.discount_for != self.item.name:
                raise ValidationError({'discount': ('The discount code is not for this type of item')})

    def __str__(self):
        return self.token


class CountryPIB(models.Model):

    country = CountryField(_('country'))
    pib_inhabitant = models.FloatField(_('pib per inhabitant'))


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

    def __str__(self):
        return self.order.__str__()
