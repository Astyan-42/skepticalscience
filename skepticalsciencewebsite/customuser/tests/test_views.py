import mock
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from skepticalsciencewebsite.utils import setup_view
from customuser.models import User
from custompayment.constants import SCIENTIST_ACCOUNT
from customuser.views import UserDetailView, UserUpdateView


class TestUserDetailView(TestCase):

    def setUp(self):
        user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        user.save()
        request = RequestFactory().get('/fake-path/')
        view = UserDetailView.as_view()
        self.response = view(request, pk=user.pk)

    def test_response_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_get_context_data(self):
        self.assertEqual(self.response.context_data['account_status'], 'Skeptic')
        self.assertEqual(self.response.context_data['order'], SCIENTIST_ACCOUNT)


