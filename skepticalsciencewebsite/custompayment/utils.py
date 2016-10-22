from django.dispatch import receiver
from payments.signals import status_changed


@receiver(status_changed)
def order_status_change(sender, instance, **kwargs):
    #instance is payment
    order = instance.order
    # if order.is_fully_paid():
    #     order.change_status('fully-paid')
    #     instance.send_confirmation_email()