from django.core.exceptions import PermissionDenied

from commercialoperator.components.stubs.utils import (
    retrieve_email_user,
    retrieve_group_members,
)


class ReferralOwnerMixin(object):

    def check_owner(self, user):
        return self.get_object().referral == user

    def dispatch(self, request, *args, **kwargs):
        if not self.check_owner(request.user):
            raise PermissionDenied
        return super(ReferralOwnerMixin, self).dispatch(request, *args, **kwargs)


class MembersEmailMixin:
    @property
    def members_email(self):
        members = retrieve_group_members(self)
        emailusers = [retrieve_email_user(i) for i in members]
        emailusers = [u for u in emailusers if u]
        return [u.email for u in emailusers]
