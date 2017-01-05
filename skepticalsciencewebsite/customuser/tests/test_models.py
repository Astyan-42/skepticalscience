import mock
from django.test import TestCase
from customuser.models import User


class UserTestCase(TestCase):

    def test_get_full_name(self):
        user = mock.Mock(spec=User)
        user.last_name = 'Test'
        user.middle_name = ''
        user.first_name = 'Test2'
        full_name_res = User.get_full_name(user)
        full_name_test = str(user.last_name)+" "+str(user.first_name)
        self.assertEqual(full_name_res, str(full_name_test))

    def test_get_full_name_empty(self):
        user = mock.Mock(spec=User)
        user.last_name = ''
        user.middle_name = ''
        user.first_name = ''
        full_name_res = User.get_full_name(user)
        full_name_test = ''
        self.assertEqual(full_name_res, str(full_name_test))