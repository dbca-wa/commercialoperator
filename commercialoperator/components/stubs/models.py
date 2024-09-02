"""Actual replacement models for ledger models
    TODO: Need to be placed in a proper location
"""

from django.db import models

from commercialoperator.components.main.models import CommunicationsLogEntry, UserAction

from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from commercialoperator.components.stubs.utils import retrieve_email_user


class EmailUserLogEntry(CommunicationsLogEntry):
    emailuser = models.IntegerField()

    def __str__(self):
        return f"Email User ID: {self.email_user} - {self.subject}"

    class Meta:
        managed = False
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
        managed = False
        app_label = "CommunicationsLogEntry"


class ReferralRecipientGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_referralrecipientgroup_members"
        managed = False
        unique_together = ("referralrecipientgroup", "emailuser")

    referralrecipientgroup = models.ForeignKey(
        "ReferralRecipientGroup",
        on_delete=models.PROTECT,
        related_name="referralrecipientgroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="referralrecipientgroup_members",
    )


class QAOfficerGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_qaofficergroup_members"
        managed = False
        unique_together = ("qaofficergroup", "emailuser")

    qaofficergroup = models.ForeignKey(
        "QAOfficerGroup",
        on_delete=models.PROTECT,
        related_name="qaofficergroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="qaofficergroup_members",
    )


class ProposalAssessorGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_proposalassessorgroup_members"
        managed = False
        unique_together = ("proposalassessorgroup", "emailuser")

    proposalassessorgroup = models.ForeignKey(
        "ProposalAssessorGroup",
        on_delete=models.PROTECT,
        related_name="proposalassessorgroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="proposalassessorgroup_members",
    )

    @property
    def emailuserro(self):
        return retrieve_email_user(self.emailuser_id)


class ProposalApproverGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_proposalapprovergroup_members"
        managed = False
        unique_together = ("proposalapprovergroup", "emailuser")

    proposalapprovergroup = models.ForeignKey(
        "ProposalApproverGroup",
        on_delete=models.PROTECT,
        related_name="proposalapprovergroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="proposalapprovergroup_members",
    )


class DistrictProposalAssessorGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_districtproposalassessorgroup_members"
        managed = False
        unique_together = ("districtproposalassessorgroup", "emailuser")

    districtproposalassessorgroup = models.ForeignKey(
        "DistrictProposalAssessorGroup",
        on_delete=models.PROTECT,
        related_name="districtproposalassessorgroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="districtproposalassessorgroup_members",
    )

    @property
    def emailuserro(self):
        return retrieve_email_user(self.emailuser_id)


class DistrictProposalApproverGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_districtproposalapprovergroup_members"
        managed = False
        unique_together = ("districtproposalapprovergroup", "emailuser")

    districtproposalapprovergroup = models.ForeignKey(
        "DistrictProposalApproverGroup",
        on_delete=models.PROTECT,
        related_name="districtproposalapprovergroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="districtproposalapprovergroup_members",
    )

    @property
    def emailuserro(self):
        return retrieve_email_user(self.emailuser_id)


class OrganisationAccessGroupMembers(models.Model):
    class Meta:
        app_label = "commercialoperator"
        # Mirror the existing django-managed through table of the m2m field
        db_table = "commercialoperator_organisationaccessgroup_members"
        managed = False
        unique_together = ("organisationaccessgroup", "emailuser")

    organisationaccessgroup = models.ForeignKey(
        "OrganisationAccessGroup",
        on_delete=models.PROTECT,
        related_name="organisationaccessgroup_members",
    )
    emailuser = models.ForeignKey(
        EmailUser,
        on_delete=models.PROTECT,
        related_name="organisationaccessgroup_members",
    )

    @property
    def emailuserro(self):
        return retrieve_email_user(self.emailuser_id)
