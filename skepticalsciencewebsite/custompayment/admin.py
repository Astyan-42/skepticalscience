from django.contrib import admin
from custompayment.models import Payment, Order, Item, Address, Discount, CountryPayment, Price
# Register your models here.

# to change to have more information in the admin


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice_nb', 'status', 'invoice_date', 'created', 'order']
    list_filter = ['invoice_nb', 'status', 'invoice_date', 'created', 'order']
    ordering = ['invoice_nb', 'status', 'invoice_date', 'created', 'order']
    search_fields = ['invoice_nb', 'status', 'invoice_date', 'created', 'order']

admin.site.register(Order)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Item)
admin.site.register(Address)
admin.site.register(Discount)
admin.site.register(CountryPayment)
admin.site.register(Price)