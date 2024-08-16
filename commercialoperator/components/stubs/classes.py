from django.db import models

from ledger_api_client.order import Order as LedgerOrder


class Ersatz(models.Model):
    """Base class for substitute classes for models in ledger
        that require additional handling in commercialoperator
        (e.g. implementing in ledger api client, refactoring cols logic)
    """

    class Meta:
        abstract = True


class Address(Ersatz):
    """ledger.accounts.models.Address"""

    line1 = models.Field()
    line2 = models.Field()
    locality = models.Field()
    state = models.Field()
    postcode = models.Field()

    class Meta:
        abstract = True


class LedgerOrganisation(Ersatz):
    """ledger.accounts.models.Organisation"""

    identification = models.Field()
    name = models.Field()
    abn = models.Field()

    class Meta:
        abstract = True


class CreateInvoiceBasket(Ersatz, LedgerOrder):
    """ledger.payments.invoice.utils.CreateInvoiceBasket"""

    class Meta:
        abstract = True


class Order(Ersatz):
    """ledger.order.models.Order"""

    class Meta:
        abstract = True
