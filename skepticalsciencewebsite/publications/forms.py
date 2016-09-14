from django import forms
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget
from publications.models import Publication
from sciences.forms import ScienceModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class PublicationCreateForm(ScienceModelForm):
    """
    create an publication form with restricted field
    """
    def __init__(self, *args, **kwargs):
        super(PublicationCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-publicationcreateForm'
        self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = Publication
        fields = ["title", "resume", "pdf_creation", "source_creation", "sciences", "licence"]
        widgets = {'sciences': Select2MultipleWidget,
                   'resume_creation': forms.Textarea(attrs={'class': 'form-control'})}
