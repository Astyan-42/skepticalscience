from io import BytesIO
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.core.files import File
from customuser.models import User
from custompayment.constants import SCIENTIST_ACCOUNT
from customuser.views import UserDetailView


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


class TestGetPHDImage(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestGetPHDImage, cls).setUpClass()
        cls.user = User.objects.create_superuser(username="testuser", password="azerty123", email="test@tests.com")
        cls.user.save()

    def test_get_phd_image_empty(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("phd_image", kwargs={'pk':self.user.pk})
        with self.assertRaises(ValueError):
            self.client.get(url)

    def test_get_phd_image_filled(self):
        self.user.phd_image = File(BytesIO(), name='lol')
        self.user.save()
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("phd_image", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_not_connected(self):
        url = reverse("phd_image", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_not_super_user(self):
        user = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        user.save()
        assert self.client.login(username="testuser2", password="azerty123")
        url = reverse("phd_image", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)