from django.db import models

# Create your models here.
class Science(models.Model):
    name = models.CharField(verbose_name="Name",
                            max_length=255,
                            unique=True)
    description = models.CharField(verbose_name="Description",
                                   max_length=2048,
                                   unique=True)
    subscience = models.ManyToManyField("self",
                                        blank=True)

    def __str__(self):
        return self.name