import datetime
from django.utils import timezone
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from custompayment.models import Order, Address, Item, CountryPayment, Discount, Price


class BillingAddressUpdateTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        self.user.save()
        self.item = Item(name="'scientist-account'", sku=self.user.pk)
        self.item.save()
        self.order = Order(status='new', user=self.user, item=self.item)
        self.order.save()
        self.url = reverse("address", kwargs={'token' :self.order.token})

    def test_not_logged(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_bad_user(self):
        # test the user in the view to return 302 if not the same
        User = get_user_model()
        bad_user = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        bad_user.save()
        assert self.client.login(username="testuser2", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_get_template(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ["custompayment/address_form.html"])

    def test_create_address(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self. assertIsInstance(resp.context_data['object'], Address)

    def test_get_existing_address_not_linked(self):
        address = Address(scientist=self.user, first_name='fname1', last_name='lname1')
        address.save()
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context_data['object'], Address)
        self.assertEqual(resp.context_data['object'].first_name, 'fname1')
        self.assertEqual(resp.context_data['object'].last_name, 'lname1')

    def test_get_existing_address_linked(self):
        address = Address(scientist=self.user, first_name='fname1', last_name='lname1')
        address.save()
        self.order.billing_address = address
        self.order.save()
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context_data['object'], Address)
        self.assertEqual(resp.context_data['object'].first_name, 'fname1')
        self.assertEqual(resp.context_data['object'].last_name, 'lname1')

    def test_form_valid(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"first_name" :'f1', "last_name": 'f1', "street_address_1": 'f1',
                                           "city": 'f1', "postal_code" :'f1', "country" :'FR'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp._headers['location'][1], '/checkout/'+self.order.token+'/')

    def test_form_invalid(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"last_name": 'f1', "street_address_1": 'f1',
                                           "city": 'f1', "postal_code": 'f1', "country": 'FR'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ["custompayment/address_form.html"])


# let just assume add_price_to_context is fine for now

class OrderDetailViewTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        self.user.save()
        self.item = Item(name='scientist-account', sku=self.user.pk)
        self.item.save()
        self.countrypayment = CountryPayment(country='FR', pib_per_inhabitant='1000', accepted=True)
        self.countrypayment.save()
        self.address = Address(scientist=self.user, first_name='fname1', last_name='lname1', country='FR')
        self.address.save()
        self.price = Price()
        self.price.save()
        self.order = Order(status='new', user=self.user, item=self.item, billing_address=self.address, price=self.price)
        self.order.save()
        sdate = timezone.now() - datetime.timedelta(days=1)
        edate = timezone.now() + datetime.timedelta(days=1)
        self.discount = Discount(name='lol', code='lol', discount_for='scientist-account', discount_type='percent',
                                 discount_value='10', starting_date=sdate, ending_date=edate)
        self.discount.save()
        self.url = reverse("detail_order", kwargs={'token': self.order.token})

    def test_not_logged(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_bad_user(self):
        # test the user in the view to return 302 if not the same
        User = get_user_model()
        bad_user = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        bad_user.save()
        assert self.client.login(username="testuser2", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_get_template(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['custompayment/order_detail.html'])

    def test_get_404(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("detail_order", kwargs={'token': '43422'})
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 404)

    def test_fill_bad_discount_code(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'discount' : '1234', 'submit': "Apply"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context_data['form'].__dict__['_errors'])

    def test_fill_good_discount_code(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'discount' : 'lol', 'submit': "Apply"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        order_discount = Order.objects.get(token=self.order.token).discount
        self.assertEqual(order_discount, self.discount)

    def test_accept(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'submit': "Accept"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, 'custompayment/payment.html')


