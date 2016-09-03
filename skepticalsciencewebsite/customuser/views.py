from django.shortcuts import render
from django.views.generic import UpdateView, DetailView
from customuser.models import User
# Create your views here.


class UserDetailView(DetailView):
    model = User
    # template_name = 'customuser/detail_user.html'

class UserUpdateView(UpdateView):
    model = User
    # fields = ["email", "first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
    #           "job_title", "sciences"]
    # template_name = 'customuser/update_user.html'
