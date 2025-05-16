from attr import has
from django.core.management.base import BaseCommand

from rest_framework import status

from ledger_api_client.utils import get_all_organisation

import logging

from commercialoperator.components.organisations.models import Organisation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Export Organisation contacts - ./manage.py export_contacts > /tmp/contacts.csv"
    )

    def handle(self, *args, **options):
        ledger_orgs_response = get_all_organisation()
        response_status = ledger_orgs_response.get("status")
        if response_status != status.HTTP_200_OK:
            print("Error retrieving organisations from Ledger API")
            return
        ledger_orgs = ledger_orgs_response.get("data")

        for ledger_org in ledger_orgs:
            try:
                cols_org = Organisation.objects.get(
                    organisation_id=ledger_org.get("organisation_id")
                )
            except Organisation.DoesNotExist:
                cols_org = None

            if hasattr(cols_org, "monthly_invoicing_allowed"):
                print(
                    "{},{},{},{}".format(
                        cols_org.name,
                        ledger_org.get("trading_name"),
                        ledger_org.get("organisation_abn"),
                        "; ".join(
                            cols_org.contacts.all().values_list("email", flat=True)
                        ),
                    )
                )
