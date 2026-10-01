import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from commercialoperator.components.approvals.models import Approval
from commercialoperator.components.main.models import ApplicationType, LicencePeriod

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Enable Approval 'Renew' button in Licence Dashboard <renewal_months> "
        "prior to when approval is due to expire (Excludes E Class, Filming, Event licences)"
    )

    def handle(self, *args, **options):
        errors = []
        updates = []

        today = timezone.localdate()
        last_week = today - timedelta(days=7)

        # Filter eligible approvals directly in the database
        approvals = Approval.objects.filter(
            expiry_date__gt=today,
            replaced_by__isnull=True,
            status__in=[
                Approval.APPROVAL_STATUS_CURRENT,
                Approval.APPROVAL_STATUS_SUSPENDED,
            ],
            current_proposal__application_type__name=ApplicationType.TCLASS,
        ).exclude(
            current_proposal__other_details__preferred_licence_period=LicencePeriod.LICENCE_PERIOD_2_MONTHS
        )

        for approval in approvals:
            try:
                if self.can_renew(approval, start_date=last_week, end_date=today):
                    approval.generate_renewal_doc()
                    approval.renewal_sent = True
                    approval.save()

                    logger.info(
                        f"Renewal notification reminder notice sent for Approval {approval.id}"
                    )
                    updates.append(approval.lodgement_number)

            except Exception:
                err_msg = f"Error sending renewal notification notice for Approval {approval.lodgement_number}"
                logger.exception(err_msg)
                errors.append(err_msg)

        # Output / Log summary
        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_color = "red" if errors else "green"
        err_str = f'<strong style="color: {err_color};">Errors: {len(errors)}</strong>'
        msg = f"<p>{cmd_name} completed. Errors: {err_str}. IDs updated: {updates}.</p>"

        logger.info(msg)
        self.stdout.write(msg)

    def can_renew(self, approval, start_date, end_date) -> bool:
        """
        Check if the approval's renew_enable_date falls within the target range
        and if the renewal notification has not yet been processed.
        """
        renew_enable_date = approval.renew_enable_date
        if not renew_enable_date:
            return False

        is_in_date_window = start_date <= renew_enable_date <= end_date
        is_pending = not approval.renewal_sent or approval.renewal_document is None

        return is_in_date_window and is_pending
