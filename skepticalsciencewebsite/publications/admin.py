from django.contrib import admin
from publications.models import Licence, EstimatedImpactFactor, KeyWord, Publication, Comment, Reviewer
# Register your models here.


class LicenceAdmin(admin.ModelAdmin):
    list_display = ['short_name']
    list_filter = ['short_name']
    ordering = ['short_name']
    search_fields = ['short_name']


class EstimatedImpactFactorAdmin(admin.ModelAdmin):
    list_display = ['scientist', 'publication', 'estimated_impact_factor']
    list_filter = ['scientist', 'publication', 'estimated_impact_factor']
    ordering = ['scientist', 'publication', 'estimated_impact_factor']
    search_fields = ['scientist', 'publication', 'estimated_impact_factor']


class KeyWordAdmin(admin.ModelAdmin):
    list_display = ['tag']
    list_filter = ['tag']
    ordering = ['tag']
    search_fields = ['tag']


class PublicationAdmin(admin.ModelAdmin):
    list_display = ['editor', 'creation_date', 'payment_date', 'validation_date',
                    'title', 'publication_score', 'estimated_impact_factor', 'status', 'licence']
    list_filter = ['editor', 'creation_date', 'payment_date', 'validation_date',
                   'title', 'publication_score', 'estimated_impact_factor', 'status', 'licence']
    ordering = ['editor', 'creation_date', 'payment_date', 'validation_date',
                'title', 'publication_score', 'estimated_impact_factor', 'status', 'licence']
    search_fields = ['editor', 'creation_date', 'payment_date', 'validation_date',
                     'title', 'publication_score', 'estimated_impact_factor', 'status', 'licence']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['publication', 'author', 'comment_type', 'seriousness', 'validated', 'corrected', 'licence']
    list_filter = ['publication', 'author', 'comment_type', 'seriousness', 'validated', 'corrected', 'licence']
    ordering = ['publication', 'author', 'comment_type', 'seriousness', 'validated', 'corrected', 'licence']
    search_fields = ['publication', 'author', 'comment_type', 'seriousness', 'validated', 'corrected', 'licence']


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['scientist', 'publication']
    list_filter = ['scientist', 'publication']
    ordering = ['scientist', 'publication']
    search_fields = ['scientist', 'publication']

admin.site.register(Licence, LicenceAdmin)
admin.site.register(EstimatedImpactFactor, EstimatedImpactFactorAdmin)
admin.site.register(KeyWord, KeyWordAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reviewer, ReviewerAdmin)