from django import forms
from django_select2.forms import Select2MultipleWidget
from publications.models import Publication


class PublicationCreateForm(forms.ModelForm):
    """
    create an user form with restricted field (the field could be directly in the view, used the for
    """
    class Meta:
        model = Publication
        fields = ["title", "resume_creation", "pdf_creation", "sciences", "licence"]
        widgets = {'sciences': Select2MultipleWidget,
                   'resume_creation': forms.Textarea(attrs={'class': 'form-control'})}
