from django.test import TestCase
from customuser.models import User
# from django.core.mail import send_mail
# Create your tests here.

# doesnt work
# class SendEmailTest(TestCase):
#
#     def test_send_mail(self):
#         res = send_mail('test', 'core', 'localhost', ['localhost'], fail_silently=False)
#         # One message send
#         self.assertEqual(res, 1)


class UserTestCase(TestCase):

    def setUp(self):
        jesus = User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                    middle_name="Our Savior", last_name="Raptor")

    def test_saving(self):
        jesus = User.objects.get(username="testuser")
        self.assertEqual(jesus.phd, True)
        self.assertEqual(jesus.first_name, "Jesus")
        self.assertEqual(jesus.middle_name, "Our Savior")
        self.assertEqual(jesus.last_name, "Raptor")
