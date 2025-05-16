from django.core.management.base import BaseCommand

from commercialoperator.components.approvals.models import Approval

from django.db.models import Q

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Export Current Licence contacts - ./manage.py export_current_licence_contacts > /tmp/contacts.csv (cp to media/cols/ to access via web)"

    def handle(self, *args, **options):
        print(
            "Logdement Number: Expiry Date: Type: ABN: Org Name: Trading Name: Org Address: Org Contacts: Org Admin Users"
        )

        approvals = Approval.objects.filter(Q(status="current")).exclude(
            Q(org_applicant=None)
        )
        for a in approvals:
            org = a.org_applicant
            if hasattr(org, "monthly_invoicing_allowed"):
                print(
                    "{}: {}: {}: {}: {}: {}: {}: {}: {}".format(
                        a.lodgement_number,
                        a.expiry_date,
                        a.current_proposal.application_type.name,
                        org.abn,
                        org.name,
                        org.trading_name,
                        org.address_summary,
                        "; ".join(org.contacts.all().values_list("email", flat=True)),
                        list(
                            org.contacts.filter(
                                is_admin=True, user_role="organisation_admin"
                            ).values_list("email", "first_name", "last_name")
                        ),
                    )
                )
