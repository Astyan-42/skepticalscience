from django.views import generic
from faq.models import Topic
from faq.models import QandA


class FAQView(generic.ListView):
    template_name = 'faq/faq.html'
    context_object_name = 'topic_list'

    def get_queryset(self):
        """Return list of FAQs"""
        return Topic.objects.all()