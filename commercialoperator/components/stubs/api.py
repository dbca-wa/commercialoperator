from rest_framework import filters

from django.db.models import Q

import logging

logger = logging.getLogger(__name__)


class LedgerOrganisationFilterBackend(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = view.search_fields
        search_term = request.GET.get("search")
        if search_term is None:
            logger.warning("No search term provided")
            return queryset
        if len(search_term) <= 1:
            logger.warning("Search term too short")
            return []

        if isinstance(queryset, list):
            search_dict = {f"{field}": search_term for field in search_fields}
            for qs in reversed(queryset):
                if any(hasattr(qs, field) == False for field in search_fields):
                    raise ValueError(
                        f"At least one search field of {search_fields} does not exist on {qs.__class__.__name__}"
                    )

                if all(
                    search_term.lower() not in getattr(qs, field).lower()
                    for field in search_fields
                    if getattr(qs, field)
                ):
                    queryset.remove(qs)
        else:
            search_dict = {
                f"{field}__icontains": search_term for field in search_fields
            }
            queryset.filter(Q(**search_dict))
            # Do we ever land in this branch of the conditional?
            raise NotImplementedError(
                "This filter_queryset implementation is not yet implemented"
            )

        return queryset
