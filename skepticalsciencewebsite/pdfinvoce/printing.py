import os
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from skepticalsciencewebsite.settings import SENDFILE_ROOT
from pyinvoice.models import Item, InvoiceInfo, ServiceProviderInfo, ClientInfo
from pyinvoice.templates import SimpleInvoice
from pyinvoice.constants import *
from custompayment.models import Order

# rules of facturation (France)
# https://www.service-public.fr/professionnels-entreprises/vosdroits/F23208
# inherite SimpleInvoice to make french invoice, add header and footer
# http://eric.sau.pe/reportlab-and-django-part-3-paragraphs-and-tables/
# http://eric.sau.pe/reportlab-and-django-part-1-the-set-up-and-a-basic-example/
# http://eric.sau.pe/reportlab-and-django-part-2-headers-and-footers-with-page-numbers/
# name and save in a separate folder

eagal_provider = ServiceProviderInfo(
    name='temp',
    provider_id='temp',
    capital='temp',
    street='temp',
    city='temp',
    country='temp',
    post_code='temp',
    vat_tax_number='temp'
)


def generate_invoice(token, language):
    invoice_name = 'invoice'+language+str(token)+'.pdf'
    invoice_path = os.path.join(SENDFILE_ROOT, 'invoices', invoice_name)
    if language == 'english':
        activate('en')
    else: # language == 'french':
        activate('fr')
    international_pyinvoice = {
        INVOICE_ID: _('Invoice id'),
        INVOICE_DATETIME: _('Invoice date'),
        INVOICE: _('Invoice'),
        DUE_DATE: _('Invoice due date'),
        NAME: _('Name'),
        STREET: _('Street'),
        CITY: _('City'),
        STATE: _('State'),
        COUNTRY: _('Country'),
        POST_CODE: _('Postal code'),
        VAT_TAX_NUMBER: _('Vat/Tax number'),
        MERCHANT: _('Merchant'),
        EMAIL: _('Email'),
        CLIENT_ID: _('Client id'),
        CLIENT: _('Client'),
        DETAIL: _('Detail'),
        DESCRIPTION: _('Description'),
        UNITS: _('Units'),
        UNIT_PRICE: _('Unit Price'),
        AMOUNT: _('Amount'),
        SUBTOTAL: _('Subtotal'),
        TAX: _('Vat/Tax'),
        TOTAL: _('Total'),
        TRANSACTION_ID: _('Transaction id'),
        GATEWAY: _('Gateway'),
        TRANSACTION_DATE: _('Transaction date'),
        TRANSACTION: _('Transaction'),
        PAID: _('PAID'),
        PROVIDER_ID: _('SIRET'),
        CAPITAL: _('Capital'),
        INVOICE_STATUS: _('Payment status')
    }
    doc = SimpleInvoice(invoice_path, constants=international_pyinvoice)
    # get the order and payment
    order = Order.objects.get(token=token)
    #payment = order.get_payment()
    payment = order.payment
    # set the invoice related data
    # if payment.status == 'confirmed' or payment.status == 'refunded':
    #     doc.is_paid = True
    doc.invoice_info = InvoiceInfo(payment.invoice_date.strftime("%Y/%m-")+str(payment.invoice_nb),
                                   payment.invoice_date.strftime("%Y/%m/%d"),
                                   invoice_status=payment.get_status_display())
    # set provider data
    doc.service_provider_info = eagal_provider
    # set the client related data
    client_address = order.billing_address
    doc.client_info = ClientInfo(email=order.user.email, name=client_address.billing_name,
                                 street=client_address.street_address_1+client_address.street_address_2,
                                 city=client_address.city, post_code=client_address.postal_code,
                                 state=client_address.country_area, country=client_address.country,
                                 client_id=order.user.pk)
    # set product related data
    item = order.item
    price = order.price
    doc.add_item(Item(item.name , str(item), 1, price.net, price.currency))
    doc.set_item_tax_rate(price.tax_percent)
    # translation to do
    doc.set_bottom_tip(_("Email: %(email)s <br/>Please contact us if you have any questions.")%{'email': 'test@test.com'})

    doc.finish()
    return doc, invoice_path