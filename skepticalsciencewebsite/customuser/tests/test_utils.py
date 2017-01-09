from django.test import TestCase
# from custompayment.models import Address
from customuser.utils import get_scientific_account_address_name


class UserTestCase(TestCase):
    # need to do the address thing

    def test_empty_address_name(self):
        res = get_scientific_account_address_name(pk=1)
        self.assertEqual(res, 'Unknown')


