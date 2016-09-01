from django.contrib import admin
from sciences.models import Science

# Register your models here.
class ScienceAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    ordering = ['name']
    search_fields = ('name', 'description')

admin.site.register(Science, ScienceAdmin)