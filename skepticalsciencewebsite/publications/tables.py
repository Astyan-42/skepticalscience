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

class PublicationTable(tables.Table):
    """
    a table to represent a list of publication
    """
    sciences = GoodScience()
    authors = GoodScience()
    # temporary use the futur view of the publication
    link = tables.LinkColumn("publication_view", text="publication", kwargs={"pk" : A('pk')})

    class Meta:
        model = Publication
        fields = ["editor", "authors", "sciences", "title", "status", "estimated_impact_factor", "publication_score"]
        attrs = {"class": "table table-responsive paleblue"}
