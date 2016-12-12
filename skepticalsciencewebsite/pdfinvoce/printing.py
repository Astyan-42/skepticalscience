from datetime import datetime, date
from pyinvoice.components import SimpleTable, TableWithHeader, PaidStamp
from pyinvoice.models import PDFInfo, Item, Transaction, InvoiceInfo, ServiceProviderInfo, ClientInfo
from pyinvoice.templates import SimpleInvoice
from pyinvoice.constants import *

# from reportlab.lib import colors
# from reportlab.lib.enums import TA_CENTER, TA_RIGHT
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer

# from django.contrib.auth import get_user_model
from custompayment.models import Order

# rules of facturation (France)
# https://www.service-public.fr/professionnels-entreprises/vosdroits/F23208
# inherite SimpleInvoice to make french invoice, add header and footer
# http://eric.sau.pe/reportlab-and-django-part-3-paragraphs-and-tables/
# http://eric.sau.pe/reportlab-and-django-part-1-the-set-up-and-a-basic-example/
# http://eric.sau.pe/reportlab-and-django-part-2-headers-and-footers-with-page-numbers/
# name and save in a separate folder

alternate_english_invoice = PYINVOICE_CONSTANTS
alternate_english_invoice[MERCHANT] = "Merchant"
alternate_english_invoice[PROVIDER_ID] = 'SIRET'

french_invoice = {
    INVOICE_ID: "Numéro",
    INVOICE_DATETIME: "Date",
    INVOICE: "Facture",
    DUE_DATE: "Date d'échéance",
    NAME: "Nom",
    STREET: "Rue",
    CITY: "Ville",
    STATE: "État",
    COUNTRY: "Pays",
    POST_CODE: "Code postal",
    VAT_TAX_NUMBER: "Numero de TVA",
    MERCHANT: "Marchant",
    EMAIL: "Email",
    CLIENT_ID: "Numéro client",
    CLIENT: "Client",
    DETAIL: "Détail",
    DESCRIPTION: "Description",
    UNITS: "Unités",
    UNIT_PRICE: "Prix à l'unité",
    AMOUNT: "Montant",
    SUBTOTAL: "Sous total",
    TAX: "Tax",
    TOTAL: "Total",
    TRANSACTION_ID: "Numero de transaction",
    GATEWAY: "Moyen de payment",
    TRANSACTION_DATE: "Date de la transaction",
    TRANSACTION: "Transaction",
    PAID: "Payé",
    PROVIDER_ID: "SIRET",
    CAPITAL: "Capital social"
}

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
    # need to add a folder / name and stuff
    invoice_name = 'invoice'+str(token)+'.pdf'
    if language == 'english':
        doc = SimpleInvoice(invoice_name, constants=alternate_english_invoice)
    elif language == 'french':
        doc = SimpleInvoice(invoice_name, constants=french_invoice)
    #get the order and payment
    order = Order.objects.get(token=token)
    payment = order.get_payment()
    # set the invoice related data
    doc.is_paid = True
    doc.invoice_info = InvoiceInfo(payment.created.strftime("%Y-%m-%d")+payment.transaction_id,
                                   payment.created.strftime("%Y-%m-%d"),
                                   payment.created.strftime("%Y-%m-%d"))
    # set provider data
    doc.service_provider_info = eagal_provider
    # set the client related data
    client_address = order.billing_address
    doc.client_info = ClientInfo(email=order.user.email, name=client_address.billing_name,
                                 street=client_address.street_address_1+client_address.street_address_2,
                                 city=client_address.city, post_code=client_address.postal_code,
                                 state=client_address.country_area, country=client_address.country,
                                 client_id=order.user.pk)

    #set product related data
    doc.add_item(Item('Item', 'Item desc', 1, '1.1'))
    doc.add_item(Item('Item', 'Item desc', 2, '2.2'))
    doc.add_item(Item('Item', 'Item desc', 3, '3.3'))
    doc.set_item_tax_rate(20)

    # doc.add_transaction(Transaction('Paypal', 111, datetime.now(), 1))
    # doc.add_transaction(Transaction('Stripe', 222, date.today(), 2))

    doc.set_bottom_tip("Email: example@example.com<br />Don't hesitate to contact us for any questions.")

    doc.finish()
    return doc, invoice_name