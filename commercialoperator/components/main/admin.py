from django.contrib import admin
from django.forms import ModelForm

from commercialoperator.components.main.models import FileExtensionWhitelist, JobQueue

@admin.register(FileExtensionWhitelist)
class FileExtensionWhitelistAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "model",
    )
    list_display = (
        "name",
        "model",
    )
    form = ModelForm

@admin.register(JobQueue)
class JobQueueAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'job_cmd',
        'status',
        'created',
        'processed_dt',
    ]
    readonly_fields = [
        'id',
        'job_cmd',
        'status',
        'parameters_json',
        'processed_dt',
        'user',
        'created',
        'system_id',
    ]
    list_filter = ['status']
    ordering = ['-id', ]

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False