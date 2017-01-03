import mock
from django.test import TestCase
from faq.models import Topic, QandA


class TopicTestCase(TestCase):

    def test__str__(self):
        topic = mock.Mock(spec=Topic)
        topic.name = "test name"
        self.assertEqual(Topic.__str__(topic), "test name")


class QandATestCase(TestCase):

    def test__str__(self):
        qanda = mock.Mock(spec=QandA)
        qanda.question = "test question"
        qanda.answer = "test answer"
        self.assertEqual(QandA.__str__(qanda), "test question")