from django.shortcuts import render
from django.http import HttpResponse
from pdfinvoce.printing import generate_invoice
from io import BytesIO
from sendfile import sendfile


def invoice_generation(request, token):
    # Create the HttpResponse object with the appropriate PDF headers.
    pdf, name = generate_invoice(token)

    return sendfile(request, name)
