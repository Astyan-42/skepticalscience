from django.conf.urls import url
from pdfinvoce.views import print_users

urlpatterns = [url(r'^$', print_users, name='invoce')]