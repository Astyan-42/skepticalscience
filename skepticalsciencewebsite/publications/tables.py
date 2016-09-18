from django.utils.translation import ugettext_lazy as _
import django_tables2 as tables
from django_tables2.utils import A
from publications.models import Publication


class GoodScience(tables.Column):
    """
    The good way to print the science in the talbe
    """
    def render(self, value):
        sciences = sorted([science.name for science in value.all()])
        sciences = ", ".join(sciences)
        return sciences


class GoodAuthor(tables.Column):

    def render(self, value):
        authors = sorted([author.get_full_name() for author in value])
        authors = ", ".join(authors)
        return authors


class PublicationTable(tables.Table):
    """
    a table to represent a list of publication
    """
    sciences = GoodScience()
    get_all_authors = GoodAuthor(orderable=False, verbose_name=_("Authors"))
    # temporary use the futur view of the publication
    link = tables.LinkColumn("publication_view", text="publication", kwargs={"pk" : A('pk')}, orderable=False)

    class Meta:
        model = Publication
        fields = ["get_all_authors", "sciences", "title", "status", "estimated_impact_factor", "publication_score"]
        attrs = {"class": "table table-responsive paleblue"}
