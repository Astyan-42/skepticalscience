from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from publications.models import Publication, Licence
from django.contrib.auth.models import Permission
from sciences.models import Science


class TestDownloadFile(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
        self.user.save()
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        self.publication = Publication.objects.create(editor=self.user, first_author=self.user, title="title",
                                                      resume="resume", pdf_creation=File(BytesIO(), name='lol'),
                                                      source_creation=File(BytesIO(), name='lol'), licence=self.licence)
        self.publication.save()

    def test_get_file_empty(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("download_publication", kwargs={'field_name': 'pdf_final',
                                                      'publication_id': self.publication.pk})
        with self.assertRaises(ValueError):
            self.client.get(url)

    def test_get_file_filled(self):
        assert self.client.login(username="testuser", password="azerty123")
        url = reverse("download_publication",  kwargs={'field_name': 'pdf_creation',
                                                       'publication_id': self.publication.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class TestPublicationCreate(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname')
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can add publication')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.url = reverse("create_publication")

    def test_not_logged(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_bad_loggin(self):
        assert self.client.login(username="testuser2", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_get_template(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_succeed_creation(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"title": 'title', "resume": 'resume',
                                           "pdf_creation": File(BytesIO(b"\x00\x01"), name='lol'),
                                           "source_creation": File(BytesIO(b"\x00\x01"), name='lol2'),
                                           "first_author": self.user.pk, "last_author": '',
                                           "sciences": self.science.pk,
                                           "licence": self.licence.pk}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_detail.html'])

    def test_failed_creation(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"title": 'title', "resume": 'resume',
                                           "pdf_creation": File(BytesIO(), name='lol'),
                                           "source_creation": File(BytesIO(b"\x00\x01"), name='lol2'),
                                           "first_author": self.user.pk, "last_author": '',
                                           "sciences": self.science.pk,
                                           "licence": self.licence.pk}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_form.html'])