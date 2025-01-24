from commercialoperator.components.approvals.models import Approval
from commercialoperator.components.main.models import ApplicationType, LicencePeriod
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


def enable_rewewals(lodgement_numbers):
    """
    from commercialoperator.utils.renewal_enable_adhoc import enable_rewewals
    enable renewals(['L001339','L000997'])

    """

    if not isinstance(lodgement_numbers, list):
        logger.error(f"list input required: {lodgement_numbers}")
        return

    today = timezone.localtime(timezone.now()).date()

    notification_conditions = {
        "expiry_date__gt": today,
        "replaced_by__isnull": True,
        "current_proposal__application_type__name__in": [ApplicationType.TCLASS],
        "lodgement_number__in": lodgement_numbers,
    }

    exclude_conditions = {
        "current_proposal__other_details__preferred_licence_period": LicencePeriod.LICENCE_PERIOD_2_MONTHS,
    }

    qs = Approval.objects.filter(**notification_conditions).exclude(
        **exclude_conditions
    )

    if not qs.exists():
        logger.warning(f"Approval(s) not found - Exiting ...")

    for idx, a in enumerate(qs):
        if a.status == "current" or a.status == "suspended":
            try:
                # Enable 'Renew' action button in Licence Dashboard - Renew button can be enable many months before notil f'n is sent
                a.generate_renewal_doc()
                a.renewal_sent = True
                a.save()

                logger.warning(f"Approval updated: {a}")
            except Exception as e:
                logger.error(f"{e}")
        else:
            logger.warning(f"Approval status incorrect - not updated: {a}")
