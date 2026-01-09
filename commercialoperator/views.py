from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.db import transaction

from datetime import datetime, timedelta

from commercialoperator.helpers import is_internal, is_customer
from commercialoperator.forms import *
from commercialoperator.components.proposals.models import Referral, Proposal, HelpPage, DistrictProposal
from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.proposals.mixins import ReferralOwnerMixin
from commercialoperator.components.main.models import Park
from commercialoperator.components.bookings.email import send_invoice_tclass_email_notification, send_confirmation_tclass_email_notification

import os
import mimetypes
from django.db.models import Q

from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
from django.core.management import call_command
import json
from decimal import Decimal

import logging
logger = logging.getLogger('payment_checkout')


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = 'commercialoperator/dash/index.html'

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super(InternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context

class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = 'commercialoperator/dash/index.html'

    def get_context_data(self, **kwargs):
        context = super(ExternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
            context['app_build_url'] = settings.DEV_APP_BUILD_URL
        return context

class ReferralView(ReferralOwnerMixin, DetailView):
    model = Referral
    template_name = 'commercialoperator/dash/index.html'

class ExternalProposalView(DetailView):
    model = Proposal
    template_name = 'commercialoperator/dash/index.html'

class ExternalComplianceView(DetailView):
    model = Compliance
    template_name = 'commercialoperator/dash/index.html'

class InternalComplianceView(DetailView):
    model = Compliance
    template_name = 'commercialoperator/dash/index.html'

class DistrictProposalView(DetailView):
    model = DistrictProposal
    template_name = 'commercialoperator/dash/index.html'

class CommercialOperatorRoutingView(TemplateView):
    template_name = 'commercialoperator/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                return redirect('internal')
            return redirect('external')
        kwargs['form'] = LoginForm
        return super(CommercialOperatorRoutingView, self).get(*args, **kwargs)

class CommercialOperatorContactView(TemplateView):
    template_name = 'commercialoperator/contact.html'

class CommercialOperatorFurtherInformationView(TemplateView):
    template_name = 'commercialoperator/further_info.html'

class InternalProposalView(DetailView):
    #template_name = 'commercialoperator/index.html'
    model = Proposal
    template_name = 'commercialoperator/dash/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                #return redirect('internal-proposal-detail')
                return super(InternalProposalView, self).get(*args, **kwargs)
            return redirect('external-proposal-detail')
        kwargs['form'] = LoginForm
        return super(CommercialOperatorRoutingDetailView, self).get(*args, **kwargs)


@login_required(login_url='ds_home')
def first_time(request):
    context = {}
    if request.method == 'POST':
        form = FirstTimeForm(request.POST)
        redirect_url = form.data['redirect_url']
        if not redirect_url:
            redirect_url = '/'
        if form.is_valid():
            # set user attributes
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.dob = form.cleaned_data['dob']
            request.user.save()
            return redirect(redirect_url)
        context['form'] = form
        context['redirect_url'] = redirect_url
        return render(request, 'commercialoperator/user_profile.html', context)
    # GET default
    if 'next' in request.GET:
        context['redirect_url'] = request.GET['next']
    else:
        context['redirect_url'] = '/'
    context['dev'] = settings.DEV_STATIC
    context['dev_url'] = settings.DEV_STATIC_URL
    if hasattr(settings, 'DEV_APP_BUILD_URL') and settings.DEV_APP_BUILD_URL:
        context['app_build_url'] = settings.DEV_APP_BUILD_URL
    #return render(request, 'commercialoperator/user_profile.html', context)
    return render(request, 'commercialoperator/dash/index.html', context)


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'commercialoperator/help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            application_type = kwargs.get('application_type', None)
            if kwargs.get('help_type', None)=='assessor':
                if is_internal(self.request):
                    qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_INTERNAL).order_by('-version')
                    context['help'] = qs.first()
#                else:
#                    return TemplateResponse(self.request, 'commercialoperator/not-permitted.html', context)
#                    context['permitted'] = False
            else:
                qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_EXTERNAL).order_by('-version')
                context['help'] = qs.first()
        return context


class ManagementCommandsView(LoginRequiredMixin, TemplateView):
    template_name = 'commercialoperator/mgt-commands.html'

    def post(self, request):
        data = {}
        command_script = request.POST.get('script', None)
        if command_script:
            print ('running {}'.format(command_script))
            call_command(command_script)
            data.update({command_script: 'true'})

        return render(request, self.template_name, data)

def is_authorised_to_access_proposal_document(request,document_id):
    if is_internal(request):
        return True
    elif is_customer(request):
        user = request.user
        user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
        return Proposal.objects.filter(id=document_id).filter(
                Q(org_applicant_id__in=user_orgs) |
                Q(submitter=user)).exists()

def get_file_path_id(check_str,file_path):
    file_name_path_split = file_path.split("/")
    #if the check_str is in the file path, the next value should be the id
    if check_str in file_name_path_split:
        id_index = file_name_path_split.index(check_str)+1
        if len(file_name_path_split) > id_index and file_name_path_split[id_index].isnumeric():
            return int(file_name_path_split[id_index])
        else:
            return False
    else:
        return False

def is_authorised_to_access_document(request):

    if is_internal(request):
        return True
    elif is_customer(request):
        p_document_id = get_file_path_id("proposals",request.path)
        if p_document_id:
            return is_authorised_to_access_proposal_document(request,p_document_id)
    else:
        return False

def getPrivateFile(request):

    if is_authorised_to_access_document(request):
        file_name_path =  request.path
        #norm path will convert any traversal or repeat / in to its normalised form
        full_file_path= os.path.normpath(settings.BASE_DIR+file_name_path) 
        #we then ensure the normalised path is within the BASE_DIR (and the file exists)
        if full_file_path.startswith(settings.BASE_DIR) and os.path.isfile(full_file_path):
            extension = file_name_path.split(".")[-1]
            the_file = open(full_file_path, 'rb')
            the_data = the_file.read()
            the_file.close()
            if extension == 'msg':
                return HttpResponse(the_data, content_type="application/vnd.ms-outlook")
            if extension == 'eml':
                return HttpResponse(the_data, content_type="application/vnd.ms-outlook")

            return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension)])

    return HttpResponse()