from django.core.exceptions import PermissionDenied

from datetime import datetime

import logging

logger = logging.getLogger(__name__)

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


class ProposedIssuanceApprovalMixin:
    def get_proposed_issuance_approval(self, obj):
        if not hasattr(obj, "proposed_issuance_approval"):
            raise AttributeError(
                "Object does not have proposed_issuance_approval attribute"
            )

        pia = obj.proposed_issuance_approval
        if not pia:
            return None

        try:
            start_date_obj = datetime.strptime(pia.get("start_date"), "%d/%m/%Y")
        except ValueError:
            logger.warning("Invalid start date format. Expecting dd/mm/YYYY")
            start_date_str = None
        else:
            start_date_str = datetime.strftime(start_date_obj, "%Y-%m-%d")

        try:
            expiry_date_obj = datetime.strptime(pia.get("expiry_date"), "%d/%m/%Y")
        except ValueError:
            logger.warning("Invalid expiry date format. Expecting dd/mm/YYYY")
            expiry_date_str = None
        else:
            expiry_date_str = datetime.strftime(expiry_date_obj, "%Y-%m-%d")

        return {
            "details": pia.get("details"),
            "start_date": start_date_str,
            "expiry_date": expiry_date_str,
            "cc_email": pia.get("cc_email"),
        }
