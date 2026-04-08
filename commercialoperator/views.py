from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


from commercialoperator.helpers import is_internal, is_commercialoperator_admin
from commercialoperator.forms import *
from commercialoperator.components.proposals.models import (
    Referral,
    Proposal,
    HelpPage,
    DistrictProposal,
)
from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.proposals.mixins import ReferralOwnerMixin

from django.core.management import call_command


import logging

logger = logging.getLogger("payment_checkout")


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
            if is_internal(self.request):
                return redirect("internal")
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

#TODO unclear if this is used anymore - investigate and remove/refactor
class HelpView(LoginRequiredMixin, TemplateView):
    template_name = "commercialoperator/help.html"

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            application_type = kwargs.get("application_type", None)
            if kwargs.get("help_type", None) == "assessor":
                if is_internal(self.request):
                    qs = HelpPage.objects.filter(
                        application_type__name__icontains=application_type,
                        help_type=HelpPage.HELP_TEXT_INTERNAL,
                    ).order_by("-version")
                    context["help"] = qs.first()
            #                else:
            #                    return TemplateResponse(self.request, 'commercialoperator/not-permitted.html', context)
            #                    context['permitted'] = False
            else:
                qs = HelpPage.objects.filter(
                    application_type__name__icontains=application_type,
                    help_type=HelpPage.HELP_TEXT_EXTERNAL,
                ).order_by("-version")
                context["help"] = qs.first()
        return context

#TODO we may need to lock this behind an env var so this is not accessible on prod
class ManagementCommandsView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = "commercialoperator/mgt-commands.html"

    def test_func(self):
        return is_commercialoperator_admin(self.request) #TODO check if admin appropriate auth (sys admin may be needed)

    def post(self, request):
        data = {}
        command_script = request.POST.get("script", None)
        if command_script:
            print("running {}".format(command_script))
            call_command(command_script)
            data.update({command_script: "true"})

        return render(request, self.template_name, data)
