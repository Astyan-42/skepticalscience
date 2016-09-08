from django import forms
from django_select2.forms import Select2MultipleWidget
from publications.models import Publication
from sciences.models import Science


def science_choices(queryset, prefix=''):
    choices = []
    for science in queryset:
        choices.append((science.id, prefix+science.__str__()))
        res = science_choices(science.sub_science.all(), prefix=prefix+'-')
        choices = choices + res
    return choices


class PublicationCreateForm(forms.ModelForm):
    """
    create an user form with restricted field (the field could be directly in the view, used the for
    """
    class Meta:
        model = Publication
        fields = ["title", "resume_creation", "pdf_creation", "source_creation", "sciences", "licence"]
        widgets = {'sciences': Select2MultipleWidget,
                   'resume_creation': forms.Textarea(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super(PublicationCreateForm, self).__init__(*args, **kwargs)
        sciences = Science.objects.filter(primary_science=True)
        choices = science_choices(sciences)
        self.fields["sciences"].choices = choices



