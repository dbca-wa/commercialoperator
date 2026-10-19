from django.conf import settings
from django.shortcuts import render
from ledger_api_client.views import OrganisationView

from commercialoperator.components.organisations.models import Organisation
from commercialoperator.components.permission.permission import is_linked_to_organisation
from commercialoperator.components.proposals.views import InternalHistoryCompareDetailView

class OrganisationHistoryCompareView(InternalHistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Organisation
    template_name = 'commercialoperator/reversion_history.html'


class OrganisationDetailView(OrganisationView):
    """
    Render the page without waiting for Ledger. The loaded details determine
    whether a linked user's trading name is still blank.
    """

    def get(self, request, *args, **kwargs):
        org_id = kwargs['pk']
        context = {
            'settings': settings,
            'org_id': org_id,
            'is_linked_to_organisation': is_linked_to_organisation(request, org_id),
        }
        return render(request, self.template_name, context)
