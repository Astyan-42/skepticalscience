from django import forms
from django.conf import settings
from payments import get_payment_model

Payment = get_payment_model()


class PaymentMethodsForm(forms.Form):
    method = forms.ChoiceField(
        choices=settings.CHECKOUT_PAYMENT_CHOICES, widget=forms.RadioSelect,
        initial=settings.CHECKOUT_PAYMENT_CHOICES[0][0])
