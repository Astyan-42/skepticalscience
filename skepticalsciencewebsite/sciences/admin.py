from django.contrib import admin
from sciences.models import Science

# Register your models here.
class ScienceAdmin(admin.ModelAdmin):
    """
    Determine the fields of Science model and there fonctions in the admin screen
    """
    list_display = ['name']
    list_filter = ['name']
    ordering = ['name']
    search_fields = ('name', 'description')

admin.site.register(Science, ScienceAdmin)