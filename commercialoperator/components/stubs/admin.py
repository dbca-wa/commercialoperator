from math import log
from django.contrib import admin

import logging

logger = logging.getLogger(__name__)


class EmailUserFieldAdminBase(admin.ModelAdmin):
    """Base class for admin classes that use ledger-api-client EmailUser fields"""

    def __init__(self, *args, **kwargs):
        list_display_map = {fn: fn for fn in self.list_display}
        # Replace list_display fields with _field
        for fn in ["requester", "organisation"]:
            if fn in list_display_map:
                logger.debug(f"Replacing {fn} with _{fn} on {self.__class__.__name__}")
                list_display_map[fn] = f"_{fn}"
                self.readonly_fields += (f"_{fn}",)

        self.list_display = [list_display_map[fn] for fn in self.list_display]

        super(EmailUserFieldAdminBase, self).__init__(*args, **kwargs)

    def _requester(self, obj):
        return obj.requester_id

    def _organisation(self, obj):
        return obj.organisation_id