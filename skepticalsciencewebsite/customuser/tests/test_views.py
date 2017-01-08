from io import BytesIO
from django.utils import timezone
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
        resp = self.client.post(self.url, {'first_name': 'john'}, follow=True)
        self.assertEqual(resp.template_name, ["customuser/update_user.html"])
        self.assertEqual(resp.status_code, 200)

    def test_not_connected(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)


class TestGetPHDImage(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username="testuser", password="azerty123", email="test@tests.com")
        self.user.save()

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


class TestUserPHDTableView(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUserPHDTableView, cls).setUpClass()
        cls.user = User.objects.create_superuser(username="testuser", password="azerty123", email="test@tests.com")
        # all of this to get one anwers in the query
        cls.user.phd_image = File(BytesIO(), name='lol')
        cls.user.phd_rate_date = None
        cls.user.phd_update_date = timezone.now()
        cls.user.save()
        cls.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        cls.user2.save()

    def test_connection_status_code_superuser(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("phd_ask_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_connection_status_code_simpleuser(self):
        assert self.client.login(username="testuser2", password="azerty123")
        url = reverse("phd_ask_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_connection_status_code_unconnected(self):
        url = reverse("phd_ask_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_get_queryset(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("phd_ask_list")
        resp = self.client.get(url)
        self.assertEqual(list(resp.context_data['object_list'])[0], self.user)

    # def test_get_table(self):
    #     # should be done

    def test_context_filter_name(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("phd_ask_list")
        resp = self.client.get(url)
        self.assertEqual(resp.context_data['filter'].data, {'phd_to_rate': True})


class TestPHDValidationViewGet(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPHDValidationViewGet, cls).setUpClass()
        cls.user = User.objects.create_superuser(username="testuser", password="azerty123", email="test@tests.com")
        # all of this to get one anwers in the query
        cls.user.phd_image = File(BytesIO(), name='lol')
        cls.user.phd_rate_date = None
        cls.user.phd_update_date = timezone.now()
        cls.user.save()
        cls.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        cls.user2.save()

    def test_get_context_data(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("user_phd", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertIsNotNone(resp.context_data['form'])
        self.assertEqual(resp.context_data['object'], self.user)
        self.assertEqual(resp.context_data['address_name'], 'Unknowned')
        self.assertEqual(resp.context_data["user_detail"], self.user)

    def test_connection_status_code_superuser(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("user_phd", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_connection_status_code_simpleuser(self):
        assert self.client.login(username="testuser2", password="azerty123")
        url = reverse("user_phd", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_connection_status_code_unconnected(self):
        url = reverse("user_phd", kwargs={'pk':self.user.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)


class TestPHDValidationViewPost(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username="testuser", password="azerty123", email="test@tests.com")
        self.user.phd_image = File(BytesIO(), name='lol')
        self.user.phd_rate_date = None
        self.user.phd_update_date = timezone.now()
        self.user.save()

    def test_post_success(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("user_phd", kwargs={'pk': self.user.pk})
        resp = self.client.post(url, {'phd_comment': 'test', 'phd': True}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['customuser/list_user_phd.html', 'customuser/user_list.html'])

    def test_post_fail(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("user_phd", kwargs={'pk': self.user.pk})
        resp = self.client.post(url, {'phd' : 'True'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ["customuser/check_phd_user.html"])
        self.assertEqual(resp.context_data["address_name"], 'Unknowned')
        self.assertIsNotNone(resp.context_data["form"])
        self.assertEqual(resp.context_data["user_detail"], self.user)
        self.assertEqual(resp.context_data['object'], self.user)