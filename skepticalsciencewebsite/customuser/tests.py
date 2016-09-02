from django.test import TestCase
from django.core.mail import send_mail
# Create your tests here.


class SendEmailTest(TestCase):

    @staticmethod
    def test_send_mail():
        send_mail(
            'Test of mail configuration with send_mail function',
            'Reading is useless.',
            'localhost',
            ['localhost'],
            fail_silently=False,
        )
