import mock
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from skepticalsciencewebsite.utils import setup_view
from customuser.models import User
from custompayment.constants import SCIENTIST_ACCOUNT
from customuser.views import UserDetailView, UserUpdateView


class TestUserDetailView(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUserDetailView, cls).setUpClass()
        user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        user.save()
        request = RequestFactory().get('/fake-path/')
        view = UserDetailView.as_view()
        cls.response = view(request, pk=user.pk)

    def test_response_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_get_context_data(self):
        self.assertEqual(self.response.context_data['account_status'], 'Skeptic')
        self.assertEqual(self.response.context_data['order'], SCIENTIST_ACCOUNT)


class TestUserUpdateView(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUserUpdateView, cls).setUpClass()
        cls.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        cls.user.save()
        cls.url = reverse("edit_profile")

    def test_show_page_response_code(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_object(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context_data['object'], self.user)

    def test_send_data_response_code(self):
        assert self.client.login(username="testuser", password="azerty123")
        # nimp is not process (normal behaviour don't need test
        resp = self.client.post(self.url, {'first_name': 'john', 'nimp': 'lol', 'email': "test@tests.com"}, follow=True)
        self.assertEqual(resp.template_name, ["customuser/detail_user.html"])
        self.assertEqual(resp.status_code, 200)

    def test_send_wrong_data_response_code(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'first_name': 'john'})
        self.assertEqual(resp.template_name, ["customuser/update_user.html"])
        self.assertEqual(resp.status_code, 200)

    def test_not_connected(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)