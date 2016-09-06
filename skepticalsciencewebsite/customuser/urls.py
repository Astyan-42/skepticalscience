from django.conf.urls import url
from registration.backends.hmac.views import RegistrationView
from customuser.forms import CustomUserForm
from customuser.views import UserUpdateView, UserDetailView


urlpatterns = [url(r'^register/$', RegistrationView.as_view(form_class=CustomUserForm), name='registration_register'),
               url(r'^edit_profile/$', UserUpdateView.as_view(), name='edit_profile'),
               url(r'^user_profile/(?P<pk>\d)', UserDetailView.as_view(), name='view_profile'),
]
