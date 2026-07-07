from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from commercialoperator.helpers import is_internal, is_commercialoperator_admin
from commercialoperator.forms import *
from commercialoperator.components.proposals.models import (
    Referral,
    Proposal,
    DistrictProposal,
)

from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.organisations.models import Organisation, OrganisationContact
from commercialoperator.components.approvals.models import Approval
from django.db.models import Q

from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.proposals.mixins import ReferralOwnerMixin

from django.core.management import call_command
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

import logging
logger = logging.getLogger("payment_checkout")

import os
import mimetypes
import shlex
import subprocess
import sys
import uuid

from commercialoperator.components.main.models import JobQueue

class InternalView(UserPassesTestMixin, TemplateView):
    template_name = "commercialoperator/dash/index.html"

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super(InternalView, self).get_context_data(**kwargs)
        return context


class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = "commercialoperator/dash/index.html"

    def get_context_data(self, **kwargs):
        context = super(ExternalView, self).get_context_data(**kwargs)
        return context


class ReferralView(ReferralOwnerMixin, DetailView):
    model = Referral
    template_name = "commercialoperator/dash/index.html"


class ExternalProposalView(DetailView):
    model = Proposal
    template_name = "commercialoperator/dash/index.html"


class ExternalComplianceView(DetailView):
    model = Compliance
    template_name = "commercialoperator/dash/index.html"


class InternalComplianceView(DetailView):
    model = Compliance
    template_name = "commercialoperator/dash/index.html"


class DistrictProposalView(DetailView):
    model = DistrictProposal
    template_name = "commercialoperator/dash/index.html"


class CommercialOperatorRoutingView(TemplateView):
    template_name = "commercialoperator/index.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            # if is_internal(self.request):
            #     return redirect("internal")
            return redirect("external")
        kwargs["form"] = LoginForm
        return super(CommercialOperatorRoutingView, self).get(*args, **kwargs)


class CommercialOperatorContactView(TemplateView):
    template_name = "commercialoperator/contact.html"


class CommercialOperatorFurtherInformationView(TemplateView):
    template_name = "commercialoperator/further_info.html"


class InternalProposalView(DetailView):
    model = Proposal
    template_name = "commercialoperator/dash/index.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if is_internal(self.request):
                return super(InternalProposalView, self).get(*args, **kwargs)


#TODO we may need to lock this behind an env var so this is not accessible on prod
class ManagementCommandsView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = "commercialoperator/mgt-commands.html"
    UPDATE_CACHE_STATE_KEY = 'update_cache_background_state'
    UPDATE_CACHE_LOCK_KEY = 'update_cache_background_lock'
    UPDATE_CACHE_ACTIVE_STATUSES = {'starting', 'running'}

    @staticmethod
    def _is_pid_running(pid):
        if not pid:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    @classmethod
    def _refresh_update_cache_state(cls):
        state = cache.get(cls.UPDATE_CACHE_STATE_KEY)
        if not state:
            return None

        if state.get('status') in cls.UPDATE_CACHE_ACTIVE_STATUSES:
            pid = state.get('pid')
            if cls._is_pid_running(pid):
                return state

            exit_code = None
            exit_path = state.get('exit_path')
            if exit_path and os.path.exists(exit_path):
                try:
                    with open(exit_path, 'r', encoding='utf-8') as exit_file:
                        exit_code = int((exit_file.read() or '').strip())
                except (TypeError, ValueError):
                    exit_code = None

            state['finished_at'] = timezone.now().isoformat()
            if exit_code == 0:
                state['status'] = 'completed'
                state['error'] = ''
            else:
                state['status'] = 'failed'
                state['error'] = 'update_cache exited with non-zero status'

            cache.set(cls.UPDATE_CACHE_STATE_KEY, state, timeout=None)

        return state

    @classmethod
    def _start_update_cache_job(cls, requested_by=''):
        state = cls._refresh_update_cache_state()
        if state and state.get('status') in cls.UPDATE_CACHE_ACTIVE_STATUSES:
            return state, False

        if not cache.add(cls.UPDATE_CACHE_LOCK_KEY, True, timeout=15):
            state = cls._refresh_update_cache_state()
            return state, False

        try:
            state = cls._refresh_update_cache_state()
            if state and state.get('status') in cls.UPDATE_CACHE_ACTIVE_STATUSES:
                return state, False

            job_id = uuid.uuid4().hex
            log_dir = os.path.join(settings.BASE_DIR, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, 'update_cache.log')
            exit_path = os.path.join(log_dir, 'update_cache.exit')

            if os.path.exists(exit_path):
                os.remove(exit_path)

            command = (
                f"{shlex.quote(sys.executable)} "
                f"{shlex.quote(os.path.join(settings.BASE_DIR, 'manage.py'))} "
                f"update_cache > {shlex.quote(log_path)} 2>&1; "
                f"echo $? > {shlex.quote(exit_path)}"
            )
            proc = subprocess.Popen(
                ['bash', '-lc', command],
                cwd=settings.BASE_DIR,
                start_new_session=True,
            )

            state = {
                'id': job_id,
                'command': 'update_cache',
                'status': 'running',
                'started_at': timezone.now().isoformat(),
                'requested_by': requested_by,
                'log_path': log_path,
                'exit_path': exit_path,
                'pid': proc.pid,
                'error': '',
            }
            cache.set(cls.UPDATE_CACHE_STATE_KEY, state, timeout=None)
            return state, True
        finally:
            cache.delete(cls.UPDATE_CACHE_LOCK_KEY)

    @classmethod
    def get_update_cache_status(cls):
        latest_job = cls._refresh_update_cache_state()
        active = bool(latest_job and latest_job.get('status') in cls.UPDATE_CACHE_ACTIVE_STATUSES)
        return {
            'active': active,
            'job': latest_job if active else None,
            'status': latest_job.get('status') if latest_job else None,
            'latest_job': latest_job,
        }

    def get(self, request, *args, **kwargs):
        if request.GET.get('update_cache_status') == '1':
            return JsonResponse(self.get_update_cache_status())
        return super(ManagementCommandsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('update_cache_active_job', self.get_update_cache_status()['job'])
        return context

    def test_func(self):
        return is_commercialoperator_admin(self.request) #TODO check if admin appropriate auth (sys admin may be needed)

    def post(self, request):
        data = {}
        command_script = request.POST.get("script", None)
        if command_script:
            print("running {}".format(command_script))
            if command_script == 'update_cache':
                requested_by = request.user.email if request.user and request.user.is_authenticated else ''
                job, created = self._start_update_cache_job(requested_by=requested_by)
                data.update({'update_cache': job['status']})
            else:
                call_command(command_script)
                data.update({command_script: "true"})

        data.update(
            {
                'update_cache_active_job': self.get_update_cache_status()['job'],
            }
        )

        return render(request, self.template_name, data)


def is_authorised_to_access_proposal_document(request,document_id):
    if is_internal(request):
        return True
    elif request.user and request.user.is_authenticated:
        user = request.user
        user_orgs = [org.id for org in user.commericaloperator_organisations.all()]
        return Proposal.objects.filter(id=document_id).filter(
                Q(applicant_id__in=user_orgs) |
                Q(submitter=user)).exists()

def is_authorised_to_access_approval_document(request,document_id):
    if is_internal(request):
        return True
    elif request.user and request.user.is_authenticated:
        user = request.user
        user_orgs = [org.id for org in user.commericaloperator_organisations.all()]
        return Approval.objects.filter(id=document_id).filter(
                Q(applicant_id__in = user_orgs) |
                Q(proxy_applicant_id=user.id)).exists()

def is_authorised_to_access_organisation_document(request,document_id):
    if is_internal(request):
        return True
    elif request.user and request.user.is_authenticated:
        user = request.user
        org_contacts = OrganisationContact.objects.filter(is_admin=True).filter(email=user.email)
        user_admin_orgs = [org.organisation.id for org in org_contacts]
        return Organisation.objects.filter(id=document_id).filter(id__in=user_admin_orgs).exists()

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
    elif request.user.is_authenticated:
        p_document_id = get_file_path_id("proposals",request.path)
        if p_document_id:
            return is_authorised_to_access_proposal_document(request,p_document_id)
        
        a_document_id = get_file_path_id("approvals",request.path)
        if a_document_id:
            return is_authorised_to_access_approval_document(request,a_document_id)
        
        #for organisation requests, this will fail and they are stored in a request subdir and by date (which is fine for current use cases)
        o_document_id = get_file_path_id("organisations",request.path)
        if o_document_id:
            return is_authorised_to_access_organisation_document(request,o_document_id)
        return False
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

            try:
                return HttpResponse(the_data, content_type=mimetypes.types_map['.'+str(extension.lower())])
            except:
                return HttpResponse(status=500)
       
    return HttpResponse(status=403)

class EmailExportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'commercialoperator/email_exports.html'

    def test_func(self):
        return is_internal(self.request)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request):
        context = self.get_context_data()
        export_model = request.POST.get('export_model', None)
        filters = request.POST.get('filters', None)
        format = request.POST.get('format', 'csv')
        num_records = request.POST.get('num_records', settings.MAX_NUM_ROWS_MODEL_EXPORT)

        try:
            num_records = min(int(num_records), settings.MAX_NUM_ROWS_MODEL_EXPORT)
        except:
            num_records = settings.MAX_NUM_ROWS_MODEL_EXPORT

        if export_model:
            parameters = {"model":export_model, "filters":filters, "format":format, "num_records": num_records}
            parameters_json = parameters
            #check if job with same params that is not completed/failed already exists - prevent needless duplicates
            if not JobQueue.objects.filter(job_cmd="email_exports", status__lt=2, parameters_json=parameters_json, user=request.user.id):
                JobQueue.objects.create(
                    job_cmd="email_exports",
                    status=0,
                    parameters_json=parameters_json,
                    user=request.user.id
                )
                context.update({"message": "{} data export shall be emailed to {} when ready.".format(export_model,request.user.email).capitalize()})
            else:
                context.update({"message": "{} data export for {} already in progress.".format(export_model,request.user.email).capitalize()})
        else:
            context.update({"message": "Export request failed."})

        return self.render_to_response(context)