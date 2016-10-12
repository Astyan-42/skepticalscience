from django.conf.urls import url
from custompayment.views import details, payment_choice, start_payment

urlpatterns = [
    url(r'^(?P<token>[-\w]+)/$', details, name='details'),
    url(r'^(?P<token>[-\w]+)/payment/$', payment_choice, name='payment'),
    url(r'^(?P<token>[-\w]+)/payment/(?P<variant>[-\w]+)/$', start_payment, name='payment')
]
