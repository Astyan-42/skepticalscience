import statistics
from collections import Counter
from django.utils import timezone
from customuser.models import User
from publications.models import Publication, Comment, Reviewer, EstimatedImpactFactor, CommentReview
from publications.constants import *


# VALIDATE COMMENT IF ENOUGH REVIEW
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
    return res_validation and res_correction


# SKEPTIC SCORE
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


# PUBLICATION SCORE
def update_publication_score_peer_review(publication_id):
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
    publication = Publication.objects.get(publication=publication_id)
    if comments.exists():
        publication.publication_score = publication_score
        publication.save()
        return True
    else:
        return False


def update_publication_score_validation(publication_id):
    comments = Comment.objects.filter(publication=publication_id, validated=VALIDATE,
                                      comment_type=CONTENT, corrected=True)
    comments_seriousness = Counter([comment.seriousness for comment in comments]).most_common()
    publication = Publication.objects.get(publication=publication_id)
    publication_score = publication.publication_score
    for key, value in comments_seriousness:
        if key == MINOR:
            publication_score += 0.5*value
        elif key == MAJOR:
            publication_score += 1*value
        elif key == CRITICAL:
            publication_score += 2*value
    publication_score = min(publication_score, 10.)
    if comments.exists():
        publication.publication_score = publication_score
        publication.save()
        return True
    else:
        return False


def update_user_mean_publication_score(publication_id):
    publication = Publication.objects.get(pk=publication_id)
    for author in publication.get_all_authors:
        sum_score = author.mean_publication_score*author.nb_publication
        sum_score += publication.publication_score
        author.nb_publication += 1
        author.mean_publication_score = sum_score/author.nb_publication
        author.save()
    return True


# REVIEWER SCORE
def update_reviewers_score_peer_review(publication_id):
    comments = Comment.objects.filter(publication=publication_id)
    reviewers = Reviewer.objects.filter(publication=publication_id, actif=True)
    for reviewer in reviewers:
        evaluated_comments = 0
        non_evaluated_comments = 0
        user = User.objects.get(pk=reviewer.scientist)
        for comment in comments:
            if CommentReview.objects.filter(comment=comment).exists():
                evaluated_comments += 1
            else:
                non_evaluated_comments += 1
        user.comments_evaluated += evaluated_comments
        user.comments_not_evaluated += non_evaluated_comments
        user.reviewer_score = float(user.comments_evaluated)/float(user.comments_evaluated+user.comments_not_evaluated)
        user.save()
    return True


def update_reviewers_score_validation(publication_id):
    comments = Comment.objects.filter(publication=publication_id, validated=VALIDATE)
    reviewers = Reviewer.objects.filter(publication=publication_id, actif=True)
    for reviewer in reviewers:
        evaluated_comments = 0
        non_evaluated_comments = 0
        user = User.objects.get(pk=reviewer.scientist)
        for comment in comments:
            if CommentReview.objects.filter(comment=comment).exclude(corrected_date=None).exists():
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
    estimated_impact_factors = EstimatedImpactFactor(publication=publication_id)
    estimated_impact_factors_list = [ estimated_impact_factor.estimated_impact_factor for
                                      estimated_impact_factor in estimated_impact_factors]
    publication.estimated_impact_factor =  statistics.median(estimated_impact_factors_list)
    publication.save()
    return True


def update_mean_impact_factor_users(publication_id):
    publication = Publication.objects.get(pk=publication_id)
    for author in publication.get_all_authors:
        default_score = author.mean_impact_factor*(author.nb_publication-1) # -1 because publication score
        default_score += publication.mean_impact_factor
        default_score = default_score/author.nb_publication
        author.mean_publication_score = default_score
        author.save()
    return True


# ESTIMATOR SCORE (not done yet)