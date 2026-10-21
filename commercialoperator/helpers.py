#!/usr/bin/env python

import logging
from urllib.parse import urlparse, urlunparse

# These functionare here to avoid circular import


def _normalize_url_parts(value):
    """Extract (scheme, netloc) whether given as 'host.com', 'https://host.com',

    'localhost:8000', or 'http://localhost:8000'.
    Ignores placeholder strings like 'APIARY_INTERNAL_URL not configured'.
    """
    if not value:
        return None, None

    val_str = str(value).strip()

    # Treat empty, "none", "not configured", or strings with spaces as unconfigured
    if (
        val_str.lower() in ("none", "")
        or "not configured" in val_str.lower()
        or " " in val_str
    ):
        return None, None

    parsed = urlparse(val_str if "://" in val_str else f"//{val_str}")
    netloc = parsed.netloc.lower()
    scheme = parsed.scheme.lower() if parsed.scheme else None

    if not scheme:
        # Default to http for local dev / cluster local domains, otherwise https
        scheme = (
            "http"
            if ("localhost" in netloc or "127.0.0.1" in netloc or ".local" in netloc)
            else "https"
        )

    return scheme, netloc


def _prepare_url(url, ext_host, int_host):
    """Disambiguate schemeless host URLs from true relative paths:

    - 'apiary-dev.../path' -> '//apiary-dev.../path' (recognized as netloc)
    - '/internal/path'     -> '/internal/path'        (recognized as path)
    - 'internal/path'      -> '/internal/path'        (recognized as path)
    """
    if not url:
        return ""

    url = url.strip()

    # 1. Already has scheme or protocol-relative slashes
    if "://" in url or url.startswith("//"):
        return url

    # 2. True relative path with leading slash
    if url.startswith("/"):
        return url

    # 3. Schemeless domain URL (e.g. 'apiary-dev.dbca.wa.gov.au/path')
    lower_url = url.lower()
    if (ext_host and lower_url.startswith(ext_host)) or (
        int_host and lower_url.startswith(int_host)
    ):
        return f"//{url}"

    # 4. Relative path missing a leading slash (e.g. 'internal/proposal/1234')
    return f"/{url}"


def convert_external_url_to_internal_url(url):
    from django.conf import settings  # Prevents circular imports

    ext_scheme, ext_host = _normalize_url_parts(
        getattr(settings, "APIARY_EXTERNAL_URL", None)
    )
    int_scheme, int_host = _normalize_url_parts(
        getattr(settings, "APIARY_INTERNAL_URL", None)
    )

    target_host = int_host or ext_host
    target_scheme = int_scheme or ext_scheme or "https"

    if not target_host or not url:
        return url

    # Fix schemeless domains before urlparse sees them
    cleaned_url = _prepare_url(url, ext_host, int_host)
    parsed = urlparse(cleaned_url)

    # 1. True relative path (e.g. '/internal/proposal/1234')
    if not parsed.netloc:
        path = parsed.path if parsed.path.startswith("/") else f"/{parsed.path}"
        return urlunparse(
            (
                target_scheme,
                target_host,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    # 2. Already internal -> ensure it has a scheme and return
    if int_host and (
        parsed.netloc.lower() == int_host
        or (parsed.hostname and parsed.hostname.lower() == int_host)
    ):
        return (
            urlunparse(parsed._replace(scheme=target_scheme))
            if not parsed.scheme
            else url
        )

    # 3. Match external netloc -> swap to internal
    if ext_host and parsed.netloc.lower() == ext_host:
        return urlunparse(parsed._replace(scheme=target_scheme, netloc=target_host))

    # 4. Match external hostname with custom port
    if ext_host and parsed.hostname and parsed.hostname.lower() == ext_host:
        port_suffix = (
            f":{parsed.port}" if parsed.port and ":" not in target_host else ""
        )
        return urlunparse(
            parsed._replace(scheme=target_scheme, netloc=f"{target_host}{port_suffix}")
        )

    return url


def convert_internal_url_to_external_url(url):
    from django.conf import settings  # Prevents circular imports

    ext_scheme, ext_host = _normalize_url_parts(
        getattr(settings, "APIARY_EXTERNAL_URL", None)
    )
    int_scheme, int_host = _normalize_url_parts(
        getattr(settings, "APIARY_INTERNAL_URL", None)
    )

    target_host = ext_host or int_host
    target_scheme = ext_scheme or int_scheme or "https"

    if not target_host or not url:
        return url

    # Fix schemeless domains before urlparse sees them
    cleaned_url = _prepare_url(url, ext_host, int_host)
    parsed = urlparse(cleaned_url)

    # 1. True relative path (e.g. '/external/proposal/1234')
    if not parsed.netloc:
        path = parsed.path if parsed.path.startswith("/") else f"/{parsed.path}"
        return urlunparse(
            (
                target_scheme,
                target_host,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    # 2. Already external -> ensure it has a scheme and return
    if ext_host and (
        parsed.netloc.lower() == ext_host
        or (parsed.hostname and parsed.hostname.lower() == ext_host)
    ):
        return (
            urlunparse(parsed._replace(scheme=target_scheme))
            if not parsed.scheme
            else url
        )

    # 3. Match internal netloc -> swap to external
    if int_host and parsed.netloc.lower() == int_host:
        return urlunparse(parsed._replace(scheme=target_scheme, netloc=target_host))

    # 4. Match internal hostname with custom port
    if int_host and parsed.hostname and parsed.hostname.lower() == int_host:
        port_suffix = (
            f":{parsed.port}" if parsed.port and ":" not in target_host else ""
        )
        return urlunparse(
            parsed._replace(scheme=target_scheme, netloc=f"{target_host}{port_suffix}")
        )

    return url


from django.conf import settings
from django.contrib.auth.models import Group
from ledger_api_client.ledger_models import UsersInGroup
from ledger_api_client.managed_models import SystemGroup

from commercialoperator.components.segregation.utils import (
    retrieve_email_user,
    retrieve_organisation_delegate_ids,
    retrieve_user_groups,
)

logger = logging.getLogger(__name__)


def is_payment_admin(user):
    print("is_payment_admin")
    if user.is_superuser:
        return True
    group = Group.objects.filter(name=settings.PAYMENT_OFFICERS_GROUP)
    if group.exists():
        return user.id in list(
            UsersInGroup.objects.filter(group_id=group.first().id).values_list(
                "emailuser_id", flat=True
            )
        )
    else:
        return False


def belongs_to_by_user_id(user_id, group_name):
    system_group = SystemGroup.objects.filter(name=group_name).first()
    return system_group and user_id in system_group.get_system_group_member_ids()


# NOTE: all belongs_to groups have been altered to require 1) settings env vars 2) system group models to be implemented
# This will require a migration plan to transition from ledger-based groups to local groups
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
    return request.user.is_authenticated and belongs_to(
        request.user, settings.ADMIN_GROUP
    )


def is_finance_officer(request):
    return belongs_to(request.user, settings.GROUP_FINANCE)


# NOTE: this is now used only in the UserSerializer for information - it should not be used to determine internal group membership
def in_dbca_domain(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False

    email = getattr(user, "email", None)
    if not email or "@" not in email:
        return False

    domain = email.rsplit("@", 1)[1].lower()
    return domain in settings.DEPT_DOMAINS


def is_in_organisation_contacts(request, organisation):
    """Takes a cols Organisation object and checks if the request.user is in the organisation's contacts."""

    delegate_ids = retrieve_organisation_delegate_ids(organisation.id)
    delegates = [retrieve_email_user(user_id) for user_id in delegate_ids]
    delegate_emails = [
        delegate.email for delegate in delegates if delegate and delegate.email
    ]

    return request.user.email in delegate_emails


def is_approver(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups("proposalapprovergroup", request.user.id).exists()
        if request.user
        else False
    )


def is_assessor(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups("proposalassessorgroup", request.user.id).exists()
        if request.user
        else False
    )


def is_district_approver(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups(
            "districtproposalapprovergroup", request.user.id
        ).exists()
        if request.user
        else False
    )


def is_district_assessor(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups(
            "districtproposalassessorgroup", request.user.id
        ).exists()
        if request.user
        else False
    )


def is_organisation_access_approver(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups("organisationaccessgroup", request.user.id).exists()
        if request.user
        else False
    )


def is_referrer(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups("referralrecipientgroup", request.user.id).exists()
        if request.user
        else False
    )


def is_qa_officer(request):
    return (
        request.user.is_superuser
        or retrieve_user_groups("qaofficergroup", request.user.id).exists()
        if request.user
        else False
    )


def is_internal(request):
    """Any users in an internal user group"""
    return (
        request.user.is_superuser
        or is_commercialoperator_admin(request)
        or is_payment_admin(request.user)
        or is_finance_officer(request)
        or is_organisation_access_approver(request)
        or is_qa_officer(request)
    )


def is_internal_user(user):

    payment_group = Group.objects.filter(name=settings.PAYMENT_OFFICERS_GROUP)
    return (
        user
        and hasattr(user, "id")
        and (
            user.is_superuser
            or belongs_to(user, settings.ADMIN_GROUP)
            or user.id
            in list(
                UsersInGroup.objects.filter(
                    group_id=payment_group.first().id
                ).values_list("emailuser_id", flat=True)
            )
            or belongs_to(user, settings.GROUP_FINANCE)
            or retrieve_user_groups("organisationaccessgroup", user.id).exists()
            or retrieve_user_groups("qaofficergroup", user.id)
        )
    )
