from django.conf.urls import url
from pdfinvoce.views import invoice_generation

urlpatterns = [url(r'^(?P<token>[-\w]+)$', invoice_generation, name='invoice')]