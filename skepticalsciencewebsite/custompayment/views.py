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
from django_tables2 import SingleTableView, RequestConfig
from payments import RedirectNeeded
from customuser.constants import *
from custompayment.models import Order, Payment, Address
from custompayment.forms import PaymentMethodsForm, AddressForm, DiscountOrderForm
from custompayment.tables import OrderTable
from custompayment.filters import OrderFilter
from custompayment.constants import *
# need a my order list


@method_decorator(login_required, name='dispatch')
class BillingAddressUpdate(UpdateView):
    form_class = AddressForm

    def get_object(self, queryset=None):
        obj, created = Address.objects.get_or_create(scientist=self.request.user)
        return obj

    def form_valid(self, form):
        res = super(BillingAddressUpdate, self).form_valid(form)
        order = Order.objects.get(token=self.kwargs["token"])
        order.billing_address = self.object
        order.save()
        return res


    def get_success_url(self):
        return reverse_lazy("detail_order", kwargs={'token':self.kwargs["token"]})


def add_price_context(context):

    def fill_scientific_score(user, current_price):
        skeptic_score = SKEPTIC_SCORE_NORMALIZE(user.skeptic_score)
        mean_publication_score = MEAN_PUBLICATION_SCORE_NORMALIZE(user.mean_publication_score)
        mean_impact_factor = MEAN_IMPACT_FACTOR_NORMALIZE(user.mean_impact_factor)
        estimator_score = ESTIMATOR_SCORE_NORMALIZE(user.estimator_score)
        reviewer_score = REVIEWER_SCORE_NORMALIZE(user.reviewer_score)
        mean_score = (skeptic_score+mean_publication_score+mean_impact_factor+estimator_score+reviewer_score)/5.
        payment_percent = -0.08+(1+0.08)/(1+(mean_score/0.1214766)**1.137504)
        new_price = round(current_price*payment_percent, 2)
        diff_price = new_price-current_price
        res = {"t_type": "scientist score compensation",
               "t_object": "score :"+str(round(mean_score, 2)),
                "t_price": diff_price}
        return res, new_price

    def fill_country_reduction(country, current_price):
        pass
        # get country and get country pib, if none message, if not supported message

    def fill_discount(discount, current_price):
        if discount is not None:
            if discount.discount_type == FIXED:
                new_price = discount.discount_value
            elif discount.discount_type == PERCENT:
                new_price = round(-current_price*(discount.discount_value/100.), 2)
            res = {"t_type": "discount code",
                   "t_object": discount.code,
                   "t_price": new_price}
            current_price = current_price + new_price
        else:
            res = None
        return res, current_price

    def fill_taxes(percent, current_price):
        taxes_amount = current_price*(percent/100)
        current_price = current_price + taxes_amount
        res = {"t_type": "taxes",
               "t_object": str(percent)+"%",
               "t_price": taxes_amount}
        return res, current_price

    prices = []
    current_price = PRODUCTS_PRICES[context["order_detail"].item.name]
    initial_price = {"t_type": "order "+context["order_detail"].item.name,
                     "t_object": context["order_detail"].item,
                      "t_price": current_price}
    # country_reduction = {"t_type": "country compensation",
    #                      "t_object": context["order_detail"].billing_address.country.name,
    #                      "t_price": -10.} # reduction in amount (always)
    scientific_score, current_price = fill_scientific_score(context["order_detail"].user,
                                                            current_price)
    discount, current_price = fill_discount(context["order_detail"].discount,
                                            current_price)
    tax, current_price = fill_taxes(TAX, current_price)
    final_price = {"t_type": "final price",
                   "t_object": "",
                   "t_price": current_price}
    prices.append(initial_price)
    # prices.append(country_reduction)
    prices.append(scientific_score)
    if discount is not None:
        prices.append(discount)
    prices.append(tax)
    prices.append(final_price)
    context["prices"] = prices
    return context


@method_decorator(login_required, name='dispatch')
class DiscountOrderUpdate(UpdateView):
    form_class = DiscountOrderForm
    context_object_name = "order_detail"
    model = Order
    template_name = "custompayment/order_detail.html"

    def get_object(self, queryset=None):
        obj, created = Order.objects.get_or_create(token=self.kwargs["token"])
        return obj

    def get_context_data(self, **kwargs):
        """ done in case of form invalid"""
        context = super(DiscountOrderUpdate, self).get_context_data(**kwargs)
        # only called when bug ?
        context["order_detail"].discount = self.get_object().discount
        return add_price_context(context)

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
        # context of the price
        return add_price_context(context)


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


@method_decorator(login_required, name='dispatch')
class OrderOwnedTableView(SingleTableView):
    model = Order
    filter_class = OrderFilter
    context_filter_name = 'filter'
    table_class = OrderTable
    template_name = 'custompayment/order_list.html'
    paginate_by = 20
    object = None
    request = None
    filter = None

    def get_queryset(self, **kwargs):
        qs = super(OrderOwnedTableView, self).get_queryset()
        filter_dict = {'user': self.request.session['_auth_user_id']}
        self.filter = self.filter_class(filter_dict, queryset=qs)
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(OrderOwnedTableView, self).get_table()
        RequestConfig(self.request, paginate={'page': self.page_kwarg,
                      "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(OrderOwnedTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


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