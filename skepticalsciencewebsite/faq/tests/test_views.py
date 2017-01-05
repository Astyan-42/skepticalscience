import mock
from django.test import RequestFactory
from django.test import TestCase
from skepticalsciencewebsite.utils import setup_view
from faq.views import FAQView
from faq.models import Topic, QandA


class TestFAQView(TestCase):
    """ just as exemple like it's kind of useless there"""

    def test_get_queryset_empty(self):
        request = RequestFactory().get('/faq-test/')
        view = FAQView()
        view = setup_view(view, request)
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [])
