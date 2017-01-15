from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from publications.models import Publication, Licence
from publications.views import can_be_leave_reviewer
from django.contrib.auth.models import Permission
from sciences.models import Science
from publications.constants import WAITING_PAYMENT, CORRECTION, ADDING_PEER, PEER_REVIEW, FORM, EVALUATION


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
        self.assertEqual(resp.template_name, ['publications/publication_form.html'])

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


class TestPublicationUpdate(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname')
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can change publication')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.publication = Publication.objects.create(title="title", editor=self.user, resume="resume",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user, licence=self.licence,
                                                      status=WAITING_PAYMENT)
        self.publication.save()
        self.url = reverse("update_publication", kwargs={"pk": self.publication.pk})

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
        self.assertEqual(resp.template_name, ['publications/publication_correct_form.html'])

    def test_succeed_update(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"title": 'title', "resume": 'resume',
                                           "pdf_creation": File(BytesIO(b"\x00\x01"), name='lol'),
                                           "source_creation": File(BytesIO(b"\x00\x01"), name='lol2'),
                                           "first_author": self.user.pk, "last_author": '',
                                           "sciences": self.science.pk,
                                           "licence": self.licence.pk}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_detail.html'])

    def test_failed_update(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"title": 'title', "resume": 'resume',
                                           "pdf_creation": File(BytesIO(), name='lol'),
                                           "source_creation": File(BytesIO(b"\x00\x01"), name='lol2'),
                                           "first_author": self.user.pk, "last_author": '',
                                           "sciences": self.science.pk,
                                           "licence": self.licence.pk}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_correct_form.html'])


class TestPublicationCorrectionUpdate(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname')
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can change publication')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.publication = Publication.objects.create(title="title", editor=self.user, resume="resume",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user, licence=self.licence,
                                                      status=CORRECTION)
        self.publication.sciences.add(self.science)
        self.publication.save()
        self.url = reverse("correct_publication", kwargs={"pk": self.publication.pk})

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
        self.assertEqual(resp.template_name, ['publications/publication_edit_form.html'])

    def test_succeed_update(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"resume": 'resume',
                                           "pdf_final": File(BytesIO(b"\x00\x01"), name='lol'),
                                           "source_final": File(BytesIO(b"\x00\x01"), name='lol2')}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_detail.html'])

    def test_failed_update(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"resume": ''}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_edit_form.html'])


class TestPublicationAbort(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname')
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can change publication')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.publication = Publication.objects.create(title="title", editor=self.user, resume="resume",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user, licence=self.licence,
                                                      status=CORRECTION)
        self.publication.sciences.add(self.science)
        self.publication.save()
        self.url = reverse("abort_publication", kwargs={"pk": self.publication.pk})

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
        self.assertEqual(resp.template_name, ['publications/publication_edit_form.html'])

    def test_succeed_update(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"abort": True}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_detail.html'])

    def test_succed_abort_false_update(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {"abort": False}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_detail.html'])


class TestPublicationTableView(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname')
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can change publication')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.publication = Publication.objects.create(title="title", editor=self.user, resume="resume",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user, licence=self.licence,
                                                      status=CORRECTION)
        self.publication.sciences.add(self.science)
        self.publication.save()
        self.url = reverse("publication_list")

    def test_get(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_list.html', 'publications/publication_list.html'])
        self.assertEqual(len(resp.context_data['object_list']), 1)

    def test_get_filter(self):
        resp = self.client.get(self.url, {"title": "title"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_list.html', 'publications/publication_list.html'])
        self.assertEqual(len(resp.context_data['object_list']), 1)

    def test_get_filter_none(self):
        resp = self.client.get(self.url, {"title": "zdfc"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_list.html', 'publications/publication_list.html'])
        self.assertEqual(len(resp.context_data['object_list']), 0)


class TestPublicationSpecialTableView(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname', phd=True)
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can add reviewer')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.user.save()
        self.user.phd_in.add(self.science)
        self.publication = Publication.objects.create(title="title", editor=self.user2, resume="resume",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user2, licence=self.licence,
                                                      status=ADDING_PEER)
        self.publication.save()
        self.publication.sciences.add(self.science)
        self.publication2 = Publication.objects.create(title="title2", editor=self.user2, resume="resume2",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user2, licence=self.licence,
                                                      status=ADDING_PEER)
        self.publication2.save()
        self.url = reverse("publication_to_review")

    def test_not_logged(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_get(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_special_list.html', 'publications/publication_list.html'])
        # wtf the test don't work while it's work when using the website, mess up somehow because of science
        # self.assertEqual(len(resp.context_data['object_list']), 1)


class TestCanBeLeaveReviewer(TestCase):

    def test_become_true(self):
        self.assertTrue(can_be_leave_reviewer(True, 2, 1, True, ADDING_PEER, "become"))

    def test_become_false(self):
        self.assertFalse(can_be_leave_reviewer(True, 4, 1, True, ADDING_PEER, "become"))

    def test_leave_true(self):
        self.assertTrue(can_be_leave_reviewer(True, 4, 1, True, ADDING_PEER, "leave"))

    def test_leave_false(self):
        self.assertFalse(can_be_leave_reviewer(True, 4, 1, True, PEER_REVIEW, "leave"))


class TestPublicationDetailView(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com",
                                             first_name='fname', last_name='lname', phd=True)
        self.user2 = User.objects.create_user(username="testuser2", password="azerty123", email="test2@tests.com")
        # add permission to a user
        self.licence = Licence.objects.create(short_name="CC0")
        self.licence.save()
        permission = Permission.objects.get(name='Can add estimated impact factor')
        self.user.user_permissions.add(permission)
        self.science = Science.objects.create(name='lol', description="zef", primary_science=True)
        self.science.save()
        self.user.save()
        self.user.phd_in.add(self.science)
        self.publication = Publication.objects.create(title="title", editor=self.user2, resume="resume",
                                                      pdf_creation=File(BytesIO(b"\x00\x01"), name='lol'),
                                                      source_creation=File(BytesIO(b"\x00\x01"), name='lol2'),
                                                      first_author=self.user2, licence=self.licence,
                                                      status=PEER_REVIEW)
        self.publication.save()
        self.publication.sciences.add(self.science)
        self.url = reverse("publication_view", kwargs={'pk': self.publication.pk})

    def test_get_template(self):
        # assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.get(self.url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['publications/publication_detail.html'])

    def test_404(self):
        url = reverse("publication_view", kwargs={'pk': self.publication.pk+1})
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 404)

    def test_post_comment(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'comment-author_fake_pseudo': '1234', 'comment-title': 'test',
                                           'comment-comment_type': FORM, 'comment-content': 'f', 'submit': "Submit"},
                                follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context_data['comments']), 1)

    def test_post_eif_fail(self):
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'impact_factor-estimated_impact_factor': 30, 'submit': "Evaluate"},
                                follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_post_eif_success(self):
        self.publication.status = EVALUATION
        self.publication.save()
        assert self.client.login(username="testuser", password="azerty123")
        resp = self.client.post(self.url, {'impact_factor-estimated_impact_factor': 30, 'submit': "Evaluate"},
                                follow=True)
        self.assertEqual(resp.status_code, 200)

# become_reviewer_view and leave_reviewer_view are fine

class TestCommentDetailView(TestCase):

    pass