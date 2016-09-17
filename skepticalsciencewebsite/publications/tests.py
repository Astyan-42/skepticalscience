from django.test import TestCase
from publications.models import Publication, Licence
from customuser.models import User

# Create your tests here.


class PublicationTestCase(TestCase):

    def setUp(self):
        """
        Store an user
        """
        jesus = User.objects.create(username="testuser", password="azerty123", phd=True, first_name="Jesus",
                                    middle_name="Our Savior", last_name="Raptor", email="testpub1@test.com")
        fsm = User.objects.create(username="testuser2", password="azerty123", phd=True, first_name="Flying",
                                  middle_name="Spaghetti", last_name="Monster", email="testpub2@test.com")
        l = Licence.objects.create(short_name="lol", full_name="lol", url="http://google.com")
        Publication.objects.create(editor=jesus, title="lol", first_author=jesus, last_author=fsm, resume="lol",
                                   licence=l)

    def test_get_all_authors(self):
        publi = Publication.objects.get(title="lol")
        self.assertEqual(2, len(publi.get_all_authors()))