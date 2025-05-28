from django.db import models
from reversion.models import Version
from reversion import revisions

from commercialoperator.components.segregation.utils import (
    retrieve_ledger_user_info_by_id,
)


class RevisionedMixin(models.Model):
    """
    A model tracked by reversion through the save method.
    """

    def save(self, **kwargs):
        if kwargs.pop("no_revision", False):
            super(RevisionedMixin, self).save(**kwargs)
        else:
            with revisions.create_revision():
                if "version_user" in kwargs:
                    revisions.set_user(kwargs.pop("version_user", None))
                if "version_comment" in kwargs:
                    revisions.set_comment(kwargs.pop("version_comment", ""))
                super(RevisionedMixin, self).save(**kwargs)

    @property
    def created_date(self):
        return Version.objects.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):
        return Version.objects.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True


class RetrieveUserResidentialAddressMixin:
    @staticmethod
    def get_user_residential_address(user_id):
        return (
            retrieve_ledger_user_info_by_id(user_id)
            .get("user", {})
            .get("residential_address", {})
        )
