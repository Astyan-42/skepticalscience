from django.contrib import admin
from customuser.models import User
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    """
    Determine the fields of User model and there fonctions in the admin screen
    """
    list_display = ['username', 'email']
    list_filter = ['username', 'email']
    ordering = ['username', 'email']
    search_fields = ['username', 'email']
    filter_horizontal = ['sciences']

admin.site.register(User, UserAdmin)