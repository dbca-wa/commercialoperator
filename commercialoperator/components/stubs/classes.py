from django.db import models

class Ersatz(models.Model):
    class Meta:
        abstract = True

class Address(Ersatz):

    line1 = models.Field()
    line2 = models.Field()
    locality = models.Field()
    state = models.Field()
    postcode = models.Field()

    class Meta:
        abstract = True

class LedgerOrganisation(Ersatz):

    identification = models.Field()
    name = models.Field()
    abn = models.Field()

    class Meta:
        abstract = True
