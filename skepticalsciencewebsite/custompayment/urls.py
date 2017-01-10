from django.conf.urls import url
from custompayment.views import (create_order, payment_choice, start_payment, cancel_order, BillingAddressUpdate,
                                 OrderDetailView, OrderOwnedTableView, delete_order)

urlpatterns = [
    url(r'^orders/', OrderOwnedTableView.as_view(), name='list_order'),
    url(r'^new_order/(?P<name>[-\w]+)/(?P<sku>\d+)/$', create_order, name='create_order'),
    url(r'^(?P<token>[-\w]+)/$', OrderDetailView.as_view(), name='detail_order'),
    url(r'^(?P<token>[-\w]+)/address/$', BillingAddressUpdate.as_view(), name='address'),
    url(r'^(?P<token>[-\w]+)/cancel/$', cancel_order, name='cancel_order'),
    url(r'^(?P<token>[-\w]+)/delete/$', delete_order, name='delete_order'),
    url(r'^(?P<token>[-\w]+)/payment/$', payment_choice, name='payment'),
    url(r'^(?P<token>[-\w]+)/payment/(?P<variant>[-\w]+)/$', start_payment, name='payment')
]
