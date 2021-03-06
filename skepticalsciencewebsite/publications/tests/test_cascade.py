from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from publications.models import Publication, Licence, Comment, CommentReview, Reviewer, EstimatedImpactFactor
from publications.cascade import (update_comment_validation, update_comment_correction, update_user_skeptic_score,
                                  update_publication_score_peer_review_to_correction,
                                  update_publication_score_validation_to_evaluation, add_publication_to_user,
                                  update_user_mean_publication_score, update_reviewers_score_peer_review_to_correction,
                                  update_reviewers_score_validation_to_evaluation,
                                  update_median_impact_factor_publication, update_mean_impact_factor_users)
from publications.constants import *


class CascadeTestCase(TestCase):

    def setUp(self):
        self.User = get_user_model()
        self.jesus = self.User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                              middle_name="Our Savior", last_name="Raptor", email="testcasc1@tests.com")
        self.fsm = self.User.objects.create(username="testuser2", password="azerty123", phd=True, first_name="Flying",
                                            middle_name="Spaghetti", last_name="Monster", email="testcasc2@tests.com")
        self.rael = self.User.objects.create(username="testuser3", password="azerty123", phd=True, first_name="Rael",
                                             last_name="ET", email="testcasc3@tests.com")
        self.ipu = self.User.objects.create(username="testuser4", password="azerty123", phd=True, first_name="Invisible",
                                            middle_name="Pink", last_name="Unicorn", email="testcasc4@tests.com")
        self.ft = self.User.objects.create(username="testuser5", password="azerty123", phd=True, first_name="Flying",
                                      last_name="Teapot", email="testcasc5@tests.com")
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
        self.assertEqual(0, self.User.objects.get_by_natural_key(self.fsm).valid_bias_found)
        self.assertEqual(0, self.User.objects.get_by_natural_key(self.fsm).invalid_bias_found)

    def test_update_user_skeptic_score_dismiss(self):
        self.comment.validated = DISMISS
        self.comment.save()
        self.assertEqual(True, update_user_skeptic_score(self.comment.pk))
        self.assertEqual(0, self.User.objects.get_by_natural_key(self.fsm).valid_bias_found)
        self.assertEqual(1, self.User.objects.get_by_natural_key(self.fsm).invalid_bias_found)
        self.assertEqual(0, self.User.objects.get_by_natural_key(self.fsm).skeptic_score)

    def test_update_user_skeptic_score_validated(self):
        self.comment.validated = VALIDATE
        self.comment.save()
        self.assertEqual(True, update_user_skeptic_score(self.comment.pk))
        self.assertEqual(1, self.User.objects.get_by_natural_key(self.fsm).valid_bias_found)
        self.assertEqual(0, self.User.objects.get_by_natural_key(self.fsm).invalid_bias_found)
        self.assertEqual(10., self.User.objects.get_by_natural_key(self.fsm).skeptic_score)

    def test_update_publication_score_peer_review_to_correction_bad_status(self):
        self.assertEqual(False, update_publication_score_peer_review_to_correction(self.publication.pk))

    def test_update_publication_score_peer_review_to_correction_no_comment(self):
        self.publication.status = CORRECTION
        self.publication.save()
        self.assertEqual(True,  update_publication_score_peer_review_to_correction(self.publication.pk))
        self.assertEqual(10., Publication.objects.get(pk=self.publication.pk).publication_score)

    def test_update_publication_score_peer_review_to_correction_comment(self):
        self.publication.status = CORRECTION
        self.publication.save()
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        self.assertEqual(True,  update_publication_score_peer_review_to_correction(self.publication.pk))
        self.assertEqual(8., Publication.objects.get(pk=self.publication.pk).publication_score)
        self.comment.seriousness = MINOR
        self.comment.save()
        self.assertEqual(True,  update_publication_score_peer_review_to_correction(self.publication.pk))
        self.assertEqual(9., Publication.objects.get(pk=self.publication.pk).publication_score)
        self.comment.seriousness = CRITICAL
        self.comment.save()
        self.assertEqual(True,  update_publication_score_peer_review_to_correction(self.publication.pk))
        self.assertEqual(7., Publication.objects.get(pk=self.publication.pk).publication_score)

    def test_update_publication_score_validation_to_evaluation_bad_status(self):
        self.assertEqual(False, update_publication_score_validation_to_evaluation(self.publication.pk))

    def test_update_publication_score_validation_to_evaluation_no_comment(self):
        self.publication.status = EVALUATION
        self.publication.publication_score = 8.
        self.publication.save()
        self.assertEqual(False, update_publication_score_validation_to_evaluation(self.publication.pk))
        self.assertEqual(8., Publication.objects.get(pk=self.publication.pk).publication_score)

    def test_update_publication_score_validation_to_evaluation_comment(self):
        self.publication.status = EVALUATION
        self.publication.publication_score = 8.
        self.publication.save()
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.corrected = True
        self.comment.save()
        self.assertEqual(True, update_publication_score_validation_to_evaluation(self.publication.pk))
        self.assertEqual(9., Publication.objects.get(pk=self.publication.pk).publication_score)
        self.publication.publication_score = 8.
        self.publication.save()
        self.comment.seriousness = MINOR
        self.comment.save()
        self.assertEqual(True, update_publication_score_validation_to_evaluation(self.publication.pk))
        self.assertEqual(8.5, Publication.objects.get(pk=self.publication.pk).publication_score)
        self.publication.publication_score = 8.
        self.publication.save()
        self.comment.seriousness = CRITICAL
        self.comment.save()
        self.assertEqual(True, update_publication_score_validation_to_evaluation(self.publication.pk))
        self.assertEqual(10., Publication.objects.get(pk=self.publication.pk).publication_score)

    def test_add_publication_to_user(self):
        self.assertEqual(True, add_publication_to_user(self.publication.pk))
        self.assertEqual(1, self.User.objects.get_by_natural_key(self.jesus).nb_publication)

    def test_update_user_mean_publication_score(self):
        self.publication.publication_score = 4.2
        self.publication.save()
        self.jesus.nb_publication = 1.
        self.jesus.save()
        self.assertEqual(True, update_user_mean_publication_score(self.publication.pk))
        self.assertEqual(4.2, self.User.objects.get_by_natural_key(self.jesus).mean_publication_score)

    def test_update_reviewers_score_peer_review_to_correction(self):
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True)
        self.assertEqual(True, update_reviewers_score_peer_review_to_correction(self.publication.pk))
        rael = self.User.objects.get_by_natural_key(self.rael)
        self.assertEqual(1, rael.comments_evaluated)
        self.assertEqual(0, rael.comments_not_evaluated)
        self.assertEqual(1.0, rael.reviewer_score)
        ipu = self.User.objects.get_by_natural_key(self.ipu)
        self.assertEqual(1, ipu.comments_evaluated)
        self.assertEqual(0, ipu.comments_not_evaluated)
        self.assertEqual(1.0, ipu.reviewer_score)
        fsm = self.User.objects.get_by_natural_key(self.fsm)
        self.assertEqual(0, fsm.comments_evaluated)
        self.assertEqual(1, fsm.comments_not_evaluated)
        self.assertEqual(0.0, fsm.reviewer_score)

    def test_update_reviewers_score_validation_to_evaluation(self):
        self.comment.validated = VALIDATE
        self.comment.seriousness = MAJOR
        self.comment.save()
        CommentReview.objects.create(reviewer=self.rfsm, comment=self.comment, seriousness=MINOR,
                                     reason_validation="lol", valid=True)
        CommentReview.objects.create(reviewer=self.rrael, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.ripu, comment=self.comment, seriousness=MAJOR,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        CommentReview.objects.create(reviewer=self.rft, comment=self.comment, seriousness=CRITICAL,
                                     reason_validation="lol", valid=True, corrected_date=timezone.now(),
                                     corrected=True, reason_correction="lol")
        self.assertEqual(True, update_reviewers_score_validation_to_evaluation(self.publication.pk))
        rael = self.User.objects.get_by_natural_key(self.rael)
        self.assertEqual(1, rael.comments_evaluated)
        self.assertEqual(0, rael.comments_not_evaluated)
        self.assertEqual(1.0, rael.reviewer_score)
        ipu = self.User.objects.get_by_natural_key(self.ipu)
        self.assertEqual(1, ipu.comments_evaluated)
        self.assertEqual(0, ipu.comments_not_evaluated)
        self.assertEqual(1.0, ipu.reviewer_score)
        fsm = self.User.objects.get_by_natural_key(self.fsm)
        self.assertEqual(0, fsm.comments_evaluated)
        self.assertEqual(1, fsm.comments_not_evaluated)
        self.assertEqual(0.0, fsm.reviewer_score)

    def test_update_median_impact_factor_publication_empty(self):
        self.assertEqual(False, update_median_impact_factor_publication(self.publication.pk))

    def test_update_median_impact_factor_publication_not_empty(self):
        EstimatedImpactFactor.objects.create(publication=self.publication, estimator=self.fsm,
                                             estimated_impact_factor=20.)
        EstimatedImpactFactor.objects.create(publication=self.publication, estimator=self.ipu,
                                             estimated_impact_factor=10.)
        EstimatedImpactFactor.objects.create(publication=self.publication, estimator=self.rael,
                                             estimated_impact_factor=30.)
        self.assertEqual(True, update_median_impact_factor_publication(self.publication.pk))
        publication = Publication.objects.get(pk=self.publication.pk)
        self.assertEqual(20., publication.estimated_impact_factor)

    def test_update_mean_impact_factor_users(self):
        self.publication.estimated_impact_factor = 23.
        self.publication.save()
        self.jesus.nb_publication = 1
        self.jesus.save()
        self.assertEqual(True, update_mean_impact_factor_users(self.publication.pk))
        jesus = self.User.objects.get_by_natural_key(self.jesus)
        self.assertEqual(23., jesus.mean_impact_factor)