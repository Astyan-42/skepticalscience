from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from sendfile import sendfile
from publications.models import Publication
from publications.forms import PublicationCreateForm
# Create your views here.


def download(request, field_name, publication_id):
    dl = get_object_or_404(Publication, pk=publication_id)
    # not using eval for security reasons
    if field_name == "pdf_creation":
        return sendfile(request, dl.pdf_creation.path)
    elif field_name == "source_creation":
        return sendfile(request, dl.source_creation.path)
    elif field_name == "pdf_final":
        return sendfile(request, dl.pdf_final.path)
    elif field_name == "source_final":
        return sendfile(request, dl.source_final.path)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.publication.can_add_publication', raise_exception=True),
                  name='dispatch')
class PublicationCreate(CreateView):
    model = Publication
    name = "Submit publication"
    form_class = PublicationCreateForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.editor = self.request.user
        obj.save()
        print(obj.sciences.all())
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(PublicationCreate, self).get_context_data(**kwargs)
        context['name'] = self.name
        return context
