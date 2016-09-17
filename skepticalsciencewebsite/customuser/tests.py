from django.test import TestCase
from customuser.models import User
from django.core.exceptions import ValidationError
# Create your tests here.


class UserTestCase(TestCase):
    """
    Test Our User model
    """

    def setUp(self):
        """
        Store an user
        """
        jesus = User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                    middle_name="Our Savior", last_name="Raptor")

    def test_saving(self):
        """
        Get and test the user we store
        """
        jesus = User.objects.get(username="testuser")
        self.assertEqual(jesus.phd, True)
        self.assertEqual(jesus.first_name, "Jesus")
        self.assertEqual(jesus.middle_name, "Our Savior")
        self.assertEqual(jesus.last_name, "Raptor")
        self.assertEqual(jesus.get_full_name(), "Raptor Our Savior Jesus")
        self.assertEqual(jesus.get_short_name(), "Jesus")

    def test_ban_username(self):
        """
        Test if non wanted name are banned
        """
        userres = User.objects.create(username="Skeptic 42", password="azerty123", phd=True, first_name="Jesus",
                                      middle_name="Our Savior", last_name="Raptor", email="testbanusername@test.com")
        self.assertRaises(ValidationError, userres.full_clean)
