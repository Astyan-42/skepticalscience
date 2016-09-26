from django.test import TestCase
from django.utils import timezone
from publications.models import Publication, Licence, Comment, CommentReview, Reviewer
from publications.cascade import (update_comment_validation, update_comment_correction, update_user_skeptic_score,
                                  update_publication_score_peer_review_to_correction)
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
        self.publication = Publication.objects.create(editor=self.jesus, title="lol", first_author=self.jesus,
                                                      resume="lol", licence=l)
        self.rfsm = Reviewer.objects.create(scientist=self.fsm, publication=self.publication)
        self.rrael = Reviewer.objects.create(scientist=self.rael, publication=self.publication)
        self.ripu = Reviewer.objects.create(scientist=self.ipu, publication=self.publication)
        self.rft = Reviewer.objects.create(scientist=self.ft, publication=self.publication)
        self.comment = Comment.objects.create(author=self.fsm, author_fake_pseudo="", publication=self.publication,
                                              comment_type=CONTENT, title="lol", content="lol", licence=l)

    def test_update_comment_validation_not_enough(self):
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol")
        self.assertEqual(False, update_comment_validation(self.comment.pk))
        self.assertEqual(IN_PROGRESS, Comment.objects.get(pk=self.comment.pk).validated)

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

    def test_update_comment_correction_not_enough(self):
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        self.assertEqual(False, update_comment_correction(self.comment.pk))
        self.assertEqual(False, Comment.objects.get(pk=self.comment.pk).corrected)
        self.assertEqual(None, Comment.objects.get(pk=self.comment.pk).corrected_date)

    def test_update_comment_correction_not_corrected(self):
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=False, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        self.assertEqual(True, update_comment_correction(self.comment.pk))
        self.assertNotEqual(None, Comment.objects.get(pk=self.comment.pk).corrected_date)
        self.assertEqual(False, Comment.objects.get(pk=self.comment.pk).corrected)

    def test_update_comment_correction_corrected(self):
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        self.assertEqual(True, update_comment_correction(self.comment.pk))
        self.assertNotEqual(None, Comment.objects.get(pk=self.comment.pk).corrected_date)
        self.assertEqual(True, Comment.objects.get(pk=self.comment.pk).corrected)

    def test_update_user_skeptic_score_not_yet(self):
        self.assertEqual(False, update_user_skeptic_score(self.comment.pk))
        self.assertEqual(0, User.objects.get_by_natural_key(self.fsm).valid_bias_found)
        self.assertEqual(0, User.objects.get_by_natural_key(self.fsm).invalid_bias_found)

    def test_update_user_skeptic_score_dismiss(self):
        self.comment.validated = DISMISS
        self.comment.save()
        self.assertEqual(True, update_user_skeptic_score(self.comment.pk))
        self.assertEqual(0, User.objects.get_by_natural_key(self.fsm).valid_bias_found)
        self.assertEqual(1, User.objects.get_by_natural_key(self.fsm).invalid_bias_found)
        self.assertEqual(0, User.objects.get_by_natural_key(self.fsm).skeptic_score)

    def test_update_user_skeptic_score_validated(self):
        self.comment.validated = VALIDATE
        self.comment.save()
        self.assertEqual(True, update_user_skeptic_score(self.comment.pk))
        self.assertEqual(1, User.objects.get_by_natural_key(self.fsm).valid_bias_found)
        self.assertEqual(0, User.objects.get_by_natural_key(self.fsm).invalid_bias_found)
        self.assertEqual(10., User.objects.get_by_natural_key(self.fsm).skeptic_score)

    def test_update_publication_score_peer_review_to_correction_bad_status(self):
        self.assertEqual(False, update_publication_score_peer_review_to_correction(self.publication.pk))

    def test_update_publication_score_peer_review_to_correction_no_comment(self):
        self.publication.status = CORRECTION
        self.publication.save()
        self.assertEqual(True,  update_publication_score_peer_review_to_correction(self.publication.pk))
        self.assertEqual(10., Publication.objects.get(pk=self.publication.pk).publication_score)

    def test_update_publication_score_peer_review_to_correction_no_comment(self):
        self.publication.status = CORRECTION
        self.publication.save()
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        self.assertEqual(True,  update_publication_score_peer_review_to_correction(self.publication.pk))
        self.assertEqual(8., Publication.objects.get(pk=self.publication.pk).publication_score)
