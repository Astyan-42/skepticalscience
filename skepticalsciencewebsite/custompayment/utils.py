from django.dispatch import receiver
from payments.signals import status_changed
from custompayment.constants import FULLY_PAID


@receiver(status_changed)
def payment_status_change(sender, instance, **kwargs):
    #instance is payment
    print("test")
    order = instance.order
    order.status = FULLY_PAID
    order.save()
    # if instance.status == 'confirmed':
    #     order.status = FULLY_PAID
    #     order.save()
        # need to change the publication status or put the user in the group of scientist
        # send a confirmation email ?