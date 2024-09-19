from django.apps import apps
from django.db import models
from django.conf import settings
from django.core.cache import cache
from rest_framework import status

from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.utils import (
    oracle_parser as ledger_oracle_parser,
    update_payments as ledger_update_payments,
    get_all_organisation,
)

import logging

logger = logging.getLogger(__name__)


def retrieve_email_user(email_user_id):
    cache_key = settings.CACHE_KEY_LEDGER_EMAIL_USER.format(email_user_id)
    cache_timeout = (
        settings.DEBUG
        and settings.CACHE_TIMEOUT_24_HOURS
        or settings.CACHE_TIMEOUT_5_SECONDS
    )
    email_user = cache.get(cache_key)

    if settings.DEBUG and email_user is EmailUser.DoesNotExist:
        return None
    elif email_user is None:
        try:
            email_user = EmailUser.objects.get(id=email_user_id)
        except EmailUser.DoesNotExist:
            # logger.error(f"EmailUser with id {email_user_id} does not exist")
            if settings.DEBUG:
                cache.set(cache_key, EmailUser.DoesNotExist, cache_timeout)
            return None
        else:
            cache.set(cache_key, email_user, cache_timeout)
    return email_user


class EmailUserQuerySet(models.QuerySet):
    def expand_emailuser_fields(self, emailuser_fk_field, emailuser_properties={}):
        """
        Adds the emailuser object to the QuerySet and expands it with additional fields that are properties
        of an EmailUser foreign key if provided through the `emailuser_properties` parameter.

        Args:
            emailuser_fk_field: str, name of the field that points to an EmailUser foreign key, e.g. "submitter"
            emailuser_properties: Set of str, names of the properties of EmailUser to be added to the QuerySet,
                e.g. ["email", "first_name", "last_name"] become submitter_email, submitter_first_name, submitter_last_name
                if emailuser_fk_field is "submitter"

        Returns:
            QuerySet with additional fields emailuser_fk_field_exists, emailuser_fk_field_email, emailuser_fk_field_first_name, emailuser_fk_field_last_name
        """

        if not emailuser_fk_field:
            raise ValueError(
                "A emailuser_fk_field that points to an EmailUser foreign key must be provided"
            )

        emailuser_fk_field_id = f"{emailuser_fk_field}_id"

        if not getattr(self.model, emailuser_fk_field_id, None):
            raise ValueError(f"Field {emailuser_fk_field} does not exist in the model")

        # I wish this would work :(((
        # from django.db.models import Subquery, OuterRef
        # return self.annotate(user_email=Subquery(EmailUser.objects.filter(id=OuterRef("submitter_id")).values("email")))

        emailuser_property_values = {
            f"{emailuser_fk_field}_{property}": models.Value("")
            for property in emailuser_properties
        }
        emailuser_property_values[f"{emailuser_fk_field}_exists"] = models.Value(False)

        self = self.annotate(**emailuser_property_values)

        for obj in self:
            emailuser_fk_field_id_value = getattr(obj, emailuser_fk_field_id)
            emailuser = retrieve_email_user(emailuser_fk_field_id_value)
            setattr(obj, emailuser_fk_field, emailuser)
            if emailuser is not None:
                for property in emailuser_properties:
                    if property == f"{emailuser_fk_field}_exists":
                        setattr(obj, f"{emailuser_fk_field}_exists", True)
                        continue
                    setattr(
                        obj,
                        f"{emailuser_fk_field}_{property}",
                        getattr(emailuser, property),
                    )

        return self


def createCustomBasket(*args, **kwargs):
    raise NotImplementedError(
        "ledger.checkout.utils.createCustomBasket needs refactoring"
    )


def oracle_parser(*args, **kwargs):
    logger.error(ledger_oracle_parser())
    raise NotImplementedError(
        "ledger.payments.utils.oracle_parser needs implementation"
    )


def update_payments(*args, **kwargs):
    logger.error(ledger_update_payments())
    raise NotImplementedError(
        "ledger.payments.utils.update_payments needs implementation"
    )


def retrieve_group_members(group_object, app_label="commercialoperator"):
    """Retrieves m2m-field members that belong to a group-object (single object or queryset), using the associated through model"""

    if hasattr(group_object, "_meta"):
        # group_object is a model object
        try:
            # The group object's model name
            model_name = group_object._meta.model_name
        except AttributeError:
            raise ValueError("The model object does not have a model name attribute")
        # Get the group object's Members through-model
        class_name = f"{model_name.lower()}members"
        InstanceClass = apps.get_model(app_label=app_label, model_name=f"{class_name}")

        return InstanceClass.objects.filter(
            **{f"{model_name.lower()}_id": group_object.id}
        ).values_list("emailuser_id", flat=True)
    else:
        # group_object is a QuerySet
        class_name = group_object.model.__name__
        return group_object.values_list(
            f"{class_name.lower()}_members__emailuser__id", flat=True
        )


def retrieve_user_groups(class_name, user_id, app_label="commercialoperator"):
    """Retrieves m2m-field groups a user belongs to, using the associated through model"""

    InstanceClass = apps.get_model(app_label=app_label, model_name=f"{class_name}")

    return InstanceClass.objects.filter(
        **{f"{class_name.lower()}_members__emailuser_id": user_id}
    )


def retrieve_members(class_object, app_label="commercialoperator"):
    """Retrieves m2m-field members using the associated through model
    `ClassWithMembersFieldMembers`.
    """

    class_name = class_object.__class__.__name__
    InstanceClass = apps.get_model(
        app_label=app_label, model_name=f"{class_name}Members"
    )
    return InstanceClass.objects.filter(
        **{f"{class_name.lower()}_id": class_object.id}
    ).values_list("emailuser_id", flat=True)


def retrieve_delegate_organisation_ids(email_user_id):
    from commercialoperator.components.organisations.models import (
        Organisation,
        UserDelegation,
    )

    organisation_ids = UserDelegation.objects.filter(user_id=email_user_id).values_list(
        "organisation_id", flat=True
    )

    # return list(
    #     Organisation.objects.filter(
    #         delegates__user=email_user_id,
    #         # contacts__user=email_user_id,
    #         # contacts__user_status=OrganisationContact.USER_STATUS_CHOICE_ACTIVE,
    #     ).values_list("id", flat=True)
    # )

    return organisation_ids


def retrieve_organisation_delegate_ids(organisation_id):
    from commercialoperator.components.organisations.models import (
        Organisation,
        UserDelegation,
    )

    delegate_ids = UserDelegation.objects.filter(
        organisation_id=organisation_id
    ).values_list("user_id", flat=True)

    return delegate_ids


class ListAsQuerySet(list):

    def __init__(self, *args, model, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self


def filter_organisation_list(view, request, *args, **kwargs):
    from commercialoperator.components.stubs.models import LedgerOrganisation

    queryset = view.get_queryset()
    ledger_organisation_response = get_all_organisation()
    if ledger_organisation_response["status"] == status.HTTP_200_OK:
        ledger_organisations = ledger_organisation_response["data"]

    org_ids = queryset.values_list("organisation_id", flat=True)

    organisation_dicts = [
        org for org in ledger_organisations if org["organisation_id"] in org_ids
    ]

    organisations = [LedgerOrganisation(**org_dict) for org_dict in organisation_dicts]
    organisations = view.filter_queryset(
        ListAsQuerySet(organisations, model=LedgerOrganisation)
    )

    return organisations
