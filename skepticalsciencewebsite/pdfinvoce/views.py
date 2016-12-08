from django.shortcuts import render
from django.http import HttpResponse
from pdfinvoce.printing import generate_invoice
from io import BytesIO
from sendfile import sendfile


def print_users(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    pdf = generate_invoice(1)

    return sendfile(request,'invoice.pdf')
