import mock
from io import BytesIO
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from custompayment.models import Address, CountryPayment, Item, Discount, Price, Payment, Order
from custompayment.constants import SCIENTIST_ACCOUNT


class AddressTestCase(TestCase):

    def test_str(self):
        address = mock.Mock(spec=Address)
        address.first_name = 'Fname'
        address.last_name = 'Lname'
        self.assertEqual(Address.__str__(address).__dict__['_mock_new_name'], 'billing_name')


class CountryPaymentTestCase(TestCase):

    def test_str(self):
        cp = mock.Mock(spec=CountryPayment)
        cp.country = mock.Mock()
        self.assertEqual(CountryPayment.__str__(cp), str(cp.country.name))


class ItemTestCase(TestCase):

    def test_str(self):
        item = mock.Mock(spec=Item)
        item.name = SCIENTIST_ACCOUNT
        item.sku = 1
        self.assertEqual(Item.__str__(item), 'Scientist account')


class DiscountTestCase(TestCase):

    def test_str(self):
        discount = mock.Mock(spec=Discount)
        discount.name = 'TEST'
        discount.code = '42'
        self.assertEqual(Discount.__str__(discount), 'TEST: 42')


class PriceTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(PriceTestCase, cls).setUpClass()
        cls.price = mock.Mock(spec=Price)
        cls.price.currency = 'EUR'
        cls.price.product_default_price = 10.2
        cls.price.country_reduction = 1.2
        cls.price.discount = 2.2
        cls.price.tax_percent = 10.
        cls.price.tax = 3.34

    def test_get_taxes(self):
        self.assertEqual(Price.__str__(self.price), str(self.price.gross)+' '+self.price.currency)

    # mock not well made for this
    # def test_to_list(self):
    #     print(Price.to_list(self.price))


class PaymentTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(PaymentTestCase, cls).setUpClass()
        cls.payment = mock.Mock(spec=Payment)
        cls.payment.token = 'token'
        cls.payment.save()

    def test_get_failure_url(self):
        self.assertEqual(Payment.get_failure_url(self.payment), 'http://example.com/failure/')

    def test_get_success_url(self):
        self.assertEqual(Payment.get_success_url(self.payment), 'http://example.com/success/')

    def test_str(self):
        self.assertEqual(Payment.__str__(self.payment), 'token')


class OrderTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(OrderTestCase, cls).setUpClass()
        cls.order = mock.Mock(spec=Order)
        cls.order.status = 'new'
        cls.order.creation_date = timezone.now()
        cls.order.last_status_change = timezone.now()
        cls.order.user = mock.Mock(spec=get_user_model())
        cls.order.discount = mock.Mock(spec=Discount)
        cls.order.billing_address = mock.Mock(spec=Address)
        cls.order.item = mock.Mock(spec=Item)
        cls.order.price = mock.Mock(spec=Price)
        cls.order.payment = mock.Mock(spec=Payment)
        cls.order.save()

    def test_str_and_save(self):
        self.assertEqual(Order.__str__(self.order), self.order.token)

    def test_change_status(self):
        Order.change_status(self.order, 'confirmed')
        self.assertEqual(self.order.status, 'confirmed')

    def test_can_add_payment(self):
        self.assertEqual(Order.can_add_payment(self.order), False)
        self.order.payment = None
        self.order.save()
        self.assertEqual(Order.can_add_payment(self.order), True)

    # def test_can_be_cancelled(self):
    #     pass

    # def test_can_be_delete(self):
    #    pass

    # def test_clean(self):
    #     pass

    # don't work with mock and need setUp not setUpClass
    # def test_delete(self):
    #     Order.delete(self.order)
        # print(self.order)
