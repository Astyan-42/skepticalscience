from django.conf.urls import url
from publications.views import (PublicationCreate, PublicationCorrectionUpdate, PublicationAbortUpdate,
                                download, PublicationTableView, PublicationToReviewTableView,
                                PublicationInReviewTableView, PublicationToEvaluateTableView, PublicationDetailView,
                                PublicationOwnedTableView, become_reviewer_view, leave_reviewer_view,
                                CommentDetailView)

urlpatterns = [url(r'^new_publication/$', PublicationCreate.as_view(), name="create_publication"),
               url(r'^correct_publication/(?P<pk>\d+)$', PublicationCorrectionUpdate.as_view(),
                   name="correct_publication"),
               url(r'^abort_publication/(?P<pk>\d+)$', PublicationAbortUpdate.as_view(),
                   name="abort_publication"),
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
               url(r'become_reviewer/(?P<publication_id>\d+)/$', become_reviewer_view, name="become_reviewer"),
               url(r'leave_reviewer/(?P<publication_id>\d+)/$', leave_reviewer_view, name="leave_reviewer"),
               url(r'^comment_detail/(?P<pk>\d+)$', CommentDetailView.as_view(),
                   name="comment_view")
]
