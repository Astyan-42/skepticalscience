from django.contrib import admin
from  custompayment.models import Payment, Order
# Register your models here.

# to change to have more information in the admin


admin.site.register(Order)
admin.site.register(Payment)