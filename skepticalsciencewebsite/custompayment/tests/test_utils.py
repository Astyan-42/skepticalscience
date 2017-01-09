from django.test import TestCase
from decimal import *
from custompayment.utils import money_quantize


class MoneyQuantizeTestCase(TestCase):

    def test_high_decimal(self):
        self.assertEqual(float(money_quantize(Decimal(12.3444444444))), 12.35)

    def test_high_premice(self):
        self.assertEqual(float(money_quantize(Decimal(12344444444.4))), 12344444444.40)

    def test_no_decimal(self):
        self.assertEqual(float(money_quantize(Decimal(12344444444))), 12344444444.)

    def test_high_limit_decimal(self):
        self.assertEqual(float(money_quantize(Decimal(12.9999))), 13.)

    def test_low_limit_decimal(self):
        self.assertEqual(float(money_quantize(Decimal(12.000001))), 12.01)