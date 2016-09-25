from django.test import TestCase
from publications.models import Publication, Licence, Comment, CommentReview, Reviewer
from publications.cascade import (update_comment_validation, update_comment_correction)
from publications.constants import *
from customuser.models import User

# Create your tests here.


class PublicationTestCase(TestCase):

    def setUp(self):
        """
        Store an user
        """
        jesus = User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                    middle_name="Our Savior", last_name="Raptor", email="testpub1@test.com")
        fsm = User.objects.create(username="testuser2", password="azerty123", phd=True, first_name="Flying",
                                  middle_name="Spaghetti", last_name="Monster", email="testpub2@test.com")
        l = Licence.objects.create(short_name="lol", full_name="lol", url="http://google.com")
        Publication.objects.create(editor=jesus, title="lol", first_author=jesus, last_author=fsm, resume="lol",
                                   licence=l)

    def test_get_all_authors(self):
        publi = Publication.objects.get(title="lol")
        self.assertEqual(2, len(publi.get_all_authors))


class CascadeTestCase(TestCase):

    def setUp(self):
        self.jesus = User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                    middle_name="Our Savior", last_name="Raptor", email="testcasc1@test.com")
        self.fsm = User.objects.create(username="testuser2", password="azerty123", phd=True, first_name="Flying",
                                       middle_name="Spaghetti", last_name="Monster", email="testcasc2@test.com")
        self.rael = User.objects.create(username="testuser3", password="azerty123", phd=True, first_name="Rael",
                                        last_name="ET", email="testcasc3@test.com")
        self.ipu = User.objects.create(username="testuser4", password="azerty123", phd=True, first_name="Invisible",
                                       middle_name="Pink", last_name="Unicorn", email="testcasc4@test.com")
        self.ft = User.objects.create(username="testuser5", password="azerty123", phd=True, first_name="Flying",
                                      last_name="Teapot", email="testcasc5@test.com")
        l = Licence.objects.create(short_name="lol", full_name="lol", url="http://google.com")
        publication = Publication.objects.create(editor=self.jesus, title="lol", first_author=self.jesus,
                                                resume="lol", licence=l)
        self.rfsm = Reviewer.objects.create(scientist=self.fsm, publication=publication)
        self.rrael = Reviewer.objects.create(scientist=self.rael, publication=publication)
        self.ripu = Reviewer.objects.create(scientist=self.ipu, publication=publication)
        self.rft = Reviewer.objects.create(scientist=self.ft, publication=publication)
        self.comment = Comment.objects.create(author=self.fsm, author_fake_pseudo="", publication=publication,
                                              comment_type=CONTENT, title="lol", content="lol", licence=l)

    def test_update_comment_validation_not_enough(self):
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol")
        self.assertEqual(False, update_comment_validation(self.comment.pk))
        self.assertEqual(IN_PROGRESS, self.comment.validated)

    def test_update_comment_validation_DISMISS(self):
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol")
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True)
        self.assertEqual(True, update_comment_validation(self.comment.pk))
        self.assertEqual(DISMISS, Comment.objects.get(pk=self.comment.pk).validated)
        self.assertEqual(MINOR, Comment.objects.get(pk=self.comment.pk).seriousness)

    def test_update_comment_validation_VALIDATE(self):
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True)
        self.assertEqual(True, update_comment_validation(self.comment.pk))
        self.assertEqual(VALIDATE, Comment.objects.get(pk=self.comment.pk).validated)
        self.assertEqual(CRITICAL, Comment.objects.get(pk=self.comment.pk).seriousness)
