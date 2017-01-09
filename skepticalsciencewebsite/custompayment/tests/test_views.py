from django.utils import timezone
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from custompayment.models import Order, Address, Item


class BillingAddressUpdateTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        self.user.save()
        self.item = Item(name="Scientist account", sku=1)
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
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_create_address(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self. assertIsInstance(resp.context_data['object'], Address)

    def test_get_existing_address_not_linked(self):
        address = Address(scientist=self.user, first_name='fname1', last_name='lname1')
        address.save()
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context_data['object'], Address)
        self.assertEqual(resp.context_data['object'].first_name, 'fname1')
        self.assertEqual(resp.context_data['object'].last_name, 'lname1')

    def get_existing_address_linked(self):
        address = Address(scientist=self.user, first_name='fname1', last_name='lname1')
        address.save()
        self.order.billing_address = address
        self.order.save()
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context_data['object'], Address)
        self.assertEqual(resp.context_data['object'].first_name, 'fname1')
        self.assertEqual(resp.context_data['object'].last_name, 'lname1')



