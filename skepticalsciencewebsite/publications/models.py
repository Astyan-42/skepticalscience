from django.db import models
from django.utils.translation import ugettext_lazy as _
from sciences.models import Science
from customuser.models import User, MinMaxFloat
# Create your models here.


class Publication(models.Model):
    # other author problem ? What to do if no account, if account ?
    first_author = models.OneToOneField(User) # or editor ?
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
    # licence


class Comment(models.Model):
    publication = models.OneToOneField(Publication)
    author = models.OneToOneField(User)
    # type = choice (content, form)
    # seriousness = choice (major, minor, critical)
    content = models.CharField(max_length=8192, blank=False, verbose_name=_("Publication comment"))
    validated = models.BooleanField(default=False)
    # constrainte : must be on the same publication
    validators = models.ManyToManyField(Reviewer, blank=True, verbose_name=_("Validator"))
    # corrected = choice (yes, no)
    # same licence as publication (forced ?)


class Reviewer(models.Model):
    scientist = models.OneToOneField(User)
    publication = models.OneToOneField(Publication)
