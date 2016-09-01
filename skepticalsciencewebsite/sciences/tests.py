from django.test import TestCase
from sciences.models import Science

# Create your tests here.
class ScienceTestCase(TestCase):
    def setUp(self):
        dataanalysis = Science.objects.create(name="DataAnalysis", description="a computer science")
        computerscience = Science.objects.create(name="ComputerScience", description="the computer science",
                                                 primary_science=True)
        computerscience.sub_science.add(dataanalysis)

    def test_affiliation(self):
        dataanalysis = Science.objects.get(name="DataAnalysis")
        computerscience = Science.objects.get(name="ComputerScience")
        # test computer_science is a primary_science
        self.assertEqual(computerscience.primary_science, True)
        # test dataanalysis is a subscience of computerscience
        self.assertEqual(computerscience.sub_science.all()[0], dataanalysis)
        # test dataanalysis have no subscience
        self.assertEqual(len(dataanalysis.sub_science.all()), 0)


