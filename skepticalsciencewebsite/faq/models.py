from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class Topic(models.Model):

    name = models.CharField(verbose_name=_("Topic"), max_length=255, unique=True)

    def __str__(self):
        return self.name


class QandA(models.Model):

    topic = models.ForeignKey(Topic)
    question = models.CharField(verbose_name=_("Question"), max_length=255, unique=True)
    answer = models.CharField(verbose_name=_("Answer"), max_length=1024, unique=True)

    def __str__(self):
        return self.question