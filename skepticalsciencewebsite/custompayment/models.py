import datetime
from uuid import uuid4
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment
from simple_history.models import HistoricalRecords
from django_countries.fields import CountryField
from customuser.models import User
from publications.models import Publication
from custompayment.constants import *
from custompayment.utils import money_quantize


class Address(models.Model):
    # creation date
    scientist = models.ForeignKey(User, verbose_name=_("Scientist"), null=True, blank=True)
    creation_date = models.DateTimeField(_('created'), auto_now_add=True)
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

    @property
    def billing_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.billing_name()


class CountryPayment(models.Model):

    country = CountryField(_('country'), unique=True)
    pib_per_inhabitant = models.FloatField(_('PIB per inhabitant'))
    accepted = models.BooleanField(_('Can pay'))

    def __str__(self):
        return str(self.country.name)


class Item(models.Model):

    name = models.CharField(_('item name'), max_length=32, choices=ITEM_CHOICES)
    sku = models.IntegerField(_('SKU'))  # used for the pk of the publication or the pk of the user

    def __str__(self):
        if self.name == SCIENTIST_ACCOUNT:
            return [verbose for simple, verbose in ITEM_CHOICES if simple==SCIENTIST_ACCOUNT][0]
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


class Price(models.Model):

    currency = models.CharField(_("currency"), max_length=3, default="EUR")
    product_default_price = models.DecimalField(_("default price"), max_digits=10, decimal_places=2)
    country_reduction = models.DecimalField(_("country reduction"), max_digits=10, decimal_places=2,
                                            null=True, blank=True, default=None)
    scientist_score = models.FloatField(_("scientist score"), null=True, blank=True) # added
    scientist_score_reduction = models.DecimalField(_("scientist reduction"), max_digits=10, decimal_places=2,
                                                    null=True, blank=True, default=None)
    discount = models.DecimalField(_("scientist reduction"), max_digits=10, decimal_places=2,
                                   null=True, blank=True, default=None)
    tax_percent = models.FloatField(_("taxes percents"), null=True, blank=True)
    tax = models.DecimalField(_("taxes"), max_digits=10, decimal_places=2)

    @property
    def gross(self):
        return money_quantize(self.product_default_price + (self.country_reduction or Decimal(0.)) +
                              (self.scientist_score_reduction or Decimal(0.)) + (self.discount or Decimal(0.)) +
                              self.tax)

    def get_taxes(self):
        return money_quantize(self.tax)

    def to_list(self):
        price_list = []
        order = Order.objects.get(price=self.pk)
        price_list.append({"t_type": "order "+order.item.name,
                           "t_object": order.item,
                           "t_price": str(self.product_default_price)+' '+str(self.currency)})
        if self.country_reduction is not None:
            price_list.append({"t_type": "country compensation",
                               "t_object": order.billing_address.country.name,
                               "t_price": str(self.country_reduction)+' '+str(self.currency)})
        if self.scientist_score_reduction is not None:
            price_list.append({"t_type": "scientist score compensation",
                               "t_object": "score :"+str(round(self.scientist_score, 2)),
                               "t_price": str(self.scientist_score_reduction)+' '+str(self.currency)})
        if self.discount is not None:
            price_list.append({"t_type": "discount code",
                              "t_object": order.discount.code,
                              "t_price": str(self.discount)+' '+str(self.currency)})
        price_list.append({"t_type": "taxes",
                          "t_object": str(self.tax_percent)+"%",
                          "t_price": str(self.tax)+' '+str(self.currency)})
        price_list.append({"t_type": "final price",
                           "t_object": "",
                           "t_price": str(self.gross)+' '+str(self.currency)})
        return price_list

    def __str__(self):
        return str(self.gross)+' '+self.currency


class Order(models.Model):

    token = models.CharField(_('token'), max_length=36, unique=True, null=True, blank=True)
    status = models.CharField(_('order status'), max_length=32, choices=ORDER_CHOICES, default=NEW)
    creation_date = models.DateTimeField(_('created'), auto_now_add=True)
    last_status_change = models.DateTimeField(_('last status change'), auto_now=True)
    user = models.ForeignKey(User, verbose_name=_('buyer'))
    discount = models.ForeignKey(Discount, verbose_name=_('discount code'), null=True, blank=True)
    billing_address = models.ForeignKey(Address, verbose_name=_('billing address'), null=True, blank=True)
    item = models.OneToOneField(Item, verbose_name=_('item'))
    # to delete, put the order in price
    price = models.ForeignKey(Price, verbose_name=_('price'), null=True, blank=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid4())
        return super(Order, self).save(*args, **kwargs)

    def change_status(self, status):
        if status != self.status:
            self.status = status
            self.save()

    def can_add_payment(self):
        return not self.payments.filter(Q(status='preauth') | Q(status='confirmed') | Q(status='refunded')).exists()

    def can_be_cancelled(self):
        if self.payments.filter(status='confirmed').exists():
            payment = self.payments.get(status='confirmed')
            t_delta = timezone.now() - payment.modified
            if t_delta < datetime.timedelta(days=REFUND_DAYS):
                return True
            else:
                return False

    def get_payment(self):
        if self.payments.filter(status='confirmed').exists():
            payment = self.payments.get(status='confirmed')
            return payment
        else:
            return None

    def clean(self):
        if self.discount is not None:
            if self.discount.discount_for != self.item.name:
                raise ValidationError({'discount': ('The discount code is not for this type of item')})

    def __str__(self):
        return self.token


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
                            quantity=1, price=Decimal(default_price), currency='EUR')

    def __str__(self):
        return self.order.__str__()
