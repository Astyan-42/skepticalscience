from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded
from custompayment.models import Order


def details(request, order):
    order = get_object_or_404(Order, order_id=order)
    return TemplateResponse(request, 'custompayment/details.html',
                            {'order': order})


def payment(request, order):
    orders = Order.objects.prefetch_related('groups__items')
    order = get_object_or_404(orders, order_id=order)
    return TemplateResponse(request, 'custompayment/details.html',
                            {'order': order})


def start_payment(request, order):
    orders = Order.objects.prefetch_related('groups__items')
    order = get_object_or_404(orders, order_id=order)
    return TemplateResponse(request, 'custompayment/details.html',
                            {'order': order})