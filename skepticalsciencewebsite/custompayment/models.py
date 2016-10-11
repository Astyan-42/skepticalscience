from django.db import models
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal
from payments import PurchasedItem
from payments.models import BasePayment


# to complete Order and Payment
# to add Billing address and Discount code

class Order(models.Model):

    order_id = models.CharField(verbose_name=_("OrderID"), max_length=50, unique=True)


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