from django.conf.urls import url
from custompayment.views import details, payment_choice, start_payment

urlpatterns = [
    url(r'^(?P<order>[-\w]+)/$', details, name='details'),
    url(r'^(?P<order>[-\w]+)/payment/$', payment_choice, name='payment'),
    url(r'^(?P<order>[-\w]+)/payment/(?P<variant>[-\w]+)/$', start_payment, name='payment')
    #url(r'^%s/cancel-payment/$' % (TOKEN_PATTERN,), views.cancel_payment, name='cancel-payment')
]
