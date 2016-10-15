from decimal import Decimal
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.template.response import TemplateResponse
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DetailView, View
from django.urls import reverse_lazy
from payments import RedirectNeeded
from custompayment.models import Order, Payment, Address
from custompayment.forms import PaymentMethodsForm, AddressForm, DiscountOrderForm


# billing address https://chriskief.com/2015/01/19/create-or-update-with-a-django-modelform/

@method_decorator(login_required, name='dispatch')
class BillingAddressUpdate(UpdateView):
    form_class = AddressForm

    def get_object(self, queryset=None):
        obj, created = Address.objects.get_or_create(scientist=self.request.user)
        return obj

    def get_success_url(self):
        return reverse_lazy("detail_order", kwargs={'token':self.kwargs["token"]})


@method_decorator(login_required, name='dispatch')
class DiscountOrderUpdate(UpdateView):
    form_class = DiscountOrderForm
    model = Order
    template_name = "custompayment/order_detail.html"

    def get_object(self, queryset=None):
        obj, created = Order.objects.get_or_create(token=self.kwargs["token"])
        return obj

    def get_context_data(self, **kwargs):
        """ done in case of form invalid"""
        context = super(DiscountOrderUpdate, self).get_context_data(**kwargs)
        context["view"] = OrderDisplay.as_view()
        context["order_detail"] = context["order"]
        return context

    def get_success_url(self):
        return reverse_lazy("detail_order", kwargs={'token':self.kwargs["token"]})


@method_decorator(login_required, name='dispatch')
class OrderDisplay(DetailView):
    context_object_name = "order_detail"
    model = Order
    fields = ["status", "creation_date", "user", "discount", "billing_address", "item"]
    object = None

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Order, token=kwargs["token"])
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(OrderDisplay, self).get_context_data(**kwargs)
        context["form"] = DiscountOrderForm()
        return context


@method_decorator(login_required, name='dispatch')
class OrderDetailView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        view = OrderDisplay.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        view = DiscountOrderUpdate.as_view()
        return view(request, *args, **kwargs)


def payment_choice(request, token):
    order = get_object_or_404(Order, token=token)
    payments = order.payments.all()
    form_data = request.POST or None
    payment_form = PaymentMethodsForm(form_data)
    # redirect if the form have been send
    if payment_form.is_valid():
        payment_method = payment_form.cleaned_data['method']
        return redirect(start_payment, token=token, variant=payment_method)
    # if the form havent been send the render the form to choose the payment method
    return TemplateResponse(request, 'custompayment/payment.html',
                            {'order': order,
                             'payment_form': payment_form,
                             'payments': payments})


def start_payment(request, token, variant):
    order = get_object_or_404(Order, token=token)
    if order.payments.filter(status='waiting').exists():
        return redirect(payment_choice, token=token)
    variant_choices = settings.CHECKOUT_PAYMENT_CHOICES
    if variant not in [code for code, dummy_name in variant_choices]:
        raise Http404('%r is not a valid payment variant' % (variant,))
    # temporary default to check if working
    defaults = {'total': Decimal(120),
                'tax': Decimal(20),
                'currency': 'USD',
                'delivery': Decimal(10),
                'billing_first_name': 'Sherlock',
                'billing_last_name': 'Holmes',
                'billing_address_1': '221B Baker Street',
                'billing_address_2': '',
                'billing_city': 'London',
                'billing_postcode': 'NW1 6XE',
                'billing_country_code': 'UK',
                'description': _('Order %(order_number)s') % {'order_number': order},
                'billing_country_area': 'Greater London',
                'customer_ip_address': '127.0.0.1'}
    with transaction.atomic():
        order.change_status('payment-pending')
        payment, dummy_created = Payment.objects.get_or_create(
            variant=variant, status='waiting', order=order, defaults=defaults)
        try:
            form = payment.get_form(data=request.POST or None)
        except RedirectNeeded as redirect_to:
            return redirect(str(redirect_to))
        except Exception:
            # logger.exception('Error communicating with the payment gateway')
            messages.error(request,
                           _('Oops, it looks like we were unable to contact the selected payment service'))
            payment.change_status('error')
            return redirect(payment_choice, token=token)
    # template to use before the default template
    template = 'custompayment/method/%s.html' % variant
    return TemplateResponse(request, [template, 'custompayment/method/default.html'],
                            {'form': form, 'payment': payment})