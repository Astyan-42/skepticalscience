from django.test import TestCase
from decimal import Decimal
from django.shortcuts import redirect
from customuser.models import User
from custompayment.models import Payment, Order, Item
# Create your tests here.


class PaymentStatusTestCase(TestCase):

    def setUp(self):
        item = Item(name="publication", sku=1)
        item.save()
        user = User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                    middle_name="Our Savior", last_name="Raptor", email="testpub1@test.com")
        order = Order(item=item, user=user)
        order.save()
        defaults = {'total': Decimal(120),
                    'tax': Decimal(20),
                    'currency': 'USD',
                    'delivery': Decimal(10),
                    'billing_first_name': 'Sherlock',
                    'billing_last_name': 'Holmes',
                    'billing_address_1': '221B Baker Street',
                    'billing_address_2': '',
                    'billing_city': 'London',
                    'billing_postcode': 'NW1 6XE',
                    'billing_country_code': 'UK',
                    'description': 'Order %(order_number)s' % {'order_number': order},
                    'billing_country_area': 'Greater London',
                    'customer_ip_address': '127.0.0.1'}
        self.payment, res = Payment.objects.get_or_create(variant="dummy", status='waiting', order=order, defaults=defaults)
        self.payment.save()

    def test_change_status(self):
        # unable to test status change or status_change don't work
        self.payment.change_status('preauth')
        order = Order.objects.get(pk=self.payment.order.pk)
        print(order.status)
        self.payment.change_status('confirmed')



