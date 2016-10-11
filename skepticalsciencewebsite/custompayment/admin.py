from django.contrib import admin
from  custompayment.models import Payment, Order
# Register your models here.


admin.site.register(Order)
admin.site.register(Payment)