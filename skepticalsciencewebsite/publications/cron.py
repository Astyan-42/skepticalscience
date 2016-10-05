from django.utils import timezone
from django_cron import CronJobBase, Schedule
from publications.models import Publication, Reviewer
from publications.cascade import (update_reviewers_score_peer_review_to_correction,
                                  update_publication_score_peer_review_to_correction,
                                  add_publication_to_user,
                                  update_reviewers_score_validation_to_evaluation,
                                  update_user_mean_publication_score,
                                  update_median_impact_factor_publication,
                                  update_mean_impact_factor_users)

from publications.constants import *


# should transform the code to be DRY
class PublicationUpdateCronJob(CronJobBase):
    RUN_EVERY_MINS = 360 # every 6 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'publications.publication_update_cron_job'    # a unique code
    MIN_NUM_FAILURES = 5

    def update_adding_peer_to_peer_review(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= ADDING_PEER_DAYS:
                reviewers = Reviewer.objects.filter(publication=publication.id, actif=True)
                if len(reviewers) == NB_REVIEWER_PER_ARTICLE:
                    publication.status = PEER_REVIEW
                    publication.update_status_date = timezone.now()
                    publication.save()

    def update_peer_review_to_correction(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= PEER_REVIEW_DAYS:
                publication.status = CORRECTION
                publication.update_status_date = timezone.now()
                publication.save()
                update_reviewers_score_peer_review_to_correction(publication.pk)
                update_publication_score_peer_review_to_correction(publication.pk)

    def update_correction_to_validation(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= CORRECTION_DAYS:
                if publication.pdf_final is not None and publication.source_final is not None:
                    publication.status = VALIDATION
                    publication.update_status_date = timezone.now()
                    publication.save()
                    add_publication_to_user(publication.pk)

    def update_validation_to_evaluation(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= VALIDATION_DAYS:
                publication.status = EVALUATION
                publication.update_status_date = timezone.now()
                publication.save()
                update_reviewers_score_validation_to_evaluation(publication.pk)
                update_user_mean_publication_score(publication.pk)

    def update_evaluation_to_published(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= EVALUATION_DAYS:
                if update_median_impact_factor_publication(publication.pk):
                    publication.status = PUBLISHED
                    publication.update_status_date = timezone.now()
                    publication.save()
                    update_mean_impact_factor_users(publication.pk)

    def do(self):
        self.update_adding_peer_to_peer_review(Publication.objects.filter(status=ADDING_PEER))
        self.update_peer_review_to_correction(Publication.objects.filter(status=PEER_REVIEW))
        self.update_correction_to_validation(Publication.objects.filter(status=CORRECTION))
        self.update_validation_to_evaluation(Publication.objects.filter(status=VALIDATION))
        self.update_evaluation_to_published(Publication.objects.filter(status=EVALUATION))
