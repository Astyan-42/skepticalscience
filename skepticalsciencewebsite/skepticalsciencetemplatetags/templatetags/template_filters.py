from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    if Group.objects.filter(name=group_name).exists():
        group = Group.objects.get(name=group_name)
        return True if group in user.groups.all() else False
    else:
        return False
