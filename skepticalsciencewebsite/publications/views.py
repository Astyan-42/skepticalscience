from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from publications.models import Publication
from publications.forms import PublicationCreateForm
# Create your views here.


class PublicationCreate(CreateView):
    model = Publication
    form_class = PublicationCreateForm
    success_url = reverse_lazy("index")