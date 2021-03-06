from django.conf.urls import url
from registration.backends.hmac.views import RegistrationView
from customuser.forms import CustomUserForm
from customuser.views import UserUpdateView, UserDetailView, UserPHDTableView, PHDValidationView, get_phd_image


urlpatterns = [url(r'^register/$', RegistrationView.as_view(form_class=CustomUserForm), name='registration_register'),
               url(r'^edit_profile/$', UserUpdateView.as_view(), name='edit_profile'),
               url(r'^user_profile/(?P<pk>\d)', UserDetailView.as_view(), name='view_profile'),
               url(r'^phd_ask_list/$', UserPHDTableView.as_view(), name='phd_ask_list'),
               url(r'^user_phd/(?P<pk>\d)', PHDValidationView.as_view(), name='user_phd'),
               url(r'^phd_image/(?P<pk>\d)', get_phd_image, name="phd_image"),
]
