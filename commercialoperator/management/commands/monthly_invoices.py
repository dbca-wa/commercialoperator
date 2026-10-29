import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from commercialoperator.components.bookings.email import (
    send_monthly_invoices_failed_tclass,
)
from commercialoperator.components.bookings.utils import create_monthly_invoice

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Run the Monthly Invoices Script - generates invoices per "
        "licence/org_applicant for previous month"
    )

    def handle(self, *args, **options):
        """
        Generate monthly invoices for eligible bookings from the previous
        month.

        A dedicated cron user is created if one does not already exist. Any
        failed booking IDs are reported by email and included in the command
        output.
        """
        try:
            user = EmailUser.objects.get(
                email=settings.CRON_EMAIL,
                defaults={"password": ""},
            )
        except EmailUser.DoesNotExist:
            raise CommandError(f"Cron user {settings.CRON_EMAIL} does not exist")

        logger.info("Running command %s", __name__)

        failed_bookings = create_monthly_invoice(
            user,
            offset_months=-1,
        )

        if failed_bookings:
            logger.warning(
                "Command %s failed for booking IDs %s",
                __name__,
                failed_bookings,
            )
            send_monthly_invoices_failed_tclass(
                failed_bookings,
            )

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()

        err_str = (
            f'<strong style="color: red;">Errors: {len(failed_bookings)}</strong>'
            if failed_bookings
            else '<strong style="color: green;">Errors: 0</strong>'
        )

        msg = f"<p>{cmd_name} completed. {err_str}.</p>"

        logger.info(msg)
        self.stdout.write(msg)
