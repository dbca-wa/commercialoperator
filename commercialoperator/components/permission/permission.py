from commercialoperator.components.organisations.models import Organisation

import logging

logger = logging.getLogger(__name__)


def organisation_permissions(request, ledger_organisation_id):
    try:
        cols_organisation = Organisation.objects.get(
            organisation_id=ledger_organisation_id
        )
    except Organisation.DoesNotExist:
        logger.error(
            "Organisation with ID %s does not exist in COLS", ledger_organisation_id
        )
        return False

    if request.user.email in cols_organisation.contacts.all().filter(
        is_admin=True
    ).values_list("email", flat=True):
        return True

    logger.warning(
        "User %s is not an admin for organisation %s",
        request.user.email,
        ledger_organisation_id,
    )
    return False
