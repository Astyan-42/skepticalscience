import django_tables2 as tables
from django_tables2.utils import A
from publications.models import Publication


class GoodScience(tables.Column):

    def render(self, value):
        sciences = sorted([science.name for science in value.all()])
        sciences = ", ".join(sciences)
        return sciences


class PublicationTable(tables.Table):
    sciences = GoodScience()
    # temporary use the futur view of the publication
    link = tables.LinkColumn("download_publication", text="publication", kwargs={"field_name" : "pdf_creation",
                                                                                 "publication_id" : A('pk')})

    class Meta:
        model = Publication
        fields = ["editor", "sciences", "title", "status", "estimated_impact_factor", "publication_score"]
        attrs = {"class": "table table-responsive paleblue"}
