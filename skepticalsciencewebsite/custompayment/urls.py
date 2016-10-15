from django.conf.urls import url
from custompayment.views import payment_choice, start_payment, BillingAddressUpdate, OrderDetailView

urlpatterns = [
    url(r'^(?P<token>[-\w]+)/$', OrderDetailView.as_view(), name='detail_order'),
    url(r'^(?P<token>[-\w]+)/address/$', BillingAddressUpdate.as_view(), name='address'),
    url(r'^(?P<token>[-\w]+)/payment/$', payment_choice, name='payment'),
    url(r'^(?P<token>[-\w]+)/payment/(?P<variant>[-\w]+)/$', start_payment, name='payment')
]
