from django.shortcuts import render
from django.views.generic import UpdateView, DetailView
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from customuser.models import User
from customuser.forms import CustomUserUpdateForm
# Create your views here.


class UserDetailView(DetailView):
    """
    DetailView for an user
    """
    context_object_name = "user_detail"
    model = User
    template_name = 'customuser/detail_user.html'
    fields = ["first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
              "job_title", "sciences", "skeptic_score", "mean_publication_score", "mean_impact_factor",
              "estimator_score"]

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        if context["user_detail"].groups.filter(name="Scientist").exists():
            context["account_status"] = _("Scientist")
        else:
            context["account_status"] = _("Skeptic")
        return context


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    """
    UpdateView made available only for logged user (the decorator). The user will change is own profile (get_object)
    """
    model = User
    form_class = CustomUserUpdateForm
    # fields = ["email", "first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
    #           "job_title", "sciences"]
    template_name = 'customuser/update_user.html'

    def get_object(self, queryset=None):
        """
        Get the user object of the logged user
        :return: the user filled model
        """
        return get_object_or_404(User, pk=self.request.session['_auth_user_id'])

    def get_success_url(self):
        """
        give the url of the user profile
        :return: The success url
        """
        return reverse_lazy('view_profile', args=(self.request.session['_auth_user_id'],))
