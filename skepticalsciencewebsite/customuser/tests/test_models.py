import mock
from django.test import TestCase
from django.utils import timezone
from django.core.files import File
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

    def test_print_phd_sciences(self):
        user = mock.Mock(spec=User)
        user.phd = False
        self.assertEqual(User.print_phd_sciences(user), False)
        user.phd = True
        self.assertEqual(User.print_phd_sciences(user), True)

    def test_print_phd_non_accepted(self):
        user = mock.Mock(spec=User)
        user.phd = False
        user.phd_rate_date = None
        self.assertEqual(User.print_phd_non_accepted(user), False)
        user.phd_rate_date = timezone.now()
        self.assertEqual(User.print_phd_non_accepted(user), True)

    def test_get_to_rate(self):
        user = mock.Mock(spec=User)
        user.phd = False
        user.phd_image = mock.MagicMock(spec=File, name='FileMock')
        user.phd_rate_date = None
        self.assertEqual(User.get_to_rate(user), True)
        user.phd_rate_date = timezone.now()
        user.phd_update_date = timezone.now()
        self.assertEqual(User.get_to_rate(user), True)
        user.phd_update_date = timezone.now()
        user.phd_rate_date = timezone.now()
        self.assertEqual(User.get_to_rate(user), False)
        user.phd_rate_date = timezone.now()
        user.phd_update_date = timezone.now()
        user.phd = True
        self.assertEqual(User.get_to_rate(user), False)