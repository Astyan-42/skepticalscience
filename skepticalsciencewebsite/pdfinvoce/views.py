from django.shortcuts import render
from django.http import HttpResponse
from pdfinvoce.printing import generate_invoice
from io import BytesIO
from sendfile import sendfile


def invoice_generation(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    pdf, name = generate_invoice('eb83c3dc-2e93-418c-82e1-59fdfa0f9d50', 'french')

    return sendfile(request, name)
