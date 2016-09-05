from django.shortcuts import render
from django.views.generic import UpdateView, DetailView
from customuser.models import User
from django.core.urlresolvers import reverse_lazy
from customuser.forms import CustomUserUpdateForm
# Create your views here.


class UserDetailView(DetailView):
    context_object_name = "user_detail"
    model = User
    template_name = 'customuser/detail_user.html'


class UserUpdateView(UpdateView):
    model = User
    form_class = CustomUserUpdateForm
    template_name = 'customuser/update_user.html'
    success_url = reverse_lazy('view_profile')
