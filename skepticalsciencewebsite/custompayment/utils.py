from decimal import *


def money_quantize(value):
    res = value.quantize(Decimal('.01'), rounding=ROUND_UP)
    return res


def get_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if ip:
        ip = ip.split(', ')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip