from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from commercialoperator.components.approvals.models import Approval, NotificationPeriod
from commercialoperator.components.approvals.email import send_approval_renewal_email_notification
from commercialoperator.components.main.models import ApplicationType, LicencePeriod
from ledger.accounts.models import EmailUser
from datetime import date, timedelta

import itertools
from dateutil.relativedelta import relativedelta

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Enable Approval \'Renew\' button in Licence Dashboard <renewal_months> prior to when approval is due to expire (Excludes E Class, Filming, Event licences)'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email=settings.CRON_EMAIL)
        except:
            user = EmailUser.objects.create(email=settings.CRON_EMAIL, password='')

        errors = []
        updates = []
        today = timezone.localtime(timezone.now()).date()
        #today = date(2023,9,30)
        last_week = today - relativedelta(weeks=1)
        #last_week = today - relativedelta(months=6)

        # Only TClass Licences can be renewed
        # also checking expiry since last week to catch renewals/notifications missed by previous recent script runs 
        notification_conditions = {
            #'expiry_date__range': [last_week, today],
            'expiry_date__gt': today,
            'replaced_by__isnull': True,
            'current_proposal__application_type__name__in': [ApplicationType.TCLASS],
        }

        # TClass '2 month' licences cannot be renewed
        exclude_conditions = {
            'current_proposal__other_details__preferred_licence_period': LicencePeriod.LICENCE_PERIOD_2_MONTHS,
        }

        qs = Approval.objects.filter(**notification_conditions).exclude(**exclude_conditions)
        #qs = Approval.objects.filter(lodgement_number='L000633')

        logger.info('{}'.format(qs))
        for idx, a in enumerate(qs):
            if a.status == 'current' or a.status == 'suspended':
                try:
                    # Enable 'Renew' action button in Licence Dashboard - Renew button can be enable many months before notil f'n is sent
                    if self.can_renew(a, last_week, today):
                        # notification has not been previously sent, so can generate approval doc
                        a.generate_renewal_doc()
                        a.renewal_sent=True
                        a.save()
                        logger.info('Renewal notification reminder notice sent for Approval {}'.format(a.id))
                        updates.append(a.lodgement_number)
                        #print(idx, a, a.current_proposal.other_details.preferred_licence_period, a.renew_months, a.renew_enable_date, a.expiry_date, a.renewal_document, a.renewal_sent)

                except Exception as e:
                    err_msg = 'Error sending renewal notification notice for Approval {}'.format(a.lodgement_number)
                    logger.error('{}\n{}'.format(err_msg, str(e)))
                    errors.append(err_msg)

        cmd_name = __name__.split('.')[-1].replace('_', ' ').upper()
        err_str = '<strong style="color: red;">Errors: {}</strong>'.format(len(errors)) if len(errors)>0 else '<strong style="color: green;">Errors: 0</strong>'
        msg = '<p>{} completed. Errors: {}. IDs updated: {}.</p>'.format(cmd_name, err_str, updates)
        logger.info(msg)
        print(msg) # will redirect to cron_tasks.log file, by the parent script

    def can_renew(self, approval, start_date, end_date):
        # check if renew_enable_date is near ('near' will catch failed cron jobs and run in the next day(s)
        renew_enable_date = approval.renew_enable_date if start_date <= approval.renew_enable_date <= end_date else None
        return renew_enable_date and (not approval.renewal_sent or approval.renewal_document is None)

