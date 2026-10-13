from commercialoperator import helpers


class AdminGroupPermissionMixin:
    def has_module_permission(self, request):
        return helpers.is_commercialoperator_admin(request) or super().has_module_permission(
            request
        )

    def has_view_permission(self, request, obj=None):
        return helpers.is_commercialoperator_admin(request) or super().has_view_permission(
            request, obj
        )

    def has_add_permission(self, request):
        return helpers.is_commercialoperator_admin(request) or super().has_add_permission(
            request
        )

    def has_change_permission(self, request, obj=None):
        return helpers.is_commercialoperator_admin(request) or super().has_change_permission(
            request, obj
        )

    def has_delete_permission(self, request, obj=None):
        return helpers.is_commercialoperator_admin(request) or super().has_delete_permission(
            request, obj
        )
