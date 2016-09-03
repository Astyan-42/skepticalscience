from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class Science(models.Model):
    """
    The Science model
    :param name: the name of the science field
    :type name: str
    :param description: the description of the science field
    :type description: str
    :param primary_science: True if the science is primary (like chemistry, biology, medicine, ...),
    False if the science is not primary (live proteomic, microbiology, ...)
    :type primary_science: bool
    :param sub_science: a list of sub sciences for chemistry => (proteomic, quantic chemistry, ...)
    :type sub_science: list
    """
    name = models.CharField(verbose_name=_("Name"), max_length=255, unique=True)
    description = models.CharField(verbose_name=_("Description"), max_length=2048, unique=True)
    primary_science = models.BooleanField(default=False)
    sub_science = models.ManyToManyField("self", blank=True, symmetrical=False)

    def __str__(self):
        """
        The ways a science object must be seen is from is name
        :return: the name of the science object
        :rtype: str
        """
        return self.name
