from django.db import models

class Ersatz(models.Model):
    class Meta:
        abstract = True

class ErsatzAddress(Ersatz):

    line1 = models.Field()
    line2 = models.Field()
    locality = models.Field()
    state = models.Field()
    postcode = models.Field()

    class Meta:
        abstract = True

class ErsatzOrganisation(Ersatz):

    identification = models.Field()
    name = models.Field()
    abn = models.Field()

    class Meta:
        abstract = True
