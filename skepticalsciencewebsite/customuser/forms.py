from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from registration.forms import RegistrationFormTermsOfService
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget
from sciences.forms import ScienceModelForm
from skepticalsciencewebsite.utils import NoLinkClearableFileInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CustomUserForm(RegistrationFormTermsOfService):
    """
    Registration for, using, username and email (password is automaticaly add)
    """
    class Meta:
        model = get_user_model()
        fields = ["username", "email"]


class CustomUserUpdateForm(ScienceModelForm):
    """
    create an user form with restricted field (the field could be directly in the view, used the for
    """

    def __init__(self, *args, **kwargs):
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-userupdateForm'
        self.helper.add_input(Submit('submit', _('Submit')))

    def save(self, commit=True):
        data = super(CustomUserUpdateForm, self).save(commit=False)
        if self.cleaned_data["phd_image"]:
            imgpath = str(self.cleaned_data["phd_image"])
            if imgpath.split('/')[0] != "PHDs":
                data.phd_update_date = timezone.now()
        if commit:
            data.save()
        return data

    class Meta:
        model = get_user_model()
        fields = ["email", "first_name", "middle_name", "last_name", "phd_image", "country", "workplace", "description",
                  "job_title", "sciences"]
        # widgets = {'sciences': Select2MultipleWidget(attrs={'class': 'form-control'})}
        widgets = {'sciences': Select2MultipleWidget,
                   'description': forms.Textarea(),
                   'phd_image':NoLinkClearableFileInput,
                   }


class CheckPHDForm(ScienceModelForm):

    def __init__(self, *args, **kwargs):
        kwargs['science_field'] = 'phd_in'
        super(CheckPHDForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-checkphdForm'
        self.helper.add_input(Submit('submit', _('Submit')))

    # on save change the date
    def save(self, commit=True):
        data = super(CheckPHDForm, self).save(commit=False)
        data.phd_rate_date = timezone.now()
        if commit:
            data.save()
        return data

    class Meta:
        model = get_user_model()
        fields = ["phd", "phd_comment", "phd_in"]
        widgets = {'phd_in': Select2MultipleWidget,
                   }