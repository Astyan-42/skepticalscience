from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from sendfile import sendfile
from publications.models import Publication
from publications.forms import PublicationCreateForm
# Create your views here.


def download(request, field_name, publication_id):
    """
    Download view, used to download any file in a publication
    :param request: the http request
    :param field_name: the name of the field (must be a filefield)
    :param publication_id: the id of the publication where download the file
    :return: the download
    """
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
    """
    Create a new publication
    """
    model = Publication
    name = "Submit publication"
    form_class = PublicationCreateForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        """
        form_valid modified method to add the user as the editor
        :param form: the form
        :return: the form_valid function of the parent applied to the form
        """
        # get the object from the form
        self.object = form.save(commit=False)
        # add the editor in object
        self.object.editor = self.request.user
        # call the parent to save correctly the ManyToManyField (sciences)
        return super(CreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        add the name to the context (useful for the template)
        :param kwargs: named arguments
        :return: the context
        """
        context = super(PublicationCreate, self).get_context_data(**kwargs)
        context['name'] = self.name
        return context
