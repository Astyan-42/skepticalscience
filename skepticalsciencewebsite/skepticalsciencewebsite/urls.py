"""skepticalsciencewebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import TemplateView


# internationalization http://www.marinamele.com/taskbuster-django-tutorial/internationalization-localization-languages-time-zones

urlpatterns = [
    url(r'^select2/', include('django_select2.urls')),
]

urlpatterns += i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('customuser.urls')),
    # https://github.com/incuna/django-registration/blob/master/registration/urls.py under accounts
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^faq/', include('faq.urls')),
    url(r'^checkout/', include('custompayment.urls')),
    url('^checkout/', include('payments.urls')),
    url(r'^publications/', include('publications.urls')),
    url(r'^invoice/', include('pdfinvoce.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="index"),
    url(r'^legal_notices$', TemplateView.as_view(template_name='legal_notices.html'), name="legal_notices"),
    url(r'^tos$', TemplateView.as_view(template_name='tos.html'), name="tos"),
    prefix_default_language=False,
)
