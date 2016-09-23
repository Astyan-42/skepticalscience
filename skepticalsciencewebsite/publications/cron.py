from django_cron import CronJobBase, Schedule
from publications.models import Publication
from publications.constants import *


class PublicationUpdateCronJob(CronJobBase):
    RUN_EVERY_MINS = 360 # every 6 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'publications.publication_update_cron_job'    # a unique code

    def update_adding_peer_to_peer_review(self, publications):
        # check if there is enough reviewer (and 1 week) then change the status
        pass

    def update_peer_review_to_correction(self, publications):
        # check the time period is over 3 week ?then change the status and update the users
        pass

    def update_correction_to_validation(self, publications):
        # check if the period is over 3 week ? then change the status
        pass

    def update_validation_to_evaluation(self, publications):
        # check if the period is over 1 week ? then change the status
        pass

    def update_evaluation_to_published(self, publications):
        # check if the period is over 1 week ? then change the status
        pass

    def do(self):
        self.update_adding_peer_to_peer_review(Publication.objects.filter(status=ADDING_PEER))
        self.update_peer_review_to_correction(Publication.objects.filter(status=PEER_REVIEW))
        self.update_correction_to_validation(Publication.objects.filter(status=CORRECTION))
        self.update_validation_to_evaluation(Publication.objects.filter(status=VALIDATION))
        self.update_evaluation_to_published(Publication.objects.filter(status=EVALUATION))
