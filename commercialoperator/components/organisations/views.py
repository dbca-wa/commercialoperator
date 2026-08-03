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
    Overrides ledger_api_client's OrganisationView to add
    `can_edit_trading_name_for_user` to the render context, so the
    ledgerui/organisation.html template can use it directly without
    computing the permission itself via a template tag.
    """

    def get(self, request, *args, **kwargs):
        org_id = kwargs['pk']
        organisation = Organisation.objects.filter(organisation_id=org_id).first()
        trading_name_blank = not bool(
            organisation and (organisation.trading_name or "").strip()
        )
        context = {
            'settings': settings,
            'org_id': org_id,
            'can_edit_trading_name_for_user': (
                trading_name_blank and is_linked_to_organisation(request, org_id)
            ),
        }
        return render(request, self.template_name, context)
