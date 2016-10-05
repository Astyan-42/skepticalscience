from django.contrib import admin

from faq.models import Topic
from faq.models import QandA


class QandAInline(admin.TabularInline):
    """
    Set up a tabular list of questions and answers
    for the admin interface
    """
    model = QandA
    extra = 2


class TopicAdmin(admin.ModelAdmin):
    """
    Set up the FAQ Topics in the admin interface
    """
    inlines = [QandAInline]


admin.site.register(Topic, TopicAdmin)