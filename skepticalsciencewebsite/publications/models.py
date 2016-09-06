from django.db import models
from django.utils.translation import ugettext_lazy as _
from sciences.models import Science
from customuser.models import User, MinMaxFloat
# Create your models here.


PUBLICATION_STATUS = [("waiting_payment", "Waiting payment"),
                      ("adding_peer", "Adding peer"),
                      ("peer_review", "Peer review"),
                      ("correction", "Correction"),
                      ("validation", "Validation"),
                      ("evaluation", "Evaluation"),
                      ("published", "Published"),
                      ("aborted", "Aborted")]


SERIOUSNESS_STATUS = [("minor", "Minor"),
                      ("major", "Major"),
                      ("critical", "Critical")]


COMMENT_ON = [("form", "Form"),
              ("content", "Content")]


class Licence(models.Model):
    short_name = models.CharField(max_length=64, blank=False, verbose_name=_("Short name"))
    full_name = models.CharField(max_length=255, blank=False, verbose_name=_("Full name"))
    url = models.URLField(max_length=255, blank=False, verbose_name=_("URL"))

    def __str__(self):
        return self.short_name


class KeyWord(models.Model):
    tag = models.CharField(max_length=64, blank=False, verbose_name=_("Keyword"))

    def __str__(self):
        return self.tag


class Publication(models.Model):
    # other author problem ? What to do if no account, if account ?
    editor = models.OneToOneField(User, verbose_name=_('Editor'))
    #create the publication before paying for
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    payment_date = models.DateTimeField(null=True, default=None, verbose_name=_('Payment date'))
    validation_date = models.DateTimeField(null=True, default=None, verbose_name=_('Validation date'))
    sciences = models.ManyToManyField(Science, blank=False, symmetrical=False, verbose_name=_("Sciences"))
    title = models.CharField(max_length=255, blank=False, verbose_name=_("Title"))
    publication_score = MinMaxFloat(min_value=0.0, max_value=10.0, default=None,
                                    verbose_name=_("Publication score"))
    estimated_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, default=None,
                                          verbose_name=_("Estimated impact factor"))
    # authors
    # resume
    # the pdf file at the creation
    # the source file at the creation
    # the pdf file after validation
    # the source file after validation
    status = models.CharField(choices=SERIOUSNESS_STATUS, max_length=100, db_index=True, default="pending_payment",
                              verbose_name=_('Status'))
    tags = models.ManyToManyField(KeyWord, blank= False, symmetrical=False, verbose_name=_("Keywords"))
    licence = models.OneToOneField(Licence, verbose_name=_("Licence"))

    def __str__(self):
        return self.title


class EstimatedImpactFactor(models.Model):
    #must be in researcher group and have a related sciences
    estimator = models.OneToOneField(User, verbose_name=_('Estimator'))
    publication = models.OneToOneField(Publication, verbose_name=_('Publication'))
    estimated_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, verbose_name=_("Estimated impact factor"))

    def __str__(self):
        return self.estimator


class Reviewer(models.Model):
    scientist = models.OneToOneField(User, verbose_name=_("Reviewer"))
    publication = models.OneToOneField(Publication, verbose_name=_("Publication"))

    def __str__(self):
        return self.scientist

class Comment(models.Model):
    publication = models.OneToOneField(Publication, verbose_name=_("Publication"))
    author = models.OneToOneField(User, verbose_name=_("Author"))
    # fake pseudo when reviewer must be reviewer (fake pseudo given automatically between: Reviewer, Scientist, Skeptic)
    author_fake_pseudo = models.CharField(max_length=100, default=None, verbose_name=_('Fake Pseudo'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    comment_type = models.CharField(choices=COMMENT_ON, max_length=100, db_index=True, verbose_name=_("Comment type"))
    seriousness = models.CharField(choices=SERIOUSNESS_STATUS, max_length=100, db_index=True,
                                   verbose_name=_("Seriousness"))
    content = models.CharField(max_length=8192, blank=False, verbose_name=_("Publication comment"))
    title = models.CharField(max_length=255, blank=False, verbose_name=_("Title"))
    #is validate by the 4 reviewers
    validated = models.BooleanField(default=False, verbose_name=_("Validated"))
    # constrainte : must be on the same publication
    validators = models.ManyToManyField(Reviewer, blank=True, verbose_name=_("Validator"))
    # if the mistake pointed by the comment has been corrected
    corrected = models.BooleanField(default=False, verbose_name=_("Corrected"))
    licence = models.OneToOneField(Licence, verbose_name=_("Licence"))

    def __str__(self):
        return self.title
