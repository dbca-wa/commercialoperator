from ledger_api_client.utils import oracle_parser, update_payments

import logging

logger = logging.getLogger(__name__)

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
