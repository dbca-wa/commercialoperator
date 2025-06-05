import functools
from commercialoperator.components.segregation.decorators import basic_exception_handler


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
