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

    def test_show_page_response_code(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("edit_profile")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_send_data_response_code(self): # don't work like wanted
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("edit_profile")
        resp = self.client.post(url, {'first_name': 'john'}, follow=True)
        print(resp.template_name) # stay on the template of edit_profile, I would like to have the template of view_profile after redirection
        self.assertEqual(resp.status_code, 200)
