from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from sciences.models import Science
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
import re
# Create your models here.

sendfile_storage = FileSystemStorage(location=settings.SENDFILE_ROOT, base_url=settings.SENDFILE_URL)


class MinMaxFloat(models.FloatField):
    """
    Change the parameter of FloatField to be able to use limit
    """
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        """
        The init fuction of our MinMaxFloat
        :param min_value: the minimal value
        :type min_value: float
        :param max_value: the maximal value
        :type max_value: float
        :param args: the rest of the arguments to pass to the FloatField
        :param kwargs: the rest of the named arguments to pass to the FloatField
        """
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)


class User(AbstractUser):
    """
    Our User class, can represent a skeptic, a great skeptic or a researcher
    """
    # all user name except if it start with skeptic, author or researcher
    username = models.CharField(max_length=255, unique=True, verbose_name=_("Username"),
                                validators=[RegexValidator(regex="^(skeptic|author|researcher|reviewer).*$",
                                                           message=_("please enter a valid username \
                                                           (not skepic, author, researcher)"),
                                                           inverse_match=True,
                                                           flags=re.IGNORECASE)])
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    # is_active to True during the tests to don't have the email registration
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True, verbose_name=_("First Name"))
    middle_name = models.CharField(max_length=255, blank=True, verbose_name=_("Middle Name"))
    last_name = models.CharField(max_length=255, blank=True, verbose_name=_("Last Name"))
    country = models.CharField(max_length=255, blank=True, verbose_name=_("Country"))
    workplace = models.CharField(max_length=255, blank=True, verbose_name=_("Workplace"))
    description = models.CharField(max_length=1024, blank=True, verbose_name=_("Personal description"))
    job_title = models.CharField(max_length=255, blank=True, verbose_name=_("Job title"))
    sciences = models.ManyToManyField(Science, blank=True, symmetrical=False, verbose_name=_("Sciences liked"),
                                      related_name="sciences_liked")
    # finding biais in publication : or number of valid biais foud and number of ivalid biais found ?
    valid_bias_found = models.IntegerField(default=0, verbose_name=_("Valid bias found"))
    invalid_bias_found = models.IntegerField(default=0, verbose_name=_("Invalid bias found"))
    skeptic_score = MinMaxFloat(min_value=0.0, max_value=10.0, default=None, null=True, blank=True,
                                verbose_name=_("Skeptic score"))
    # publish without biais
    nb_publication = models.IntegerField(default=0, verbose_name=_("Number of publication"))
    mean_publication_score = MinMaxFloat(min_value=0.0, max_value=10.0, default=None, null=True, blank=True,
                                         verbose_name=_("Mean publication score"))
    # mean estimated impact factor
    mean_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, default=None, null=True, blank=True,
                                     verbose_name=_("Mean impact factor"))
    # estimator score (when estimate the impact factor of a publication make good estimation)
    estimator_score = MinMaxFloat(min_value=0.0, max_value=1.0, default=None, null=True, blank=True,
                                  verbose_name=_("Estimator Score"))
    # reviewer score to add
    comments_evaluated = models.IntegerField(default=0, verbose_name=_("Comments evaluated"))
    comments_not_evaluated = models.IntegerField(default=0, verbose_name=_("Comments not evaluated"))
    reviewer_score = MinMaxFloat(min_value=0.0, max_value=1.0, default=None, null=True, blank=True,
                                 verbose_name=_("Reviewer score"))
    phd = models.BooleanField(default=False, verbose_name=_("PHD"))
    phd_image = models.ImageField(upload_to="PHDs/%Y/%m/%d", null=True, blank=True, storage=sendfile_storage,
                                  verbose_name=_("PHD"))
    phd_comment = models.CharField(max_length=1024, blank=True, verbose_name=_("PHD comment"))
    phd_update_date = models.DateField(blank=True, null=True, verbose_name=_('PHD update date'))
    phd_rate_date = models.DateField(blank=True, null=True, verbose_name=_('PHD rate date'))
    phd_in = models.ManyToManyField(Science, blank=True, symmetrical=False, verbose_name=_("PHD in"),
                                    related_name="phd_sciences")

    def to_rate(self):
        return (self.phd_rate_date is None or self.phd_rate_date <= self.phd_update_date) and (self.phd_image is not None and self.phd is False)

    def print_phd_sciences(self):
        return self.phd

    def print_phd_non_accepted(self):
        return self.phd_rate_date is not None and self.phd == False

    def get_full_name(self):
        full_name = str(self.last_name)+" "+str(self.middle_name)+" "+str(self.first_name)
        full_name = ' '.join(full_name.split())
        return full_name
