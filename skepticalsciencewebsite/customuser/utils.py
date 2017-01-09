from django.utils.translation import ugettext_lazy as _
from custompayment.models import Address
from custompayment.constants import SCIENTIST_ACCOUNT


def get_scientific_account_address_name(pk):
    if Address.objects.filter(order__item__sku=pk, order__item__name=SCIENTIST_ACCOUNT).exists():
        address_name = Address.objects.filter(order__item__sku=pk, order__item__name=SCIENTIST_ACCOUNT)[0].billing_name
    else:
        address_name = _('Unknown')
    return address_name
