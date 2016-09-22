from publications.models import Publication, Comment, Reviewer, EstimatedImpactFactor, CommentReview
from publications.constants import *


def update_comment(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if comment.validated != IN_PROGRESS and comment.corrected_date is not None:
        return False
    comment_review = CommentReview.objects.filter(comment=comment_id)
    if comment_review != NB_REVIEWER_PER_ARTICLE:
        return False


