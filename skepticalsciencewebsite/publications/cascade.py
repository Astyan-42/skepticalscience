from collections import Counter
from django.utils import timezone
from customuser.models import User
from publications.models import Publication, Comment, Reviewer, EstimatedImpactFactor, CommentReview
from publications.constants import *


def update_comment_validation(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    comment_reviews = CommentReview.objects.filter(comment=comment_id)
    if comment.validated == IN_PROGRESS and len(comment_reviews) == NB_REVIEWER_PER_ARTICLE:
        validation = [comment_review.valid for comment_review in comment_reviews]
        if False in validation:
            comment.validated = DISMISS
        else:
            comment.validated = VALIDATE
        seriousness_l = [comment_review.seriousness for comment_review in comment_reviews]
        seriousness, = Counter(seriousness_l).most_common(1)[0]
        comment.seriousness = seriousness
        comment.save()
        return True
    return False


def update_comment_correction(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    comment_reviews = CommentReview.objects.filter(comment=comment_id)
    correction_dates = [comment_review.corrected for comment_review in comment_reviews]
    if None not in correction_dates and comment.validated == VALIDATE:
        corrections = [comment_review.corrected for comment_review in comment_reviews]
        comment.corrected_date = timezone.now()
        if False in corrections:
            comment.corrected = False
        else:
            comment.corrected = True
        comment.save()
        return True
    return False


def update_comment(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    res_validation = update_comment_validation(comment_id)
    res_correction = False
    if comment.publication.status == VALIDATION:
        res_correction = update_comment_correction(comment_id)
    return (res_validation and res_correction)


def update_user_skeptic_score(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    user = User.objects.get(comment.author.id)
    if comment.validated:
        user.valid_bias_found = user.valid_bias_found + 1
    else:
        user.invalid_bias_found = user.invalid_bias_found + 1
    user.skeptic_score = user.valid_bias_found / (user.valid_bias_found + user.invalid_bias_found) * 10.
    user.save()
    return True


def update_user_mean_publication_score(publication_id):
    pass


def update_mean_impact_factor(publication_id):
    pass


