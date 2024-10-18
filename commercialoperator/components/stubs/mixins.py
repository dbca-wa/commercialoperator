from commercialoperator.components.stubs.utils import (
    retrieve_email_user,
    retrieve_group_members,
)


class MembersPropertiesMixin:
    @property
    def all_members(self):
        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        return all_members

    @property
    def filtered_members(self):
        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        emailuser = [retrieve_email_user(m) for m in all_members]
        return [u for u in emailuser if u]

    @property
    def members_list(self):
        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        emailuser = [retrieve_email_user(m) for m in all_members]
        return [u.email for u in emailuser if u]
