from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from commercialoperator.components.approvals.models import Approval, NotificationPeriod
from commercialoperator.components.approvals.email import (
    send_approval_renewal_email_notification,
)
from commercialoperator.components.main.models import ApplicationType, LicencePeriod
from ledger_api_client.ledger_models import EmailUserRO as EmailUser


from dateutil.relativedelta import relativedelta

import traceback

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send Approval renewal notice when approval is due to expire, date specified in <notification_period_list> ([3,6,12] etc) (Excludes E Class, Filming, Event licences)"

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password="")

        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        # today = date(2023,9,30)
        last_week = today - relativedelta(weeks=1)

        # Only TClass Licences can be renewed
        # also checking expiry since last week to catch renewals/notifications missed by previous recent script runs
        notification_conditions = {
            #'expiry_date__range': [last_week, today],
            "expiry_date__gt": today,
            "replaced_by__isnull": True,
            "current_proposal__application_type__name__in": [ApplicationType.TCLASS],
        }

        # TClass '2 month' licences cannot be renewed
        exclude_conditions = {
            "current_proposal__other_details__preferred_licence_period": LicencePeriod.LICENCE_PERIOD_2_MONTHS,
        }

        qs = Approval.objects.filter(**notification_conditions).exclude(
            **exclude_conditions
        )
        # qs = Approval.objects.filter(lodgement_number='L000633')

        logger.info("{}".format(qs))
        for idx, a in enumerate(qs):
            if a.status == "current" or a.status == "suspended":
                try:
                    # Send periodic renewal notification, if notification_date has arrived
                    notification_date = self.get_notification_date(a, last_week, today)
                    if notification_date:
                        np, created = NotificationPeriod.objects.get_or_create(
                            approval=a, notification_date=notification_date
                        )

                        if created:
                            # notification has not been previously sent for this notification_date
                            send_approval_renewal_email_notification(a)
                            np.notification_sent = True
                            np.save()
                            logger.info(
                                "Renewal notification reminder notice sent for Approval {}".format(
                                    a.id
                                )
                            )
                            updates.append(a.lodgement_number)
                            # print(idx, a, a.current_proposal.other_details.preferred_licence_period, notification_date, a.expiry_date)

                        # double check that renewal_sent and renewal_document also exists - if notif'n is sent, then renewal_doc should also exist
                        if a.renewal_document is None:
                            a.generate_renewal_doc()

                        if not a.renewal_sent:
                            a.renewal_sent = True
                            a.save()
                            # print(idx, a, a.current_proposal.other_details.preferred_licence_period, a.renew_months, a.renew_enable_date, a.expiry_date, a.renewal_document, a.renewal_sent)

                except Exception as e:
                    err_msg = "Error sending renewal notification notice for Approval {}".format(
                        a.lodgement_number
                    )
                    logger.error("{}\n{}".format(err_msg, str(e)))
                    logger.error("{}".format(traceback.format_exc()))
                    errors.append(err_msg)

        cmd_name = __name__.split(".")[-1].replace("_", " ").upper()
        err_str = (
            '<strong style="color: red;">Errors: {}</strong>'.format(len(errors))
            if len(errors) > 0
            else '<strong style="color: green;">Errors: 0</strong>'
        )
        msg = "<p>{} completed. Errors: {}. IDs updated: {}.</p>".format(
            cmd_name, err_str, updates
        )
        logger.info(msg)
        print(msg)  # will redirect to cron_tasks.log file, by the parent script

    def get_notification_date(self, approval, start_date, end_date):
        # check if notification_date is near ('near' will catch failed cron jobs and run in the next day(s)
        current_notifications_dates = [
            dt
            for dt in approval._notification_dates(end_date)
            if start_date <= dt <= end_date
        ]
        return (
            current_notifications_dates[0]
            if len(current_notifications_dates) > 0
            else None
        )
