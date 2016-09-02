from django.test import TestCase
from django.core.mail import send_mail
# Create your tests here.


class SendEmailTest(TestCase):

    def test_send_mail(self):
        res = send_mail('test', 'core', 'localhost', ['localhost'], fail_silently=False)
        # One message send
        self.assertEqual(res, 1)
