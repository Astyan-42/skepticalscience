from django.conf.urls import url
from publications.views import (PublicationCreate, download, PublicationTableView, PublicationToReviewTableView,
                                PublicationInReviewTableView, PublicationToEvaluateTableView, PublicationDetailView,
                                PublicationOwnedTableView, become_reviewer_view)

urlpatterns = [url(r'^new_publication/$', PublicationCreate.as_view(), name="create_publication"),
               url(r'^download_publication/(?P<field_name>\w+)/(?P<publication_id>\d+)/$', download,
                   name="download_publication"),
               url(r'^publication_list/$', PublicationTableView.as_view(), name="publication_list"),
               url(r'^publication_to_review/$', PublicationToReviewTableView.as_view(),name="publication_to_review"),
               url(r'^publication_in_review/$', PublicationInReviewTableView.as_view(), name="publication_in_review"),
               url(r'^publication_to_evaluate/$', PublicationToEvaluateTableView.as_view(),
                   name="publication_to_evaluate"),
               url(r'^publication_owned/$', PublicationOwnedTableView.as_view(), name="publication_owned"),
               url(r'publication_detail/(?P<pk>\d+)/$', PublicationDetailView.as_view(),
                   name="publication_view"),
               url(r'^comment_evaluation/$', PublicationToEvaluateTableView.as_view(),
                   name="comment_evaluation"),
               url(r'become_reviewer/(?P<publication_id>\d+)/$',become_reviewer_view, name="become_reviewer")
]
