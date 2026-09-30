import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from commercialoperator.components.approvals.email import (
    send_approval_renewal_email_notification,
)
from commercialoperator.components.approvals.models import Approval, NotificationPeriod
from commercialoperator.components.main.models import ApplicationType, LicencePeriod

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Send Approval renewal notice when approval is due to expire, date specified in "
        "<notification_period_list> ([3,6,12] etc) (Excludes E Class, Filming, Event licences)"
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
            status__in=["current", "suspended"],
            current_proposal__application_type__name=ApplicationType.TCLASS,
        ).exclude(
            current_proposal__other_details__preferred_licence_period=LicencePeriod.LICENCE_PERIOD_2_MONTHS
        )

        for approval in approvals:
            try:
                # Send periodic renewal notification if a notification date falls in the current window
                notification_date = self.get_notification_date(
                    approval, start_date=last_week, end_date=today
                )

                if notification_date:
                    np, created = NotificationPeriod.objects.get_or_create(
                        approval=approval, notification_date=notification_date
                    )

                    if created:
                        send_approval_renewal_email_notification(approval)
                        np.notification_sent = True
                        np.save()

                        logger.info(
                            f"Renewal notification reminder notice sent for Approval {approval.id}"
                        )
                        updates.append(approval.lodgement_number)

                    # Ensure renewal document and flag exist alongside the notification
                    if approval.renewal_document is None:
                        approval.generate_renewal_doc()

                    if not approval.renewal_sent:
                        approval.renewal_sent = True
                        approval.save()

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

    def get_notification_date(self, approval, start_date, end_date):
        """
        Returns the first notification date that falls between start_date and end_date, or None.
        """
        notification_dates = approval._notification_dates(end_date) or []
        return next(
            (dt for dt in notification_dates if start_date <= dt <= end_date),
            None,
        )
