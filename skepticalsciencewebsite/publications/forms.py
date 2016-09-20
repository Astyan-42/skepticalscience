from django import forms
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import Field
from publications.models import Publication, Comment, EstimatedImpactFactor, CommentReview
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


class EstimatedImpactFactorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EstimatedImpactFactorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_id = 'id-estimatedimpactfactorForm'
        self.helper.layout = Layout(Field("estimated_impact_factor", min=0, max=1000, value="",
                                    template=self.helper.field_template))
        self.helper.add_input(Submit('submit', _('Evaluate')))

    class Meta:
        model = EstimatedImpactFactor
        fields = ["estimated_impact_factor"]


class CommentReviewValidationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentReviewValidationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-commentreviewvalidationForm'
        self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = CommentReview
        fields = ["valid", "seriousness", "reason_validation"]
        widgets = {'reason_validation': forms.Textarea()}
