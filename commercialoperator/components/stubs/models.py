"""Actual replacement models for ledger models
    TODO: Need to be placed in a proper location
"""

from django.db import models

from commercialoperator.components.main.models import CommunicationsLogEntry, UserAction


class EmailUserLogEntry(CommunicationsLogEntry):
    emailuser = models.IntegerField()

    def __str__(self):
        return f"Email User ID: {self.email_user} - {self.subject}"

    class Meta:
        abstract = True
        app_label = "boranga"


class EmailUserAction(UserAction):
    email_user = models.IntegerField()

    @classmethod
    def log_action(cls, email_user, action, request_user):
        return cls.objects.create(
            email_user=email_user.id,
            who=request_user.id,
            what=str(action),
        )

    class Meta:
        abstract = True
        app_label = "CommunicationsLogEntry"
