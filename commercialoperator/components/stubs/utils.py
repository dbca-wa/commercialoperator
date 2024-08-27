from django.conf import settings
from django.core.cache import cache
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.utils import oracle_parser, update_payments

import logging

logger = logging.getLogger(__name__)


def retrieve_email_user(email_user_id):
    cache_key = settings.CACHE_KEY_LEDGER_EMAIL_USER.format(email_user_id)
    email_user = cache.get(cache_key)
    if email_user is None:
        try:
            email_user = EmailUser.objects.get(id=email_user_id)
        except EmailUser.DoesNotExist:
            logger.error(f"EmailUser with id {email_user_id} does not exist")
            return None
        else:
            cache.set(cache_key, email_user, settings.CACHE_TIMEOUT_5_SECONDS)
    return email_user


def createCustomBasket(*args, **kwargs):
    raise NotImplementedError(
        "ledger.checkout.utils.createCustomBasket needs refactoring"
    )


def oracle_parser(*args, **kwargs):
    logger.error(oracle_parser())
    raise NotImplementedError(
        "ledger.payments.utils.oracle_parser needs implementation"
    )


def update_payments(*args, **kwargs):
    logger.error(update_payments())
    raise NotImplementedError(
        "ledger.payments.utils.update_payments needs implementation"
    )
