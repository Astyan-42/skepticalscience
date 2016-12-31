from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic import View
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from sendfile import sendfile
from django_tables2 import SingleTableView, RequestConfig
from skepticalsciencewebsite.utils import same_user, check_status
from custompayment.constants import PUBLICATION
from publications.models import Publication, Comment, Reviewer, EstimatedImpactFactor, CommentReview
from publications.forms import (PublicationCreateForm, CommentForm, EstimatedImpactFactorForm,
                                CommentReviewValidationForm, CommentReviewCorrectionForm, PublicationCorrectForm,
                                PublicationAbortForm)
from publications.tables import PublicationTable
from publications.filters import PublicationFilter, PublicationFilterFormHelper
from publications.constants import *
from publications.cascade import update_comment_validation, update_comment_correction, update_user_skeptic_score
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
@method_decorator(permission_required('publications.add_publication', raise_exception=True),
                  name='dispatch')
class PublicationCreate(CreateView):
    """
    Create a new publication
    """
    model = Publication
    name = "Submit publication"
    form_class = PublicationCreateForm
    object = None

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
        return super(PublicationCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        add the name to the context (useful for the template)
        :param kwargs: named arguments
        :return: the context
        """
        context = super(PublicationCreate, self).get_context_data(**kwargs)
        context['name'] = self.name
        return context

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.object.id})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.change_publication', raise_exception=True),
                  name='dispatch')
class PublicationUpdate(UpdateView):
    model = Publication
    name = "Edit publication"
    form_class = PublicationCreateForm
    template_name = 'publications/publication_correct_form.html'
    object = None

    @same_user("editor")
    @check_status(WAITING_PAYMENT, "status")
    def form_valid(self, form):
        """
        form_valid modified method to add the user as the editor
        :param form: the form
        :return: the form_valid function of the parent applied to the form
        """
        print("haha")
        self.object = form.save(commit=False)
        return super(PublicationUpdate, self).form_valid(form)

    @same_user("editor")
    @check_status(WAITING_PAYMENT, "status")
    def get_context_data(self, **kwargs):
        """
        add the name to the context (useful for the template)
        :param kwargs: named arguments
        :return: the context
        """
        context = super(PublicationUpdate, self).get_context_data(**kwargs)
        context['name'] = self.name
        context['constants'] = CONSTANTS_TEMPLATE
        return context

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.object.id})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.change_publication', raise_exception=True),
                  name='dispatch')
class PublicationCorrectionUpdate(UpdateView):
    model = Publication
    name = "Correct publication"
    form_class = PublicationCorrectForm
    template_name = 'publications/publication_edit_form.html'
    object = None
    request = None

    @same_user("editor")
    @check_status(CORRECTION, "status")
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(PublicationCorrectionUpdate, self).form_valid(form)

    @same_user("editor")
    @check_status(CORRECTION, "status")
    def get_context_data(self, **kwargs):
        """
        add the name to the context (useful for the template)
        :param kwargs: named arguments
        :return: the context
        """
        context = super(PublicationCorrectionUpdate, self).get_context_data(**kwargs)
        context['name'] = self.name
        context['constants'] = CONSTANTS_TEMPLATE
        return context

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.kwargs["pk"]})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.change_publication', raise_exception=True),
                  name='dispatch')
class PublicationAbortUpdate(UpdateView):
    model = Publication
    name = "Abort publication"
    form_class = PublicationAbortForm
    success_url = reverse_lazy("index")
    template_name = 'publications/publication_edit_form.html'
    object = None
    request = None

    @same_user("editor")
    @check_status(CORRECTION, "status")
    def form_valid(self, form):
        self.object = form.save(commit=False)
        return super(PublicationAbortUpdate, self).form_valid(form)

    @same_user("editor")
    @check_status(CORRECTION, "status")
    def get_context_data(self, **kwargs):
        """
        add the name to the context (useful for the template)
        :param kwargs: named arguments
        :return: the context
        """
        context = super(PublicationAbortUpdate, self).get_context_data(**kwargs)
        context['name'] = self.name
        context['constants'] = CONSTANTS_TEMPLATE
        return context

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.kwargs["pk"]})


class PublicationFilteredTableView(SingleTableView):
    """
    A class used to combine the filter, the table and the form helper
    """
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'
    request = None
    filter = None

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


@method_decorator(login_required, name='dispatch')
class PublicationSpecialTableView(SingleTableView):
    """
    A class used to combine the filter and the table (only the ordering is possible the filtering is already done
    as a built-in).
    Filter get only the publications on the science the user follow
    """
    filter_class = PublicationFilter
    context_filter_name = 'filter'
    name = ""
    filter_dict = {}
    model = Publication
    table_class = PublicationTable
    template_name = 'publications/publication_special_list.html'
    paginate_by = 20
    science_filter = True
    object = None
    request = None
    filter = None

    def fill_user_science(self):
        User = get_user_model()
        user = User.objects.get(pk=self.request.session['_auth_user_id'])
        sciences = [sid.pk for sid in user.sciences.all()]
        self.filter_dict["sciences"] = sciences

    def get_queryset(self, **kwargs):
        qs = super(PublicationSpecialTableView, self).get_queryset()
        # filter from the user information
        if self.science_filter:
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


@method_decorator(permission_required('publications.add_reviewer', raise_exception=True),
                  name='dispatch')
class PublicationToReviewTableView(PublicationSpecialTableView):
    """
    Show the publications about the sciences of the user and in need of peer for a review.
    Only for the user in scientist group
    """
    name = "to review"
    filter_dict = {'status': ADDING_PEER}


class PublicationInReviewTableView(PublicationSpecialTableView):
    """
    show the publications about the science of the user and in review. In need of comment
    """
    name = "to comment"
    filter_dict = {'status': PEER_REVIEW}


@method_decorator(permission_required('publications.add_estimated_impact_factor',
                                      raise_exception=True), name='dispatch')
class PublicationToEvaluateTableView(PublicationSpecialTableView):
    """
    show the publications about the sciences of the user and in evaluation. In need of an estimated impact factor.
    Only for user in the scientist group
    """
    name = "to evaluate"
    filter_dict = {'status': EVALUATION}


@method_decorator(permission_required('publications.add_publication', raise_exception=True),
                  name='dispatch')
class PublicationOwnedTableView(PublicationSpecialTableView):
    name = "owned"
    science_filter = False

    def get_queryset(self, **kwargs):
        self.filter_dict = {'authors': self.request.session['_auth_user_id']}
        return super(PublicationOwnedTableView, self).get_queryset()


@method_decorator(permission_required('publications.add_reviewer', raise_exception=True),
                  name='dispatch')
class PublicationYouReviewTableView(PublicationSpecialTableView):
    """
    Show the publications the user review
    """
    name = "your review"
    science_filter = False

    def get_queryset(self, **kwargs):
        lreviewer = list(Reviewer.objects.filter(scientist=self.request.session['_auth_user_id'], actif=True))
        lreviewer = [reviewer.pk for reviewer in lreviewer]
        if not lreviewer:
            lreviewer = [-1]  # -1 because no reviewer will have the -1 id
        self.filter_dict = {'reviewer': lreviewer}
        return super(PublicationYouReviewTableView, self).get_queryset()


def can_be_leave_reviewer(phd, nb_reviewer_actif, nb_common_science, not_in_authors, publication_status, action):
    if action == "become":
        return (phd and nb_reviewer_actif < NB_REVIEWER_PER_ARTICLE and not_in_authors and
                nb_common_science > 0 and publication_status in [ADDING_PEER, ABORTED, EVALUATION, PUBLISHED])
    elif action == "leave":
        return (phd and not_in_authors and
                nb_common_science > 0 and publication_status in [ADDING_PEER, ABORTED, EVALUATION, PUBLISHED])


def reviewer_action(user, publication_id, action):
    phd = user.phd
    nb_reviewer_actif = len(Reviewer.objects.filter(publication=publication_id, actif=True))
    publication = Publication.objects.get(pk=publication_id)
    not_in_authors = user not in publication.get_all_authors
    user_sciences = [science.id for science in user.sciences.all()]
    publication_sciences = [science.id for science in publication.sciences.all()]
    nb_common_sciences = len(set(user_sciences) & set(publication_sciences))
    publication_status = publication.status
    return can_be_leave_reviewer(phd, nb_reviewer_actif, nb_common_sciences,
                                 not_in_authors, publication_status, action=action)


class PublicationDisplay(DetailView):
    context_object_name = "publication_detail"
    model = Publication
    # template_name = 'publications/publication_detail.html'
    fields = ["title", "sciences", "resume", "status", "licence", "publication_score", "estimated_impact_factor",
              "pdf_creation", "source_creation", "pdf_final", "source_final"]
    kwargs = None
    request = None

    def get_alert_status(self, context):
        """
        get the alert status: if validated of not. If validated is there no corrected comment ?
        :return:
        """
        status = context["publication_detail"].status
        alert = {}
        if status < EVALUATION:
            if status == ABORTED:
                alert["class"] = "alert-danger"
                alert["title"] = _("Publication cancelled")
                alert["message"] = _("This publication hasn't been validated. Be careful. We appreciate your help!")
            else:
                alert["class"] = "alert-warning"
                alert["title"] = _("Publication is not finished")
                alert["message"] = _("This publication haven't been validated yet. It could have some bias. \
                                      We appreciate your help!")
        else:
            if Comment.objects.filter(publication=self.kwargs["pk"], comment_type=CONTENT,
                                      validated=True, corrected=False).exists():
                alert["class"] = "alert-danger"
                alert["title"] = _("Publication with bias")
                alert["message"] = _("This publication contains some bias. Be careful. We appreciate your help!")
            else:
                alert["class"] = "alert-success"
                alert["title"] = _("Publication validated")
                alert["message"] = _("This publication has been validated. \
                                     You can help us by trying to find more bias !")
        return alert

    def get_is_reviewer(self):
        is_reviewer = Reviewer.objects.filter(scientist=self.request.session['_auth_user_id'],
                                              publication=self.kwargs["pk"], actif=True).exists()
        return is_reviewer

    def get_evaluated(self):
        evaluated = EstimatedImpactFactor.objects.filter(estimator=self.request.session['_auth_user_id'],
                                                         publication=self.kwargs["pk"]).exists()
        return evaluated

    def get_is_editor(self, editor):
        return editor.pk == int(self.request.session['_auth_user_id'])

    def get_context_data(self, **kwargs):
        context = super(PublicationDisplay, self).get_context_data(**kwargs)
        # adding comment to the view, better order by
        context['comments'] = Comment.objects.filter(publication=self.kwargs["pk"]).order_by('validated',
                                                                                             '-comment_type',
                                                                                             'corrected',
                                                                                             '-seriousness',
                                                                                             'creation_date')
        # put the initial licence as the licence of the publication
        try:
            context['is_editor'] = self.get_is_editor(context["publication_detail"].editor)
            context['is_reviewer'] = self.get_is_reviewer()
            context['evaluated'] = self.get_evaluated()
            if context['is_reviewer']:
                context['reviewer_registration'] = reviewer_action(self.request.user, self.kwargs["pk"], "leave")
            else:
                context['reviewer_registration'] = reviewer_action(self.request.user, self.kwargs["pk"], "become")
        except KeyError:
            context['is_editor'] = False
            context['is_reviewer'] = False
            context['evaluated'] = False
        context['constants'] = CONSTANTS_TEMPLATE
        context['order'] = PUBLICATION
        context['alert'] = self.get_alert_status(context)
        context['form_comment'] = CommentForm()
        context['form_eif'] = EstimatedImpactFactorForm()
        return context


@method_decorator(login_required, name='dispatch')
class PublicationInterest(CreateView):
    # template_name = 'publications/publication_detail.html'
    form_class = CommentForm
    model = Comment
    object = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.publication = Publication.objects.get(pk=self.kwargs["pk"])
        self.object.licence = self.object.publication.licence
        # just to add the right name before the fake pseudo
        if self.object.author_fake_pseudo != "":
            if Reviewer.objects.filter(scientist=self.object.author, publication=self.object.publication).exists():
                self.object.author_fake_pseudo = "Reviewer " + self.object.author_fake_pseudo
            elif self.object.author.groups.filter(name="Scientist").exists():
                self.object.author_fake_pseudo = "Scientist " + self.object.author_fake_pseudo
            else:
                self.object.author_fake_pseudo = "Skeptic " + self.object.author_fake_pseudo
        return super(PublicationInterest, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.kwargs["pk"]})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.add_estimatedimpactfactor', raise_exception=True),
                  name='dispatch')
class EstimatedImpactFactorInterest(CreateView):
    # template_name = 'publications/publication_detail.html'
    form_class = EstimatedImpactFactorForm
    model = EstimatedImpactFactor
    object = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.estimator = self.request.user
        self.object.publication = Publication.objects.get(pk=self.kwargs["pk"])
        if self.object.publication.status != EVALUATION:
            raise PermissionDenied
        if self.request.user in self.object.publication.get_all_authors:
            raise PermissionDenied
        return super(EstimatedImpactFactorInterest, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('publication_view', kwargs={'pk': self.kwargs["pk"]})


class PublicationDetailView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        view = PublicationDisplay.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        if request.POST["submit"].lower() == _("Evaluate").lower():
            view = EstimatedImpactFactorInterest.as_view()
        else:
            view = PublicationInterest.as_view()
        return view(request, *args, **kwargs)


@login_required
@permission_required('publications.add_reviewer', raise_exception=True)
@permission_required('publications.change_reviewer', raise_exception=True)
def become_reviewer_view(request, publication_id):
    # add to reviewer if: phd & not enough rewiewers, group scientist, has sciences in common with the article
    if reviewer_action(request.user, publication_id, "become"):
        if Reviewer.objects.filter(publication=publication_id, scientist=request.user).exists():
            reviewer = Reviewer.objects.get(publication=publication_id, scientist=request.user)
            reviewer.actif = True
            reviewer.save()
        else:
            publication = Publication.objects.get(pk=publication_id)
            reviewer = Reviewer(scientist=request.user, publication=publication)
            reviewer.save()
        return redirect('publication_view', pk=publication_id)
    raise PermissionDenied


@login_required
@permission_required('publications.change_reviewer', raise_exception=True)
def leave_reviewer_view(request, publication_id):
    if reviewer_action(request.user, publication_id, "leave"):
        try:
            reviewer = Reviewer.objects.get(publication=publication_id, scientist=request.user)
            reviewer.actif = False
            reviewer.save()
            return redirect('publication_view', pk=publication_id)
        except ObjectDoesNotExist:
            raise PermissionDenied
    raise PermissionDenied


class CommentDisplay(DetailView):
    context_object_name = "comment_detail"
    model = Comment
    fields = ["publication", "author", "author_fake_pseudo", "creation_date", "comment_type", "seriousness",
              "content", "title", "validated", "corrected", "licence"]
    request = None
    kwargs = None

    def get_review_state(self, comment_context):
        publication_id = comment_context.publication.pk
        try:
            reviewer = Reviewer.objects.get(scientist=self.request.session['_auth_user_id'],
                                            publication=publication_id, actif=True)
        except (ObjectDoesNotExist, KeyError):
            return "not_reviewer"
        if not CommentReview.objects.filter(comment=self.kwargs["pk"], reviewer=reviewer).exists():
            if comment_context.validated == IN_PROGRESS:
                return "to_review_validation"
        elif comment_context.validated == VALIDATE and not comment_context.corrected:
            return "to_review_correction"
        return "nothing_to_do"

    def get_context_data(self, **kwargs):
        context = super(CommentDisplay, self).get_context_data(**kwargs)
        context['constants'] = CONSTANTS_TEMPLATE
        context['reviews'] = CommentReview.objects.filter(comment=self.kwargs["pk"])
        context['review_state'] = self.get_review_state(context["comment_detail"])
        context['publication_status'] = Publication.objects.get(pk=context['comment_detail'].publication.pk).status
        context['form_review_validation'] = CommentReviewValidationForm()
        context['form_review_correction'] = CommentReviewCorrectionForm()
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.add_commentreview', raise_exception=True),
                  name='dispatch')
class CommentReviewValidationInterest(CreateView):
    form_class = CommentReviewValidationForm
    model = CommentReview
    object = None

    def cascade_modifications(self):
        res = update_comment_validation(self.kwargs["pk"])
        if res:
            update_user_skeptic_score(self.kwargs["pk"])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.comment = Comment.objects.get(pk=self.kwargs["pk"])
        publication = self.object.comment.publication.id
        author = self.request.user
        try:
            self.object.reviewer = Reviewer.objects.get(scientist=author, publication=publication, actif=True)
        except ObjectDoesNotExist:
            raise PermissionDenied
        return super(CommentReviewValidationInterest, self).form_valid(form)

    def get_success_url(self):
        self.cascade_modifications()
        return reverse_lazy('comment_view', kwargs={'pk': self.kwargs["pk"]})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('publications.change_commentreview', raise_exception=True),
                  name='dispatch')
class CommentReviewCorrectionInterest(UpdateView):
    form_class = CommentReviewCorrectionForm
    model = CommentReview
    object = None

    def cascade_modifications(self):
        update_comment_correction(self.kwargs["pk"])

    def get_object(self, queryset=None):
        comment = Comment.objects.get(pk=self.kwargs["pk"])
        publication = comment.publication.id
        author = self.request.user
        try:
            reviewer = Reviewer.objects.get(scientist=author, publication=publication, actif=True)
            commentreview = CommentReview.objects.get(reviewer=reviewer)
        except ObjectDoesNotExist:
            raise PermissionDenied
        obj = commentreview
        return obj

    def form_valid(self, form):
        # need to be clever to get the object to update
        self.object = form.save(commit=False)
        self.object.corrected_date = timezone.now()
        return super(CommentReviewCorrectionInterest, self).form_valid(form)

    def get_success_url(self):
        self.cascade_modifications()
        return reverse_lazy('comment_view', kwargs={'pk': self.kwargs["pk"]})


class CommentDetailView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        view = CommentDisplay.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        if request.POST["submit"].lower() == _("Validate").lower():
            view = CommentReviewValidationInterest.as_view()
        else:
            view = CommentReviewCorrectionInterest.as_view()
        return view(request, *args, **kwargs)
