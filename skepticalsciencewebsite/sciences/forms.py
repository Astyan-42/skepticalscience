from django import forms
from sciences.models import Science


def _science_choices(queryset, prefix=''):
    choices = []
    queryset = sorted(queryset, key=lambda science: science.name)
    for science in queryset:
        choices.append((science.id, prefix+science.__str__()))
        res = _science_choices(science.sub_science.all(), prefix=prefix+'-')
        choices = choices + res
    return choices


class ScienceModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ScienceModelForm, self).__init__(*args, **kwargs)
        sciences = Science.objects.filter(primary_science=True)
        choices = _science_choices(sciences)
        self.fields["sciences"].choices = choices
