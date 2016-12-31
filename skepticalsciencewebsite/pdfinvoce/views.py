from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from custompayment.models import Order
from pdfinvoce.printing import generate_invoice
from io import BytesIO
from sendfile import sendfile


def invoice_generation(request, token):
    # check if request and invoice have the same user
    # Create the HttpResponse object with the appropriate PDF headers.
    order = get_object_or_404(Order, token=token)
    if order.user != request.user:
        return HttpResponseForbidden()

    pdf, name = generate_invoice(token)
    return sendfile(request, name)
