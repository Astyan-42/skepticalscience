from django.db import models

# Create your models here.
class Science(models.Model):
    name = models.CharField(verbose_name="Name",
                            max_length=255,
                            unique=True)
    description = models.CharField(verbose_name="Description",
                                   max_length=2048,
                                   unique=True)
    primary_science = models.BooleanField(default=False)
    sub_science = models.ManyToManyField("self",
                                         blank=True,
                                         symmetrical=False)

    def __str__(self):
        return self.name