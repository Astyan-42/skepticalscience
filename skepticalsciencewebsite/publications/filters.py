import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Field
from crispy_forms.layout import Layout, Submit
from django_select2.forms import Select2MultipleWidget
from sciences.models import Science
from sciences.forms import _science_choices
from customuser.models import User
from publications.models import Publication, PUBLICATION_STATUS

PUBLICATION_STATUS_AND_EMPTY = [('','All status')] + PUBLICATION_STATUS


class PublicationFilter(django_filters.FilterSet):
    """
    a filter used in publication with wanted field to filter done
    """
    sciences = django_filters.MultipleChoiceFilter(
        choices=_science_choices(Science.objects.filter(primary_science=True)),
        widget=Select2MultipleWidget
    )
    editor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        empty_label="All editors"
    )
    status = django_filters.ChoiceFilter(
        choices= PUBLICATION_STATUS_AND_EMPTY
    )
    estimated_impact_factor = django_filters.NumberFilter(lookup_expr='gte')
    publication_score = django_filters.NumberFilter(lookup_expr='gte')
    title = django_filters.CharFilter(lookup_expr='icontains')
    resume = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Publication
        fields = ["editor", "sciences", "title", "status", "estimated_impact_factor", "publication_score",
                  "resume"]


class PublicationFilterFormHelper(FormHelper):
    """
    A form helper to create a form to filter the publication with the filter we like.
    Contain the field we want, there parameter, a template, and a class to add to the form
    """
    model = Publication
    form_class = 'form-inline' # this force us to make science of a bigger size
    field_template = 'bootstrap3/layout/inline_field.html'
    help_text_inline = True
    form_id = 'id_filterForm'
    form_method = 'get'
    layout = Layout("title", "status", "editor", "resume",
                    Field("sciences", style="min-width: 320px;", template=field_template),
                    Field("estimated_impact_factor", placeholder="(Minimal)", min=0., value="",
                          template=field_template),
                    Field("publication_score", placeholder="(Minimal)", min=0, value="", template=field_template),
                    FormActions(Submit('submit_filter', 'Filter'))
                                # Reset('reset_filter', 'Reset')
                                # Button('clear', 'Clear')
                    )