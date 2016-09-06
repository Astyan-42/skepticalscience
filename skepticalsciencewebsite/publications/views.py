from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from publications.models import Publication
# Create your views here.


class PublicationCreate(CreateView):
    model = Publication
    fields = ["sciences", "title", "tags", "licence"]