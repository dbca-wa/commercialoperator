from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.managed_models import SystemGroup
from django.conf import settings

import logging

from commercialoperator.components.stubs.utils import (
    retrieve_email_user,
    retrieve_organisation_delegate_ids,
)

logger = logging.getLogger(__name__)


def belongs_to_by_user_id(user_id, group_name):
    system_group = SystemGroup.objects.filter(name=group_name).first()
    return system_group and user_id in system_group.get_system_group_member_ids()


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """

    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    return belongs_to_by_user_id(user.id, group_name)


def is_commercialoperator_admin(request):
    return (
        request.user.is_authenticated
        and in_dbca_domain(request)
        and belongs_to(request.user, settings.ADMIN_GROUP)
    )


def in_dbca_domain(request):
    user = request.user
    domain = user.email.split("@")[1]
    if domain in settings.DEPT_DOMAINS:
        if not user.is_staff:
            # hack to reset department user to is_staff==True, if the user logged in externally (external departmentUser login defaults to is_staff=False)
            user.is_staff = True
            user.save()
        return True
    return False


def is_in_organisation_contacts(request, organisation):
    delegate_ids = retrieve_organisation_delegate_ids(organisation.id)
    delegates = [retrieve_email_user(user_id) for user_id in delegate_ids]
    delegate_emails = [delegate.email for delegate in delegates]

    return request.user.email in delegate_emails


def is_departmentUser(request):
    return request.user.is_authenticated and in_dbca_domain(request)


def is_customer(request):
    return request.user.is_authenticated and not request.user.is_staff


def is_internal(request):
    return is_departmentUser(request)


def get_all_officers():
    return EmailUser.objects.filter(groups__name="Commercial Operator Admin")


def email_in_dbca_domain(email: str) -> bool:
    return email.split("@")[1] in settings.DEPT_DOMAINS


def in_dbca_domain(request):
    user = request.user
    if not email_in_dbca_domain(user.email):
        return False

    if not user.is_staff:
        # hack to reset department user to is_staff==True, if the user logged in externally
        # (external departmentUser login defaults to is_staff=False)
        user.is_staff = True
        user.save()

    return True
