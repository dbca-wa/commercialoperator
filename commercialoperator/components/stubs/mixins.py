from commercialoperator.components.stubs.utils import retrieve_group_members


class MembersPropertiesMixin:
    @property
    def all_members(self):
        all_members = []
        all_members.extend(retrieve_group_members(group_object=self))
        return all_members

    # TODO: filtered_members
    # TODO: members_list
