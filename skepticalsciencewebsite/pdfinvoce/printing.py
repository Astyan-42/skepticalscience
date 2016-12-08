from datetime import datetime, date
from pyinvoice.models import InvoiceInfo, ServiceProviderInfo, ClientInfo, Item, Transaction
from pyinvoice.templates import SimpleInvoice
from django.contrib.auth import get_user_model


# rules of facturation (France)
# https://www.service-public.fr/professionnels-entreprises/vosdroits/F23208
# inherite SimpleInvoice to make french invoice, add header and footer
# http://eric.sau.pe/reportlab-and-django-part-3-paragraphs-and-tables/
# http://eric.sau.pe/reportlab-and-django-part-1-the-set-up-and-a-basic-example/
# http://eric.sau.pe/reportlab-and-django-part-2-headers-and-footers-with-page-numbers/
# name and save in a separate folder


def generate_invoice(order_id):
    doc = SimpleInvoice('invoice.pdf')
    doc.is_paid = True
    doc.invoice_info = InvoiceInfo(1023, datetime.now(), datetime.now())
    doc.service_provider_info = ServiceProviderInfo(
        name='PyInvoice',
        street='My Street',
        city='My City',
        state='My State',
        country='My Country',
        post_code='222222',
        vat_tax_number='Vat/Tax number'
    )

    doc.client_info = ClientInfo(email='client@example.com')
    doc.add_item(Item('Item', 'Item desc', 1, '1.1'))
    doc.add_item(Item('Item', 'Item desc', 2, '2.2'))
    doc.add_item(Item('Item', 'Item desc', 3, '3.3'))
    doc.set_item_tax_rate(20)

    doc.add_transaction(Transaction('Paypal', 111, datetime.now(), 1))
    doc.add_transaction(Transaction('Stripe', 222, date.today(), 2))

    doc.set_bottom_tip("Email: example@example.com<br />Don't hesitate to contact us for any questions.")

    doc.finish()
    return doc