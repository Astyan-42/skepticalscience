from django.conf.urls import url
from publications.views import PublicationCreate

urlpatterns = [url(r'^new_publication/$', PublicationCreate.as_view(), name="create_publication"),
]
