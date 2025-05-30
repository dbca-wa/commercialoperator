from itertools import islice, chain

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
    get_organisation,
    get_search_organisation,
)
from ledger_api_client.common import get_ledger_user_info_by_id

from typing import override

import logging

logger = logging.getLogger(__name__)


def retrieve_email_user(email_user_id):
    if not email_user_id:
        logger.error("Needs an email_user_id to retrieve an EmailUser object")
        return None

    if isinstance(email_user_id, EmailUser):
        logger.warning(
            f"Retrieved EmailUser object {email_user_id} directly. Returning."
        )
        return email_user_id

    cache_key = settings.CACHE_KEY_LEDGER_EMAIL_USER.format(email_user_id)
    cache_timeout = settings.CACHE_TIMEOUT_10_SECONDS
    email_user = cache.get(cache_key)

    if email_user is None:
        try:
            email_user = EmailUser.objects.get(id=email_user_id)
        except EmailUser.DoesNotExist:
            logger.error(f"EmailUser with id {email_user_id} does not exist")
            # Cache an empty EmailUser object to prevent repeated queries
            cache.set(cache_key, EmailUser(), cache_timeout)
            return None
        except TypeError:
            logger.error(
                f"Type {type(email_user_id)} `email_user_id` parameter {email_user_id} must be an integer."
            )
            raise TypeError(
                f"Type {type(email_user_id)} `email_user_id` parameter {email_user_id} must be an integer."
            )
        else:
            cache.set(cache_key, email_user, cache_timeout)
            return email_user
    elif not email_user.email:
        return None
    else:
        return email_user


def retrieve_organisation(organisation_id):
    if not organisation_id:
        logger.error("Needs an organisation_id to retrieve a Ledger Organisation object")
        return None

    cache_key = settings.CACHE_KEY_LEDGER_ORGANISATION.format(organisation_id)
    cache_timeout = settings.CACHE_TIMEOUT_10_SECONDS
    organisation = cache.get(cache_key)

    if organisation is None:
        organisation_response = get_organisation(organisation_id)
        if organisation_response.get("status", None) != status.HTTP_200_OK:
            logger.error(f"Error retrieving organisation {organisation_id}: {organisation_response.get('message', '')}")
            return None
        else:
            organisation = organisation_response.get("data", {})
            cache.set(cache_key, organisation, cache_timeout)
            return organisation
    else:
        return organisation

class EmailUserQuerySet(models.QuerySet):
    LEDGER_EXPAND_TARGET_EMAILUSER = "emailuser"
    LEDGER_EXPAND_TARGET_ORGANISATION = "organisation"
    LEDGER_EXPAND_TARGETS = {
        LEDGER_EXPAND_TARGET_EMAILUSER: "expand_emailuser_fields",
        LEDGER_EXPAND_TARGET_ORGANISATION: "expand_organisation_fields",
    }

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

        emailuser_fk_field_ids = []
        emailuser_fk_field_property_values = {}

        for obj in self:
            emailuser_fk_field_id_value = getattr(obj, emailuser_fk_field_id)
            emailuser = retrieve_email_user(emailuser_fk_field_id_value)
            if emailuser:
                setattr(obj, emailuser_fk_field, emailuser)
                if emailuser.id not in emailuser_fk_field_ids:
                    # Collect unique emailuser ids
                    emailuser_fk_field_ids.append(emailuser.id)
                if emailuser.id not in emailuser_fk_field_property_values:
                    # Collect emailuser properties
                    emailuser_fk_field_property_values[emailuser.id] = {}
                for property in emailuser_properties:
                    # Collect emailuser property values
                    emailuser_fk_field_property_values[emailuser.id][property] = (
                        getattr(emailuser, property)
                    )

        # Create a dictionary of Case expressions for each emailuser property
        # E.g. {
        #     "submitter_email": Case(
        #         When(submitter_id=1, then=Value("email1")),
        #         When(submitter_id=2, then=Value("email2")),
        #         default=Value(""),
        #         output_field=CharField()
        #     ),
        case_whens = {
            f"{emailuser_fk_field}_{property}": models.Case(
                *[
                    models.When(
                        **{f"{emailuser_fk_field_id}": emailuser_fk_field_id_value},
                        then=models.Value(
                            emailuser_fk_field_property_values[
                                emailuser_fk_field_id_value
                            ][property]
                        ),
                    )
                    for emailuser_fk_field_id_value in emailuser_fk_field_ids
                ],
                default=models.Value(""),
                output_field=models.CharField(),
            )
            for property in emailuser_properties
        }

        # Add the emailuser_fk_field_exists field, e.g. submitter_exists
        self = self.annotate(
            **{
                f"{emailuser_fk_field}_exists": models.Case(
                    models.When(
                        **{f"{emailuser_fk_field_id}__in": emailuser_fk_field_ids},
                        then=models.Value(True),
                    ),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                )
            }
        ).annotate(**case_whens)

        return self

    def expand_organisation_fields(self, organisation_foreign_key_field, organisation_properties={}):
        if not organisation_foreign_key_field:
            raise ValueError(
                "A organisation_foreign_key_field that points to an Organisation foreign key must be provided"
            )

        organisation_foreign_key_field_id = f"{organisation_foreign_key_field}_id"

        if not getattr(self.model, organisation_foreign_key_field_id, None):
            raise ValueError(f"Field {organisation_foreign_key_field} does not exist in the model")

        for obj in self:
            pass
        
        if True:
            obj = self.last()
            cols_organisation = getattr(obj, organisation_foreign_key_field, None)

            ledger_organisations = {}
            for organisation_property in organisation_properties:
                props = organisation_property.split("__")
                ledger_object_name = props[0]
                ledger_object_value = props[1]

                ledger_organisation_id_name = f"{ledger_object_name}_id"

                if ledger_organisation_id_name not in ledger_organisations:
                    ledger_organisations[ledger_organisation_id_name] = []
                
                ledger_organisations[ledger_organisation_id_name] += [ledger_object_value]

            ledger_organisation_ids = []
            ledger_organisation_property_values = {}
            for ledger_organisation_id_name, ledger_organisation_id_properties in ledger_organisations.items():
                if not ledger_organisation_id_properties:
                    continue

                ledger_organisation_id = getattr(cols_organisation, ledger_organisation_id_name, None)
                ledger_organisation = retrieve_organisation(ledger_organisation_id)
                if not ledger_organisation:
                    logger.error(
                        f"Organisation with id {ledger_organisation_id} does not exist in the ledger"
                    )
                    continue

            if ledger_organisation:
                if ledger_organisation_id not in ledger_organisation_ids:
                    # Collect unique organisation ids
                    ledger_organisation_ids.append(ledger_organisation_id)
                if ledger_organisation_id not in ledger_organisation_property_values:
                    # Collect organisation properties
                    ledger_organisation_property_values[ledger_organisation_id] = {}
                for property in ledger_organisation_id_properties:
                    # Collect organisation property values
                    ledger_organisation_property_values[ledger_organisation_id][property] = (
                        ledger_organisation.get(property, "")
                    )

        # MONDAY continue here
        case_whens = {
            f"{organisation_foreign_key_field}_{property}": models.Case(
                *[
                    models.When(
                        **{f"{organisation_foreign_key_field_id}": ledger_organisation_id_value},
                        then=models.Value(
                            ledger_organisation_property_values[
                                ledger_organisation_id_value
                            ][property]
                        ),
                    )
                    for ledger_organisation_id_value in ledger_organisation_ids
                ],
                default=models.Value(""),
                output_field=models.CharField(),
            )
            for property in organisation_properties
        }









        


    @override
    def order_by(self, *field_names, **kwargs):
        ledger_lookup_fields = kwargs.get("ledger_lookup_fields", {})
        ledger_lookup_extras = kwargs.get("ledger_lookup_extras", {})

        # Check if any of the field names are ledger lookup fields. Only have to look at the first part of the field name before the '__'
        field_name_sublists = [f.split("__") for f in field_names]
        is_ledger_lookup = any(
            sublist[0].replace("-", "") in ledger_lookup_fields
            for sublist in field_name_sublists
        )

        if not is_ledger_lookup:
            # If no ledger lookup fields are provided, use the default ordering
            return super().order_by(*field_names)

        # A dictionary of each ledger lookup field and its subfields
        expand_fields = {}
        for sublist in field_name_sublists:
            # The field name is the first part of the sublist, e.g. "submitter" in "submitter__email"
            field_name = sublist[0].replace("-", "")
            if field_name not in expand_fields:
                expand_fields[field_name] = []

            expand_fields[field_name] += ["__".join(sublist[1:])]

        # Expand the queryset with annotations in the form of submitter__email translates to submitter_email
        for key, value in expand_fields.items():
            # Emailuser or organisation (default is emailuser if not provided in the kwargs)
            retrieve_function_target = ledger_lookup_extras.get(key, self.LEDGER_EXPAND_TARGET_EMAILUSER)
            retrieve_function_name = self.LEDGER_EXPAND_TARGETS.get(retrieve_function_target)
            retrieve_function = getattr(self, retrieve_function_name, None)
            if not retrieve_function:
                raise ValueError(
                    f"Invalid ledger lookup target '{retrieve_function_target}' for field '{key}'."
                )
            
            # Call the proper retrieve function with the key and value
            self = retrieve_function(
                key,
                value
            )
            # self = self.expand_emailuser_fields(key, value)
            # self.expand_organisation_fields(key)

        # A list of field names that have been expanded in the prior step to order by, e.g. ["submitter_email", "submitter_first_name"] or ['-submitter_first_name', '-submitter_last_name']
        expanded_field_names = [("_").join(sublist) for sublist in field_name_sublists]

        return super().order_by(*expanded_field_names)


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
        "organisation__organisation_id", flat=True
    )

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


def retrieve_ledger_user_info_by_id(email_user_id):
    """Queries ledger user info, that contains user details or information status"""

    cache_key = settings.CACHE_KEY_LEDGER_USER_INFO.format(email_user_id)
    cache_timeout = settings.CACHE_TIMEOUT_5_SECONDS

    user_info = cache.get(cache_key)

    if user_info is None:
        user_info = get_ledger_user_info_by_id(f"{email_user_id}")
        if user_info.get("status", None) != status.HTTP_200_OK:
            return {}

        cache.set(cache_key, user_info, cache_timeout)
        return user_info
    else:
        return user_info


def retrieve_cols_organisations_from_ledger_org_ids(user):
    """Takes a user object, retrieves the organisations that the user is a delegate of from the ledger
    and adds the corresponding organisation model id to the ledger organisation object.
    """

    from commercialoperator.components.organisations.models import Organisation

    user_id = user.id
    # user_id = 163998  # An existing user id for testing
    user_ledger_org_ids = retrieve_delegate_organisation_ids(user_id)

    commercialoperator_organisations = []

    for org_id in user_ledger_org_ids:

        cache_key = settings.CACHE_KEY_LEDGER_ORGANISATION.format(org_id)
        cache_timeout = settings.CACHE_TIMEOUT_5_SECONDS

        ledger_organisation = cache.get(cache_key)

        if ledger_organisation:
            # If the organisation is in the cache, use it
            logger.debug(f"Organisation {org_id} found in cache")
            commercialoperator_organisations.append(ledger_organisation)
            continue

        organisations_response = get_organisation(org_id)

        if organisations_response.get("status", None) == status.HTTP_200_OK:
            # Get the organisation object from ledger
            ledger_organisation = organisations_response.get("data", [])
            # Add the cols organisation model id to the ledger organisation object
            commercialoperator_organisation = Organisation.objects.get(
                organisation_id=org_id
            )
            ledger_organisation["id"] = commercialoperator_organisation.id
            commercialoperator_organisations.append(ledger_organisation)

            cache.set(cache_key, ledger_organisation, cache_timeout)
        else:
            raise ValueError(f"Error retrieving organisations for user {user_id}")
        logger.info(
            f"Retrieved organisations for user {user_id}: {commercialoperator_organisations}"
        )

    return commercialoperator_organisations


class ListAsQuerySet(list):

    def __init__(self, *args, model, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self


def filter_organisation_list(view, request, *args, **kwargs):
    from commercialoperator.components.segregation.models import LedgerOrganisation

    queryset = view.get_queryset()

    search_term = request.query_params.get("search", None)
    if search_term is None:
        ledger_organisation_response = get_all_organisation()
    elif search_term.isdigit():
        logger.debug("Searching for organisation ABN")
        # Function signature: get_search_organisation(organisation_name, organisation_abn)
        ledger_organisation_response = get_search_organisation(None, search_term)
    else:
        logger.debug("Searching for organisation name")
        ledger_organisation_response = get_search_organisation(search_term, None)

    if ledger_organisation_response["status"] == status.HTTP_200_OK:
        ledger_organisations = ledger_organisation_response["data"]
    else:
        logger.debug(
            f"Failed to retrieve organisations from ledger: {ledger_organisation_response.get("message", "")}"
        )
        return LedgerOrganisation.objects.none()

    org_ids = queryset.values_list("organisation_id", flat=True)

    organisation_dicts = [
        org for org in ledger_organisations if org["organisation_id"] in org_ids
    ]

    organisations = [LedgerOrganisation(**org_dict) for org_dict in organisation_dicts]
    organisations = view.filter_queryset(
        ListAsQuerySet(organisations, model=LedgerOrganisation)
    )[:10]

    return organisations


class QuerySetChain(object):
    """
    Chains multiple subquerysets (possibly of different models) and behaves as
    one queryset.  Supports minimal methods needed for use with
    django.core.paginator.
    """

    def __init__(self, *subquerysets):
        self.querysets = subquerysets

    def count(self):
        """
        Performs a .count() for all subquerysets and returns the number of
        records as an integer.
        """

        return sum(qs.count() for qs in self.querysets)

    def order_by(self, *field_names):
        """
        Returns a list of the unique ordering fields for all subquerysets.
        """
        querysets = ()
        for qs in self.querysets:
            querysets += (qs.distinct().order_by(*field_names),)

        return self.__init__(*querysets)

    def _clone(self):
        "Returns a clone of this queryset chain"

        return self.__class__(*self.querysets)

    def _all(self):
        "Iterates records in all subquerysets"

        return chain(*self.querysets)

    def __getitem__(self, ndx):
        """
        Retrieves an item or slice from the chained set of results from all
        subquerysets.
        """

        if type(ndx) is slice:
            return list(islice(self._all(), ndx.start, ndx.stop, ndx.step or 1))
        else:
            return next(islice(self._all(), ndx, ndx + 1))
