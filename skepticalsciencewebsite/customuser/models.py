from django.db import models
from sciences.models import Science
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# Create your models here.


class MinMaxFloat(models.FloatField):
    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(MinMaxFloat, self).__init__(*args, **kwargs)


class UserManager(BaseUserManager):

    def create_user(self, username, password, **kwargs):
        user = self.model(
            username=self.normalize_username(username),
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **kwargs):
        user = self.model(
            username=username,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, verbose_name="Username")
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True, verbose_name="First Name")
    middle_name = models.CharField(max_length=255, blank=True, verbose_name="Middle Name")
    last_name = models.CharField(max_length=255, blank=True, verbose_name="Last Name")
    phd = models.BooleanField(default=False)
    country = models.CharField(max_length=255, blank=True, verbose_name="Country")
    register_date = models.DateField(auto_now_add=True)
    workplace = models.CharField(max_length=255, blank=True, verbose_name="Workplace")
    description = models.CharField(max_length=1024, blank=True, verbose_name="Personnal description")
    job_title = models.CharField(max_length=255, blank=True, verbose_name="Job title")
    sciences = models.ManyToManyField(Science, blank=True, symmetrical=False, verbose_name="Sciences")
    # finding biais in publication : or number of valid biais foud and number of ivalid biais found ?
    valid_biais_found = models.IntegerField(default=0, verbose_name="Valid biais found")
    invalid_biais_found = models.IntegerField(default=0, verbose_name="Invalid biais found")
    skeptic_score = MinMaxFloat(min_value=0.0, max_value=10.0, default=0.0, verbose_name="Skeptic score")
    # publish without biais
    mean_publication_score = MinMaxFloat(min_value=0.0, max_value=10.0, default=0.0,
                                         verbose_name="Mean publication score")
    # mean estimated impact factor
    mean_impact_factor = MinMaxFloat(min_value=0.0, max_value=1000.0, default=0.0, verbose_name="Mean impact factor")
    # estimator score (when estimate the impact factor of a publication make good estimation)
    estimator_score = MinMaxFloat(min_value=0.0, max_value=1.0, default=0.0, verbose_name="Estimator Score")
    USERNAME_FIELD = 'username'
    object = UserManager()

    # temporary to avoid any problem. Should contain the real name
    def get_full_name(self):
        return self.get_username()

    def get_short_name(self):
        return self.get_username()
