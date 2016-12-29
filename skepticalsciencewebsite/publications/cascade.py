import statistics
from collections import Counter
from django.utils import timezone
from django.contrib.auth import get_user_model
from publications.models import Publication, Comment, Reviewer, EstimatedImpactFactor, CommentReview
from publications.constants import *


# VALIDATE COMMENT IF ENOUGH REVIEW
def update_comment_validation(comment_id):
    """
    not linked to cron
    :param comment_id:
    :return:
    """
    comment = Comment.objects.get(pk=comment_id)
    comment_reviews = CommentReview.objects.filter(comment=comment_id)
    if comment.validated == IN_PROGRESS and len(comment_reviews) == NB_REVIEWER_PER_ARTICLE:
        validation = [comment_review.valid for comment_review in comment_reviews]
        if False in validation:
            comment.validated = DISMISS
        else:
            comment.validated = VALIDATE
        seriousness_l = [comment_review.seriousness for comment_review in comment_reviews]
        seriousness, other = Counter(seriousness_l).most_common(1)[0]
        comment.seriousness = seriousness
        comment.save()
        return True
    return False


def update_comment_correction(comment_id):
    """
    not linked to cron
    :param comment_id:
    :return:
    """
    comment = Comment.objects.get(pk=comment_id)
    comment_reviews = CommentReview.objects.filter(comment=comment_id)
    correction_dates = [comment_review.corrected_date for comment_review in comment_reviews]
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
    """
    Useless for now
    :param comment_id:
    :return:
    """
    comment = Comment.objects.get(pk=comment_id)
    res_validation = update_comment_validation(comment_id)
    res_correction = False
    if comment.publication.status == VALIDATION:
        res_correction = update_comment_correction(comment_id)
    return res_validation or res_correction


# SKEPTIC SCORE
def update_user_skeptic_score(comment_id):
    """
    not linked to cron
    :param comment_id:
    :return:
    """
    comment = Comment.objects.get(pk=comment_id)
    User = get_user_model()
    user = User.objects.get(pk=comment.author.id)
    if comment.validated == VALIDATE :
        user.valid_bias_found = user.valid_bias_found + 1
    elif comment.validated == DISMISS:
        user.invalid_bias_found = user.invalid_bias_found + 1
    elif comment.validated == IN_PROGRESS:
        return False
    user.skeptic_score = user.valid_bias_found / (user.valid_bias_found + user.invalid_bias_found) * 10.
    user.save()
    return True


# PUBLICATION SCORE
def update_publication_score_peer_review_to_correction(publication_id):
    publication = Publication.objects.get(pk=publication_id)
    # correction because the publication just passed from peer review to correction
    if publication.status != CORRECTION:
        return False
    comments = Comment.objects.filter(publication=publication_id, validated=VALIDATE, comment_type=CONTENT)
    comments_seriousness = Counter([comment.seriousness for comment in comments]).most_common()
    publication_score = 10.
    for key, value in comments_seriousness:
        if key == MINOR:
            publication_score -= 1*value
        elif key == MAJOR:
            publication_score -= 2*value
        elif key == CRITICAL:
            publication_score -= 3*value
    publication_score = max(publication_score, 0.)
    publication.publication_score = publication_score
    publication.save()
    return True


def update_publication_score_validation_to_evaluation(publication_id):
    publication = Publication.objects.get(pk=publication_id)
    comments = Comment.objects.filter(publication=publication_id, validated=VALIDATE,
                                      comment_type=CONTENT, corrected=True)
    if publication.status != EVALUATION or len(comments) == 0:
        return False
    comments_seriousness = Counter([comment.seriousness for comment in comments]).most_common()
    publication_score = publication.publication_score
    for key, value in comments_seriousness:
        if key == MINOR:
            publication_score += 0.5*value
        elif key == MAJOR:
            publication_score += 1*value
        elif key == CRITICAL:
            publication_score += 2*value
    publication_score = min(publication_score, 10.)
    publication.publication_score = publication_score
    publication.save()
    return True


def add_publication_to_user(publication_id):
    """
    to do when going in validation ?
    :param publication_id:
    :return:
    """
    publication = Publication.objects.get(pk=publication_id)
    for author in publication.get_all_authors:
        author.nb_publication += 1
        author.save()
    return True


def update_user_mean_publication_score(publication_id):
    publication = Publication.objects.get(pk=publication_id)
    for author in publication.get_all_authors:
        try:
            sum_score = author.mean_publication_score*(author.nb_publication-1)
        except TypeError:
            sum_score = 0.
        sum_score += publication.publication_score
        author.mean_publication_score = sum_score/author.nb_publication
        author.save()
    return True


# REVIEWER SCORE
def update_reviewers_score_peer_review_to_correction(publication_id):
    comments = Comment.objects.filter(publication=publication_id)
    reviewers = Reviewer.objects.filter(publication=publication_id, actif=True)
    for reviewer in reviewers:
        evaluated_comments = 0
        non_evaluated_comments = 0
        User = get_user_model()
        user = User.objects.get_by_natural_key(reviewer.scientist)
        for comment in comments:
            if CommentReview.objects.filter(comment=comment, reviewer=reviewer).exists():
                evaluated_comments += 1
            else:
                non_evaluated_comments += 1
        user.comments_evaluated += evaluated_comments
        user.comments_not_evaluated += non_evaluated_comments
        user.reviewer_score = float(user.comments_evaluated)/float(user.comments_evaluated+user.comments_not_evaluated)
        user.save()
    return True


def update_reviewers_score_validation_to_evaluation(publication_id):
    comments = Comment.objects.filter(publication=publication_id, validated=VALIDATE)
    reviewers = Reviewer.objects.filter(publication=publication_id, actif=True)
    for reviewer in reviewers:
        evaluated_comments = 0
        non_evaluated_comments = 0
        User = get_user_model()
        user = User.objects.get_by_natural_key(reviewer.scientist)
        for comment in comments:
            if CommentReview.objects.filter(comment=comment, reviewer=reviewer).exclude(corrected_date=None).exists():
                evaluated_comments += 1
            else:
                non_evaluated_comments += 1
        user.comments_evaluated += evaluated_comments
        user.comments_not_evaluated += non_evaluated_comments
        user.reviewer_score = float(user.comments_evaluated) / float(user.comments_evaluated + user.comments_not_evaluated)
        user.save()
    return True


# ESTIMATED IMPACT FACTOR
def update_median_impact_factor_publication(publication_id):
    # compute with all impact factor and take the median ?
    publication = Publication.objects.get(pk=publication_id)
    estimated_impact_factors = EstimatedImpactFactor.objects.filter(publication=publication)
    estimated_impact_factors_list = [ estimated_impact_factor.estimated_impact_factor for
                                      estimated_impact_factor in estimated_impact_factors]
    try:
        publication.estimated_impact_factor = statistics.median(estimated_impact_factors_list)
    except statistics.StatisticsError:
        return False
    publication.save()
    return True


def update_mean_impact_factor_users(publication_id):
    publication = Publication.objects.get(pk=publication_id)
    for author in publication.get_all_authors:
        try:
            default_score = author.mean_impact_factor*(author.nb_publication-1) # -1 because publication added earlier
        except TypeError:
            default_score = 0.
        default_score += publication.estimated_impact_factor
        default_score = default_score/author.nb_publication
        author.mean_impact_factor = default_score
        author.save()
    return True


# ESTIMATOR SCORE (not done yet)