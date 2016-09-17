from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from sendfile import sendfile
from django_tables2 import SingleTableView, RequestConfig
from customuser.models import User
from publications.models import Publication, Comment, Reviewer
from publications.forms import PublicationCreateForm, CommentForm
from publications.tables import PublicationTable
from publications.filters import PublicationFilter, PublicationFilterFormHelper
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
    """
    A class used to combine the filter, the table and the form helper
    """
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
        RequestConfig(self.request, paginate={'page': self.page_kwarg,
                      "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PublicationFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context


class PublicationTableView(PublicationFilteredTableView):
    """
    A class for the publication list with the form and the table
    """
    model = Publication
    table_class = PublicationTable
    template_name = 'publications/publication_list.html'
    paginate_by = 20
    filter_class = PublicationFilter
    formhelper_class = PublicationFilterFormHelper


class PublicationSpecialTableView(SingleTableView):
    """
    A class used to combine the filter and the table (only the ordering is possible the filtering is already done
    as a built-in).
    Filter get only the publications on the science the user follow
    """
    filter_class = None
    context_filter_name = 'filter'
    name = ""
    filter_dict = {}
    model = Publication
    table_class = PublicationTable
    template_name = 'publications/publication_special_list.html'
    paginate_by = 20

    def fill_user_science(self):
        user = User.objects.get(pk=self.request.session['_auth_user_id'])
        sciences = [sid.pk for sid in user.sciences.all()]
        self.filter_dict["sciences"] = sciences

    def get_queryset(self, **kwargs):
        qs = super(PublicationSpecialTableView, self).get_queryset()
        # filter from the user information
        self.fill_user_science()
        self.filter = self.filter_class(self.filter_dict, queryset=qs)
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PublicationSpecialTableView, self).get_table()
        RequestConfig(self.request, paginate={'page': self.page_kwarg,
                      "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PublicationSpecialTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        context['name'] = self.name
        return context


class PublicationToReviewTableView(PublicationSpecialTableView):
    """
    Show the publications about the sciences of the user and in need of peer for a review.
    Only for the user in scientist group
    """
    name = "to review"
    filter_class = PublicationFilter
    filter_dict = {'status': 'adding_peer'}


class PublicationInReviewTableView(PublicationSpecialTableView):
    """
    show the publications about the science of the user and in review. In need of comment
    """
    name = "to comment"
    filter_class = PublicationFilter
    filter_dict = {'status': 'peer_review'}


class PublicationToEvaluateTableView(PublicationSpecialTableView):
    """
    show the publications about the sciences of the user and in evaluation. In need of an estimated impact factor.
    Only for user in the scientist group
    """
    name = "to evaluate"
    filter_class = PublicationFilter
    filter_dict = {'status' : 'evaluation'}


class PublicationDisplay(DetailView):
    context_object_name = "publication_detail"
    model = Publication
    # template_name = 'publications/publication_detail.html'
    fields = ["title", "sciences", "resume", "status", "licence", "publication_score", "estimated_impact_factor",
              "pdf_creation", "source_creation", "pdf_final", "source_final"]

    def get_alert_status(self):
        """
        get the alert status: if validated of not. If validated is there no corrected comment ?
        :return:
        """
        pass

    def get_is_reviewer(self):
        pass


    def get_context_data(self, **kwargs):
        context = super(PublicationDisplay, self).get_context_data(**kwargs)
        # adding comment to the view, better order by
        context['comments'] = Comment.objects.filter(publication=self.kwargs["pk"]).order_by('seriousness')
        # put the initial licence as the licence of the publication
        context['form'] = CommentForm(initial={"licence": Publication.objects.get(pk=self.kwargs["pk"]).licence})
        return context


class PublicationInterest(CreateView):
    # template_name = 'publications/publication_detail.html'
    form_class = CommentForm
    model = Comment

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.publication = Publication.objects.get(pk=self.kwargs["pk"])
        # just to add the right name before the fake pseudo
        if self.object.author_fake_pseudo != "":
            if Reviewer.objects.filter(scientist=self.object.author, publication=self.object.publication).exists():
                self.object.author_fake_pseudo = "Reviewer " + self.object.author_fake_pseudo
            elif self.object.author.groups.filter(name="Scientist").exists():
                self.object.author_fake_pseudo = "Scientist " + self.object.author_fake_pseudo
            else:
                self.object.author_fake_pseudo = "Skeptic " + self.object.author_fake_pseudo
        return super(PublicationInterest, self).form_valid(form)

    # def post(self, request, *args, **kwargs):
    #     print("trigerred")
    #     if not request.user.is_authenticated():
    #         return HttpResponseForbidden()
    #     return super(PublicationInterest, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.kwargs["pk"]})


class PublicationDetailView(View):

    def get(self, request, *args, **kwargs):
        view = PublicationDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PublicationInterest.as_view()
        return view(request, *args, **kwargs)
