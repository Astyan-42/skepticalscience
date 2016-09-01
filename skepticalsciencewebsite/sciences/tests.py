from django.test import TestCase
from sciences.models import Science
# Create your tests here.


class ScienceTestCase(TestCase):
    """
    Test the Science model
    """

    def setUp(self):
        """
        Store two Science object in the database, one being "the son" of the other
        """
        dataanalysis = Science.objects.create(name="DataAnalysis", description="a computer science")
        computerscience = Science.objects.create(name="ComputerScience", description="the computer science",
                                                 primary_science=True)
        computerscience.sub_science.add(dataanalysis)

    def test_affiliation(self):
        """
        Get the two object of the database and test if there is one accessible from the other one
        and the first one must not be accessible from the second one
        """
        dataanalysis = Science.objects.get(name="DataAnalysis")
        computerscience = Science.objects.get(name="ComputerScience")
        # test computer_science is a primary_science
        self.assertEqual(computerscience.primary_science, True)
        # test dataanalysis is a subscience of computerscience
        self.assertEqual(computerscience.sub_science.all()[0], dataanalysis)
        # test dataanalysis have no subscience
        self.assertEqual(len(dataanalysis.sub_science.all()), 0)
