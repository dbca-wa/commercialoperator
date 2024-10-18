from django.conf import settings
from ledger_api_client import utils as ledger_api_utils

from commercialoperator.components.organisations.models import Organisation
from commercialoperator.settings import (
    TEMPLATE_GROUP,
    TEMPLATE_HEADER_LOGO,
    TEMPLATE_TITLE,
)


def commercialoperator_url(request):
    organisations_user_can_admin = Organisation.organisations_user_can_admin(
        request.user.id
    )
    ledger_totals = ledger_api_utils.get_ledger_totals()
    return {
        "template_group": TEMPLATE_GROUP,
        "template_header_logo": TEMPLATE_HEADER_LOGO,
        "template_title": TEMPLATE_TITLE,
        "organisations_user_can_admin": organisations_user_can_admin,
        "build_tag": settings.BUILD_TAG,
        "LEDGER_UI_URL": settings.LEDGER_UI_URL,
        "PAYMENT_SYSTEM_PREFIX": settings.PAYMENT_SYSTEM_PREFIX,
        "app_build_url": settings.DEV_APP_BUILD_URL,
        "ledger_totals": ledger_totals,
    }
