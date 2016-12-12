from django.conf.urls import url
from pdfinvoce.views import invoice_generation

urlpatterns = [url(r'^$', invoice_generation, name='invoice')]