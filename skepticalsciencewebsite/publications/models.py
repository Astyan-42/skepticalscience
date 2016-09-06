from django.db import models
from django.utils.translation import ugettext_lazy as _
from sciences.models import Science
from customuser.models import User, MinMaxFloat
# Create your models here.


PUBLICATION_STATUS = [("adding_peer", "Adding peer"),
                      ("peer_review", "Peer review"),
                      ("correction", "Correction"),
                      ("validation", "Validation"),
                      ("evaluation", "Evaluation"),
                      ("published", "Published")]


SERIOUSNESS_STATUS = [("minor", "Minor"),
                      ("major", "Major"),
                      ("critical", "Critical")]


COMMENT_ON = [("form", "Form"),
              ("content", "Content")]


class Licence(models.Model):
    short_name = models.CharField(max_length=64, blank=False, verbose_name=_("Short name"))
    full_name = models.CharField(max_length=255, blank=False, verbose_name=_("Full name"))
    url = models.URLField(max_length=255, blank=False, verbose_name=_("URL"))


class EstimatedImpactFactor(models.Model):
    #must be in researcher group and have a related sciences
    scientist = models.OneToOneField(User)
    publication = models.OneToOneField(Publication)
    estimated_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, verbose_name=_("Estimated impact factor"))


class Publication(models.Model):
    # other author problem ? What to do if no account, if account ?
    editor = models.OneToOneField(User) # or editor ?
    creation_date = models.DateTimeField()
    validation_date = models.DateTimeField()
    sciences = models.ManyToManyField(Science, blank=False, symmetrical=False, verbose_name=_("Sciences"))
    # the pdf file at the creation
    # the source file at the creation
    # the pdf file after validation
    # the source file after validation
    # estimated impact factor
    # publication score
    # status = choice
    # tags
    licence = models.OneToOneField(Licence)


class Comment(models.Model):
    publication = models.OneToOneField(Publication)
    author = models.OneToOneField(User)
    comment_type = models.CharField(choices=COMMENT_ON, max_length=100, db_index=True)
    seriousness = models.CharField(choices=SERIOUSNESS_STATUS, max_length=100, db_index=True)
    content = models.CharField(max_length=8192, blank=False, verbose_name=_("Publication comment"))
    #is validate by the 4 reviewers
    validated = models.BooleanField(default=False)
    # constrainte : must be on the same publication
    validators = models.ManyToManyField(Reviewer, blank=True, verbose_name=_("Validator"))
    # if the mistake pointed by the comment has been corrected
    corrected = models.BooleanField(default=False)
    licence = models.OneToOneField(Licence)


class Reviewer(models.Model):
    scientist = models.OneToOneField(User)
    publication = models.OneToOneField(Publication)
