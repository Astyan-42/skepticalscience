from django.shortcuts import render
from django.views.generic import UpdateView, DetailView
from customuser.models import User
from django.core.urlresolvers import reverse_lazy
from customuser.forms import CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
# Create your views here.


class UserDetailView(DetailView):
    context_object_name = "user_detail"
    model = User
    template_name = 'customuser/detail_user.html'
    fields = ["first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
              "job_title", "sciences", "skeptic_score", "mean_publication_score", "mean_impact_factor",
              "estimator_score"]


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    form_class = CustomUserUpdateForm
    template_name = 'customuser/update_user.html'
    success_url = reverse_lazy('edit_profile')

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.session['_auth_user_id'])