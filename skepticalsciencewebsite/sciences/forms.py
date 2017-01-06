from django import forms
from django.db.utils import OperationalError
from sciences.models import Science


def _science_choices(queryset, prefix=''):
    """
    Transform the queryset in choices. Used to add '-' in front of subscience
    :param queryset: A science queryset (should be only with primary science
    :param prefix: the recursive prefix a str compatible with the  regex '-*'
    :return: a choice list
    :rtype: list((int, str))
    """
    choices = []
    try:
        queryset = sorted(queryset, key=lambda science: science.name)
        for science in queryset:
            choices.append((science.id, prefix+science.__str__()))
            res = _science_choices(science.sub_science.all(), prefix=prefix+'-')
            choices = choices + res
    except OperationalError:
        pass # for the creation of the db

    return choices


class ScienceModelForm(forms.ModelForm):
    """
    A modelform with science choices already made
    """

    def __init__(self, *args, **kwargs):
        super(ScienceModelForm, self).__init__(*args, **kwargs)
        sciences = Science.objects.filter(primary_science=True)
        choices = _science_choices(sciences)
        science_field = kwargs.get("science_field", "sciences")
        self.fields[science_field].choices = choices
