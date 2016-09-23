from django_cron import CronJobBase, Schedule


class PublicationUpdateCronJob(CronJobBase):
    RUN_EVERY_MINS = 360 # every 6 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'publications.publication_update_cron_job'    # a unique code

    def do(self):
        pass    # do your thing here
