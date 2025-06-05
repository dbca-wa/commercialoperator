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
    def rgetattr(self, obj, attr, *args):
        def _getattr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr, None)
            else:
                return getattr(obj, attr, *args) if hasattr(obj, attr) else None

        return functools.reduce(_getattr, [obj] + attr.split("."))
