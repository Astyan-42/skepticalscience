from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from custompayment.models import Address, Order


class AddressForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id_addressForm'
        self.helper.add_input(Submit('submit', _('Save')))

    class Meta:
        model = Address
        fields = ["first_name", "last_name", "company_name", "street_address_1", "street_address_2", "city",
                  "city_area", "postal_code", "country", "country_area", "phone"]


class DiscountOrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DiscountOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id_discountorderForm'
        self.helper.add_input(Submit('submit', _('Apply')))

    class Meta:
        model = Order
        fields = ["discount"]
        widgets = {'discount' : forms.TextInput()}


class PaymentMethodsForm(forms.Form):
    method = forms.ChoiceField(
        choices=settings.CHECKOUT_PAYMENT_CHOICES, widget=forms.RadioSelect,
        initial=settings.CHECKOUT_PAYMENT_CHOICES[0][0])

    def __init__(self, *args, **kwargs):
        super(PaymentMethodsForm, self).__init__(*args, ** kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id_paymentmethodForm'
        self.helper.add_input(Submit('submit', _('Proceed to payment')))
