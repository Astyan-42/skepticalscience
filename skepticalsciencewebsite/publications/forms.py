from django import forms
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from publications.models import Publication, Comment
from sciences.forms import ScienceModelForm
from customuser.models import User


class UserModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.get_full_name()


class PublicationCreateForm(ScienceModelForm):
    """
    create an publication form with restricted field
    """
    first_author=UserModelChoiceField(queryset=User.objects.filter(~Q(first_name="") & ~Q(last_name="")))

    def __init__(self, *args, **kwargs):
        super(PublicationCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-publicationcreateForm'
        self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = Publication
        fields = ["title", "resume", "pdf_creation", "source_creation", "first_author", "sciences", "licence"]
        widgets = {'sciences': Select2MultipleWidget,
                   'resume': forms.Textarea()}


class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-commentForm'
        self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = Comment
        fields = ["author_fake_pseudo", "comment_type", "title", "content"]
        widgets = {'content': forms.Textarea()}
