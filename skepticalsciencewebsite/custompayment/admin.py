from django.contrib import admin
from  custompayment.models import Payment, Order, Item, Address, Discount, CountryPayment, Price
# Register your models here.

# to change to have more information in the admin


admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Item)
admin.site.register(Address)
admin.site.register(Discount)
admin.site.register(CountryPayment)
admin.site.register(Price)