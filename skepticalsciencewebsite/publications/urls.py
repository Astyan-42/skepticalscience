from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from publications.views import PublicationCreate, download

urlpatterns = [url(r'^new_publication/$', PublicationCreate.as_view(), name="create_publication"),
               url(r'^download_publication/(?P<field_name>\w+)/(?P<publication_id>\d+)/$', download, name="download_publication")
]
