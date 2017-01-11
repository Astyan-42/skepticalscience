from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from publications.models import Publication, Licence

"download_publication"

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
