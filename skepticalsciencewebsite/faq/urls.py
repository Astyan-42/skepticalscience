from django.conf.urls import url
from django.views.generic import TemplateView
from faq.views import FAQView

urlpatterns = [url(r'^$', FAQView.as_view(), name='faq')]