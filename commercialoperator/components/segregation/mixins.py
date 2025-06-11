import functools

from django.core.exceptions import FieldDoesNotExist
from django.db.models.functions import Lower
from django.forms import CharField

from commercialoperator.components.segregation.decorators import basic_exception_handler

import logging

logger = logging.getLogger(__name__)


class MembersPropertiesMixin:
    @property
    def all_members(self):
        from commercialoperator.components.segregation.utils import (
            retrieve_group_members,
        )

        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        return all_members

    @property
    def filtered_members(self):
        from commercialoperator.components.segregation.utils import (
            retrieve_group_members,
            retrieve_email_user,
        )

        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        emailuser = [retrieve_email_user(m) for m in all_members]
        return [u for u in emailuser if u]

    @property
    def members_list(self):
        from commercialoperator.components.segregation.utils import (
            retrieve_group_members,
            retrieve_email_user,
        )

        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        emailuser = [retrieve_email_user(m) for m in all_members]
        return [u.email for u in emailuser if u]


class RecursiveGetAttributeMixin:

    @basic_exception_handler
    def rgetattr(self, obj, attr, *args, **kwargs):
        """Recursively get an attribute from an object or a dictionary.
        This method allows to access nested attributes using dot notation.

        Args:
            obj: The object or dictionary to retrieve the attribute from.
            attr: The attribute name, which can be a nested path (e.g. "a.b.c").
            *args: Additional arguments to pass to `getattr
            kwargs: Additional keyword arguments, including:
                - raise_exception: If True, raises an exception if the attribute is not found.
                                  Defaults to False.
        Returns:
            The value of the attribute if found, otherwise None.
        Raises:
            ValueError: If `raise_exception` is True and the attribute is not found.
        """

        raise_exception = kwargs.get("raise_exception", False)

        def _getattr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr, None)
            else:
                has_attr = hasattr(obj, attr)
                if raise_exception and not has_attr:
                    raise ValueError(
                        f"Attribute '{attr}' not found in {obj.__class__.__name__}"
                    )
                return getattr(obj, attr, *args) if has_attr else None

        return functools.reduce(_getattr, [obj] + attr.split("."))


class FilterHelperMixin:
    # List of field type names that should be treated as case-insensitive
    case_insensitive_fields = []

    def __init__(self, *args, **kwargs):
        self.case_insensitive_fields = kwargs.pop(
            "case_insensitive_fields", [CharField.__name__]
        )

        super().__init__(*args, **kwargs)

    def to_case_insensitive_ordering(self, ordering, queryset):
        """
        Converts the ordering list to a case-insensitive ordering
        by applying the Lower function to fields that are of any type
        specified in `case_insensitive_fields`.
        Args:
            ordering (list): List of field names to order by.
            queryset (QuerySet): The queryset to apply the ordering to.
        Returns:
            tuple: A tuple containing the modified ordering list and a boolean indicating
                   whether the ordering is in reverse.
                   In case of reverse ordering, the reverse class function needs to be called
                     on the queryset.
        """

        reverse = (
            ordering[0].startswith("-")
            if bool(ordering) and ordering[0] is not None
            else False
        )
        # Remove the leading '-' if present
        if reverse:
            ordering = [o.replace("-", "") for o in ordering]
        # Apply Lower function to fields that need to be case-insensitive
        ordering = [
            (Lower(o) if self._is_stringy_field(queryset, o) else o) for o in ordering
        ]

        logger.debug(
            f"Converted ordering: {ordering} with reverse={reverse} for queryset {queryset.model.__name__}"
        )
        return ordering, reverse

    def _is_stringy_field(self, queryset, field_name):
        """
        Checks if the queryset field is a string or can be treated as a string.
        Args:
            queryset: The queryset to check the field against.
            field_name: The name of the field to check.
        Returns:
            bool: True if the field is a string or can be treated as a string, False otherwise.
        """

        _field_name = field_name.lstrip("-")  # Remove leading '-' if present
        field = None

        try:
            field = queryset.model._meta.get_field(_field_name)
        except FieldDoesNotExist:
            # If the field does not exist, we check if it is an annotation
            if _field_name in queryset.query.annotations:
                # If the field is an annotation, we retrieve its type
                field = queryset.query.annotations.get(_field_name, None).field.__class__
        else:
            # If the field exists, we have to check its type next
            field = type(field)

        if not field:
            logger.warning(
                f"Field or annotation '{_field_name}' does not exist in the model {queryset.model.__name__}."
            )
            return False
        return field.__name__ in [CharField.__name__]
