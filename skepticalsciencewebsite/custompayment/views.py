from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded
from custompayment.models import Order, Payment
from custompayment.forms import PaymentMethodsForm


def details(request, order):
    order = get_object_or_404(Order, order_id=order)
    return TemplateResponse(request, 'custompayment/details.html',
                            {'order': order})


def payment(request, order):
    order = get_object_or_404(Order, order_id=order)
    payments = order.payments.all()
    form_data = request.POST or None
    payment_form = PaymentMethodsForm(form_data)
    return TemplateResponse(request, 'custompayment/payment.html',
                            {'order': order,
                             'payment_form': payment_form,
                             'payments': payments})


def start_payment(request, order):
    orders = Order.objects.prefetch_related('groups__items')
    order = get_object_or_404(orders, order_id=order)
    return TemplateResponse(request, 'custompayment/details.html',
                            {'order': order})