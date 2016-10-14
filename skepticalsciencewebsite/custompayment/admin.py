from django.contrib import admin
from  custompayment.models import Payment, Order, Item, Address, Discount
# Register your models here.

# to change to have more information in the admin


admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Item)
admin.site.register(Address)
admin.site.register(Discount)