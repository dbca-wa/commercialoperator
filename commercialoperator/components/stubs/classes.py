from typing import Any
from django.db import models

from ledger_api_client.order import (
    Order as LedgerOrder,
)  # Exists in ledger_api_client.order, but is empty

import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)

class ErsatzQuerySet(models.QuerySet):
    def filter(self, *args: Any, **kwargs: Any):
        raise NotImplementedError(f"{self.model.__name__} model needs implementation")


class Ersatz(models.Model):
    """Base class for substitute classes for models in ledger
    that require additional handling in commercialoperator
    (e.g. implementing in ledger api client, refactoring cols logic)
    """

    objects = ErsatzQuerySet.as_manager()

    class Meta:
        abstract = True


class CreateInvoiceBasket(Ersatz, LedgerOrder):
    """ledger.payments.invoice.utils.CreateInvoiceBasket"""

    class Meta:
        managed = False
        app_label = "cols_segregation_app"


class Order(Ersatz):
    """ledger.order.models.Order"""

    class Meta:
        managed = False
        app_label = "cols_segregation_app"


class CashTransaction(Ersatz):
    """ledger.payments.models.CashTransaction"""

    class Meta:
        managed = False
        app_label = "cols_segregation_app"


class BpointTransaction(Ersatz):
    """ledger.payments.models.BpointTransaction"""

    class Meta:
        managed = False
        app_label = "cols_segregation_app"


class BpayTransaction(Ersatz):
    """ledger.payments.models.BpayTransaction"""

    class Meta:
        managed = False
        app_label = "cols_segregation_app"


class Invoice(Ersatz):
    """ledger.payments.models.Invoice"""

    class Meta:
        managed = False
        app_label = "cols_segregation_app"
