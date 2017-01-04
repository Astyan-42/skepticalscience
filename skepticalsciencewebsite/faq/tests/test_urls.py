from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve


class URLSTestCase(TestCase):

    def test_url_resolve(self):
        url = reverse('faq')
        self.assertEqual(url, '/faq/')

    def test_connect_view(self):
        resolver = resolve('/faq/')
        self.assertEqual(resolver.view_name, 'faq')
