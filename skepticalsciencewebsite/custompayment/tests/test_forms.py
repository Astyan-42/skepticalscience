# import datetime
# from django.test import TestCase
# from django.utils import timezone
# from custompayment.forms import DiscountOrderForm
# from custompayment.models import Discount

# just far to bothering with the interaction with the model, just test the view
# class DiscountOrderFormTestCase(TestCase):
    #  need to register a discount
    # def setUp(self):
    #     sdate = timezone.now()-datetime.timedelta(days=1)
    #     edate = timezone.now() + datetime.timedelta(days=1)
    #     self.discount = Discount(name='test', code='test', discount_value=20., starting_date=sdate, ending_date=edate)
    #     self.discount.save()

    # def test_valid(self):
    #     form_data = {'discount': 'test'}
    #     form = DiscountOrderForm(data=form_data)
    #     self.assertTrue(form.is_valid())

