from django.conf.urls import url
from publications.views import PublicationCreate, download, PublicationTableView

urlpatterns = [url(r'^new_publication/$', PublicationCreate.as_view(), name="create_publication"),
               url(r'^download_publication/(?P<field_name>\w+)/(?P<publication_id>\d+)/$', download,
                   name="download_publication"),
               url(r'^publication_list/$', PublicationTableView.as_view(), name="publication_list")
]
