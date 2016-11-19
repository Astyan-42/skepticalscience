from decimal import Decimal
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.conf import settings
from django.db import transaction
from django.db.models import Max, Min
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import UpdateView, DetailView, View
from django.urls import reverse_lazy
from django_tables2 import SingleTableView, RequestConfig
from payments import RedirectNeeded
from skepticalsciencewebsite.utils import same_user, check_status
from customuser.constants import *
from customuser.models import User
from publications.models import Publication
from custompayment.models import Order, Payment, Address, Item, CountryPayment, Price
from custompayment.forms import PaymentMethodsForm, AddressForm, DiscountOrderForm
from custompayment.tables import OrderTable
from custompayment.filters import OrderFilter
from custompayment.constants import *
from custompayment.utils import get_ip, money_quantize
# need a my order list


@method_decorator(login_required, name='dispatch')
class BillingAddressUpdate(UpdateView):
    form_class = AddressForm
    # template_name = 'custompayment/address_form.html'

    def get_object(self, queryset=None):
        order = Order.objects.get(token=self.kwargs["token"])
        if order.billing_address is None:
            if Address.objects.filter(scientist=self.request.user).exists():
                obj = Address.objects.filter(scientist=self.request.user).order_by("-creation_date")[0]
                obj.pk = None
            else:
                obj = Address(scientist=self.request.user)
        else:
            obj = order.billing_address
        return obj

    @same_user('scientist')
    def form_valid(self, form):
        res = super(BillingAddressUpdate, self).form_valid(form)
        order = Order.objects.get(token=self.kwargs["token"])
        order.billing_address = self.object
        order.save()
        return res

    def get_success_url(self):
        return reverse_lazy("detail_order", kwargs={'token': self.kwargs["token"]})


def add_price_context(context):
    # this function is the ugliest thing on earth, it need to be exterminated
    def fill_scientific_score(user, order_type, current_price):
        if order_type == SCIENTIST_ACCOUNT:
            return None, current_price
        skeptic_score = SKEPTIC_SCORE_NORMALIZE(user.skeptic_score)
        mean_publication_score = MEAN_PUBLICATION_SCORE_NORMALIZE(user.mean_publication_score)
        mean_impact_factor = MEAN_IMPACT_FACTOR_NORMALIZE(user.mean_impact_factor)
        estimator_score = ESTIMATOR_SCORE_NORMALIZE(user.estimator_score)
        reviewer_score = REVIEWER_SCORE_NORMALIZE(user.reviewer_score)
        mean_score = (skeptic_score+mean_publication_score+mean_impact_factor+estimator_score+reviewer_score)/5.
        payment_percent = -0.08+(1+0.08)/(1+(mean_score/0.1214766)**1.137504)
        new_price = money_quantize(current_price*Decimal(payment_percent))
        diff_price = money_quantize(new_price-current_price)
        res = {"t_type": "scientist score compensation",
               "t_object": "score :"+str(round(mean_score, 2)),
               "t_price": str(diff_price)+' €'}
        return res, new_price

    def fill_country_reduction(address, current_price):
        db_countriespayment = CountryPayment.objects.all()
        max_pib = db_countriespayment.aggregate(Max('pib_per_inhabitant'))['pib_per_inhabitant__max']
        min_pib = db_countriespayment.aggregate(Min('pib_per_inhabitant'))['pib_per_inhabitant__min']
        try:
            country= address.country
            own_country_payment = CountryPayment.objects.get(country=country)
        except (AttributeError, ObjectDoesNotExist):
            return None, current_price
        factor = COUNTRY_PPP_TO_PERCENT(min_pib, max_pib, own_country_payment.pib_per_inhabitant)
        new_price = money_quantize(current_price*Decimal(factor))
        diff_price = money_quantize(new_price-current_price)
        res = {"t_type": "country compensation",
               "t_object": country.name,
               "t_price": str(diff_price)+' €'}
        return res, new_price

    def fill_discount(discount, current_price):
        if (discount is not None and discount.starting_date < timezone.now().date() and
            discount.ending_date > timezone.now().date()):
            if discount.discount_type == FIXED:
                discount_price = money_quantize(Decimal(discount.discount_value))
            else:
                discount_price = money_quantize(-current_price*Decimal(discount.discount_value/100.))
            new_price = money_quantize(current_price + discount_price)
            res = {"t_type": "discount code",
                   "t_object": discount.code,
                   "t_price": str(discount_price)+' €'}
        else:
            res = None
            new_price = current_price
        return res, new_price

    def fill_taxes(percent, current_price):
        taxes_amount = money_quantize(current_price*Decimal(percent/100))
        new_price = money_quantize(current_price+taxes_amount)
        res = {"t_type": "taxes",
               "t_object": str(percent)+"%",
               "t_price": str(taxes_amount)+' €'}
        return res, new_price

    def change_price(price_instance, current_prices):
        if price_instance is None:
            price_instance = Price()
        price_instance.product_default_price = current_prices[0]
        price_instance.country_reduction = current_prices[1] - current_prices[0]
        price_instance.scientist_score_reduction = current_prices[2] - current_prices[1]
        price_instance.discount = current_prices[3] - current_prices[2]
        price_instance.tax = current_prices[4] - current_prices[3]
        price_instance.save()
        return price_instance

    prices = []
    current_prices = []
    current_price = Decimal(PRODUCTS_PRICES[context["order_detail"].item.name])
    current_prices.append(current_price)
    initial_price = {"t_type": "order "+context["order_detail"].item.name,
                     "t_object": context["order_detail"].item,
                     "t_price": str(current_price)+' €'}
    country_reduction, current_price = fill_country_reduction(context["order_detail"].billing_address,
                                                              current_price)
    current_prices.append(current_price)
    scientific_score, current_price = fill_scientific_score(context["order_detail"].user,
                                                            context["order_detail"].item.name,
                                                            current_price)
    current_prices.append(current_price)
    discount, current_price = fill_discount(context["order_detail"].discount,
                                            current_price)
    current_prices.append(current_price)
    tax, current_price = fill_taxes(TAX, current_price)
    current_prices.append(current_price)
    final_price = {"t_type": "final price",
                   "t_object": "",
                   "t_price": str(current_price)+' €'}
    # change price in the model
    priceobj = change_price(context["order_detail"].price, current_prices)
    context["order_detail"].price = priceobj
    context["order_detail"].save()

    prices.append(initial_price)
    if country_reduction is not None:
        prices.append(country_reduction)
    if scientific_score is not None:
        prices.append(scientific_score)
    if discount is not None:
        prices.append(discount)
    prices.append(tax)
    prices.append(final_price)
    context["prices"] = prices
    return context


def add_price_to_context2(context):
    pass


@method_decorator(login_required, name='dispatch')
class DiscountOrderUpdate(UpdateView):
    form_class = DiscountOrderForm
    context_object_name = "order_detail"
    model = Order
    template_name = "custompayment/order_detail.html"

    def get_object(self, queryset=None):
        obj, created = Order.objects.get_or_create(token=self.kwargs["token"])
        return obj

    @same_user('user')
    def get_context_data(self, **kwargs):
        """ done in case of form invalid"""
        context = super(DiscountOrderUpdate, self).get_context_data(**kwargs)
        # seems to be only called when bug
        # constants needed !!!
        context["constants"] = PAYMENT_CONSTANTS_TEMPLATE
        context["order_detail"].discount = self.get_object().discount
        return add_price_context(context)

    def get_success_url(self):
        return reverse_lazy("detail_order", kwargs={'token': self.kwargs["token"]})


@method_decorator(login_required, name='dispatch')
class OrderDisplay(DetailView):
    context_object_name = "order_detail"
    model = Order
    fields = ["status", "creation_date", "last_status_change", "user", "discount", "billing_address", "item"]
    object = None

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Order, token=kwargs["token"])
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    @same_user('user')
    def get_context_data(self, **kwargs):
        context = super(OrderDisplay, self).get_context_data(**kwargs)
        context["form"] = DiscountOrderForm()
        context["constants"] = PAYMENT_CONSTANTS_TEMPLATE
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


def create_order(request, name, sku):

    def can_create_publication_order(request, sku):
        if Publication.objects.filter(pk=sku).exists():
            publication = Publication.objects.get(pk=sku)
            if publication.editor == request.user:
                # when the item is created and only one (due to the rest of the process of create_order)
                if not Item.objects.filter(name=name, sku=sku).exists():
                    return True
        return False

    def can_create_scientist_account_order(request, sku):
        if User.objects.filter(pk=sku).exists():
            if int(request.user.pk) == int(sku):
                # when the item is created and only one (due to the rest of the process of create_order)
                if not Item.objects.filter(name=name, sku=sku).exists():
                    return True
        return False

    if name == PUBLICATION:
        if not can_create_publication_order(request, sku):
            return HttpResponseForbidden()
    elif name == SCIENTIST_ACCOUNT:
        if not can_create_scientist_account_order(request, sku):
            return HttpResponseForbidden()
    else:
        return Http404()
    item = Item(name=name, sku=int(sku))
    item.save()
    order = Order(item=item, user=request.user)
    order.save()
    return redirect('detail_order', token=order.token)


def payment_choice(request, token):
    order = get_object_or_404(Order, token=token)
    if order.user != request.user:
        return HttpResponseForbidden()
    form_data = request.POST or None
    payment_form = PaymentMethodsForm(form_data)
    # redirect if the form have been send
    if order.can_add_payment():
        if payment_form.is_valid():
            payment_method = payment_form.cleaned_data['method']
            return redirect('payment', token=token, variant=payment_method)
        # if there is no form then show the form to choose the method
        return TemplateResponse(request, 'custompayment/payment.html',
                                {'order': order,
                                 'payment_form': payment_form})
    #if cannot add payment (because already paid, on in payment confirmation, or refundd)
    return HttpResponseForbidden()


def start_payment(request, token, variant):
    order = get_object_or_404(Order, token=token)
    if order.user != request.user:
        return HttpResponseForbidden()
    if order.payments.filter(status='waiting').exists():
        return redirect('payment', token=token)
    variant_choices = settings.CHECKOUT_PAYMENT_CHOICES
    if variant not in [code for code, dummy_name in variant_choices]:
        raise Http404('%r is not a valid payment variant' % (variant,))
    # temporary default to check if working
    defaults = {'total': order.price.gross,
                'tax': order.price.get_taxes(),
                'currency': order.price.currency,
                'delivery': Decimal(0),
                'billing_first_name': order.billing_address.first_name,
                'billing_last_name': order.billing_address.last_name,
                'billing_address_1': order.billing_address.street_address_1,
                'billing_address_2': order.billing_address.street_address_2,
                'billing_city': order.billing_address.city,
                'billing_postcode': order.billing_address.postal_code,
                'billing_country_code': order.billing_address.country,
                'description': _('Order %(order_number)s') % {'order_number': order},
                'billing_country_area': order.billing_address.country_area,
                'customer_ip_address': get_ip(request)}
    with transaction.atomic():
        order.change_status('payment-pending')
        payment, created = Payment.objects.get_or_create(variant=variant, status='waiting',
                                                         order=order, defaults=defaults)
        try:
            # why we get the data from the form ? Change the status to input with the dummy provider
            form = payment.get_form(data=request.POST or None)
        except RedirectNeeded as redirect_to:
            # redirection on success or faillure
            return redirect(str(redirect_to))
        except Exception:
            # logger.exception('Error communicating with the payment gateway')
            messages.error(request,
                           _('Oops, it looks like we were unable to contact the selected payment service'))
            payment.change_status('error')
            return redirect('payment', token=token)
    # template to use before the default template
    template = 'custompayment/method/%s.html' % variant
    return TemplateResponse(request, [template, 'custompayment/method/default.html'],
                            {'form': form, 'payment': payment})


def cancer_order(request, token):
    order = get_object_or_404(Order, token=token)
    if order.user != request.user:
        return HttpResponseForbidden()
    if order.can_be_cancelled():
        with transaction.atomic():
            payment = order.payments.get(status='confirmed')
            payment.refund()
            #everything else is done in signal
            return redirect('detail_order', token=token)
    else:
        return HttpResponseForbidden()
