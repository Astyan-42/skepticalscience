"""
Django settings for skepticalsciencewebsite project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')5#l@il%$!sjh9^f&5zzt5xr869&o6a5-q$i3b(lhe5h(oz#49'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'django_select2',
    'crispy_forms',
    'django_filters',
    'django_tables2',
    'sendfile',
    'sciences',
    'customuser',
    'publications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skepticalsciencewebsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'skepticalsciencewebsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Auth user model
AUTH_USER_MODEL = "customuser.User"

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATIC_URL = '/static/'

#sendfile settings
SENDFILE_BACKEND = 'sendfile.backends.development'
SENDFILE_ROOT = os.path.join(BASE_DIR, 'media')
SENDFILE_URL = '/media/'

# Registration settings
REGISTRATION_OPEN = True                # If True, users can register
ACCOUNT_ACTIVATION_DAYS = 7     # One-week activation window; you may, of course, use a different value.
REGISTRATION_SALT = "github"
# REGISTRATION_AUTO_LOGIN = True  # If True, the user will be automatically logged in.
LOGIN_REDIRECT_URL = '/accounts/login/'  # The page you want users to arrive at after they successful log in
LOGIN_URL = '/accounts/login/'  # The page users are directed to if they are not logged in,

# Email
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/djangomail/'
EMAIL_SUBJECT_PREFIX = "[DjangoTest] "
EMAIL_TIMEOUT = 3
EMAIL_HOST_USER = "fakeuser@fakeemail.com"

# Bootstrap3 module setting
BOOTSTRAP3 = {
    # The URL to the jQuery JavaScript file
    'jquery_url': "//code.jquery.com/jquery.min.js",
    # The Bootstrap base URL
    'base_url': "//netdna.bootstrapcdn.com/bootstrap/3.3.6",
    # The complete URL to the Bootstrap CSS file (None means derive it from base_url)
    'css_url': None,
    # The complete URL to the Bootstrap CSS file (None means no theme)
    'theme_url': None,
    # The complete URL to the Bootstrap JavaScript file (None means derive it from base_url)
    'javascript_url': None,
    # Put JavaScript in the HEAD section of the HTML document (only relevant if you use bootstrap3.html)
    'javascript_in_head': False,
    # Include jQuery with Bootstrap JavaScript (affects django-bootstrap3 template tags)
    'include_jquery': True,
    # Label class to use in horizontal forms
    'horizontal_label_class': 'col-md-3',
    # Field class to use in horizontal forms
    'horizontal_field_class': 'col-md-9',
    # Set HTML required attribute on required fields
    'set_required': True,
    # Set HTML disabled attribute on disabled fields
    'set_disabled': False,
    # Set placeholder attributes to label if no placeholder is provided
    'set_placeholder': True,
    # Class to indicate required (better to set this in your Django form)
    'required_css_class': '',
    # Class to indicate error (better to set this in your Django form)
    'error_css_class': 'has-error',
    # Class to indicate success, meaning the field has valid input (better to set this in your Django form)
    'success_css_class': 'has-success',
    # Renderers (only set these if you have studied the source and understand the inner workings)
    'formset_renderers': {
        'default': 'bootstrap3.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'bootstrap3.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap3.renderers.FieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
    },
}

SELECT2_CSS = '/static/css/select2.css'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

