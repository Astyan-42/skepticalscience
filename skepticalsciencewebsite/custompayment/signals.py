from django.dispatch import receiver
from payments.signals import status_changed
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from publications.models import Publication
from publications.constants import ADDING_PEER, ABORTED
from custompayment.constants import FULLY_PAID, CANCELLED, PUBLICATION, SCIENTIST_ACCOUNT


@receiver(status_changed)
def payment_status_change(sender, instance, **kwargs):
    User = get_user_model()
    order = instance.order
    scientist_group = Group.objects.get_by_natural_key("Scientist")
    if instance.status == 'confirmed':
        order.status = FULLY_PAID
        order.save()
        if order.item.name == PUBLICATION:
            publication = Publication.objects.get(pk=order.item.sku)
            publication.status = ADDING_PEER
            publication.save()
        elif order.item.name == SCIENTIST_ACCOUNT:
            user = User.objects.get(pk=order.item.sku)
            user.groups.add(scientist_group)
            user.save()
        # send a confirmation email
    if instance.status == 'refunded':
        order.status = CANCELLED
        order.save()
        if order.item.name == PUBLICATION:
            publication = Publication.objects.get(pk=order.item.sku)
            publication.status = ABORTED
            publication.save()
        elif order.item.name == SCIENTIST_ACCOUNT:
            user = User.objects.get(pk=order.item.sku)
            user.groups.remove(scientist_group)
            user.save()
        # send a confirmation email
