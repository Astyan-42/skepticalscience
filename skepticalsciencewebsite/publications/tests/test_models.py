import mock
from io import BytesIO
from django.core.files import File
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from publications.models import Licence, Publication, EstimatedImpactFactor, Reviewer, Comment, CommentReview


class LicenceTestCase(TestCase):

    def test_str(self):
        licence = mock.Mock(spec=Licence)
        licence.short_name = 'CC0'
        self.assertEqual(Licence.__str__(licence), 'CC0')


class PublicationTestCase(TestCase):

    def test_str(self):
        publication = mock.Mock(spec=Publication)
        publication.title = 'Title'
        self.assertEqual(Publication.__str__(publication), 'Title')

    def test_clean_error(self):
        publication = mock.Mock(spec=Publication)
        publication.title = 'Title'
        publication.pdf_creation = File(BytesIO(), name='lol')
        publication.source_creation = None
        with self.assertRaises(ValidationError):
            Publication.clean(publication)

    def test_clean_pass(self):
        publication = mock.Mock(spec=Publication)
        publication.title = 'Title'
        publication.pdf_creation = File(BytesIO(), name='lol')
        publication.source_creation = File(BytesIO(), name='lol')
        # just pass the test
        Publication.clean(publication)


class EstimatedImpactFactorTestCase(TestCase):

    def test_str(self):
        eif = mock.Mock(spec=EstimatedImpactFactor)
        user = mock.Mock()
        eif.estimator = user
        self.assertEqual(EstimatedImpactFactor.__str__(eif).__dict__['_mock_new_parent'], user.get_full_name)


class ReviewerTestCase(TestCase):

    def test_str(self):
        reviewer = mock.Mock(spec=Reviewer)
        user = mock.Mock()
        reviewer.scientist = user
        self.assertEqual(Reviewer.__str__(reviewer).__dict__['_mock_new_parent'], user.get_full_name)


class CommentTestCase(TestCase):

    def test_str(self):
        comment = mock.Mock(spec=Comment)
        comment.title = 'title'
        self.assertEqual(Comment.__str__(comment), 'title')


class CommentReviewTestCase(TestCase):

    def test_str(self):
        comment = mock.Mock(spec=Comment)
        comment.title = 'title'
        commentreview = mock.Mock(spec=CommentReview)
        commentreview.comment = comment
        self.assertEqual(CommentReview.__str__(commentreview), 'title')