from django.shortcuts import render
from django.views.generic import UpdateView, DetailView
from customuser.models import User
from django.core.urlresolvers import reverse_lazy
from customuser.forms import CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.


class UserDetailView(DetailView):
    context_object_name = "user_detail"
    model = User
    template_name = 'customuser/detail_user.html'


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    form_class = CustomUserUpdateForm
    template_name = 'customuser/update_user.html'
    success_url = reverse_lazy('view_profile')
