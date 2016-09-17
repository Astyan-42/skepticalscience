from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from sciences.models import Science
from customuser.models import User, MinMaxFloat


sendfile_storage = FileSystemStorage(location=settings.SENDFILE_ROOT)
# Create your models here.


PUBLICATION_STATUS = [("", "All status"),
                      ("waiting_payment", "Waiting payment"),
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
    """
    Legal licence Model
    """
    short_name = models.CharField(max_length=64, blank=False, verbose_name=_("Short name"))
    full_name = models.CharField(max_length=255, blank=False, verbose_name=_("Full name"))
    url = models.URLField(max_length=255, blank=False, verbose_name=_("URL"))

    def __str__(self):
        return self.short_name


class Publication(models.Model):
    """
    Publication Model. Need the author
    """
    # other author problem ? What to do if no account, if account ?
    editor = models.ForeignKey(User, verbose_name=_('Editor'))
    #create the publication before paying for
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    payment_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name=_('Payment date'))
    validation_date = models.DateTimeField(null=True, blank=True, default=None, verbose_name=_('Validation date'))
    sciences = models.ManyToManyField(Science, blank=True, symmetrical=False, verbose_name=_("Sciences"))
    title = models.CharField(max_length=255, blank=False, verbose_name=_("Title"))
    publication_score = MinMaxFloat(min_value=0.0, max_value=10.0, default=None, null=True, blank=True,
                                    verbose_name=_("Publication score"))
    estimated_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, default=None, null=True, blank=True,
                                          verbose_name=_("Estimated impact factor"))
    # authors ????
    first_author = models.ForeignKey(User, related_name='first_author', verbose_name=_("First author"))
    authors = models.ManyToManyField(User, blank=True, related_name='authors', verbose_name=_("Authors"))
    last_author = models.ForeignKey(User, blank=True, null=True, related_name='last_author',
                                    verbose_name=_("First author"))
    # the pdf file at the creation
    pdf_creation = models.FileField(upload_to="pdf_creation/%Y/%m/%d", storage=sendfile_storage,
                                    verbose_name=_("Publication draft (PDF)"))
    source_creation = models.FileField(upload_to="source_creation/%Y/%m/%d", storage=sendfile_storage,
                                       verbose_name=_("Publication draft (sources)"))
    pdf_final = models.FileField(upload_to="pdf_final/%Y/%m/%d", storage=sendfile_storage, null=True, blank=True,
                                 verbose_name=_("Publication final (pdf)"))
    source_final = models.FileField(upload_to="source_final/%Y/%m/%d", storage=sendfile_storage, null=True, blank=True,
                                    verbose_name=_("Publication final (sources)"))
    resume = models.CharField(max_length=1024, blank=False, verbose_name=_("Resume"))
    status = models.CharField(choices=PUBLICATION_STATUS, max_length=100, db_index=True, default="waiting_payment",
                              verbose_name=_('Status'))
    # or just resume ?
    # tags = models.ManyToManyField(KeyWord, blank= False, symmetrical=False, verbose_name=_("Keywords"))
    licence = models.ForeignKey(Licence, verbose_name=_("Licence"))
    history = HistoricalRecords()

    def get_all_authors(self):
        authors = [self.first_author] + [author for author in self.authors.all()] + \
                  [author for author in [self.last_author] if author is not None]
        return authors

    def __str__(self):
        return self.title


class EstimatedImpactFactor(models.Model):
    """
    EstimatedImpactFactor Model
    """
    #must be in researcher group and have a related sciences
    estimator = models.ForeignKey(User, verbose_name=_('Estimator'))
    publication = models.ForeignKey(Publication, verbose_name=_('Publication'))
    estimated_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, verbose_name=_("Estimated impact factor"))

    def __str__(self):
        return self.estimator


class Reviewer(models.Model):
    """
    Reviewer Model
    """
    scientist = models.ForeignKey(User, verbose_name=_("Reviewer"))
    publication = models.ForeignKey(Publication, verbose_name=_("Publication"))

    def __str__(self):
        return self.scientist.get_full_name()


class Comment(models.Model):
    """
    Comment model
    """
    publication = models.ForeignKey(Publication, verbose_name=_("Publication"))
    author = models.ForeignKey(User, verbose_name=_("Author"))
    # fake pseudo when reviewer must be reviewer (fake pseudo given automatically between: Reviewer, Scientist, Skeptic)
    author_fake_pseudo = models.CharField(max_length=100, default=None, blank=True, verbose_name=_('Fake Pseudo'))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    comment_type = models.CharField(choices=COMMENT_ON, max_length=100, db_index=True, verbose_name=_("Comment type"))
    seriousness = models.CharField(choices=SERIOUSNESS_STATUS, max_length=100, db_index=True, blank=True,
                                   verbose_name=_("Seriousness"))
    content = models.CharField(max_length=8192, blank=False, verbose_name=_("Publication comment"))
    title = models.CharField(max_length=255, blank=False, verbose_name=_("Title"))
    validated = models.BooleanField(default=False, verbose_name=_("Validated"))
    corrected = models.BooleanField(default=False, verbose_name=_("Corrected"))
    licence = models.ForeignKey(Licence, verbose_name=_("Licence"))

    def __str__(self):
        return self.title


class CommentRating(models.Model):
    """
     when done must check if every other reviewer have already done it
    """
    reviewer = models.ForeignKey(Reviewer, verbose_name=_("Reviewer"))
    comment = models.ForeignKey(Comment, verbose_name=_("Comment"))
    valid = models.BooleanField(default=False, verbose_name=_("Valid"))
    seriousness = models.CharField(choices=SERIOUSNESS_STATUS, max_length=100, db_index=True, blank=True,
                                   verbose_name=_("Seriousness"))
    reason_validation = models.CharField(max_length=8192, blank=False, verbose_name=_("Reason of (in)validation"))
    corrected = models.BooleanField(default=False, verbose_name=_("Corrected"))

    def clean(self):
        if self.reviewer.publication != self.comment.publication:
            raise ValidationError('You are not a reviewer of this publication. Therefor You cannot rate this comment')