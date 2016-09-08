from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from sendfile import sendfile
from publications.models import Publication
from publications.forms import PublicationCreateForm
# Create your views here.


def download(request, publication_id):
    dl = get_object_or_404(Publication, pk=publication_id)
    return sendfile(request, dl.pdf_creation.path)


@method_decorator(login_required, name='dispatch')
class PublicationCreate(CreateView):
    model = Publication
    form_class = PublicationCreateForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.editor = self.request.user
        obj.save()
        print(obj.sciences.all())
        return HttpResponseRedirect(self.success_url)
