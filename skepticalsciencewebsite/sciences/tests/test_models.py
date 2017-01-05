import mock
from django.test import TestCase
from sciences.models import Science


class ScienceTestCase(TestCase):

    def test__str__(self):
        science = mock.Mock(spec=Science)
        self.assertEqual(Science.__str__(science), science.name)
