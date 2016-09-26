from django.utils import timezone
from django_cron import CronJobBase, Schedule
from publications.models import Publication, Reviewer
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
                # modification of the reviewer score (number of comment rated, number of comment not rated) (validated)
                # modification of the publication score

    def update_correction_to_validation(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= CORRECTION_DAYS:
                if publication.pdf_final is not None and publication.source_final is not None:
                    publication.status = VALIDATION
                    publication.update_status_date = timezone.now()
                    publication.save()

    def update_validation_to_evaluation(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= VALIDATION_DAYS:
                publication.status = EVALUATION
                publication.update_status_date = timezone.now()
                publication.save()
                # modification of the reviewer score (number of comment rated, number of comment not rated) (corrected)
                # modification of the publication score of all authors (also in peer review to correction ?)

    def update_evaluation_to_published(self, publications):
        for publication in publications:
            if (timezone.now() - publication.update_status_date).days >= EVALUATION_DAYS:
                # update the estimated impact factor of the publication
                publication.status = PUBLISHED
                publication.update_status_date = timezone.now()
                publication.save()
                # modification of the estimated impact factor of all author

    def do(self):
        self.update_adding_peer_to_peer_review(Publication.objects.filter(status=ADDING_PEER))
        self.update_peer_review_to_correction(Publication.objects.filter(status=PEER_REVIEW))
        self.update_correction_to_validation(Publication.objects.filter(status=CORRECTION))
        self.update_validation_to_evaluation(Publication.objects.filter(status=VALIDATION))
        self.update_evaluation_to_published(Publication.objects.filter(status=EVALUATION))
