import mock
from django.test import TestCase
from faq.models import Topic, QandA


class TopicTestCase(TestCase):

    def test__str__(self):
        topic = mock.Mock(spec=Topic)
        self.assertEqual(Topic.__str__(topic), topic.name)


class QandATestCase(TestCase):

    def test__str__(self):
        qanda = mock.Mock(spec=QandA)
        self.assertEqual(QandA.__str__(qanda), qanda.question)