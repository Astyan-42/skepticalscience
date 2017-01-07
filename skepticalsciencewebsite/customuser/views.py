from django.views.generic import UpdateView, DetailView, View
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_tables2 import SingleTableView, RequestConfig
from sendfile import sendfile
from customuser.models import User
from customuser.forms import CustomUserUpdateForm, CheckPHDForm
from customuser.filters import UserFilter
from customuser.tables import UserTable
from customuser.utils import get_scientific_account_address_name
from custompayment.constants import SCIENTIST_ACCOUNT
# Create your views here.


@login_required
@staff_member_required
def get_phd_image(request, pk):
    dl = get_object_or_404(User, pk=pk)
    return sendfile(request, dl.phd_image.path)


class UserDetailView(DetailView):
    """
    DetailView for an user
    """
    context_object_name = "user_detail"
    model = get_user_model()
    template_name = 'customuser/detail_user.html'
    fields = ["first_name", "middle_name", "last_name", "phd", "country", "workplace", "description",
              "job_title", "sciences", "skeptic_score", "mean_publication_score", "mean_impact_factor",
              "estimator_score", "phd_in"]

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        if context["user_detail"].groups.filter(name="Scientist").exists():
            context["account_status"] = _("Scientist")
        else:
            context["account_status"] = _("Skeptic")
        context["order"] = SCIENTIST_ACCOUNT
        return context


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    """
    UpdateView made available only for logged user (the decorator). The user will change is own profile (get_object)
    """
    model = get_user_model()
    form_class = CustomUserUpdateForm
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


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserPHDTableView(SingleTableView):
    model = User
    filter_class = UserFilter
    context_filter_name = 'filter'
    table_class = UserTable
    template_name = 'customuser/list_user_phd.html'
    paginate_by = 20
    object = None
    request = None
    filter = None

    def get_queryset(self, **kwargs):
        qs = super(UserPHDTableView, self).get_queryset()
        filter_dict = {'phd_to_rate': True}
        self.filter = self.filter_class(filter_dict, queryset=qs)
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(UserPHDTableView, self).get_table()
        RequestConfig(self.request, paginate={'page': self.page_kwarg,
                      "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(UserPHDTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PHDValidation(UpdateView):
    form_class = CheckPHDForm
    context_object_name = "user_detail"
    model = User
    template_name = "customuser/check_phd_user.html"

    def get_object(self, queryset=None):
        obj, created = User.objects.get_or_create(pk=self.kwargs["pk"])
        return obj

    def get_context_data(self, **kwargs):
        context = super(PHDValidation, self).get_context_data(**kwargs)
        context["address_name"] = get_scientific_account_address_name(pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return reverse_lazy("phd_ask_list")


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PHDDisplay(DetailView):
    context_object_name = "user_detail"
    model = User
    object = None
    template_name = "customuser/check_phd_user.html"

    def get_context_data(self, **kwargs):
        context = super(PHDDisplay, self).get_context_data(**kwargs)
        context["form"] = CheckPHDForm()
        # for the address get the item then get the order and get the addess
        context["address_name"] = get_scientific_account_address_name(pk=self.kwargs["pk"])
        return context


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PHDValidationView(View):
    # template_name = "customuser/check_phd_user.html"

    @staticmethod
    def get(request, *args, **kwargs):
        view = PHDDisplay.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        view = PHDValidation.as_view()
        return view(request, *args, **kwargs)

