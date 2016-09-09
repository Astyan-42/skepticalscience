from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from sendfile import sendfile
from django_tables2 import SingleTableView
from publications.models import Publication, PublicationFilter, PublicationFilterFormHelper, PublicationTable
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


class PublicationFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = super(PublicationFilteredTableView, self).get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PublicationFilteredTableView, self).get_table()
        PublicationFilteredTableView(self.request, paginate={'page': self.kwargs['page'],
                            "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PublicationFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


class PublicationTableView(PublicationFilteredTableView):
    model = Publication
    table_class = PublicationTable
    template_name = 'publication/publication_list.html'
    paginate_by = 50
    filter_class = PublicationFilter
    formhelper_class = PublicationFilterFormHelper