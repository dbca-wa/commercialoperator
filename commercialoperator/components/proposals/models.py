from __future__ import unicode_literals

import json
import os
import datetime
import string
from dateutil.relativedelta import relativedelta
from django.db import models,transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError, MultipleObjectsReturned, ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import OrganisationAddress
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.payments.models import Invoice
#from ledger.accounts.models import EmailUser
from ledger.licence.models import  Licence
from ledger.address.models import Country
from commercialoperator import exceptions
from commercialoperator.components.organisations.models import Organisation, OrganisationContact, UserDelegation
from commercialoperator.components.main.models import CommunicationsLogEntry, UserAction, Document, Region, District, Tenure, ApplicationType, Park, Activity, ActivityCategory, AccessType, Trail, Section, Zone, RequiredDocument, LicencePeriod
from commercialoperator.components.main.utils import get_department_user
from commercialoperator.components.proposals.email import (
    send_referral_email_notification,
    send_proposal_decline_email_notification,
    send_proposal_approval_email_notification,
    send_proposal_awaiting_payment_approval_email_notification,
    send_amendment_email_notification,
)
from commercialoperator.ordered_model import OrderedModel
from commercialoperator.components.proposals.email import send_submit_email_notification, send_external_submit_email_notification, send_approver_decline_email_notification, send_approver_approve_email_notification, send_referral_complete_email_notification, send_proposal_approver_sendback_email_notification, send_qaofficer_email_notification, send_qaofficer_complete_email_notification, send_district_proposal_submit_email_notification,send_district_proposal_approver_sendback_email_notification, send_district_approver_decline_email_notification, send_district_approver_approve_email_notification, send_district_proposal_decline_email_notification, send_district_proposal_approval_email_notification
import copy
import subprocess
from django.db.models import Q
from reversion.models import Version
from dirtyfields import DirtyFieldsMixin
from decimal import Decimal as D
import csv
import time
from multiselectfield import MultiSelectField



import logging
logger = logging.getLogger(__name__)


def update_proposal_doc_filename(instance, filename):
    return '{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_onhold_doc_filename(instance, filename):
    return '{}/proposals/{}/on_hold/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_qaofficer_doc_filename(instance, filename):
    return '{}/proposals/{}/qaofficer/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_referral_doc_filename(instance, filename):
    return '{}/proposals/{}/referral/{}'.format(settings.MEDIA_APP_DIR, instance.referral.proposal.id,filename)

def update_proposal_required_doc_filename(instance, filename):
    return '{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_requirement_doc_filename(instance, filename):
    return '{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, instance.requirement.proposal.id,filename)

def update_proposal_comms_log_filename(instance, filename):
    return '{}/proposals/{}/communications/{}'.format(settings.MEDIA_APP_DIR, instance.log_entry.proposal.id,filename)

def update_filming_park_doc_filename(instance, filename):
    return '{}/proposals/{}/filming_park_documents/{}'.format(settings.MEDIA_APP_DIR, instance.filming_park.proposal.id,filename)

def update_events_park_doc_filename(instance, filename):
    return '{}/proposals/{}/events_park_documents/{}'.format(settings.MEDIA_APP_DIR, instance.events_park.proposal.id,filename)

def update_pre_event_park_doc_filename(instance, filename):
    return '{}/proposals/{}/pre_event_park_documents/{}'.format(settings.MEDIA_APP_DIR, instance.pre_event_park.proposal.id,filename)


def application_type_choicelist():
    try:
        return [( (choice.name), (choice.name) ) for choice in ApplicationType.objects.filter(visible=True)]
    except:
        # required because on first DB tables creation, there are no ApplicationType objects -- setting a default value
        return ( ('T Class', 'T Class'), )

class ProposalType(models.Model):
    #name = models.CharField(verbose_name='Application name (eg. commercialoperator, Apiary)', max_length=24)
    #application_type = models.ForeignKey(ApplicationType, related_name='aplication_types')
    description = models.CharField(max_length=256, blank=True, null=True)
    #name = models.CharField(verbose_name='Application name (eg. commercialoperator, Apiary)', max_length=24, choices=application_type_choicelist(), default=application_type_choicelist()[0][0])
    name = models.CharField(verbose_name='Application name (eg. T Class, Filming, Event, E Class)', max_length=64, choices=application_type_choicelist(), default='T Class')
    schema = JSONField(default=[{}])
    #activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.")
    #site = models.OneToOneField(Site, default='1')
    replaced_by = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    #replaced_by = models.ForeignKey('self', blank=True, null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    def __str__(self):
        return '{} - v{}'.format(self.name, self.version)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('name', 'version')

class TaggedProposalAssessorGroupRegions(TaggedItemBase):
    content_object = models.ForeignKey("ProposalAssessorGroup")

    class Meta:
        app_label = 'commercialoperator'

class TaggedProposalAssessorGroupActivities(TaggedItemBase):
    content_object = models.ForeignKey("ProposalAssessorGroup")

    class Meta:
        app_label = 'commercialoperator'

class ProposalAssessorGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(EmailUser)
    region = models.ForeignKey(Region, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Assessor Group"
        verbose_name_plural = "Application Assessor Group"

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = ProposalAssessorGroup.objects.get(default=True)
        except ProposalAssessorGroup.DoesNotExist:
            default = None

        if self.pk:
            if not self.default and not self.region:
                raise ValidationError('Only default can have no region set for proposal assessor group. Please specifiy region')
#            elif default and not self.default:
#                raise ValidationError('There can only be one default proposal assessor group')
        else:
            if default and self.default:
                raise ValidationError('There can only be one default proposal assessor group')

    def member_is_assigned(self,member):
        for p in self.current_proposals:
            if p.assigned_officer == member:
                return True
        return False

    @property
    def current_proposals(self):
        assessable_states = ['with_assessor','with_referral','with_assessor_requirements']
        return Proposal.objects.filter(processing_status__in=assessable_states)

    @property
    def members_email(self):
        return [i.email for i in self.members.all()]

class TaggedProposalApproverGroupRegions(TaggedItemBase):
    content_object = models.ForeignKey("ProposalApproverGroup")

    class Meta:
        app_label = 'commercialoperator'

class TaggedProposalApproverGroupActivities(TaggedItemBase):
    content_object = models.ForeignKey("ProposalApproverGroup")

    class Meta:
        app_label = 'commercialoperator'

class ProposalApproverGroup(models.Model):
    name = models.CharField(max_length=255)
    #members = models.ManyToManyField(EmailUser,blank=True)
    #regions = TaggableManager(verbose_name="Regions",help_text="A comma-separated list of regions.",through=TaggedProposalApproverGroupRegions,related_name = "+",blank=True)
    #activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.",through=TaggedProposalApproverGroupActivities,related_name = "+",blank=True)
    members = models.ManyToManyField(EmailUser)
    region = models.ForeignKey(Region, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Approver Group"
        verbose_name_plural = "Application Approver Group"

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = ProposalApproverGroup.objects.get(default=True)
        except ProposalApproverGroup.DoesNotExist:
            default = None

        if self.pk:
            if not self.default and not self.region:
                raise ValidationError('Only default can have no region set for proposal assessor group. Please specifiy region')

#            if int(self.pk) != int(default.id):
#                if default and self.default:
#                    raise ValidationError('There can only be one default proposal approver group')
        else:
            if default and self.default:
                raise ValidationError('There can only be one default proposal approver group')

    def member_is_assigned(self,member):
        for p in self.current_proposals:
            if p.assigned_approver == member:
                return True
        return False

    @property
    def current_proposals(self):
        assessable_states = ['with_approver']
        return Proposal.objects.filter(processing_status__in=assessable_states)

    @property
    def members_email(self):
        return [i.email for i in self.members.all()]


class DefaultDocument(Document):
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    class Meta:
        app_label = 'commercialoperator'
        abstract =True

    def delete(self):
        if self.can_delete:
            return super(DefaultDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))



class ProposalDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    can_hide= models.BooleanField(default=False) # after initial submit, document cannot be deleted but can be hidden
    hidden=models.BooleanField(default=False) # after initial submit prevent document from being deleted

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Document"

class OnHoldDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='onhold_documents')
    _file = models.FileField(upload_to=update_onhold_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    def delete(self):
        if self.can_delete:
            return super(ProposalDocument, self).delete()

#Documents on Activities(land)and Activities(Marine) tab for T-Class related to required document questions
class ProposalRequiredDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='required_documents')
    _file = models.FileField(upload_to=update_proposal_required_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    required_doc = models.ForeignKey('RequiredDocument',related_name='proposals')
    can_hide= models.BooleanField(default=False) # after initial submit, document cannot be deleted but can be hidden
    hidden=models.BooleanField(default=False) # after initial submit prevent document from being deleted

    def delete(self):
        if self.can_delete:
            return super(ProposalRequiredDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'commercialoperator'

class QAOfficerDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='qaofficer_documents')
    _file = models.FileField(upload_to=update_qaofficer_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    def delete(self):
        if self.can_delete:
            return super(QAOfficerDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'commercialoperator'


class ReferralDocument(Document):
    referral = models.ForeignKey('Referral',related_name='referral_documents')
    _file = models.FileField(upload_to=update_referral_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted

    def delete(self):
        if self.can_delete:
            return super(ProposalDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'commercialoperator'

class RequirementDocument(Document):
    requirement = models.ForeignKey('ProposalRequirement',related_name='requirement_documents')
    _file = models.FileField(upload_to=update_requirement_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    def delete(self):
        if self.can_delete:
            return super(RequirementDocument, self).delete()


class ProposalApplicantDetails(models.Model):
    first_name = models.CharField(max_length=24, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'


class ProposalActivitiesLand(models.Model):
    activities_land = models.CharField(max_length=24, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Activity (Land)"
        verbose_name_plural = "Application Activities (Land)"


class ProposalActivitiesMarine(models.Model):
    activities_marine = models.CharField(max_length=24, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Activity (Marine)"
        verbose_name_plural = "Application Activities (Marine)"


@python_2_unicode_compatible
class ParkEntry(models.Model):
    park = models.ForeignKey('Park', related_name='park_entries')
    proposal = models.ForeignKey('Proposal', related_name='park_entries')
    arrival_date = models.DateField()
    number_adults = models.PositiveSmallIntegerField('No. of Adults', null=True, blank=True)
    number_children = models.PositiveSmallIntegerField('No. of Children', null=True, blank=True)
    number_seniors = models.PositiveSmallIntegerField('No. of Senior Citizens', null=True, blank=True)
    number_free_of_charge = models.PositiveSmallIntegerField('No. of Individuals Free of Charge', null=True, blank=True)

    class Meta:
        ordering = ['park__name']
        app_label = 'commercialoperator'
        verbose_name = "Park Entry"
        verbose_name_plural = "Park Entries"
        #unique_together = ('id', 'proposal',)

    def __str__(self):
        return self.park.name

    @property
    def park_prices(self):
        return self.park.park_prices

    @property
    def price_adult(self):
        return (self.park_prices.adult * self.number_adults)

    @property
    def price_child(self):
        return (self.park_prices.child * self.number_children)

    @property
    def price_senior(self):
        return (self.park_prices.senior * self.number_senior)

    @property
    def price_net(self):
        return (self.price_adult + self.price_child + self.price_senior)


class Proposal(DirtyFieldsMixin, RevisionedMixin):
#class Proposal(DirtyFieldsMixin, models.Model):
    APPLICANT_TYPE_ORGANISATION = 'ORG'
    APPLICANT_TYPE_PROXY = 'PRX'
    APPLICANT_TYPE_SUBMITTER = 'SUB'

    #Filming approval type choices
    LAWFUL_AUTHORITY='lawful_authority'
    LICENCE='licence'

    CUSTOMER_STATUS_TEMP = 'temp'
    CUSTOMER_STATUS_WITH_ASSESSOR = 'with_assessor'
    CUSTOMER_STATUS_AMENDMENT_REQUIRED = 'amendment_required'
    CUSTOMER_STATUS_APPROVED = 'approved'
    CUSTOMER_STATUS_DECLINED = 'declined'
    CUSTOMER_STATUS_DISCARDED = 'discarded'
    CUSTOMER_STATUS_PARTIALLY_APPROVED = 'partially_approved'
    CUSTOMER_STATUS_PARTIALLY_DECLINED = 'partially_declined'
    CUSTOMER_STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    CUSTOMER_STATUS_CHOICES = ((CUSTOMER_STATUS_TEMP, 'Temporary'), ('draft', 'Draft'),
                               (CUSTOMER_STATUS_WITH_ASSESSOR, 'Under Review'),
                               (CUSTOMER_STATUS_AMENDMENT_REQUIRED, 'Amendment Required'),
                               (CUSTOMER_STATUS_APPROVED, 'Approved'),
                               (CUSTOMER_STATUS_DECLINED, 'Declined'),
                               (CUSTOMER_STATUS_DISCARDED, 'Discarded'),
                               (CUSTOMER_STATUS_PARTIALLY_APPROVED, 'Partially Approved'),
                               (CUSTOMER_STATUS_PARTIALLY_DECLINED, 'Partially Declined'),
                               (CUSTOMER_STATUS_AWAITING_PAYMENT, 'Awaiting Payment'),
                               )

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = ['temp',
                                'draft',
                                'amendment_required',
                            ]

    # List of statuses from above that allow a customer to view an application (read-only)
    CUSTOMER_VIEWABLE_STATE = ['with_assessor', 'under_review', 'id_required', 'returns_required', 'awaiting_payment', 'approved', 'declined','partially_approved', 'partially_declined']

    PROCESSING_STATUS_TEMP = 'temp'
    PROCESSING_STATUS_DRAFT = 'draft'
    PROCESSING_STATUS_WITH_ASSESSOR = 'with_assessor'
    PROCESSING_STATUS_WITH_DISTRICT_ASSESSOR = 'with_district_assessor'
    PROCESSING_STATUS_ONHOLD = 'on_hold'
    PROCESSING_STATUS_WITH_QA_OFFICER = 'with_qa_officer'
    PROCESSING_STATUS_WITH_REFERRAL = 'with_referral'
    PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS = 'with_assessor_requirements'
    PROCESSING_STATUS_WITH_APPROVER = 'with_approver'
    PROCESSING_STATUS_RENEWAL = 'renewal'
    PROCESSING_STATUS_LICENCE_AMENDMENT = 'licence_amendment'
    PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE = 'awaiting_applicant_respone'
    PROCESSING_STATUS_AWAITING_ASSESSOR_RESPONSE = 'awaiting_assessor_response'
    PROCESSING_STATUS_AWAITING_RESPONSES = 'awaiting_responses'
    PROCESSING_STATUS_READY_FOR_CONDITIONS = 'ready_for_conditions'
    PROCESSING_STATUS_READY_TO_ISSUE = 'ready_to_issue'
    PROCESSING_STATUS_APPROVED = 'approved'
    PROCESSING_STATUS_DECLINED = 'declined'
    PROCESSING_STATUS_DISCARDED = 'discarded'
    PROCESSING_STATUS_PARTIALLY_APPROVED = 'partially_approved'
    PROCESSING_STATUS_PARTIALLY_DECLINED = 'partially_declined'
    PROCESSING_STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    PROCESSING_STATUS_CHOICES = ((PROCESSING_STATUS_TEMP, 'Temporary'),
                                 (PROCESSING_STATUS_DRAFT, 'Draft'),
                                 (PROCESSING_STATUS_WITH_ASSESSOR, 'With Assessor'),
                                 (PROCESSING_STATUS_WITH_DISTRICT_ASSESSOR, 'With District Assessor'),
                                 (PROCESSING_STATUS_ONHOLD, 'On Hold'),
                                 (PROCESSING_STATUS_WITH_QA_OFFICER, 'With QA Officer'),
                                 (PROCESSING_STATUS_WITH_REFERRAL, 'With Referral'),
                                 (PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS, 'With Assessor (Requirements)'),
                                 (PROCESSING_STATUS_WITH_APPROVER, 'With Approver'),
                                 (PROCESSING_STATUS_RENEWAL, 'Renewal'),
                                 (PROCESSING_STATUS_LICENCE_AMENDMENT, 'Licence Amendment'),
                                 (PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE, 'Awaiting Applicant Response'),
                                 (PROCESSING_STATUS_AWAITING_ASSESSOR_RESPONSE, 'Awaiting Assessor Response'),
                                 (PROCESSING_STATUS_AWAITING_RESPONSES, 'Awaiting Responses'),
                                 (PROCESSING_STATUS_READY_FOR_CONDITIONS, 'Ready for Conditions'),
                                 (PROCESSING_STATUS_READY_TO_ISSUE, 'Ready to Issue'),
                                 (PROCESSING_STATUS_APPROVED, 'Approved'),
                                 (PROCESSING_STATUS_DECLINED, 'Declined'),
                                 (PROCESSING_STATUS_DISCARDED, 'Discarded'),
                                 (PROCESSING_STATUS_PARTIALLY_APPROVED, 'Partially Approved'),
                                 (PROCESSING_STATUS_PARTIALLY_DECLINED, 'Partially Declined'),
                                 (PROCESSING_STATUS_AWAITING_PAYMENT, 'Awaiting Payment'),
                                )

    ID_CHECK_STATUS_CHOICES = (('not_checked', 'Not Checked'), ('awaiting_update', 'Awaiting Update'),
                               ('updated', 'Updated'), ('accepted', 'Accepted'))

    COMPLIANCE_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('awaiting_returns', 'Awaiting Returns'), ('completed', 'Completed'),
        ('accepted', 'Accepted'))

    CHARACTER_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('accepted', 'Accepted'))

    REVIEW_STATUS_CHOICES = (
        ('not_reviewed', 'Not Reviewed'), ('awaiting_amendments', 'Awaiting Amendments'), ('amended', 'Amended'),
        ('accepted', 'Accepted'))

#    PROPOSAL_STATE_NEW_LICENCE = 'New Licence'
#    PROPOSAL_STATE_AMENDMENT = 'Amendment'
#    PROPOSAL_STATE_RENEWAL = 'Renewal'
#    PROPOSAL_STATE_CHOICES = (
#        (1, PROPOSAL_STATE_NEW_LICENCE),
#        (2, PROPOSAL_STATE_AMENDMENT),
#        (3, PROPOSAL_STATE_RENEWAL),
#    )

    APPLICATION_TYPE_CHOICES = (
        ('new_proposal', 'New Application'),
        ('amendment', 'Amendment'),
        ('renewal', 'Renewal'),
        ('external', 'External'),
    )

    FILMING_APPROVAL_TYPE_CHOICES = ((LAWFUL_AUTHORITY, 'Lawful Authority'),
                               (LICENCE, 'Licence'),
                               )

    HALF_DAY_CHARGE='half_day_charge'
    FULL_DAY_CHARGE='full_day_charge'
    TWO_DAYS_CHARGE = '2_days_charge'
    THREE_OR_MORE_DAYS_CHARGE='3_or_more_days_charge'
    NON_STANDARD_CHARGE='non_standard_charge'

    FILMING_LICENCE_CHARGE_CHOICES=((HALF_DAY_CHARGE, 'Half day charge'),
                                    (FULL_DAY_CHARGE, 'Full day charge'),
                                    (TWO_DAYS_CHARGE, '2 days charge'),
                                    (THREE_OR_MORE_DAYS_CHARGE, '3 or more days charge'),
                                    (NON_STANDARD_CHARGE, 'Non standard charge'),
                                )

    proposal_type = models.CharField('Application Status Type', max_length=40, choices=APPLICATION_TYPE_CHOICES,
                                        default=APPLICATION_TYPE_CHOICES[0][0])
    #proposal_state = models.PositiveSmallIntegerField('Proposal state', choices=PROPOSAL_STATE_CHOICES, default=1)

    data = JSONField(blank=True, null=True)
    assessor_data = JSONField(blank=True, null=True)
    comment_data = JSONField(blank=True, null=True)
    schema = JSONField(blank=False, null=False)
    proposed_issuance_approval = JSONField(blank=True, null=True)
    #hard_copy = models.ForeignKey(Document, blank=True, null=True, related_name='hard_copy')

    customer_status = models.CharField('Customer Status', max_length=40, choices=CUSTOMER_STATUS_CHOICES,
                                       default=CUSTOMER_STATUS_CHOICES[1][0])
    #applicant = models.ForeignKey(Organisation, blank=True, null=True, related_name='proposals')
    org_applicant = models.ForeignKey(
        Organisation,
        blank=True,
        null=True,
        related_name='org_applications')
    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    #lodgement_date = models.DateField(blank=True, null=True)
    lodgement_date = models.DateTimeField(blank=True, null=True)

    proxy_applicant = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proxy')
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proposals')

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proposals_assigned', on_delete=models.SET_NULL)
    assigned_approver = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proposals_approvals', on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_approved_by')
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[1][0])
    prev_processing_status = models.CharField(max_length=30, blank=True, null=True)
    id_check_status = models.CharField('Identification Check Status', max_length=30, choices=ID_CHECK_STATUS_CHOICES,
                                       default=ID_CHECK_STATUS_CHOICES[0][0])
    compliance_check_status = models.CharField('Return Check Status', max_length=30, choices=COMPLIANCE_CHECK_STATUS_CHOICES,
                                            default=COMPLIANCE_CHECK_STATUS_CHOICES[0][0])
    character_check_status = models.CharField('Character Check Status', max_length=30,
                                              choices=CHARACTER_CHECK_STATUS_CHOICES,
                                              default=CHARACTER_CHECK_STATUS_CHOICES[0][0])
    review_status = models.CharField('Review Status', max_length=30, choices=REVIEW_STATUS_CHOICES,
                                     default=REVIEW_STATUS_CHOICES[0][0])

    approval = models.ForeignKey('commercialoperator.Approval',null=True,blank=True)

    #previous_application = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    previous_application = models.ForeignKey('self', blank=True, null=True)
    proposed_decline_status = models.BooleanField(default=False)
    #qaofficer_referral = models.BooleanField(default=False)
    #qaofficer_referral = models.OneToOneField('QAOfficerReferral', blank=True, null=True)
    # Special Fields
    title = models.CharField(max_length=255,null=True,blank=True)
    activity = models.CharField(max_length=255,null=True,blank=True)
    #region = models.CharField(max_length=255,null=True,blank=True)
    tenure = models.CharField(max_length=255,null=True,blank=True)
    #activity = models.ForeignKey(Activity, null=True, blank=True)
    region = models.ForeignKey(Region, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    #tenure = models.ForeignKey(Tenure, null=True, blank=True)
    application_type = models.ForeignKey(ApplicationType)
    approval_level = models.CharField('Activity matrix approval level', max_length=255,null=True,blank=True)
    approval_level_document = models.ForeignKey(ProposalDocument, blank=True, null=True, related_name='approval_level_document')
    approval_comment = models.TextField(blank=True)
    #If the proposal is created as part of migration of approvals
    migrated=models.BooleanField(default=False)


    # common
    #applicant_details = models.OneToOneField(ProposalApplicantDetails, blank=True, null=True) #, related_name='applicant_details')
    training_completed = models.BooleanField(default=False)
    #payment = models.OneToOneField(ProposalPayment, blank=True, null=True)
    #confirmation = models.OneToOneField(ProposalConfirmation, blank=True, null=True)

    # T Class
    activities_land = models.OneToOneField(ProposalActivitiesLand, blank=True, null=True) #, related_name='activities_land')
    activities_marine = models.OneToOneField(ProposalActivitiesMarine, blank=True, null=True) #, related_name='activities_marine')
    #other_details = models.OneToOneField(ProposalOtherDetails, blank=True, null=True, related_name='proposal')
    #online_training = models.OneToOneField(ProposalOnlineTraining, blank=True, null=True)

    # Filming
    #Following field is only used to approval type for Filming application otherwise ignore
    filming_approval_type = models.CharField('Filming Approval Type', max_length=30, choices=FILMING_APPROVAL_TYPE_CHOICES,
                                     default=FILMING_APPROVAL_TYPE_CHOICES[1][0])
    #Following field is only used to licence type for Filming application otherwise ignore
    filming_licence_charge_type = models.CharField('Filming Licence charge Type', max_length=30, choices=FILMING_LICENCE_CHARGE_CHOICES,
                                     default=FILMING_LICENCE_CHARGE_CHOICES[1][0])
    filming_non_standard_charge = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')

    # Event

    fee_invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')
    property_cache = JSONField(null=True, blank=True, default={})

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return str(self.id)

    #Append 'P' to Proposal id to generate Lodgement number. Lodgement number and lodgement sequence are used to generate Reference.
    def save(self, *args, **kwargs):
        self.update_property_cache(False)
        orig_processing_status = self._original_state['processing_status']
        super(Proposal, self).save(*args,**kwargs)
        if self.processing_status != orig_processing_status:
            self.save(version_comment='processing_status: {}'.format(self.processing_status))

        if self.lodgement_number == '' and self.application_type.name != 'E Class':
            new_lodgment_id = 'A{0:06d}'.format(self.pk)
            self.lodgement_number = new_lodgment_id
            self.save(version_comment='processing_status: {}'.format(self.processing_status))

    def get_property_cache(self):
        '''
        Get properties which were previously resolved.
        '''
        if len(self.property_cache) == 0:
            self.update_property_cache()

        if self.processing_status == self.PROCESSING_STATUS_AWAITING_PAYMENT:
            self.update_property_cache()

        return self.property_cache

    def get_property_cache_key(self, key):
        '''
        Get properties which were previously resolved with key.
        '''
        try:

            self.property_cache[key]

        except KeyError:
            self.update_property_cache()

        return self.property_cache[key]

    def update_property_cache(self, save=True):
        '''
        Refresh cached properties with updated properties.
        '''
        logger.debug('Proposal.update_property_cache()')

        self.property_cache['fee_paid'] = self._fee_paid
        self.set_property_cache_fee_amount(self._fee_amount)

        if save is True:
            self.save()

        return self.property_cache

    @property
    def invoice(self):
        """ specific to application fee invoices """
        return Invoice.objects.get(reference=self.fee_invoice_reference) if self.fee_invoice_reference else None

    @property
    def fee_paid(self):
        """ get cached value, if it exists """
        if 'fee_paid' not in self.property_cache:
            self.update_property_cache()

        return self.get_property_cache_key('fee_paid')

    @property
    def _fee_paid(self):
        if (self.invoice and self.invoice.payment_status in ['paid','over_paid']) or self.proposal_type=='amendment':
            return True
        return False

    @property
    def fee_amount(self):
        """ get cached value, if it exists """
        if 'fee_amount' not in self.property_cache:
            self.update_property_cache()

        return self.get_property_cache_key('fee_amount')

    @property
    def _fee_amount(self):
        return self.invoice.amount if self.invoice and self._fee_paid else None

    def set_property_cache_fee_amount(self, amount):
        '''
        Setter for fee_amount on the property cache.
        '''
        import json
        from decimal import Decimal as D

        class DecimalEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, D):
                    return float(obj)
                return json.JSONEncoder.default(self, obj)

        if self.id:
            data = DecimalEncoder().encode(amount)
            self.property_cache['fee_amount'] = data


    @property
    def filming_fee_invoice_reference(self):
        try: 
            filming_fee = self.filming_fees.order_by('-id').first()
            return filming_fee.filming_fee_invoices.order_by('-id').first().invoice_reference
        except:
            return None

    @property
    def can_create_final_approval(self):
        return self.fee_paid and self.processing_status==Proposal.PROCESSING_STATUS_AWAITING_PAYMENT

    @property
    def licence_fee_amount(self):
        if self.application_type.name==ApplicationType.TCLASS:
            period = self.other_details.preferred_licence_period
            if period.split('_')[1].endswith('months'):
                return self.application_type.licence_fee_2mth
            else:
                return int(period.split('_')[0]) * self.application_type.licence_fee_1yr
        if self.application_type.name==ApplicationType.EVENT:
            return self.application_type.licence_fee_1yr

    @property
    def event_name(self):
        try:
            if self.application_type.name == ApplicationType.EVENT:
                if self.event_activity.event_name:
                    return self.event_activity.event_name
            return ''
        except:
            return ''

    def reset_licence_discount(self, user):
        """ reset when licence is issued"""
        org = self.org_applicant
        if self.application_type.name==ApplicationType.TCLASS and org and org.licence_discount > 0:
            if org.licence_discount > 0:
                try:
                    lic_disc = self.fee_discounts.get(discount_type=ApplicationFeeDiscount.DISCOUNT_TYPE_LICENCE)
                    lic_disc.reset_date = timezone.now()
                    lic_disc.save()
                except ObjectDoesNotExist as e:
                    lic_disc = ApplicationFeeDiscount.objects.create(
                        proposal=self, discount_type=ApplicationFeeDiscount.DISCOUNT_TYPE_LICENCE, discount=org.licence_discount, user=user, reset_date=timezone.now()
                    )
            org.apply_licence_discount = False
            org.licence_discount = 0.0
            org.save()

    def reset_application_discount(self, user):
        """ reset when application is submitted"""
        org = self.org_applicant
        if self.application_type.name==ApplicationType.TCLASS and org:
            if org.application_discount > 0 or org.licence_discount > 0:
                app_disc = ApplicationFeeDiscount.objects.create(proposal=self, discount_type=ApplicationFeeDiscount.DISCOUNT_TYPE_APPLICATION, discount=org.application_discount, reset_date=timezone.now(), user=user)
                lic_disc = ApplicationFeeDiscount.objects.create(proposal=self, discount_type=ApplicationFeeDiscount.DISCOUNT_TYPE_LICENCE, discount=org.licence_discount, user=user)

            org.apply_application_discount = False
            org.application_discount = 0.0
            org.save()

    @property
    def allow_full_discount(self):
        """ checks if a fee is payable after discount is applied """
        org = self.org_applicant
        if self.application_type.name==ApplicationType.TCLASS and self.other_details.preferred_licence_period and org:
            application_fee = max( round(float(self.application_type.application_fee) - org.application_discount, 2), 0)
            licence_fee = max( round(float(self.licence_fee_amount) - org.licence_discount, 2), 0)
            if licence_fee == 0 and application_fee == 0:
                return True
        return False

    @property
    def reference(self):
        return '{}-{}'.format(self.lodgement_number, self.lodgement_sequence)

    @property
    def reversion_ids(self):
        current_revision_id = Version.objects.get_for_object(self).first().revision_id
        versions = Version.objects.get_for_object(self).select_related("revision__user").filter(Q(revision__comment__icontains='status') | Q(revision_id=current_revision_id))
        version_ids = [[i.id,i.revision.date_created] for i in versions]
        return [dict(cur_version_id=version_ids[0][0], prev_version_id=version_ids[i+1][0], created=version_ids[i][1]) for i in range(len(version_ids)-1)]

    @property
    def applicant(self):
        if self.org_applicant:
            return self.org_applicant.organisation.name
        elif self.proxy_applicant:
            return "{} {}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name)
        else:
            return "{} {}".format(
                self.submitter.first_name,
                self.submitter.last_name)

    @property
    def applicant_email(self):
        if self.org_applicant and hasattr(self.org_applicant.organisation, 'email') and self.org_applicant.organisation.email:
            return self.org_applicant.organisation.email
        elif self.proxy_applicant:
            return self.proxy_applicant.email
        else:
            return self.submitter.email

    @property
    def applicant_details(self):
        if self.org_applicant:
            return '{} \n{}'.format(
                self.org_applicant.organisation.name,
                self.org_applicant.address)
        elif self.proxy_applicant:
            return "{} {}\n{}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name,
                self.proxy_applicant.addresses.all().first())
        else:
            return "{} {}\n{}".format(
                self.submitter.first_name,
                self.submitter.last_name,
                self.submitter.addresses.all().first())

    @property
    def applicant_address(self):
        if self.org_applicant:
            return self.org_applicant.address
        elif self.proxy_applicant:
            #return self.proxy_applicant.addresses.all().first()
            return self.proxy_applicant.residential_address
        else:
            #return self.submitter.addresses.all().first()
            return self.submitter.residential_address

    @property
    def applicant_id(self):
        if self.org_applicant:
            return self.org_applicant.id
        elif self.proxy_applicant:
            return self.proxy_applicant.id
        else:
            return self.submitter.id

    @property
    def applicant_type(self):
        if self.org_applicant:
            return self.APPLICANT_TYPE_ORGANISATION
        elif self.proxy_applicant:
            return self.APPLICANT_TYPE_PROXY
        else:
            return self.APPLICANT_TYPE_SUBMITTER

    @property
    def applicant_field(self):
        if self.org_applicant:
            return 'org_applicant'
        elif self.proxy_applicant:
            return 'proxy_applicant'
        else:
            return 'submitter'

    def reset_training_completed(self, request):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        if self.application_type.name == ApplicationType.EVENT:
            if self.org_applicant: 
                if self.org_applicant.event_training_completed:
                    future_date =self.org_applicant.event_training_date+timedelta(days=365)
                    #if future_date < today:
                    if True:
                        org_applicant = self.org_applicant
                        org_applicant.event_training_completed = False
                        org_applicant.event_training_date = None
                        org_applicant.save()

                        self.training_completed = False
                        self.save()

                        self.log_user_action(ProposalUserAction.ACTION_RESET_TRAINING_COMPLETED.format(self.id),request)

            elif self.proxy_applicant:
                if self.proxy_applicant.system_settings.event_training_completed:
                    future_date =self.proxy_applicant.system_settings.event_training_date+timedelta(days=365)
                    if future_date < today:
                        system_settings = self.proxy_applicant.system_settings
                        system_settings.event_training_completed = False
                        system_settings.event_training_date = None
                        system_settings.save()

                        self.training_completed = False
                        self.save()

                        self.log_user_action(ProposalUserAction.ACTION_RESET_TRAINING_COMPLETED.format(self.id),request)

            else:
                if self.submitter.system_settings.event_training_completed:
                    future_date =self.submitter.system_settings.event_training_date+timedelta(days=365)
                    if future_date < today:
                        system_settings = self.submitter.system_settings
                        system_settings.event_training_completed = False
                        system_settings.event_training_date = None
                        system_settings.save()

                        self.training_completed = False
                        self.save()

                        self.log_user_action(ProposalUserAction.ACTION_RESET_TRAINING_COMPLETED.format(self.id),request)

    @property
    def applicant_training_completed(self):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        if self.org_applicant: 
            if self.org_applicant.event_training_completed:
                future_date =self.org_applicant.event_training_date+timedelta(days=365)
                if future_date < today:
                    return False
                else:
                    return self.org_applicant.event_training_completed
        elif self.proxy_applicant:
            if self.proxy_applicant.system_settings.event_training_completed:
                future_date =self.proxy_applicant.system_settings.event_training_date+timedelta(days=365)
                if future_date < today:
                    return False
                else:
                    return self.proxy_applicant.system_settings.event_training_completed
        else:
            if self.submitter.system_settings.event_training_completed:
                future_date =self.submitter.system_settings.event_training_date+timedelta(days=365)
                if future_date < today:
                    return False
                else:
                    return self.submitter.system_settings.event_training_completed
        return False

    def qa_officers(self, name=None):
        if not name:
            return QAOfficerGroup.objects.get(default=True).members.all().values_list('email', flat=True)
        else:
            return QAOfficerGroup.objects.get(name=name).members.all().values_list('email', flat=True)

    @property
    def get_history(self):
        """ Return the prev proposal versions """
        l = []
        p = copy.deepcopy(self)
        while (p.previous_application):
            l.append( dict(id=p.previous_application.id, modified=p.previous_application.modified_date) )
            p = p.previous_application
        return l

#    def _get_history(self):
#        """ Return the prev proposal versions """
#        l = []
#        p = copy.deepcopy(self)
#        while (p.previous_application):
#            l.append( [p.id, p.previous_application.id] )
#            p = p.previous_application
#        return l

    @property
    def proposal_submitter_email(self):
        fallback_recipient = self.org_applicant.all_admin_emails if len(self.org_applicant.all_admin_emails)>0 else self.submitter.email
        if self.org_applicant:
            try:
                contact=self.org_applicant.contacts.filter(email=self.submitter)
                if contact:
                    contact=contact[0]
                    if contact.user_status=='active':
                        return self.submitter.email
                    else:
                        return fallback_recipient
                return fallback_recipient
            except:
                return fallback_recipient
        else:
            return self.submitter.email

    @property
    def is_assigned(self):
        return self.assigned_officer is not None

    @property
    def is_temporary(self):
        return self.customer_status == 'temp' and self.processing_status == 'temp'

    @property
    def can_user_edit(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.customer_status in self.CUSTOMER_EDITABLE_STATE

    @property
    def can_user_view(self):
        """
        :return: True if the application is in one of the approved status.
        """
        return self.customer_status in self.CUSTOMER_VIEWABLE_STATE



    @property
    def is_discardable(self):
        """
        An application can be discarded by a customer if:
        1 - It is a draft
        2- or if the application has been pushed back to the user
        """
        return self.customer_status == 'draft' or self.processing_status == 'awaiting_applicant_response'

    @property
    def is_deletable(self):
        """
        An application can be deleted only if it is a draft and it hasn't been lodged yet
        :return:
        """
        return self.customer_status == 'draft' and not self.lodgement_number

    @property
    def latest_referrals(self):
        return self.referrals.all()[:2]

    @property
    def land_parks(self):
        return self.parks.filter(park__park_type='land')

    @property
    def land_parks_exclude_free(self):
        """ exlude parks with free admission """
        return self.parks.filter(park__park_type='land').exclude(park__adult_price=D(0.0), park__child_price=D(0.0))

    @property
    def marine_parks(self):
        return self.parks.filter(park__park_type='marine')

    @property
    def regions_list(self):
        #return self.region.split(',') if self.region else []
        return [self.region.name] if self.region else []

    @property
    def assessor_assessment(self):
        qs=self.assessment.filter(referral_assessment=False, referral_group=None)
        if qs:
            return qs[0]
        else:
            return None

    @property
    def referral_assessments(self):
        qs=self.assessment.filter(referral_assessment=True, referral_group__isnull=False)
        if qs:
            return qs
        else:
            return None


    @property
    def permit(self):
        return self.approval.licence_document._file.url if self.approval else None

    @property
    def allowed_assessors(self):
        if self.processing_status == 'with_approver':
            group = self.__approver_group()
        elif self.processing_status =='with_qa_officer':
            group = QAOfficerGroup.objects.get(default=True)
        else:
            group = self.__assessor_group()
        return group.members.all() if group else []

    @property
    def compliance_assessors(self):
        group = self.__assessor_group()
        return group.members.all() if group else []

    @property
    def can_officer_process(self):
        """ :return: True if the application is in one of the processable status for Assessor role."""
        officer_view_state = ['draft','approved','declined','temp','discarded', 'with_referral', 'with_qa_officer', 'waiting_payment', 'partially_approved', 'partially_declined', 'with_district_assessor']
        return False if self.processing_status in officer_view_state else True

    @property
    def can_view_district_table(self):
        officer_view_state = ['with_district_assessor','approved','declined','partially_approved','partially_declined', ]
        if self.filming_approval_type=='lawful_authority' and self.processing_status in officer_view_state:
            return True
        else:
            return False

    @property
    def amendment_requests(self):
        qs =AmendmentRequest.objects.filter(proposal = self)
        return qs

    #Check if there is an pending amendment request exist for the proposal
    @property
    def pending_amendment_request(self):
        qs =AmendmentRequest.objects.filter(proposal = self, status = "requested")
        if qs:
            return True
        return False

    @property
    def is_amendment_proposal(self):
        if self.proposal_type=='amendment':
            return True
        return False

    @property
    def is_lawful_authority(self):
        if self.application_type.name==ApplicationType.FILMING and self.filming_approval_type=='lawful_authority':
            return True
        return False

    @property
    def is_filming_application(self):
        if self.application_type.name==ApplicationType.FILMING:
            return True
        return False

    @property
    def is_event_application(self):
        if self.application_type.name==ApplicationType.EVENT:
            return True
        return False

    @property
    def is_filming_licence(self):
        if self.application_type.name==ApplicationType.FILMING and self.filming_approval_type=='licence':
            return True
        return False

    @property
    def is_lawful_authority_finalised(self):
        if self.application_type.name==ApplicationType.FILMING and self.filming_approval_type=='lawful_authority':
            final_status=['declined', 'approved', 'discarded']
            if self.district_proposals.all().count()==self.district_proposals.filter(processing_status__in=final_status).count():
                return True
        return False

    def search_data_orig(self):
        search_data={}
        parks=[]
        trails=[]
        activities=[]
        vehicles=[]
        vessels=[]
        accreditations=[]
        for p in self.parks.all():
            parks.append(p.park.name)
            if p.park.park_type=='land':
                for a in p.activities.all():
                    activities.append(a.activity_name)
            if p.park.park_type=='marine':
                for z in p.zones.all():
                    for a in z.park_activities.all():
                        activities.append(a.activity_name)
        for t in self.trails.all():
            trails.append(t.trail.name)
            for s in t.sections.all():
                for ts in s.trail_activities.all():
                  activities.append(ts.activity_name)
        for v in self.vehicles.all():
            vehicles.append(v.rego)
        for vs in self.vessels.all():
            vessels.append(vs.spv_no)
        search_data.update({'parks': parks})
        search_data.update({'trails': trails})
        search_data.update({'vehicles': vehicles})
        search_data.update({'vessels': vessels})
        search_data.update({'activities': activities})

        try:
            other_details=ProposalOtherDetails.objects.get(proposal=self)
            search_data.update({'other_details': other_details.other_comments})
            search_data.update({'mooring': other_details.mooring})
            for acr in other_details.accreditations.all():
                accreditations.append(acr.get_accreditation_type_display())
            search_data.update({'accreditations': accreditations})
        except ProposalOtherDetails.DoesNotExist:
            search_data.update({'other_details': []})
            search_data.update({'mooring': []})
            search_data.update({'accreditations':[]})
        return search_data


    #@property
    def search_data_tclass(self):
        search_data={}
        parks=[]
        trails=[]
        activities=[]
        vehicles=[]
        vessels=[]
        accreditations=[]

        land_parks_name=list(self.parks.filter(park__park_type='land').values_list('park__name', flat=True))
        land_activities_name=list(self.parks.filter(park__park_type='land', activities__isnull=False).values_list('activities__activity__name', flat=True))
        marine_parks_name=list(self.parks.filter(park__park_type='marine').values_list('park__name', flat=True))
        marine_activities_name=list(self.parks.filter(park__park_type='marine',zones__isnull=False, zones__park_activities__isnull=False).values_list('zones__park_activities__activity__name', flat=True))
        trails_name=list(self.trails.all().values_list('trail__name', flat=True))
        trail_activities_name=list(self.trails.filter(sections__isnull=False, sections__trail_activities__isnull=False).values_list('sections__trail_activities__activity__name', flat=True))
        vehicles=list(self.vehicles.all().values_list('rego', flat=True))
        vessels=list(self.vessels.all().values_list('spv_no', flat=True))

        parks=land_parks_name + marine_parks_name
        activities = land_activities_name + marine_activities_name + trail_activities_name


        search_data.update({'parks': parks})
        search_data.update({'trails': trails_name})
        search_data.update({'vehicles': vehicles})
        search_data.update({'vessels': vessels})
        search_data.update({'activities': activities})

        try:
            other_details=ProposalOtherDetails.objects.get(proposal=self)
            search_data.update({'other_details': other_details.other_comments})
            search_data.update({'mooring': other_details.mooring})
            for acr in other_details.accreditations.all():
                 accreditations.append(acr.get_accreditation_type_display())
            # accreditations=[acr.get_accreditation_type_display() for acr in other_details.accreditations.all()]
            search_data.update({'accreditations': accreditations})
        except ProposalOtherDetails.DoesNotExist:
            search_data.update({'other_details': []})
            search_data.update({'mooring': []})
            search_data.update({'accreditations':[]})
        return search_data


    def search_data_event(self):
        search_data={}
        parks=[]
        trails=[]
        activities=[]
        vehicles=[]
        vessels=[]

        parks=list(self.events_parks.all().values_list('park__name', flat=True))
        park_activities_name=list(self.events_parks.filter(event_activities__isnull=False).values_list('event_activities', flat=True))
        trails_name=list(self.trails.all().values_list('trail__name', flat=True))
        trail_activities_name=list(self.trails.filter(sections__isnull=False, sections__trail_activities__isnull=False).values_list('sections__trail_activities__activity__name', flat=True))
        vehicles=list(self.vehicles.all().values_list('rego', flat=True))
        vessels=list(self.vessels.all().values_list('spv_no', flat=True))

        activities = park_activities_name + trail_activities_name


        search_data.update({'parks': parks})
        search_data.update({'trails': trails_name})
        search_data.update({'vehicles': vehicles})
        search_data.update({'vessels': vessels})
        search_data.update({'activities': activities})

        return search_data


    def search_data_filming(self):
        search_data={}
        parks=[]
        vehicles=[]
        vessels=[]
        title=[]
        film_types=[]
        film_purposes=[]

        if self.title:
            title=[self.title]
        film_types=[self.filming_activity.get_film_type_display()]
        film_purposes=[self.filming_activity.get_film_purpose_display()]
        parks=list(self.filming_parks.all().values_list('park__name', flat=True))
        vehicles=list(self.vehicles.all().values_list('rego', flat=True))
        vessels=list(self.vessels.all().values_list('spv_no', flat=True))

        search_data.update({'title': title})
        search_data.update({'film_types': film_types})
        search_data.update({'film_purposes': film_purposes})
        search_data.update({'parks': parks})
        search_data.update({'vehicles': vehicles})
        search_data.update({'vessels': vessels})

        return search_data



    @property
    def search_data(self):
        if self.application_type.name== ApplicationType.TCLASS:
            return self.search_data_tclass()
        if self.application_type.name== ApplicationType.EVENT:
            return self.search_data_event()
        if self.application_type.name== ApplicationType.FILMING:
            return self.search_data_filming()
        return {}


    @property
    def selected_parks_activities(self):
        #list of selected parks and activities (to print on licence pdf)
        selected_parks_activities=[]
        for p in self.parks.all():
            park_activities=[]
            #parks.append(p.park.name)
            if p.park.park_type=='land':
                for a in p.activities.all():
                    park_activities.append(a.activity_name)
                selected_parks_activities.append({'park': p.park.name, 'activities': park_activities})
            if p.park.park_type=='marine':
                zone_activities=[]
                for z in p.zones.all():
                    for a in z.park_activities.all():
                        zone_activities.append(a.activity_name)
                    selected_parks_activities.append({'park': '{} - {}'.format(p.park.name, z.zone.name), 'activities': park_activities})
        for t in self.trails.all():
            #trails.append(t.trail.name)
            #trail_activities=[]
            for s in t.sections.all():
                trail_activities=[]
                for ts in s.trail_activities.all():
                  trail_activities.append(ts.activity_name)
                selected_parks_activities.append({'park': '{} - {}'.format(t.trail.name, s.section.name), 'activities': trail_activities})
        return selected_parks_activities

    @property
    def selected_parks_activities_pdf(self):
        """ duplicated selected_parks_activities to quickly fix the pdf licence generation of marine zonal activities
            which was not previously displayed correctly. This function is called by pdf.py only. """
        #list of selected parks and activities (to print on licence pdf)
        selected_parks_activities=[]
        if self.application_type.name==ApplicationType.TCLASS:
            for p in self.parks.all():
                park_activities=[]
                park_access_types=[]
                #parks.append(p.park.name)
                if p.park.park_type=='land':
                    for a in p.access_types.all():
                        park_access_types.append(a.access_type.name)
                    for a in p.activities.all():
                        park_activities.append(a.activity_name)
                    selected_parks_activities.append({'park': p.park.name, 'activities': park_activities, 'access_types': park_access_types })
                if p.park.park_type=='marine':
                    for z in p.zones.all():
                        zone_activities = []
                        for a in z.park_activities.all():
                            zone_activities.append(a.activity_name)
                        selected_parks_activities.append({'park': '{} - {}'.format(p.park.name, z.zone.name), 'activities': zone_activities})
            for t in self.trails.all():
                #trails.append(t.trail.name)
                #trail_activities=[]
                for s in t.sections.all():
                    trail_activities=[]
                    for ts in s.trail_activities.all():
                      trail_activities.append(ts.activity_name)
                    selected_parks_activities.append({'park': '{} - {}'.format(t.trail.name, s.section.name), 'activities': trail_activities})
        if self.application_type.name==ApplicationType.EVENT:
            # for p in self.events_parks.all():
            #     selected_parks_activities.append({'park': p.park.name, 'activities': p.event_activities})
            for t in self.trails.all():
                for s in t.sections.all():
                    trail_activities=[]
                    for ts in s.trail_activities.all():
                      trail_activities.append(ts.activity_name)
                    selected_parks_activities.append({'park': '{} - {}'.format(t.trail.name, s.section.name), 'activities': trail_activities})

        return selected_parks_activities

#    @property
#    def selected_parks_access_types_pdf(self):
#        #list of selected parks and access_types (to print on licence pdf)
#        selected_park_access_types=[]
#        for p in self.parks.all():
#            park_access_types=[]
#            if p.park.park_type=='land':
#                for a in p.access_types.all():
#                    park_access_types.append(a.access_type.name)
#                selected_park_access_types.append({'park': p.park.name, 'access_types': park_access_types})
#        return selected_park_access_types

    def __assessor_group(self):
        # TODO get list of assessor groups based on region and activity
        if self.region and self.activity:
            try:
                check_group = ProposalAssessorGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    region__name__in=self.regions_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except ProposalAssessorGroup.DoesNotExist:
                pass
        default_group = ProposalAssessorGroup.objects.get(default=True)

        return default_group


    def __approver_group(self):
        # TODO get list of approver groups based on region and activity
        if self.region and self.activity:
            try:
                check_group = ProposalApproverGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    region__name__in=self.regions_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except ProposalApproverGroup.DoesNotExist:
                pass
        default_group = ProposalApproverGroup.objects.get(default=True)

        return default_group

    def __check_proposal_filled_out(self):
        if not self.data:
            raise exceptions.ProposalNotComplete()
        missing_fields = []
        required_fields = {
        #    'region':'Region/District',
        #    'title': 'Title',
        #    'activity': 'Activity'
        }
        for k,v in required_fields.items():
            val = getattr(self,k)
            if not val:
                missing_fields.append(v)
        return missing_fields

    @property
    def assessor_recipients(self):
        recipients = []
        try:
            recipients = ProposalAssessorGroup.objects.get(region=self.region).members_email
        except:
            recipients = ProposalAssessorGroup.objects.get(default=True).members_email

        #if self.submitter.email not in recipients:
        #    recipients.append(self.submitter.email)
        return recipients

    @property
    def approver_recipients(self):
        recipients = []
        try:
            recipients = ProposalApproverGroup.objects.get(region=self.region).members_email
        except:
            recipients = ProposalApproverGroup.objects.get(default=True).members_email

        #if self.submitter.email not in recipients:
        #    recipients.append(self.submitter.email)
        return recipients

    #Check if the user is member of assessor group for the Proposal
    def is_assessor(self,user):
            return self.__assessor_group() in user.proposalassessorgroup_set.all()

    #Check if the user is member of assessor group for the Proposal
    def is_approver(self,user):
            return self.__approver_group() in user.proposalapprovergroup_set.all()


    def can_assess(self,user):
        #if self.processing_status == 'on_hold' or self.processing_status == 'with_assessor' or self.processing_status == 'with_referral' or self.processing_status == 'with_assessor_requirements':
        if self.processing_status in ['on_hold', 'with_qa_officer', 'with_assessor', 'with_referral', 'with_assessor_requirements']:
            return self.__assessor_group() in user.proposalassessorgroup_set.all()
        elif self.processing_status == 'with_approver':
            return self.__approver_group() in user.proposalapprovergroup_set.all()
        else:
            return False

    #To allow/ prevent internal user to edit activities (Land and Marine) for T-class licence
    #still need to check to assessor mode in on or not
    def can_edit_activities(self,user):
        if self.processing_status == 'with_assessor' or self.processing_status == 'with_assessor_requirements':
            return self.__assessor_group() in user.proposalassessorgroup_set.all()
        elif self.processing_status == 'with_approver':
            return self.__approver_group() in user.proposalapprovergroup_set.all()
        else:
            return False

    def can_edit_period(self,user):
        if self.processing_status == 'with_assessor' or self.processing_status == 'with_assessor_requirements':
            return self.__assessor_group() in user.proposalassessorgroup_set.all()
        else:
            return False

    def assessor_comments_view(self,user):

        if self.processing_status == 'with_assessor' or self.processing_status == 'with_referral' or self.processing_status == 'with_assessor_requirements' or self.processing_status == 'with_approver':
            try:
                referral = Referral.objects.get(proposal=self,referral=user)
            except:
                referral = None
            if referral:
                return True
            elif self.__assessor_group() in user.proposalassessorgroup_set.all():
                return True
            elif self.__approver_group() in user.proposalapprovergroup_set.all():
                return True
            else:
                return False
        else:
            return False

    def has_assessor_mode(self,user):
        status_without_assessor = ['with_approver','approved','waiting_payment','declined','draft']
        if self.processing_status in status_without_assessor:
            return False
        else:
            if self.assigned_officer:
                if self.assigned_officer == user:
                    return self.__assessor_group() in user.proposalassessorgroup_set.all()
                else:
                    return False
            else:
                return self.__assessor_group() in user.proposalassessorgroup_set.all()

    def log_user_action(self, action, request):
        return ProposalUserAction.log_action(self, action, request.user)

    def submit(self,request,viewset):
        from commercialoperator.components.proposals.utils import save_proponent_data
        with transaction.atomic():
            if self.can_user_edit:
                # Save the data first
                save_proponent_data(self,request,viewset)
                # Check if the special fields have been completed
                missing_fields = self.__check_proposal_filled_out()
                if missing_fields:
                    error_text = 'The proposal has these missing fields, {}'.format(','.join(missing_fields))
                    raise exceptions.ProposalMissingFields(detail=error_text)
                self.submitter = request.user
                #self.lodgement_date = datetime.datetime.strptime(timezone.now().strftime('%Y-%m-%d'),'%Y-%m-%d').date()
                self.lodgement_date = timezone.now()
                if (self.amendment_requests):
                    qs = self.amendment_requests.filter(status = "requested")
                    if (qs):
                        for q in qs:
                            q.status = 'amended'
                            q.save()

                # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)
                # Create a log entry for the organisation
                #self.applicant.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)

                ret1 = send_submit_email_notification(request, self)
                ret2 = send_external_submit_email_notification(request, self)

                #self.save_form_tabs(request)
                if ret1 and ret2:
                    self.processing_status = 'with_assessor'
                    self.customer_status = 'with_assessor'
                    self.documents.all().update(can_delete=False)
                    self.save()
                else:
                    raise ValidationError('An error occurred while submitting proposal (Submit email notifications failed)')
                #Create assessor checklist with the current assessor_list type questions
                #Assessment instance already exits then skip.
                try:
                    assessor_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=None, referral_assessment=False)
                except ProposalAssessment.DoesNotExist:
                    assessor_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=None, referral_assessment=False)
                    checklist=ChecklistQuestion.objects.filter(list_type='assessor_list', application_type=self.application_type, obsolete=False)
                    for chk in checklist:
                        try:
                            chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=assessor_assessment)
                        except ProposalAssessmentAnswer.DoesNotExist:
                            chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=assessor_assessment)

            else:
                raise ValidationError('You can\'t edit this proposal at this moment')

    #TODO: remove this function as it is not used anywhere.
    def save_form_tabs(self,request):
        #self.applicant_details = ProposalApplicantDetails.objects.create(first_name=request.data['first_name'])
        self.activities_land = ProposalActivitiesLand.objects.create(activities_land=request.data['activities_land'])
        self.activities_marine = ProposalActivitiesMarine.objects.create(activities_marine=request.data['activities_marine'])
        #self.save()

    def save_parks(self,request,parks):
        with transaction.atomic():
            if parks:
                try:
                    current_parks=self.parks.all()
                    if current_parks:
                        #print current_parks
                        for p in current_parks:
                            p.delete()
                    for item in parks:
                        try:
                            park=Park.objects.get(id=item)
                            ProposalPark.objects.create(proposal=self, park=park)
                        except:
                            raise
                except:
                    raise



    def update(self,request,viewset):
        from commercialoperator.components.proposals.utils import save_proponent_data
        with transaction.atomic():
            if self.can_user_edit:
                # Save the data first
                save_proponent_data(self,request,viewset)
                self.save()
            else:
                raise ValidationError('You can\'t edit this proposal at this moment')


    def send_referral(self,request,referral_email,referral_text):
        with transaction.atomic():
            try:
                if self.processing_status == 'with_assessor' or self.processing_status == 'with_referral':
                    self.processing_status = 'with_referral'
                    self.save()
                    referral = None

                    # Check if the user is in ledger
                    try:
                        #user = EmailUser.objects.get(email__icontains=referral_email)
                        #referral_group = ReferralRecipientGroup.objects.get(name__icontains=referral_email)
                        referral_group = ReferralRecipientGroup.objects.get(name__iexact=referral_email)
                    #except EmailUser.DoesNotExist:
                    except ReferralRecipientGroup.DoesNotExist:
                        raise exceptions.ProposalReferralCannotBeSent()
#                        # Validate if it is a deparment user
#                        department_user = get_department_user(referral_email)
#                        if not department_user:
#                            raise ValidationError('The user you want to send the referral to is not a member of the department')
#                        # Check if the user is in ledger or create
#                        email = department_user['email'].lower()
#                        user,created = EmailUser.objects.get_or_create(email=department_user['email'].lower())
#                        if created:
#                            user.first_name = department_user['given_name']
#                            user.last_name = department_user['surname']
#                            user.save()
                    try:
                        #Referral.objects.get(referral=user,proposal=self)
                        Referral.objects.get(referral_group=referral_group,proposal=self)
                        raise ValidationError('A referral has already been sent to this group')
                    except Referral.DoesNotExist:
                        # Create Referral
                        referral = Referral.objects.create(
                            proposal = self,
                            #referral=user,
                            referral_group=referral_group,
                            sent_by=request.user,
                            text=referral_text
                        )
                        #Create assessor checklist with the current assessor_list type questions
                        #Assessment instance already exits then skip.
                        try:
                            referral_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        except ProposalAssessment.DoesNotExist:
                            referral_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                            checklist=ChecklistQuestion.objects.filter(list_type='referral_list', application_type=self.application_type, obsolete=False)
                            for chk in checklist:
                                try:
                                    chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=referral_assessment)
                                except ProposalAssessmentAnswer.DoesNotExist:
                                    chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=referral_assessment)
                    # Create a log entry for the proposal
                    #self.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    self.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}'.format(referral_group.name)),request)
                    # Create a log entry for the organisation
                    #self.applicant.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    applicant_field=getattr(self, self.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}'.format(referral_group.name)),request)
                    # send email
                    recipients = referral_group.members_list
                    send_referral_email_notification(referral,recipients,request)
                else:
                    raise exceptions.ProposalReferralCannotBeSent()
            except:
                raise

    def assign_officer(self,request,officer):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not self.can_assess(officer):
                    raise ValidationError('The selected person is not authorised to be assigned to this proposal')
                if self.processing_status == 'with_approver':
                    if officer != self.assigned_approver:
                        self.assigned_approver = officer
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                else:
                    if officer != self.assigned_officer:
                        self.assigned_officer = officer
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
            except:
                raise

    def assing_approval_level_document(self, request):
        with transaction.atomic():
            try:
                approval_level_document = request.data['approval_level_document']
                if approval_level_document != 'null':
                    try:
                        document = self.documents.get(input_name=str(approval_level_document))
                    except ProposalDocument.DoesNotExist:
                        document = self.documents.get_or_create(input_name=str(approval_level_document), name=str(approval_level_document))[0]
                    document.name = str(approval_level_document)
                    # commenting out below tow lines - we want to retain all past attachments - reversion can use them
                    #if document._file and os.path.isfile(document._file.path):
                    #    os.remove(document._file.path)
                    document._file = approval_level_document
                    document.save()
                    d=ProposalDocument.objects.get(id=document.id)
                    self.approval_level_document = d
                    comment = 'Approval Level Document Added: {}'.format(document.name)
                else:
                    self.approval_level_document = None
                    comment = 'Approval Level Document Deleted: {}'.format(request.data['approval_level_document_name'])
                #self.save()
                self.save(version_comment=comment) # to allow revision to be added to reversion history
                self.log_user_action(ProposalUserAction.ACTION_APPROVAL_LEVEL_DOCUMENT.format(self.id),request)
                # Create a log entry for the organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_APPROVAL_LEVEL_DOCUMENT.format(self.id),request)
                return self
            except:
                raise

    def unassign(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status == 'with_approver':
                    if self.assigned_approver:
                        self.assigned_approver = None
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_UNASSIGN_APPROVER.format(self.id),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_APPROVER.format(self.id),request)
                else:
                    if self.assigned_officer:
                        self.assigned_officer = None
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_UNASSIGN_ASSESSOR.format(self.id),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_ASSESSOR.format(self.id),request)
            except:
                raise

    def add_default_requirements(self):
        #Add default standard requirements to Proposal
        due_date=None
        if self.application_type.name==ApplicationType.TCLASS:
            due_date=self.other_details.nominated_start_date
        if self.application_type.name==ApplicationType.FILMING:
            due_date=self.filming_activity.commencement_date
        if self.application_type.name==ApplicationType.EVENT:
            due_date=self.event_activity.commencement_date
        default_requirements=ProposalStandardRequirement.objects.filter(application_type=self.application_type, default=True, obsolete=False)
        if default_requirements:
            for req in default_requirements:
                r, created=ProposalRequirement.objects.get_or_create(proposal=self, standard_requirement=req, due_date= due_date)

    def move_to_status(self,request,status, approver_comment):
        if not self.can_assess(request.user):
            raise exceptions.ProposalNotAuthorized()
        if status in ['with_assessor','with_assessor_requirements','with_approver']:
            if self.processing_status == 'with_referral' or self.can_user_edit:
                raise ValidationError('You cannot change the current status at this time')
            if self.processing_status != status:
                if self.processing_status =='with_approver':
                    self.approver_comment=''
                    if approver_comment:
                        self.approver_comment = approver_comment
                        self.save()
                        send_proposal_approver_sendback_email_notification(request, self)
                self.processing_status = status
                self.save()
                if status=='with_assessor_requirements':
                    self.add_default_requirements()

                # Create a log entry for the proposal
                if self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR:
                    self.log_user_action(ProposalUserAction.ACTION_BACK_TO_PROCESSING.format(self.id),request)
                elif self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS:
                    self.log_user_action(ProposalUserAction.ACTION_ENTER_REQUIREMENTS.format(self.id),request)
        else:
            raise ValidationError('The provided status cannot be found.')


    def reissue_approval(self,request,status):
        if self.application_type.name==ApplicationType.FILMING and self.filming_approval_type=='lawful_authority':
            allowed_status=['approved', 'partially_approved']
            if not self.processing_status in allowed_status and not self.is_lawful_authority_finalised:
                raise ValidationError('You cannot change the current status at this time')
            elif self.approval and self.approval.can_reissue:
                if self.__assessor_group() in request.user.proposalassessorgroup_set.all():
                    self.processing_status = status
                    self.save(version_comment='Reissue Approval: {}'.format(self.approval.lodgement_number))
                    #self.save()
                    # Create a log entry for the proposal
                    self.log_user_action(ProposalUserAction.ACTION_REISSUE_APPROVAL.format(self.id),request)
                else:
                    raise ValidationError('Cannot reissue Approval. User not permitted.')
            else:
                raise ValidationError('Cannot reissue Approval')

        else:
            if not self.processing_status=='approved' :
                raise ValidationError('You cannot change the current status at this time')
            elif self.approval and self.approval.can_reissue:
                if self.__approver_group() in request.user.proposalapprovergroup_set.all():
                    self.processing_status = status
                    #self.save()
                    self.save(version_comment='Reissue Approval: {}'.format(self.approval.lodgement_number))
                    # Create a log entry for the proposal
                    self.log_user_action(ProposalUserAction.ACTION_REISSUE_APPROVAL.format(self.id),request)
                else:
                    raise ValidationError('Cannot reissue Approval. User not permitted.')
            else:
                raise ValidationError('Cannot reissue Approval')


    def proposed_decline(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_assessor':
                    raise ValidationError('You cannot propose to decline if it is not with assessor')

                reason = details.get('reason')
                ProposalDeclinedDetails.objects.update_or_create(
                    proposal = self,
                    defaults={'officer': request.user, 'reason': reason, 'cc_email': details.get('cc_email',None)}
                )
                self.proposed_decline_status = True
                approver_comment = ''
                self.move_to_status(request,'with_approver', approver_comment)
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_PROPOSED_DECLINE.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_PROPOSED_DECLINE.format(self.id),request)

                send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def final_decline(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot decline if it is not with approver')

                proposal_decline, success = ProposalDeclinedDetails.objects.update_or_create(
                    proposal = self,
                    defaults={'officer':request.user,'reason':details.get('reason'),'cc_email':details.get('cc_email',None)}
                )
                self.proposed_decline_status = True
                self.processing_status = 'declined'
                self.customer_status = 'declined'
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_DECLINE.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_DECLINE.format(self.id),request)
                send_proposal_decline_email_notification(self,request, proposal_decline)
            except:
                raise

    def on_hold(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (self.processing_status == 'with_assessor' or self.processing_status == 'with_referral'):
                    raise ValidationError('You cannot put on hold if it is not with assessor or with referral')

                self.prev_processing_status = self.processing_status
                self.processing_status = self.PROCESSING_STATUS_ONHOLD
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_PUT_ONHOLD.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_PUT_ONHOLD.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def on_hold_remove(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'on_hold':
                    raise ValidationError('You cannot remove on hold if it is not currently on hold')

                self.processing_status = self.prev_processing_status
                self.prev_processing_status = self.PROCESSING_STATUS_ONHOLD
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_REMOVE_ONHOLD.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_REMOVE_ONHOLD.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def with_qaofficer(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (self.processing_status == 'with_assessor' or self.processing_status == 'with_referral'):
                    raise ValidationError('You cannot send to QA Officer if it is not with assessor or with referral')

                self.prev_processing_status = self.processing_status
                self.processing_status = self.PROCESSING_STATUS_WITH_QA_OFFICER
                self.qaofficer_referral = True
                if self.qaofficer_referrals.exists():
                    qaofficer_referral = self.qaofficer_referrals.first()
                    qaofficer_referral.sent_by = request.user
                    qaofficer_referral.processing_status = 'with_qaofficer'
                else:
                    qaofficer_referral = self.qaofficer_referrals.create(sent_by=request.user)

                qaofficer_referral.save()
                self.save()

                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_WITH_QA_OFFICER.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_WITH_QA_OFFICER.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
                recipients = self.qa_officers()
                send_qaofficer_email_notification(self, recipients, request)

            except:
                raise

    def with_qaofficer_completed(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_qa_officer':
                    raise ValidationError('You cannot Complete QA Officer Assessment if processing status not currently With Assessor')

                self.processing_status = self.prev_processing_status
                self.prev_processing_status = self.PROCESSING_STATUS_WITH_QA_OFFICER

                qaofficer_referral = self.qaofficer_referrals.first()
                qaofficer_referral.qaofficer = request.user
                qaofficer_referral.qaofficer_group = QAOfficerGroup.objects.get(default=True)
                qaofficer_referral.qaofficer_text = request.data['text']
                qaofficer_referral.processing_status = 'completed'

                qaofficer_referral.save()
                self.assigned_officer = None
                self.save()

                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_QA_OFFICER_COMPLETED.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_QA_OFFICER_COMPLETED.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
                recipients = self.qa_officers()
                send_qaofficer_complete_email_notification(self, recipients, request)
            except:
                raise


    def proposed_approval(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_assessor_requirements':
                    raise ValidationError('You cannot propose for approval if it is not with assessor for requirements')
                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                approver_comment = ''
                self.move_to_status(request,'with_approver', approver_comment)
                self.assigned_officer = None
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_PROPOSED_APPROVAL.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_PROPOSED_APPROVAL.format(self.id),request)

                send_approver_approve_email_notification(request, self)
            except:
                raise

    def eclass_approval(self,request,details):
        from commercialoperator.components.approvals.models import Approval
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot issue the approval if it is not with an approver')
                if not self.applicant.organisation.postal_address:
                    raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')

                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                self.processing_status = 'approved'
                self.customer_status = 'approved'
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)

                if self.proposal_type == 'renewal':
                    pass
                else:
                    approval,created = Approval.objects.update_or_create(
                        current_proposal = self,
                        defaults = {
                            #'title' : self.title,
                            #'issue_date' : timezone.now(),
                            'issue_date' : details.get('issue_date'),
                            'expiry_date' : details.get('expiry_date'),
                            'start_date' : details.get('start_date'),
                            'applicant' : self.applicant
                        }
                    )
                self.approval = approval

                #send Proposal approval email with attachment
                #send_proposal_approval_email_notification(self,request)
                self.save(version_comment='Final Approval: {}'.format(self.approval.lodgement_number))
                self.approval.documents.all().update(can_delete=False)

            except:
                raise

    def preview_approval(self,request,details):
        from commercialoperator.components.approvals.models import PreviewTempApproval
        with transaction.atomic():
            try:
                #if self.processing_status != 'with_assessor_requirements' or self.processing_status != 'with_approver':
                if not (self.processing_status == 'with_assessor_requirements' or self.processing_status == 'with_approver'):
                    raise ValidationError('Licence preview only available when processing status is with_approver. Current status {}'.format(self.processing_status))
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                #if not self.applicant.organisation.postal_address:
                if not self.applicant_address:
                    raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')

                lodgement_number = self.previous_application.approval.lodgement_number if self.proposal_type in ['renewal', 'amendment'] else None # renewals/amendments keep same licence number
                preview_approval = PreviewTempApproval.objects.create(
                    current_proposal = self,
                    issue_date = timezone.now(),
                    expiry_date = datetime.datetime.strptime(details.get('due_date'), '%d/%m/%Y').date(),
                    start_date = datetime.datetime.strptime(details.get('start_date'), '%d/%m/%Y').date(),
                    submitter = self.submitter,
                    #org_applicant = self.applicant if isinstance(self.applicant, Organisation) else None,
                    #proxy_applicant = self.applicant if isinstance(self.applicant, EmailUser) else None,
                    org_applicant = self.org_applicant,
                    proxy_applicant = self.proxy_applicant,
                    lodgement_number = lodgement_number
                )

                # Generate the preview document - get the value of the BytesIO buffer
                licence_buffer = preview_approval.generate_doc(request.user, preview=True)

                # clean temp preview licence object
                transaction.set_rollback(True)

                return licence_buffer
            except:
                raise


    def final_approval(self,request,details):
        from commercialoperator.components.approvals.models import Approval
        from commercialoperator.helpers import is_departmentUser
        with transaction.atomic():
            try:
                self.proposed_decline_status = False

                if (self.processing_status==Proposal.PROCESSING_STATUS_AWAITING_PAYMENT and self.fee_paid) or (self.proposal_type=='amendment'):
                    # for 'Awaiting Payment' approval. External/Internal user fires this method after full payment via Make/Record Payment
                    pass
                else:
                    if not self.can_assess(request.user):
                        raise exceptions.ProposalNotAuthorized()
                    if self.processing_status != 'with_approver':
                        raise ValidationError('You cannot issue the approval if it is not with an approver')
                    #if not self.applicant.organisation.postal_address:
                    if not self.applicant_address:
                        raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')

                    self.proposed_issuance_approval = {
                        'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                        'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                        'details': details.get('details'),
                        'cc_email':details.get('cc_email')
                    }

                    if is_departmentUser(request):
                        # needed because external users come through this workflow following 'awaiting_payment; status
                        self.approved_by = request.user

                if (self.application_type.name == ApplicationType.FILMING and self.filming_approval_type == self.LICENCE and \
                        self.processing_status in [Proposal.PROCESSING_STATUS_WITH_APPROVER]) and \
                        not self.proposal_type=='amendment' and \
                        not self.fee_paid:

                    self.processing_status = self.PROCESSING_STATUS_AWAITING_PAYMENT
                    self.customer_status = self.CUSTOMER_STATUS_AWAITING_PAYMENT
                    self.approved_by = request.user
                    invoice = self.__create_filming_fee_invoice(request)
                    #confirmation = self.__create_filming_fee_confirmation(request)
                    #
                    #if confirmation:
                    if invoice:
                        # send Proposal awaiting payment approval email & Log proposal action
                        send_proposal_awaiting_payment_approval_email_notification(self, request)
                        self.log_user_action(ProposalUserAction.ACTION_AWAITING_PAYMENT_APPROVAL_.format(self.id),request)

                        # Log entry for organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_AWAITING_PAYMENT_APPROVAL_.format(self.id),request)
                        self.save(version_comment='Final Approval - Awaiting Payment, Proposal: {}'.format(self.lodgement_number))

                    else:
                        logger.info('Cannot create Filming awaiting payment confirmation')
                        raise Exception('Cannot create Filming awaiting payment confirmation')

                else:
                    self.processing_status = 'approved'
                    self.customer_status = 'approved'
                    # Log proposal action
                    self.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)
                    # Log entry for organisation
                    applicant_field=getattr(self, self.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)

                if self.processing_status == self.PROCESSING_STATUS_APPROVED:
                    # TODO if it is an ammendment proposal then check appropriately
                    checking_proposal = self
                    if self.proposal_type == 'renewal':
                        if self.previous_application:
                            previous_approval = self.previous_application.approval
                            approval,created = Approval.objects.update_or_create(
                                current_proposal = checking_proposal,
                                defaults = {
                                    'issue_date' : timezone.now(),
                                    'expiry_date' : datetime.datetime.strptime(self.proposed_issuance_approval.get('expiry_date'), '%d/%m/%Y').date(),
                                    'start_date' : datetime.datetime.strptime(self.proposed_issuance_approval.get('start_date'), '%d/%m/%Y').date(),
                                    'submitter': self.submitter,
                                    #'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                    #'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                    'org_applicant' : self.org_applicant,
                                    'proxy_applicant' : self.proxy_applicant,
                                    'lodgement_number': previous_approval.lodgement_number
                                }
                            )
                            if created:
                                previous_approval.replaced_by = approval
                                previous_approval.save()

                            self.reset_licence_discount(request.user)

                    elif self.proposal_type == 'amendment':
                        if self.previous_application:
                            previous_approval = self.previous_application.approval
                            approval,created = Approval.objects.update_or_create(
                                current_proposal = checking_proposal,
                                defaults = {
                                    'issue_date' : timezone.now(),
                                    'expiry_date' : datetime.datetime.strptime(self.proposed_issuance_approval.get('expiry_date'), '%d/%m/%Y').date(),
                                    'start_date' : datetime.datetime.strptime(self.proposed_issuance_approval.get('start_date'), '%d/%m/%Y').date(),
                                    'submitter': self.submitter,
                                    #'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                    #'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                    'org_applicant' : self.org_applicant,
                                    'proxy_applicant' : self.proxy_applicant,
                                    'lodgement_number': previous_approval.lodgement_number
                                }
                            )
                            if created:
                                previous_approval.replaced_by = approval
                                previous_approval.save()
                    else:
                        approval,created = Approval.objects.update_or_create(
                            current_proposal = checking_proposal,
                            defaults = {
                                'issue_date' : timezone.now(),
                                'expiry_date' : datetime.datetime.strptime(self.proposed_issuance_approval.get('expiry_date'), '%d/%m/%Y').date(),
                                'start_date' : datetime.datetime.strptime(self.proposed_issuance_approval.get('start_date'), '%d/%m/%Y').date(),
                                'submitter': self.submitter,
                                #'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                #'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                'org_applicant' : self.org_applicant,
                                'proxy_applicant' : self.proxy_applicant,
                                #'extracted_fields' = JSONField(blank=True, null=True)
                            }
                        )
                        self.reset_licence_discount(request.user)
                    # Generate compliances
                    from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
                    if created:
                        if self.proposal_type == 'amendment':
                            approval_compliances = Compliance.objects.filter(approval= previous_approval, proposal = self.previous_application, processing_status='future')
                            if approval_compliances:
                                for c in approval_compliances:
                                    c.delete()
                        # Log creation
                        # Generate the document
                        approval.generate_doc(request.user)
                        self.generate_compliances(approval, request)
                        # send the doc and log in approval and org
                    else:
                        # Generate the document
                        approval.generate_doc(request.user)
                        #Delete the future compliances if Approval is reissued and generate the compliances again.
                        approval_compliances = Compliance.objects.filter(approval= approval, proposal = self, processing_status='future')
                        if approval_compliances:
                            for c in approval_compliances:
                                c.delete()
                        self.generate_compliances(approval, request)
                        # Log proposal action
                        self.log_user_action(ProposalUserAction.ACTION_UPDATE_APPROVAL_.format(self.id),request)
                        # Log entry for organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UPDATE_APPROVAL_.format(self.id),request)
                    self.approval = approval

                    #send Proposal approval email with attachment
                    send_proposal_approval_email_notification(self,request)
                    self.save(version_comment='Final Approval: {}'.format(self.approval.lodgement_number))
                    self.approval.documents.all().update(can_delete=False)

            except:
                raise

    def __create_filming_fee_invoice(self, request):

        from dateutil.relativedelta import relativedelta
        from commercialoperator.components.bookings.models import FilmingFee
        from commercialoperator.components.bookings.utils import create_filming_fee_lines
        from ledger.checkout.utils import createCustomBasket
        from ledger.payments.invoice.utils import CreateInvoiceBasket

        filming_fee = None
        if self.application_type.name == ApplicationType.FILMING and self.filming_approval_type==self.LICENCE \
            and not self.fee_invoice_reference and len(self.filming_activity.film_type)>0:

            lines, lines_aggregated = create_filming_fee_lines(self)

            with transaction.atomic():
                try:
                    logger.info('Creating filming fee invoice')

                    deferred_payment_date = timezone.now() + relativedelta(months=1)

                    basket  = createCustomBasket(lines, request.user, settings.PAYMENT_SYSTEM_ID)
                    order = CreateInvoiceBasket(
                            payment_method='other', system=settings.PAYMENT_SYSTEM_PREFIX
                        ).create_invoice_and_order(basket, 0, None, None, user=request.user, invoice_text='Payment Invoice')
                    invoice = Invoice.objects.get(order_number=order.number)

                    filming_fee = FilmingFee.objects.create(proposal=self,
                            lines=lines, 
                            lines_aggregated=lines_aggregated,
                            created_by=request.user, 
                            payment_type=FilmingFee.PAYMENT_TYPE_TEMPORARY, 
                            deferred_payment_date=deferred_payment_date
                    )
                    filming_fee.filming_fee_invoices.create(invoice_reference=invoice.reference)

                except Exception as e:
                    logger.error('Failed to create filming fee confirmation')
                    logger.error('{}'.format(e))

        return filming_fee


    def generate_compliances(self,approval, request):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
        #For amendment type of Proposal, check for copied requirements from previous proposal
        if self.proposal_type == 'amendment':
            try:
                for r in self.requirements.filter(copied_from__isnull=False):
                    cs=[]
                    cs=Compliance.objects.filter(requirement=r.copied_from, proposal=self.previous_application, processing_status='due')
                    if cs:
                        if r.is_deleted == True:
                            for c in cs:
                                c.processing_status='discarded'
                                c.customer_status = 'discarded'
                                c.reminder_sent=True
                                c.post_reminder_sent=True
                                c.save()
                        if r.is_deleted == False:
                            for c in cs:
                                c.proposal= self
                                c.approval=approval
                                c.requirement=r
                                c.save()
            except:
                raise
        #requirement_set= self.requirements.filter(copied_from__isnull=True).exclude(is_deleted=True)
        requirement_set= self.requirements.all().exclude(is_deleted=True)

        #for req in self.requirements.all():
        for req in requirement_set:
            try:
                if req.due_date and req.due_date >= today:
                    current_date = req.due_date
                    #create a first Compliance
                    try:
                        compliance= Compliance.objects.get(requirement = req, due_date = current_date)
                    except Compliance.DoesNotExist:
                        compliance =Compliance.objects.create(
                                    proposal=self,
                                    due_date=current_date,
                                    processing_status='future',
                                    approval=approval,
                                    requirement=req,
                        )
                        compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
                    if req.recurrence:
                        while current_date < approval.expiry_date:
                            for x in range(req.recurrence_schedule):
                            #Weekly
                                if req.recurrence_pattern == 1:
                                    current_date += timedelta(weeks=1)
                            #Monthly
                                elif req.recurrence_pattern == 2:
                                    current_date += timedelta(weeks=4)
                                    pass
                            #Yearly
                                elif req.recurrence_pattern == 3:
                                    current_date += timedelta(days=365)
                            # Create the compliance
                            if current_date <= approval.expiry_date:
                                try:
                                    compliance= Compliance.objects.get(requirement = req, due_date = current_date)
                                except Compliance.DoesNotExist:
                                    compliance =Compliance.objects.create(
                                                proposal=self,
                                                due_date=current_date,
                                                processing_status='future',
                                                approval=approval,
                                                requirement=req,
                                    )
                                    compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
            except:
                raise



    def renew_approval(self,request):
        with transaction.atomic():
            previous_proposal = self
            try:
                renew_conditions = {
                    'previous_application': previous_proposal,
                    'customer_status': 'with_assessor'

                }
                #proposal=Proposal.objects.get(previous_application = previous_proposal)
                proposal=Proposal.objects.get(**renew_conditions)
                #if proposal.customer_status=='with_assessor':
                if proposal:
                    raise ValidationError('A renewal/ amendment for this licence has already been lodged and is awaiting review.')
            except Proposal.DoesNotExist:
                previous_proposal = Proposal.objects.get(id=self.id)
                proposal = clone_proposal_with_status_reset(previous_proposal)
                proposal.proposal_type = 'renewal'
                proposal.training_completed = False
                #proposal.schema = ProposalType.objects.first().schema
                ptype = ProposalType.objects.filter(name=proposal.application_type).latest('version')
                proposal.schema = ptype.schema
                proposal.submitter = request.user
                proposal.previous_application = self
                proposal.proposed_issuance_approval= None

                if proposal.application_type.name==ApplicationType.TCLASS:
                    # require user to re-enter mandatory info in 'Other Details' tab, when renewing
                    proposal.other_details.insurance_expiry = None
                    proposal.other_details.preferred_licence_period = None
                    proposal.other_details.nominated_start_date = None
                    ProposalAccreditation.objects.filter(proposal_other_details__proposal=proposal).delete()
                    proposal.documents.filter(input_name__in=['deed_poll','currency_certificate']).delete()

                    # require  user to pay Application and Licence Fee again
                    proposal.fee_invoice_reference = None

                    try:
                        ProposalOtherDetails.objects.get(proposal=proposal)
                    except ProposalOtherDetails.DoesNotExist:
                        ProposalOtherDetails.objects.create(proposal=proposal)
                    # Create a log entry for the proposal
                    proposal.other_details.nominated_start_date=self.approval.expiry_date+ datetime.timedelta(days=1)
                    proposal.other_details.save()
                if proposal.application_type.name==ApplicationType.FILMING:

                    proposal.filming_other_details.insurance_expiry = None
                    proposal.filming_other_details.save()
                    proposal.filming_activity.commencement_date=None
                    proposal.filming_activity.completion_date=None
                    proposal.filming_activity.save()
                    proposal.documents.filter(input_name__in=['deed_poll','currency_certificate']).delete()

                    # require  user to pay Application and Licence Fee again
                    proposal.fee_invoice_reference = None

                if proposal.application_type.name==ApplicationType.EVENT:

                    proposal.event_other_details.insurance_expiry = None
                    proposal.event_other_details.save()
                    proposal.event_activity.commencement_date=None
                    proposal.event_activity.completion_date=None
                    proposal.event_activity.save()
                    proposal.documents.filter(input_name__in=['deed_poll','currency_certificate']).delete()

                    # require  user to pay Application and Licence Fee again
                    proposal.fee_invoice_reference = None
                    
                    proposal.reset_training_completed(request)

                req=self.requirements.all().exclude(is_deleted=True)
                from copy import deepcopy
                if req:
                    for r in req:
                        old_r = deepcopy(r)
                        r.proposal = proposal
                        r.copied_from=None
                        r.copied_for_renewal=True
                        if r.due_date:
                            r.due_date=None
                            r.require_due_date=True
                        r.id = None
                        r.district_proposal=None
                        r.save()
                #copy all the requirement documents from previous proposal
                for requirement in proposal.requirements.all():
                    for requirement_document in RequirementDocument.objects.filter(requirement=requirement.copied_from):
                        requirement_document.requirement = requirement
                        requirement_document.id = None
                        requirement_document._file.name = u'{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, requirement_document.name)
                        requirement_document.can_delete = True
                        requirement_document.save()
                        # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_RENEW_PROPOSAL.format(self.id),request)
                # Create a log entry for the organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_RENEW_PROPOSAL.format(self.id),request)
                #Log entry for approval
                from commercialoperator.components.approvals.models import ApprovalUserAction
                self.approval.log_user_action(ApprovalUserAction.ACTION_RENEW_APPROVAL.format(self.approval.id),request)
                proposal.save(version_comment='New Amendment/Renewal Application created, from origin {}'.format(proposal.previous_application_id))
                #proposal.save()
            return proposal

    def amend_approval(self,request):
        with transaction.atomic():
            previous_proposal = self
            try:
                amend_conditions = {
                'previous_application': previous_proposal,
                'proposal_type': 'amendment'

                }
                proposal=Proposal.objects.get(**amend_conditions)
                if proposal.customer_status=='with_assessor':
                    raise ValidationError('An amendment for this licence has already been lodged and is awaiting review.')
            except Proposal.DoesNotExist:
                previous_proposal = Proposal.objects.get(id=self.id)
                proposal = clone_proposal_with_status_reset(previous_proposal)
                proposal.proposal_type = 'amendment'
                #proposal.training_completed = proposal.applicant_training_completed if proposal.application_type.name==ApplicationType.EVENT else True 
                proposal.training_completed = True
                proposal.reset_training_completed(request)

                #proposal.schema = ProposalType.objects.first().schema
                ptype = ProposalType.objects.filter(name=proposal.application_type).latest('version')
                proposal.schema = ptype.schema
                proposal.submitter = request.user
                proposal.previous_application = self
                if proposal.application_type.name==ApplicationType.TCLASS:
                    try:
                        ProposalOtherDetails.objects.get(proposal=proposal)
                    except ProposalOtherDetails.DoesNotExist:
                        ProposalOtherDetails.objects.create(proposal=proposal)
                #copy all the requirements from the previous proposal
                #req=self.requirements.all()
                req=self.requirements.all().exclude(is_deleted=True)
                from copy import deepcopy
                if req:
                    for r in req:
                        old_r = deepcopy(r)
                        r.proposal = proposal
                        r.copied_from=old_r
                        r.id = None
                        r.district_proposal=None
                        r.save()
                #copy all the requirement documents from previous proposal
                for requirement in proposal.requirements.all():
                    for requirement_document in RequirementDocument.objects.filter(requirement=requirement.copied_from):
                        requirement_document.requirement = requirement
                        requirement_document.id = None
                        requirement_document._file.name = u'{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, requirement_document.name)
                        requirement_document.can_delete = True
                        requirement_document.save()
                            # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_AMEND_PROPOSAL.format(self.id),request)
                # Create a log entry for the organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_AMEND_PROPOSAL.format(self.id),request)
                #Log entry for approval
                from commercialoperator.components.approvals.models import ApprovalUserAction
                self.approval.log_user_action(ApprovalUserAction.ACTION_AMEND_APPROVAL.format(self.approval.id),request)
                proposal.save(version_comment='New Amendment/Renewal Application created, from origin {}'.format(proposal.previous_application_id))
                #proposal.save()
            return proposal

    #Filming application method
    #This is to show basic logic behind creating district Proposal for each district related to parks listed with Filming Application.
    def send_to_districts(self, request):
        with transaction.atomic():
            try:
                if self.application_type.name==ApplicationType.FILMING and self.processing_status=='with_assessor':
                    #If reissueing approval check for compare previous district proposals and new district proposals
                    new_district_proposal_ids=[]
                    previous_district_proposal_ids=[]
                    if self.approval:
                        previous_district_proposal_ids= self.district_proposals.all().values_list('id', flat=True)

                    #Get the list all the Districts of the Parks linked to the Proposal
                    districts_list=self.filming_parks.all().values_list('park__district', flat=True)

                    if districts_list:
                        for district in districts_list:
                            district_instance=District.objects.get(id=district)
                            #Get the list of all the Filming Parks in each district
                            #parks_list=list(ProposalFilmingParks.objects.filter(park__district=district, proposal=self).values_list('id',flat=True))
                            #create a District proposal for each district
                            district_proposal, created=DistrictProposal.objects.update_or_create(district=district_instance,proposal= self)
                            #district_proposal.proposal_park= parks_list
                            status=district_proposal.processing_status #for reissue
                            district_proposal.processing_status='with_assessor'
                            district_proposal.save()
                            new_district_proposal_ids.append(district_proposal.id)
                            if created or status!='with_assessor' :
                                send_district_proposal_submit_email_notification(district_proposal, request)
                        self.processing_status='with_district_assessor'
                        self.save()
                        self.log_user_action(ProposalUserAction.SEND_TO_DISTRICTS.format(self.id),request)

                    #for Amendment Proposal, Find the Requirements copied from previous application and assign to district Proposal according to distrcit
                    if self.proposal_type=='amendment':
                        for district_proposal in self.district_proposals.all():
                            qs=self.requirements.filter(district=district_proposal.district, district_proposal__isnull=True)
                            qs.update(district_proposal=district_proposal)
                        #Mark the remaining requirements as deleted
                        qs_requirements= self.requirements.filter(district_proposal__isnull=True)
                        qs_requirements.update(is_deleted=True)

                    if self.approval: #If reissuing proposal
                        for item in previous_district_proposal_ids:
                            if item not in new_district_proposal_ids:
                                instance=DistrictProposal.objects.get(id=item)
                                instance.processing_status='discarded' #Mark proposal as discarded
                                instance.save()
                                qs= instance.district_proposal_requirements.all()
                                qs.update(is_deleted=True)#Delete all the requirements
                                from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
                                due_compliances=Compliance.objects.filter(processing_status='due', district_proposal=item)
                                due_compliances.update(processing_status='discarded', customer_status='discarded', reminder_sent=True, post_reminder_sent=True)
                                future_compliances=Compliance.objects.filter(processing_status='future', district_proposal=item)
                                future_compliances.delete()

                return self

            except:
                raise

    #Filming application method
    #This is to show basic logic behind creating district Proposal for each district related to parks listed with Filming Application.
    def send_to_kensington(self, request):
        with transaction.atomic():
            try:
                if self.application_type.name==ApplicationType.FILMING and self.processing_status=='with_assessor':
                    #If reissueing approval check for compare previous district proposals and new district proposals
                    new_district_proposal_ids=[]
                    previous_district_proposal_ids=[]
                    if self.approval:
                        previous_district_proposal_ids= self.district_proposals.all().values_list('id', flat=True)
                    try:
                        district_instance=District.objects.get(name__icontains='Kensington')
                        district_proposal, created=DistrictProposal.objects.update_or_create(district=district_instance,proposal= self)
                        status=district_proposal.processing_status #for reissue
                        district_proposal.processing_status='with_assessor'
                        district_proposal.save()
                        new_district_proposal_ids.append(district_proposal.id)
                        if created or status!='with_assessor' :
                            send_district_proposal_submit_email_notification(district_proposal, request)
                        self.processing_status='with_district_assessor'
                        self.save()
                        self.log_user_action(ProposalUserAction.SEND_TO_DISTRICTS.format(self.id),request)

                        #for Amendment Proposal, Find the Requirements copied from previous application and assign to district Proposal according to distrcit
                        if self.proposal_type=='amendment':
                            for district_proposal in self.district_proposals.all():
                                qs=self.requirements.filter(district=district_proposal.district, district_proposal__isnull=True)
                                qs.update(district_proposal=district_proposal)
                            #Mark the remaining requirements as deleted
                            qs_requirements= self.requirements.filter(district_proposal__isnull=True)
                            qs_requirements.update(is_deleted=True)

                        if self.approval: #If reissuing proposal
                            for item in previous_district_proposal_ids:
                                if item not in new_district_proposal_ids:
                                    instance=DistrictProposal.objects.get(id=item)
                                    instance.processing_status='discarded' #Mark proposal as discarded
                                    instance.save()
                                    qs= instance.district_proposal_requirements.all()
                                    qs.update(is_deleted=True)#Delete all the requirements
                                    from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
                                    due_compliances=Compliance.objects.filter(processing_status='due', district_proposal=item)
                                    due_compliances.update(processing_status='discarded', customer_status='discarded', reminder_sent=True, post_reminder_sent=True)
                                    future_compliances=Compliance.objects.filter(processing_status='future', district_proposal=item)
                                    future_compliances.delete()
                        return self
                    except:
                        raise

            except:
                raise

    def reapply_event(self,request):
        with transaction.atomic():
            previous_proposal = self
            previous_proposal = Proposal.objects.get(id=self.id)
            proposal = clone_proposal_with_status_reset(previous_proposal)
            proposal.proposal_type = 'new_proposal'
            proposal.training_completed = False
            #proposal.schema = ProposalType.objects.first().schema
            ptype = ProposalType.objects.filter(name=proposal.application_type).latest('version')
            proposal.schema = ptype.schema
            proposal.submitter = request.user
            #proposal.previous_application = self
            proposal.proposed_issuance_approval= None
            if proposal.application_type.name==ApplicationType.TCLASS:
                # require user to re-enter mandatory info in 'Other Details' tab, when renewing
                proposal.other_details.insurance_expiry = None
                proposal.other_details.preferred_licence_period = None
                proposal.other_details.nominated_start_date = None
                ProposalAccreditation.objects.filter(proposal_other_details__proposal=proposal).delete()
                proposal.documents.filter(input_name__in=['deed_poll','currency_certificate']).delete()
                # require  user to pay Application and Licence Fee again
                proposal.fee_invoice_reference = None
                try:
                    ProposalOtherDetails.objects.get(proposal=proposal)
                except ProposalOtherDetails.DoesNotExist:
                    ProposalOtherDetails.objects.create(proposal=proposal)
                # Create a log entry for the proposal
                proposal.other_details.nominated_start_date=self.approval.expiry_date+ datetime.timedelta(days=1)
                proposal.other_details.save()
            if proposal.application_type.name==ApplicationType.FILMING:
                proposal.filming_other_details.insurance_expiry = None
                proposal.filming_other_details.save()
                proposal.filming_activity.commencement_date=None
                proposal.filming_activity.completion_date=None
                proposal.filming_activity.save()
                proposal.documents.filter(input_name__in=['deed_poll','currency_certificate']).delete()
                # require  user to pay Application and Licence Fee again
                proposal.fee_invoice_reference = None
            if proposal.application_type.name==ApplicationType.EVENT:
                proposal.event_other_details.insurance_expiry = None
                proposal.event_other_details.save()
                proposal.event_activity.commencement_date=None
                proposal.event_activity.completion_date=None
                proposal.event_activity.save()
                #Delete all the files for Event application for Prefil functionality
                # proposal.documents.filter(input_name__in=['deed_poll','currency_certificate']).delete()
                proposal.documents.all().delete()
                # require  user to pay Application and Licence Fee again
                proposal.fee_invoice_reference = None
                proposal.property_cache={}
                proposal.save()

                proposal.reset_training_completed(request)
            req=self.requirements.all().exclude(is_deleted=True)
            from copy import deepcopy
            if req:
                for r in req:
                    old_r = deepcopy(r)
                    r.proposal = proposal
                    r.copied_from=None
                    r.copied_for_renewal=True
                    if r.due_date:
                        r.due_date=None
                        r.require_due_date=True
                    r.id = None
                    r.district_proposal=None
                    r.save()
            #copy all the requirement documents from previous proposal
            for requirement in proposal.requirements.all():
                for requirement_document in RequirementDocument.objects.filter(requirement=requirement.copied_from):
                    requirement_document.requirement = requirement
                    requirement_document.id = None
                    requirement_document._file.name = u'{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, requirement_document.name)
                    requirement_document.can_delete = True
                    requirement_document.save()
                    # Create a log entry for the proposal
            #self.log_user_action(ProposalUserAction.ACTION_RENEW_PROPOSAL.format(self.id),request)
            # Create a log entry for the organisation
            #applicant_field=getattr(self, self.applicant_field)
            #applicant_field.log_user_action(ProposalUserAction.ACTION_RENEW_PROPOSAL.format(self.id),request)
            #Log entry for approval
            #from commercialoperator.components.approvals.models import ApprovalUserAction
            #self.approval.log_user_action(ApprovalUserAction.ACTION_RENEW_APPROVAL.format(self.approval.id),request)
            #proposal.save(version_comment='New Amendment/Renewal Application created, from origin {}'.format(proposal.previous_application_id))
            #proposal.save()
            return proposal
        
    
    
class ApplicationFeeDiscount(RevisionedMixin):
    DISCOUNT_TYPE_APPLICATION = 0
    DISCOUNT_TYPE_LICENCE = 1
    DISCOUNT_TYPE_CHOICES = (
                (DISCOUNT_TYPE_APPLICATION, 'Discount application'),
                (DISCOUNT_TYPE_LICENCE, 'Discount licence'),
    )
    proposal = models.ForeignKey(Proposal, related_name='fee_discounts', null=True)
    discount_type = models.CharField(max_length=40, choices=DISCOUNT_TYPE_CHOICES)
    discount = models.FloatField(validators=[MinValueValidator(0.0)])
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(EmailUser,on_delete=models.PROTECT, related_name='created_by_fee_discount')
    reset_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} - {}% - {}'.format(self.get_discount_type_display(), self.discount, self.proposal.fee_invoice_reference)

    @property
    def invoice(self):
        try:
            invoice = Invoice.objects.get(reference=self.proposal.fee_invoice_reference)
            return invoice
        except Invoice.DoesNotExist:
            pass
        return False

    class Meta:
        app_label = 'commercialoperator'

    @property
    def payment_amount(self):
        return self.invoice.amount

    class Meta:
        app_label = 'commercialoperator'


class ProposalLogDocument(Document):
    log_entry = models.ForeignKey('ProposalLogEntry',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_comms_log_filename, max_length=512)

    class Meta:
        app_label = 'commercialoperator'


class ProposalLogEntry(CommunicationsLogEntry):
    proposal = models.ForeignKey(Proposal, related_name='comms_logs')

    def __str__(self):
        return '{} - {}'.format(self.reference, self.subject)

    class Meta:
        app_label = 'commercialoperator'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.proposal.reference
        super(ProposalLogEntry, self).save(**kwargs)

class ProposalOtherDetails(models.Model):
    preferred_licence_period=models.CharField('Preferred licence period', max_length=40, choices=LicencePeriod.LICENCE_PERIOD_CHOICES, null=True, blank=True)
    nominated_start_date= models.DateField(blank=True, null=True)
    insurance_expiry= models.DateField(blank=True, null=True)
    other_comments=models.TextField(blank=True)
    mooring = JSONField(default=[''])
    #if credit facilities for payment of fees is required
    credit_fees=models.BooleanField(default=False)
    #if credit/ cash payment docket books are required
    credit_docket_books=models.BooleanField(default=False)
    docket_books_number=models.CharField('Docket books number', max_length=20, blank=True )
    proposal = models.OneToOneField(Proposal, related_name='other_details', null=True)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def proposed_end_date(self):
        end_date=None
        if self.preferred_licence_period and self.nominated_start_date:
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_2_MONTHS:
                end_date=self.nominated_start_date + relativedelta(months=+2) - relativedelta(days=1)
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_1_YEAR:
                end_date=self.nominated_start_date + relativedelta(months=+12)- relativedelta(days=1)
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_3_YEAR:
                end_date=self.nominated_start_date + relativedelta(months=+36)- relativedelta(days=1)
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_5_YEAR:
                end_date=self.nominated_start_date + relativedelta(months=+60)- relativedelta(days=1)
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_7_YEAR:
                end_date=self.nominated_start_date + relativedelta(months=+84)- relativedelta(days=1)
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_10_YEAR:
                end_date=self.nominated_start_date + relativedelta(months=+120)- relativedelta(days=1)
            if self.preferred_licence_period == LicencePeriod.LICENCE_PERIOD_20_YEAR:
                end_date=self.nominated_start_date + relativedelta(months=+240)- relativedelta(days=1)
        return end_date

    @property
    def notification_months_tolist(self):
        return LicencePeriod.objects.get(licence_period=self.preferred_licence_period).notification_months_tolist

class ProposalAccreditation(models.Model):
    #activities_land = models.CharField(max_length=24, blank=True, default='')
    ACCREDITATION_TYPE_CHOICES = (
        ('no', 'None'),
        ('atap', 'QTA'),
        ('eco_certification', 'Eco Certification'),
        ('narta', 'NARTA'),
        ('other', 'Other')
    )

    accreditation_type = models.CharField('Accreditation', max_length=40, choices=ACCREDITATION_TYPE_CHOICES,
                                       default=ACCREDITATION_TYPE_CHOICES[0][0])
    accreditation_expiry= models.DateField(blank=True, null=True)
    comments=models.TextField(blank=True)
    proposal_other_details = models.ForeignKey(ProposalOtherDetails, related_name='accreditations', null=True)

    def __str__(self):
        return '{} - {}'.format(self.accreditation_type, self.comments)

    class Meta:
        app_label = 'commercialoperator'


class ProposalPark(models.Model):
    park = models.ForeignKey(Park, blank=True, null=True, related_name='proposals')
    proposal = models.ForeignKey(Proposal, blank=True, null=True, related_name='parks')

    def __str__(self):
        return self.park.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('park', 'proposal')

    @property
    def land_activities(self):
        qs=self.activities.all()
        categories=ActivityCategory.objects.filter(activity_type='land')
        activities=qs.filter(Q(activity__activity_category__in = categories)& Q(activity__visible=True))
        return activities

    @property
    def marine_activities(self):
        qs=self.activities.all()
        categories=ActivityCategory.objects.filter(activity_type='marine')
        activities=qs.filter(Q(activity__activity_category__in = categories)& Q(activity__visible=True))
        return activities

#To store Park activities related to Proposal T class land parks
class ProposalParkActivity(models.Model):
    proposal_park = models.ForeignKey(ProposalPark, blank=True, null=True, related_name='activities')
    activity = models.ForeignKey(Activity, blank=True, null=True)

    def __str__(self):
        return self.activity.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal_park', 'activity')

    @property
    def activity_name(self):
        return self.activity.name


#To store Park access_types related to Proposal T class land parks
class ProposalParkAccess(models.Model):
    proposal_park = models.ForeignKey(ProposalPark, blank=True, null=True, related_name='access_types')
    access_type = models.ForeignKey(AccessType, blank=True, null=True)

    def __str__(self):
        return self.access_type.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal_park', 'access_type')

#To store Park zones related to Proposal T class marine parks
class ProposalParkZone(models.Model):
    proposal_park = models.ForeignKey(ProposalPark, blank=True, null=True, related_name='zones')
    zone = models.ForeignKey(Zone, blank=True, null=True, related_name='proposal_zones')
    access_point = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.zone.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('zone', 'proposal_park')

class ProposalParkZoneActivity(models.Model):
    park_zone = models.ForeignKey(ProposalParkZone, blank=True, null=True, related_name='park_activities')
    activity = models.ForeignKey(Activity, blank=True, null=True)
    #section=models.ForeignKey(Section, blank=True, null= True)

    def __str__(self):
        return '{} - {}'.format(self.activity.name, self.park_zone.zone.name)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('park_zone', 'activity')

    @property
    def activity_name(self):
        return self.activity.name


class ProposalTrail(models.Model):
    trail = models.ForeignKey(Trail, blank=True, null=True, related_name='proposals')
    proposal = models.ForeignKey(Proposal, blank=True, null=True, related_name='trails')

    def __str__(self):
        return self.trail.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('trail', 'proposal')


class ProposalTrailSection(models.Model):
    proposal_trail = models.ForeignKey(ProposalTrail, blank=True, null=True, related_name='sections')
    section = models.ForeignKey(Section, blank=True, null=True, related_name='proposal_trails')

    def __str__(self):
        return '{} - {}'.format(self.proposal_trail, self.section.name)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('section', 'proposal_trail')


class ProposalTrailSectionActivity(models.Model):
    trail_section = models.ForeignKey(ProposalTrailSection, blank=True, null=True, related_name='trail_activities')
    activity = models.ForeignKey(Activity, blank=True, null=True)
    #section=models.ForeignKey(Section, blank=True, null= True)

    def __str__(self):
        return '{} - {}'.format(self.trail_section, self.activity.name)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('trail_section', 'activity')

    @property
    def activity_name(self):
        return self.activity.name

@python_2_unicode_compatible
class Vehicle(models.Model):
    capacity = models.CharField(max_length=200, blank=True)
    rego = models.CharField(max_length=200, blank=True)
    license = models.CharField(max_length=200, blank=True)
    access_type= models.ForeignKey(AccessType,null=True, related_name='vehicles')
    rego_expiry= models.DateField(blank=True, null=True)
    proposal = models.ForeignKey(Proposal, related_name='vehicles')

    def __str__(self):
        return '{} - {}'.format(self.rego, self.access_type)

    class Meta:
        app_label = 'commercialoperator'

    def __str__(self):
        return self.rego


@python_2_unicode_compatible
class Vessel(models.Model):
    nominated_vessel = models.CharField(max_length=200, blank=True)
    spv_no = models.CharField(max_length=200, blank=True)
    hire_rego = models.CharField(max_length=200, blank=True)
    craft_no = models.CharField(max_length=200, blank=True)
    size = models.CharField(max_length=200, blank=True)
    #rego_expiry= models.DateField(blank=True, null=True)
    proposal = models.ForeignKey(Proposal, related_name='vessels')

    def __str__(self):
        return '{} - {}'.format(self.spv_no, self.nominated_vessel)

    class Meta:
        app_label = 'commercialoperator'

    def __str__(self):
        return self.nominated_vessel

@python_2_unicode_compatible
class ProposalRequest(models.Model):
    proposal = models.ForeignKey(Proposal, related_name='proposalrequest_set')
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    officer = models.ForeignKey(EmailUser, null=True)

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)

    class Meta:
        app_label = 'commercialoperator'

class ComplianceRequest(ProposalRequest):
    REASON_CHOICES = (('outstanding', 'There are currently outstanding returns for the previous licence'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

    class Meta:
        app_label = 'commercialoperator'


class AmendmentReason(models.Model):
    reason = models.CharField('Reason', max_length=125)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Amendment Reason" # display name in Admin
        verbose_name_plural = "Application Amendment Reasons"

    def __str__(self):
        return self.reason


class AmendmentRequest(ProposalRequest):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    #REASON_CHOICES = (('insufficient_detail', 'The information provided was insufficient'),
    #                  ('missing_information', 'There was missing information'),
    #                  ('other', 'Other'))
    # try:
    #     # model requires some choices if AmendmentReason does not yet exist or is empty
    #     REASON_CHOICES = list(AmendmentReason.objects.values_list('id', 'reason'))
    #     if not REASON_CHOICES:
    #         REASON_CHOICES = ((0, 'The information provided was insufficient'),
    #                           (1, 'There was missing information'),
    #                           (2, 'Other'))
    # except:
    #     REASON_CHOICES = ((0, 'The information provided was insufficient'),
    #                       (1, 'There was missing information'),
    #                       (2, 'Other'))


    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    #reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])
    reason = models.ForeignKey(AmendmentReason, blank=True, null=True)
    #reason = models.ForeignKey(AmendmentReason)

    class Meta:
        app_label = 'commercialoperator'


    def generate_amendment(self,request):
        with transaction.atomic():
            try:
                if not self.proposal.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.status == 'requested':
                    proposal = self.proposal
                    if proposal.processing_status != 'draft':
                        proposal.processing_status = 'draft'
                        proposal.customer_status = 'draft'
                        proposal.save()
                        proposal.documents.all().update(can_hide=True)
                        proposal.required_documents.all().update(can_hide=True)
                    # Create a log entry for the proposal
                    proposal.log_user_action(ProposalUserAction.ACTION_ID_REQUEST_AMENDMENTS,request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(proposal, proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_ID_REQUEST_AMENDMENTS,request)

                    # send email

                    send_amendment_email_notification(self,request, proposal)

                self.save()
            except:
                raise

class Assessment(ProposalRequest):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'),
                      ('assessment_expired', 'Assessment Period Expired'))
    assigned_assessor = models.ForeignKey(EmailUser, blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    date_last_reminded = models.DateField(null=True, blank=True)
    #requirements = models.ManyToManyField('Requirement', through='AssessmentRequirement')
    comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)

    class Meta:
        app_label = 'commercialoperator'

class ProposalDeclinedDetails(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='declined_details')
    proposal = models.OneToOneField(Proposal)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)
    cc_email = models.TextField(null=True)

    class Meta:
        app_label = 'commercialoperator'

class ProposalOnHold(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='onhold')
    proposal = models.OneToOneField(Proposal)
    officer = models.ForeignKey(EmailUser, null=False)
    comment = models.TextField(blank=True)
    documents = models.ForeignKey(ProposalDocument, blank=True, null=True, related_name='onhold_documents')

    class Meta:
        app_label = 'commercialoperator'


@python_2_unicode_compatible
#class ProposalStandardRequirement(models.Model):
class ProposalStandardRequirement(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    obsolete = models.BooleanField(default=False)
    application_type = models.ForeignKey(ApplicationType, null=True, blank=True)
    participant_number_required=models.BooleanField(default=False)
    default=models.BooleanField(default=False)
    #require_due_date = models.BooleanField(default=False)


    def __str__(self):
        return self.code

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Standard Requirement"
        verbose_name_plural = "Application Standard Requirements"

    # def clean(self):
    #     if self.application_type:
    #         try:
    #             default = ProposalStandardRequirement.objects.get(default=True, application_type=self.application_type)
    #         except ProposalStandardRequirement.DoesNotExist:
    #             default = None

    #     if not self.pk:
    #         if default and self.default:
    #             raise ValidationError('There can only be one default Standard requirement per Application type')



class ProposalUserAction(UserAction):
    ACTION_CREATE_CUSTOMER_ = "Create customer {}"
    ACTION_CREATE_PROFILE_ = "Create profile {}"
    ACTION_LODGE_APPLICATION = "Lodge application {}"
    ACTION_ASSIGN_TO_ASSESSOR = "Assign application {} to {} as the assessor"
    ACTION_UNASSIGN_ASSESSOR = "Unassign assessor from application {}"
    ACTION_ASSIGN_TO_APPROVER = "Assign application {} to {} as the approver"
    ACTION_UNASSIGN_APPROVER = "Unassign approver from application {}"
    ACTION_ACCEPT_ID = "Accept ID"
    ACTION_RESET_ID = "Reset ID"
    ACTION_ID_REQUEST_UPDATE = 'Request ID update'
    ACTION_ACCEPT_CHARACTER = 'Accept character'
    ACTION_RESET_CHARACTER = "Reset character"
    ACTION_ACCEPT_REVIEW = 'Accept review'
    ACTION_RESET_REVIEW = "Reset review"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_SEND_FOR_ASSESSMENT_TO_ = "Send for assessment to {}"
    ACTION_SEND_ASSESSMENT_REMINDER_TO_ = "Send assessment reminder to {}"
    ACTION_DECLINE = "Decline application {}"
    ACTION_ENTER_CONDITIONS = "Enter requirement"
    ACTION_CREATE_CONDITION_ = "Create requirement {}"
    ACTION_ISSUE_APPROVAL_ = "Issue Licence for application {}"
    ACTION_AWAITING_PAYMENT_APPROVAL_ = "Awaiting Payment for application {}"
    ACTION_UPDATE_APPROVAL_ = "Update Licence for application {}"
    ACTION_EXPIRED_APPROVAL_ = "Expire Approval for proposal {}"
    ACTION_DISCARD_PROPOSAL = "Discard application {}"
    ACTION_APPROVAL_LEVEL_DOCUMENT = "Assign Approval level document {}"
    ACTION_RESET_TRAINING_COMPLETED = "Reset Training Completed {}"
    #T-Class licence
    ACTION_LINK_PARK = "Link park {} to application {}"
    ACTION_UNLINK_PARK = "Unlink park {} from application {}"
    ACTION_LINK_ACCESS = "Link access {} to park {}"
    ACTION_UNLINK_ACCESS = "Unlink access {} from park {}"
    ACTION_LINK_ACTIVITY = "Link activity {} to park {}"
    ACTION_UNLINK_ACTIVITY = "Unlink activity {} from park {}"
    ACTION_LINK_ACTIVITY_SECTION = "Link activity {} to section {} of trail {}"
    ACTION_UNLINK_ACTIVITY_SECTION = "Unlink activity {} from section {} of trail {}"
    ACTION_LINK_ACTIVITY_ZONE = "Link activity {} to zone {} of park {}"
    ACTION_UNLINK_ACTIVITY_ZONE = "Unlink activity {} from zone {} of park {}"
    ACTION_LINK_TRAIL = "Link trail {} to application {}"
    ACTION_UNLINK_TRAIL = "Unlink trail {} from application {}"
    ACTION_LINK_SECTION = "Link section {} to trail {}"
    ACTION_UNLINK_SECTION = "Unlink section {} from trail {}"
    ACTION_LINK_ZONE = "Link zone {} to park {}"
    ACTION_UNLINK_ZONE = "Unlink zone {} from park {}"
    SEND_TO_DISTRICTS = "Send Proposal {} to district assessors"
    # Assessors
    ACTION_SAVE_ASSESSMENT_ = "Save assessment {}"
    ACTION_CONCLUDE_ASSESSMENT_ = "Conclude assessment {}"
    ACTION_PROPOSED_APPROVAL = "Application {} has been proposed for approval"
    ACTION_PROPOSED_DECLINE = "Application {} has been proposed for decline"

    # Referrals
    ACTION_SEND_REFERRAL_TO = "Send referral {} for application {} to {}"
    ACTION_RESEND_REFERRAL_TO = "Resend referral {} for application {} to {}"
    ACTION_REMIND_REFERRAL = "Send reminder for referral {} for application {} to {}"
    ACTION_ENTER_REQUIREMENTS = "Enter Requirements for application {}"
    ACTION_BACK_TO_PROCESSING = "Back to processing for application {}"
    RECALL_REFERRAL = "Referral {} for application {} has been recalled"
    CONCLUDE_REFERRAL = "{}: Referral {} for application {} has been concluded by group {}"
    ACTION_REFERRAL_DOCUMENT = "Assign Referral document {}"
    ACTION_REFERRAL_ASSIGN_TO_ASSESSOR = "Assign Referral  {} of application {} to {} as the assessor"
    ACTION_REFERRAL_UNASSIGN_ASSESSOR = "Unassign assessor from Referral {} of application {}"
    
    #Approval
    ACTION_REISSUE_APPROVAL = "Reissue licence for application {}"
    ACTION_CANCEL_APPROVAL = "Cancel licence for application {}"
    ACTION_EXTEND_APPROVAL = "Extend licence"
    ACTION_SUSPEND_APPROVAL = "Suspend licence for application {}"
    ACTION_REINSTATE_APPROVAL = "Reinstate licence for application {}"
    ACTION_SURRENDER_APPROVAL = "Surrender licence for application {}"
    ACTION_RENEW_PROPOSAL = "Create Renewal application for application {}"
    ACTION_AMEND_PROPOSAL = "Create Amendment application for application {}"
    #Vehicle
    ACTION_CREATE_VEHICLE = "Create Vehicle {}"
    ACTION_EDIT_VEHICLE = "Edit Vehicle {}"
    #Vessel
    ACTION_CREATE_VESSEL = "Create Vessel {}"
    ACTION_EDIT_VESSEL= "Edit Vessel {}"
    ACTION_PUT_ONHOLD = "Put Application On-hold {}"
    ACTION_REMOVE_ONHOLD = "Remove Application On-hold {}"
    ACTION_WITH_QA_OFFICER = "Send Application QA Officer {}"
    ACTION_QA_OFFICER_COMPLETED = "QA Officer Assessment Completed {}"

    #Filming
    ACTION_CREATE_FILMING_PARK = "Create Filming Park {}"
    ACTION_EDIT_FILMING_PARK = "Edit Filming Park {}"
    ACTION_ASSIGN_TO_DISTRICT_APPROVER = "Assign District application {} of application {} to {} as the approver"
    ACTION_ASSIGN_TO_DISTRICT_ASSESSOR = "Assign District application {} of application {} to {} as the assessor"
    ACTION_UNASSIGN_DISTRICT_ASSESSOR = "Unassign assessor from District application {} of application {}"
    ACTION_UNASSIGN_DISTRICT_APPROVER = "Unassign approver from District application {} of application {}"
    ACTION_BACK_TO_PROCESSING_DISTRICT = "Back to processing for district application {} of application {}"
    ACTION_ENTER_REQUIREMENTS_DISTRICT = "Enter Requirements for district application {} of application {}"
    ACTION_DISTRICT_PROPOSED_APPROVAL = "District application {} of application {} has been proposed for approval"
    ACTION_DISTRICT_PROPOSED_DECLINE = "District application {} of application {} has been proposed for decline"
    ACTION_DISTRICT_DECLINE = "District application {} of application {} has been declined"
    ACTION_UPDATE_APPROVAL_DISTRICT = "Update Licence by district application {} of application {}"
    ACTION_ISSUE_APPROVAL_DISTRICT = "Issue Licence by district application {} of application {}"

    #Event
    ACTION_CREATE_EVENT_PARK= "Create Event Park {}"
    ACTION_EDIT_EVENT_PARK = "Edit Event Park {}"
    ACTION_CREATE_PRE_EVENT_PARK= "Create Pre Event Park {}"
    ACTION_EDIT_PRE_EVENT_PARK = "Edit Pre Event Park {}"
    ACTION_CREATE_ABSEILING_CLIMBING_ACTIVITY= "Create Abseiling Climbing Activity {}"
    ACTION_EDIT_ABSEILING_CLIMBING_ACTIVITY= "Edit Abseiling Climbing Activity {}"


    # monthly invoicing by cron
    ACTION_SEND_BPAY_INVOICE = "Send BPAY invoice {} for application {} to {}"
    ACTION_SEND_MONTHLY_INVOICE = "Send monthly invoice {} for application {} to {}"
    ACTION_SEND_MONTHLY_CONFIRMATION = "Send monthly confirmation for booking ID {}, for application {} to {}"
    ACTION_SEND_PAYMENT_DUE_NOTIFICATION = "Send monthly invoice/BPAY payment due notification {} for application {} to {}"

    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, proposal, action, user):
        return cls.objects.create(
            proposal=proposal,
            who=user,
            what=str(action)
        )

    proposal = models.ForeignKey(Proposal, related_name='action_logs')


class ReferralRecipientGroup(models.Model):
    #site = models.OneToOneField(Site, default='1')
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(EmailUser)

    def __str__(self):
        #return 'Referral Recipient Group'
        return self.name

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        #all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    @property
    def members_list(self):
            return list(self.members.all().values_list('email', flat=True))

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Referral group"
        verbose_name_plural = "Referral groups"

class QAOfficerGroup(models.Model):
    #site = models.OneToOneField(Site, default='1')
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(EmailUser)
    default = models.BooleanField(default=False)

    def __str__(self):
        return 'QA Officer Group'

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        #all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    @property
    def members_list(self):
            return list(self.members.all().values_list('email', flat=True))

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "QA group"
        verbose_name_plural = "QA group"


    def _clean(self):
        try:
            default = QAOfficerGroup.objects.get(default=True)
        except ProposalAssessorGroup.DoesNotExist:
            default = None

        if default and self.default:
            raise ValidationError('There can only be one default proposal QA Officer group')

    @property
    def current_proposals(self):
        assessable_states = ['with_qa_officer']
        return Proposal.objects.filter(processing_status__in=assessable_states)

#
#class ReferralRequestUserAction(UserAction):
#    ACTION_LODGE_REQUEST = "Lodge request {}"
#    ACTION_ASSIGN_TO = "Assign to {}"
#    ACTION_UNASSIGN = "Unassign"
#    ACTION_DECLINE_REQUEST = "Decline request"
#    # Assessors
#
#    ACTION_CONCLUDE_REQUEST = "Conclude request {}"
#
#    @classmethod
#    def log_action(cls, request, action, user):
#        return cls.objects.create(
#            request=request,
#            who=user,
#            what=str(action)
#        )
#
#    request = models.ForeignKey(ReferralRequest,related_name='action_logs')
#
#    class Meta:
#        app_label = 'commercialoperator'


#class Referral(models.Model):
class Referral(RevisionedMixin):
    SENT_CHOICES = (
        (1,'Sent From Assessor'),
        (2,'Sent From Referral')
    )
    PROCESSING_STATUS_CHOICES = (
                                 ('with_referral', 'Awaiting'),
                                 ('recalled', 'Recalled'),
                                 ('completed', 'Completed'),
                                 )
    lodged_on = models.DateTimeField(auto_now_add=True)
    proposal = models.ForeignKey(Proposal,related_name='referrals')
    sent_by = models.ForeignKey(EmailUser,related_name='commercialoperator_assessor_referrals')
    referral = models.ForeignKey(EmailUser,null=True,blank=True,related_name='commercialoperator_referalls')
    referral_group = models.ForeignKey(ReferralRecipientGroup,null=True,blank=True,related_name='commercialoperator_referral_groups')
    linked = models.BooleanField(default=False)
    sent_from = models.SmallIntegerField(choices=SENT_CHOICES,default=SENT_CHOICES[0][0])
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    text = models.TextField(blank=True) #Assessor text
    referral_text = models.TextField(blank=True)
    document = models.ForeignKey(ReferralDocument, blank=True, null=True, related_name='referral_document')
    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_referrals_assigned', on_delete=models.SET_NULL)


    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-lodged_on',)

    def __str__(self):
        return 'Application {} - Referral {}'.format(self.proposal.id,self.id)

    # Methods
    @property
    def application_type(self):
        return self.proposal.application_type.name

    @property
    def latest_referrals(self):
        return Referral.objects.filter(sent_by=self.referral, proposal=self.proposal)[:2]

    @property
    def referral_assessment(self):
        qs=self.assessment.filter(referral_assessment=True, referral_group=self.referral_group)
        if qs:
            return qs[0]
        else:
            return None


    @property
    def can_be_completed(self):
        return True
        #Referral cannot be completed until second level referral sent by referral has been completed/recalled
        qs=Referral.objects.filter(sent_by=self.referral, proposal=self.proposal, processing_status='with_referral')
        if qs:
            return False
        else:
            return True

    @property
    def allowed_assessors(self):
        group = self.referral_group
        return group.members.all() if group else []

    def can_process(self, user):
        if self.processing_status=='with_referral':
            group =  ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
            #user=request.user
            if group and group[0] in user.referralrecipientgroup_set.all():
                return True
            else:
                return False
        return False

    def assign_officer(self,request,officer):
        with transaction.atomic():
            try:
                if not self.can_process(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not self.can_process(officer):
                    raise ValidationError('The selected person is not authorised to be assigned to this Referral')
                if officer != self.assigned_officer:
                    self.assigned_officer = officer
                    self.save()
                    self.proposal.log_user_action(ProposalUserAction.ACTION_REFERRAL_ASSIGN_TO_ASSESSOR.format(self.id,self.proposal.id, '{}({})'.format(officer.get_full_name(),officer.email)),request)
            except:
                raise

    def unassign(self,request):
        with transaction.atomic():
            try:
                if not self.can_process(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.assigned_officer:
                    self.assigned_officer = None
                    self.save()
                    # Create a log entry for the proposal
                    self.proposal.log_user_action(ProposalUserAction.ACTION_REFERRAL_UNASSIGN_ASSESSOR.format(self.id, self.proposal.id),request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_REFERRAL_UNASSIGN_ASSESSOR.format(self.id, self.proposal.id),request)
            except:
                raise

    def recall(self,request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            self.processing_status = 'recalled'
            self.save()
            # TODO Log proposal action
            self.proposal.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)
            # TODO log organisation action
            applicant_field=getattr(self.proposal, self.proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)

    def remind(self,request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            # Create a log entry for the proposal
            #self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # Create a log entry for the organisation
            applicant_field=getattr(self.proposal, self.proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # send email
            recipients = self.referral_group.members_list
            send_referral_email_notification(self,recipients,request,reminder=True)

    def resend(self,request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            self.processing_status = 'with_referral'
            self.proposal.processing_status = 'with_referral'
            self.proposal.save()
            self.sent_from = 1
            self.save()
            # Create a log entry for the proposal
            #self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # Create a log entry for the organisation
            #self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            applicant_field=getattr(self.proposal, self.proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # send email
            recipients = self.referral_group.members_list
            send_referral_email_notification(self,recipients,request)

    def complete(self,request):
        with transaction.atomic():
            try:
                #if request.user != self.referral:
                group =  ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
                #print u.referralrecipientgroup_set.all()
                user=request.user
                if group and group[0] not in user.referralrecipientgroup_set.all():
                    raise exceptions.ReferralNotAuthorized()
                self.processing_status = 'completed'
                self.referral = request.user
                self.referral_text = request.user.get_full_name() + ': ' + request.data.get('referral_comment')
                self.add_referral_document(request)
                self.save()
                # TODO Log proposal action
                #self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
                self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
                # TODO log organisation action
                #self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
                applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
                send_referral_complete_email_notification(self,request)
            except:
                raise

    def add_referral_document(self, request):
        with transaction.atomic():
            try:
                #if request.data.has_key('referral_document'):
                if 'referral_document' in request.data:
                    referral_document = request.data['referral_document']
                    if referral_document != 'null':
                        try:
                            document = self.referral_documents.get(input_name=str(referral_document))
                        except ReferralDocument.DoesNotExist:
                            document = self.referral_documents.get_or_create(input_name=str(referral_document), name=str(referral_document))[0]
                        document.name = str(referral_document)
                        # commenting out below tow lines - we want to retain all past attachments - reversion can use them
                        #if document._file and os.path.isfile(document._file.path):
                        #    os.remove(document._file.path)
                        document._file = referral_document
                        document.save()
                        d=ReferralDocument.objects.get(id=document.id)
                        #self.referral_document = d
                        self.document = d
                        comment = 'Referral Document Added: {}'.format(document.name)
                    else:
                        #self.referral_document = None
                        self.document = None
                        #comment = 'Referral Document Deleted: {}'.format(request.data['referral_document_name'])
                        comment = 'Referral Document Deleted'
                    #self.save()
                    self.save(version_comment=comment) # to allow revision to be added to reversion history
                    self.proposal.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
                return self
            except:
                raise


    def send_referral(self,request,referral_email,referral_text):
        with transaction.atomic():
            try:
                if self.proposal.processing_status == 'with_referral':
                    if request.user != self.referral:
                        raise exceptions.ReferralNotAuthorized()
                    if self.sent_from != 1:
                        raise exceptions.ReferralCanNotSend()
                    self.proposal.processing_status = 'with_referral'
                    self.proposal.save()
                    referral = None
                    # Check if the user is in ledger
                    try:
                        user = EmailUser.objects.get(email__icontains=referral_email.lower())
                    except EmailUser.DoesNotExist:
                        # Validate if it is a deparment user
                        department_user = get_department_user(referral_email)
                        if not department_user:
                            raise ValidationError('The user you want to send the referral to is not a member of the department')
                        # Check if the user is in ledger or create

                        user,created = EmailUser.objects.get_or_create(email=department_user['email'].lower())
                        if created:
                            user.first_name = department_user['given_name']
                            user.last_name = department_user['surname']
                            user.save()
                    qs=Referral.objects.filter(sent_by=user, proposal=self.proposal)
                    if qs:
                        raise ValidationError('You cannot send referral to this user')
                    try:
                        Referral.objects.get(referral=user,proposal=self.proposal)
                        raise ValidationError('A referral has already been sent to this user')
                    except Referral.DoesNotExist:
                        # Create Referral
                        referral = Referral.objects.create(
                            proposal = self.proposal,
                            referral=user,
                            sent_by=request.user,
                            sent_from=2,
                            text=referral_text
                        )
                        # try:
                        #     referral_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        # except ProposalAssessment.DoesNotExist:
                        #     referral_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        #     checklist=ChecklistQuestion.objects.filter(list_type='referral_list', obsolete=False)
                        #     for chk in checklist:
                        #         try:
                        #             chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=referral_assessment)
                        #         except ProposalAssessmentAnswer.DoesNotExist:
                        #             chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=referral_assessment)
                    # Create a log entry for the proposal
                    self.proposal.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    # send email
                    recipients = self.email_group.members_list
                    send_referral_email_notification(referral,recipients,request)
                else:
                    raise exceptions.ProposalReferralCannotBeSent()
            except:
                raise


    # Properties
    @property
    def region(self):
        return self.proposal.region

    @property
    def activity(self):
        return self.proposal.activity

    @property
    def title(self):
        return self.proposal.title

    # @property
    # def applicant(self):
    #     return self.proposal.applicant.name

    @property
    def applicant(self):
        return self.proposal.applicant

    @property
    def can_be_processed(self):
        return self.processing_status == 'with_referral'

    def can_assess_referral(self,user):
        return self.processing_status == 'with_referral'

class ProposalRequirement(OrderedModel):
    RECURRENCE_PATTERNS = [(1, 'Weekly'), (2, 'Monthly'), (3, 'Yearly')]
    standard_requirement = models.ForeignKey(ProposalStandardRequirement,null=True,blank=True)
    free_requirement = models.TextField(null=True,blank=True)
    standard = models.BooleanField(default=True)
    proposal = models.ForeignKey(Proposal,related_name='requirements')
    due_date = models.DateField(null=True,blank=True)
    recurrence = models.BooleanField(default=False)
    recurrence_pattern = models.SmallIntegerField(choices=RECURRENCE_PATTERNS,default=1)
    recurrence_schedule = models.IntegerField(null=True,blank=True)
    copied_from = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    copied_for_renewal = models.BooleanField(default=False)
    require_due_date = models.BooleanField(default=False)
    #To determine if requirement has been added by referral and the group of referral who added it
    #Null if added by an assessor
    referral_group = models.ForeignKey(ReferralRecipientGroup,null=True,blank=True,related_name='requirement_referral_groups')
    #order = models.IntegerField(default=1)
    #application_type = models.ForeignKey(ApplicationType, null=True, blank=True)
    #fee_invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')
    #To determing requirements related to district Proposal
    district_proposal = models.ForeignKey('DistrictProposal',null=True,blank=True,related_name='district_proposal_requirements')
    district = models.ForeignKey(District, related_name='district_requirements', null=True,blank=True)
    notification_only = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'


    @property
    def requirement(self):
        return self.standard_requirement.text if self.standard else self.free_requirement

    def can_referral_edit(self,user):
        if self.proposal.processing_status=='with_referral':
            if self.referral_group:
                group =  ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
                #user=request.user
                if group and group[0] in user.referralrecipientgroup_set.all():
                    return True
                else:
                    return False
        return False

    def can_district_assessor_edit(self,user):
        allowed_status=['with_district_assessor', 'partially_approved', 'partially_declined']
        if self.district_proposal and self.district_proposal.processing_status=='with_assessor_requirements' and self.proposal.processing_status in allowed_status:
            if self.district_proposal.can_process_requirements(user):
                return True
        return False

    def add_documents(self, request):
        with transaction.atomic():
            try:
                # save the files
                data = json.loads(request.data.get('data'))
                if not data.get('update'):
                    documents_qs = self.requirement_documents.filter(input_name='requirement_doc', visible=True)
                    documents_qs.delete()
                for idx in range(data['num_files']):
                    _file = request.data.get('file-'+str(idx))
                    document = self.requirement_documents.create(_file=_file, name=_file.name)
                    document.input_name = data['input_name']
                    document.can_delete = True
                    document.save()
                # end save documents
                self.save()
            except:
                raise
        return



@python_2_unicode_compatible
#class ProposalStandardRequirement(models.Model):
class ChecklistQuestion(RevisionedMixin):
    TYPE_CHOICES = (
        ('assessor_list','Assessor Checklist'),
        ('referral_list','Referral Checklist')
    )
    ANSWER_TYPE_CHOICES = (
        ('yes_no','Yes/No type'),
        ('free_text','Free text type')
    )
    text = models.TextField()
    list_type = models.CharField('Checklist type', max_length=30, choices=TYPE_CHOICES,
                                         default=TYPE_CHOICES[0][0])
    answer_type = models.CharField('Answer type', max_length=30, choices=ANSWER_TYPE_CHOICES,
                                         default=ANSWER_TYPE_CHOICES[0][0])

    #correct_answer= models.BooleanField(default=False)
    application_type = models.ForeignKey(ApplicationType,blank=True, null=True)
    obsolete = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.text

    class Meta:
        app_label = 'commercialoperator'


class ProposalAssessment(RevisionedMixin):
    proposal=models.ForeignKey(Proposal, related_name='assessment')
    completed = models.BooleanField(default=False)
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='proposal_assessment')
    referral_assessment=models.BooleanField(default=False)
    referral_group = models.ForeignKey(ReferralRecipientGroup,null=True,blank=True,related_name='referral_assessment')
    referral=models.ForeignKey(Referral, related_name='assessment',blank=True, null=True )
    # def __str__(self):
    #     return self.proposal

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal', 'referral_group',)

    @property
    def checklist(self):
        return self.answers.all()

    @property
    def referral_group_name(self):
        if self.referral_group:
            return self.referral_group.name
        else:
            return ''


class ProposalAssessmentAnswer(RevisionedMixin):
    question=models.ForeignKey(ChecklistQuestion, related_name='answers')
    answer = models.NullBooleanField()
    assessment=models.ForeignKey(ProposalAssessment, related_name='answers', null=True, blank=True)
    text_answer= models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.question.text

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Assessment answer"
        verbose_name_plural = "Assessment answers"


class QAOfficerReferral(RevisionedMixin):
    SENT_CHOICES = (
        (1,'Sent From Assessor'),
        (2,'Sent From Referral')
    )
    PROCESSING_STATUS_CHOICES = (
                                 ('with_qaofficer', 'Awaiting'),
                                 ('recalled', 'Recalled'),
                                 ('completed', 'Completed'),
                                 )
    lodged_on = models.DateTimeField(auto_now_add=True)
    proposal = models.ForeignKey(Proposal,related_name='qaofficer_referrals')
    sent_by = models.ForeignKey(EmailUser,related_name='assessor_qaofficer_referrals')
    qaofficer = models.ForeignKey(EmailUser, null=True, blank=True, related_name='qaofficers')
    qaofficer_group = models.ForeignKey(QAOfficerGroup,null=True,blank=True,related_name='qaofficer_groups')
    linked = models.BooleanField(default=False)
    sent_from = models.SmallIntegerField(choices=SENT_CHOICES,default=SENT_CHOICES[0][0])
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    text = models.TextField(blank=True) #Assessor text
    qaofficer_text = models.TextField(blank=True)
    document = models.ForeignKey(QAOfficerDocument, blank=True, null=True, related_name='qaofficer_referral_document')


    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-lodged_on',)

    def __str__(self):
        return 'Application {} - QA Officer referral {}'.format(self.proposal.id,self.id)

    # Methods
    @property
    def latest_qaofficer_referrals(self):
        return QAOfficer.objects.filter(sent_by=self.qaofficer, proposal=self.proposal)[:2]

#    @property
#    def can_be_completed(self):
#        #Referral cannot be completed until second level referral sent by referral has been completed/recalled
#        qs=Referral.objects.filter(sent_by=self.referral, proposal=self.proposal, processing_status='with_referral')
#        if qs:
#            return False
#        else:
#            return True
#
#    def recall(self,request):
#        with transaction.atomic():
#            if not self.proposal.can_assess(request.user):
#                raise exceptions.ProposalNotAuthorized()
#            self.processing_status = 'recalled'
#            self.save()
#            # TODO Log proposal action
#            self.proposal.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)
#            # TODO log organisation action
#            self.proposal.applicant.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)
#
#    def remind(self,request):
#        with transaction.atomic():
#            if not self.proposal.can_assess(request.user):
#                raise exceptions.ProposalNotAuthorized()
#            # Create a log entry for the proposal
#            #self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#            self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # Create a log entry for the organisation
#            self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # send email
#            recipients = self.referral_group.members_list
#            send_referral_email_notification(self,recipients,request,reminder=True)
#
#    def resend(self,request):
#        with transaction.atomic():
#            if not self.proposal.can_assess(request.user):
#                raise exceptions.ProposalNotAuthorized()
#            self.processing_status = 'with_referral'
#            self.proposal.processing_status = 'with_referral'
#            self.proposal.save()
#            self.sent_from = 1
#            self.save()
#            # Create a log entry for the proposal
#            #self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#            self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # Create a log entry for the organisation
#            #self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#            self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # send email
#            recipients = self.referral_group.members_list
#            send_referral_email_notification(self,recipients,request)
#
#    def complete(self,request):
#        with transaction.atomic():
#            try:
#                #if request.user != self.referral:
#                group =  ReferralRecipientGroup.objects.filter(name=self.referral_group)
#                if group and group[0] in u.referralrecipientgroup_set.all():
#                    raise exceptions.ReferralNotAuthorized()
#                self.processing_status = 'completed'
#                self.referral = request.user
#                self.referral_text = request.user.get_full_name() + ': ' + request.data.get('referral_comment')
#                self.add_referral_document(request)
#                self.save()
#                # TODO Log proposal action
#                #self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#                self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#                # TODO log organisation action
#                #self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#                self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#                send_referral_complete_email_notification(self,request)
#            except:
#                raise
#
#    def add_referral_document(self, request):
#        with transaction.atomic():
#            try:
#                referral_document = request.data['referral_document']
#                if referral_document != 'null':
#                    try:
#                        document = self.referral_documents.get(input_name=str(referral_document))
#                    except ReferralDocument.DoesNotExist:
#                        document = self.referral_documents.get_or_create(input_name=str(referral_document), name=str(referral_document))[0]
#                    document.name = str(referral_document)
#                    # commenting out below tow lines - we want to retain all past attachments - reversion can use them
#                    #if document._file and os.path.isfile(document._file.path):
#                    #    os.remove(document._file.path)
#                    document._file = referral_document
#                    document.save()
#                    d=ReferralDocument.objects.get(id=document.id)
#                    self.referral_document = d
#                    comment = 'Referral Document Added: {}'.format(document.name)
#                else:
#                    self.referral_document = None
#                    comment = 'Referral Document Deleted: {}'.format(request.data['referral_document_name'])
#                #self.save()
#                self.save(version_comment=comment) # to allow revision to be added to reversion history
#                self.proposal.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
#                # Create a log entry for the organisation
#                self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
#                return self
#            except:
#                raise
#
#
#    def send_referral(self,request,referral_email,referral_text):
#        with transaction.atomic():
#            try:
#                if self.proposal.processing_status == 'with_referral':
#                    if request.user != self.referral:
#                        raise exceptions.ReferralNotAuthorized()
#                    if self.sent_from != 1:
#                        raise exceptions.ReferralCanNotSend()
#                    self.proposal.processing_status = 'with_referral'
#                    self.proposal.save()
#                    referral = None
#                    # Check if the user is in ledger
#                    try:
#                        user = EmailUser.objects.get(email__icontains=referral_email)
#                    except EmailUser.DoesNotExist:
#                        # Validate if it is a deparment user
#                        department_user = get_department_user(referral_email)
#                        if not department_user:
#                            raise ValidationError('The user you want to send the referral to is not a member of the department')
#                        # Check if the user is in ledger or create
#
#                        user,created = EmailUser.objects.get_or_create(email=department_user['email'].lower())
#                        if created:
#                            user.first_name = department_user['given_name']
#                            user.last_name = department_user['surname']
#                            user.save()
#                    qs=Referral.objects.filter(sent_by=user, proposal=self.proposal)
#                    if qs:
#                        raise ValidationError('You cannot send referral to this user')
#                    try:
#                        Referral.objects.get(referral=user,proposal=self.proposal)
#                        raise ValidationError('A referral has already been sent to this user')
#                    except Referral.DoesNotExist:
#                        # Create Referral
#                        referral = Referral.objects.create(
#                            proposal = self.proposal,
#                            referral=user,
#                            sent_by=request.user,
#                            sent_from=2,
#                            text=referral_text
#                        )
#                    # Create a log entry for the proposal
#                    self.proposal.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
#                    # Create a log entry for the organisation
#                    self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
#                    # send email
#                    recipients = self.email_group.members_list
#                    send_referral_email_notification(referral,recipients,request)
#                else:
#                    raise exceptions.ProposalReferralCannotBeSent()
#            except:
#                raise


    # Properties
    @property
    def region(self):
        return self.proposal.region

    @property
    def activity(self):
        return self.proposal.activity

    @property
    def title(self):
        return self.proposal.title

    @property
    def applicant(self):
        return self.proposal.applicant.name

    @property
    def can_be_processed(self):
        return self.processing_status == 'with_qa_officer'

    def can_asses(self):
        return self.can_be_processed and self.proposal.is_qa_officer()


@receiver(pre_delete, sender=Proposal)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()

def clone_proposal_with_status_reset(proposal, copy_requirement_documents=False):
    """
    To Test:
         from commercialoperator.components.proposals.models import clone_proposal_with_status_reset
         p=Proposal.objects.get(id=57)
         p0=clone_proposal_with_status_reset(p)
    """
    with transaction.atomic():
        try:
            original_proposal = copy.deepcopy(proposal)
            #proposal = duplicate_object(proposal) # clone object and related objects
            if original_proposal.application_type.name==ApplicationType.TCLASS:
                proposal=duplicate_tclass(proposal)
            if original_proposal.application_type.name==ApplicationType.FILMING:
                proposal=duplicate_filming(proposal)
            if original_proposal.application_type.name==ApplicationType.EVENT:
                proposal=duplicate_event(proposal)
            # manually duplicate the comms logs -- hck, not hndled by duplicate object (maybe due to inheritance?)
            # proposal.comms_logs.create(text='cloning proposal reset (original proposal {}, new proposal {})'.format(original_proposal.id, proposal.id))
            # for comms_log in proposal.comms_logs.all():
            #     comms_log.id=None
            #     comms_log.communicationslogentry_ptr_id=None
            #     comms_log.proposal_id=original_proposal.id
            #     comms_log.save()

            # reset some properties
            proposal.customer_status = 'draft'
            proposal.processing_status = 'draft'
            proposal.assessor_data = None
            proposal.comment_data = None

            proposal.lodgement_number = ''
            proposal.lodgement_sequence = 0
            proposal.lodgement_date = None

            proposal.assigned_officer = None
            proposal.assigned_approver = None

            proposal.approval = None
            proposal.approval_level_document = None
            proposal.migrated=False

            proposal.save(no_revision=True)

            #clone_documents(proposal, original_proposal, media_prefix='media')
            if copy_requirement_documents:
                _clone_requirement_documents(proposal, original_proposal, media_prefix='media')
            else:
                _clone_documents(proposal, original_proposal, media_prefix='media')
            return proposal
        except:
            raise

def clone_documents(proposal, original_proposal, media_prefix):
    for proposal_document in ProposalDocument.objects.filter(proposal_id=proposal.id):
        proposal_document._file.name = u'{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_document.name)
        proposal_document.can_delete = True
        proposal_document.save()

    for proposal_required_document in ProposalRequiredDocument.objects.filter(proposal_id=proposal.id):
        proposal_required_document._file.name = u'{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_required_document.name)
        proposal_required_document.can_delete = True
        proposal_required_document.save()

    for referral in proposal.referrals.all():
        for referral_document in ReferralDocument.objects.filter(referral=referral):
            referral_document._file.name = u'{}/proposals/{}/referral/{}'.format(settings.MEDIA_APP_DIR, proposal.id, referral_document.name)
            referral_document.can_delete = True
            referral_document.save()

    for qa_officer_document in QAOfficerDocument.objects.filter(proposal_id=proposal.id):
        qa_officer_document._file.name = u'{}/proposals/{}/qaofficer/{}'.format(settings.MEDIA_APP_DIR, proposal.id, qa_officer_document.name)
        qa_officer_document.can_delete = True
        qa_officer_document.save()

    for onhold_document in OnHoldDocument.objects.filter(proposal_id=proposal.id):
        onhold_document._file.name = u'{}/proposals/{}/on_hold/{}'.format(settings.MEDIA_APP_DIR, proposal.id, onhold_document.name)
        onhold_document.can_delete = True
        onhold_document.save()

    for requirement in proposal.requirements.all():
        for requirement_document in RequirementDocument.objects.filter(requirement=requirement):
            requirement_document._file.name = u'{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, requirement_document.name)
            requirement_document.can_delete = True
            requirement_document.save()

    for log_entry_document in ProposalLogDocument.objects.filter(log_entry__proposal_id=proposal.id):
        log_entry_document._file.name = log_entry_document._file.name.replace(str(original_proposal.id), str(proposal.id))
        log_entry_document.can_delete = True
        log_entry_document.save()

    # copy documents on file system and reset can_delete flag
    media_dir = '{}/{}'.format(media_prefix, settings.MEDIA_APP_DIR)
    subprocess.call('cp -pr {0}/proposals/{1} {0}/proposals/{2}'.format(media_dir, original_proposal.id, proposal.id), shell=True)


def _clone_documents(proposal, original_proposal, media_prefix):
    for proposal_document in ProposalDocument.objects.filter(proposal=original_proposal.id):
        proposal_document.proposal = proposal
        proposal_document.id = None
        proposal_document._file.name = u'{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_document.name)
        proposal_document.can_delete = True
        proposal_document.save()

    for proposal_required_document in ProposalRequiredDocument.objects.filter(proposal=original_proposal.id):
        proposal_required_document.proposal = proposal
        proposal_required_document.id = None
        proposal_required_document._file.name = u'{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_required_document.name)
        proposal_required_document.can_delete = True
        proposal_required_document.save()

    # copy documents on file system and reset can_delete flag
    media_dir = '{}/{}'.format(media_prefix, settings.MEDIA_APP_DIR)
    subprocess.call('cp -pr {0}/proposals/{1} {0}/proposals/{2}'.format(media_dir, original_proposal.id, proposal.id), shell=True)

def _clone_requirement_documents(proposal, original_proposal, media_prefix):
    for proposal_required_document in ProposalRequiredDocument.objects.filter(proposal=original_proposal.id):
        proposal_required_document.proposal = proposal
        proposal_required_document.id = None
        proposal_required_document._file.name = u'{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_required_document.name)
        proposal_required_document.can_delete = True
        proposal_required_document.save()

    # copy documents on file system and reset can_delete flag
    media_dir = '{}/{}'.format(media_prefix, settings.MEDIA_APP_DIR)
    subprocess.call('cp -pr {0}/proposals/{1} {0}/proposals/{2}'.format(media_dir, original_proposal.id, proposal.id), shell=True)

def duplicate_object(self):
    """
    Duplicate a model instance, making copies of all foreign keys pointing to it.
    There are 3 steps that need to occur in order:

        1.  Enumerate the related child objects and m2m relations, saving in lists/dicts
        2.  Copy the parent object per django docs (doesn't copy relations)
        3a. Copy the child objects, relating to the copied parent object
        3b. Re-create the m2m relations on the copied parent object

    """
    related_objects_to_copy = []
    relations_to_set = {}
    # Iterate through all the fields in the parent object looking for related fields
    for field in self._meta.get_fields():
        if field.name in ['proposal', 'approval']:
            print('Continuing ...')
            pass
        elif field.one_to_many:
            # One to many fields are backward relationships where many child objects are related to the
            # parent (i.e. SelectedPhrases). Enumerate them and save a list so we can copy them after
            # duplicating our parent object.
            print('Found a one-to-many field: {}'.format(field.name))

            # 'field' is a ManyToOneRel which is not iterable, we need to get the object attribute itself
            related_object_manager = getattr(self, field.name)
            related_objects = list(related_object_manager.all())
            if related_objects:
                print(' - {len(related_objects)} related objects to copy')
                related_objects_to_copy += related_objects

        elif field.many_to_one:
            # In testing so far, these relationships are preserved when the parent object is copied,
            # so they don't need to be copied separately.
            print('Found a many-to-one field: {}'.format(field.name))

        elif field.many_to_many:
            # Many to many fields are relationships where many parent objects can be related to many
            # child objects. Because of this the child objects don't need to be copied when we copy
            # the parent, we just need to re-create the relationship to them on the copied parent.
            print('Found a many-to-many field: {}'.format(field.name))
            related_object_manager = getattr(self, field.name)
            relations = list(related_object_manager.all())
            if relations:
                print(' - {} relations to set'.format(len(relations)))
                relations_to_set[field.name] = relations

    # Duplicate the parent object
    self.pk = None
    self.lodgement_number = ''
    self.save()
    print('Copied parent object {}'.format(str(self)))

    # Copy the one-to-many child objects and relate them to the copied parent
    for related_object in related_objects_to_copy:
        # Iterate through the fields in the related object to find the one that relates to the
        # parent model (I feel like there might be an easier way to get at this).
        for related_object_field in related_object._meta.fields:
            if related_object_field.related_model == self.__class__:
                # If the related_model on this field matches the parent object's class, perform the
                # copy of the child object and set this field to the parent object, creating the
                # new child -> parent relationship.
                related_object.pk = None
                #if related_object_field.name=='approvals':
                #    related_object.lodgement_number = None
                ##if isinstance(related_object, Approval):
                ##    related_object.lodgement_number = ''

                setattr(related_object, related_object_field.name, self)
                print(related_object_field)
                try:
                    related_object.save()
                except Exception as e:
                    logger.warn(e)

                text = str(related_object)
                text = (text[:40] + '..') if len(text) > 40 else text
                print('|- Copied child object {}'.format(text))

    # Set the many-to-many relations on the copied parent
    for field_name, relations in relations_to_set.items():
        # Get the field by name and set the relations, creating the new relationships
        field = getattr(self, field_name)
        field.set(relations)
        text_relations = []
        for relation in relations:
            text_relations.append(str(relation))
        print('|- Set {} many-to-many relations on {} {}'.format(len(relations), field_name, text_relations))

    return self

def duplicate_tclass(p):
    original_proposal=copy.deepcopy(p)
    p.id=None
    p.save()
    print ('new proposal',p)

    for park in original_proposal.parks.all():

        original_park=copy.deepcopy(park)
        park.id=None
        park.proposal=p
        park.save()
        print('new park', park,park.id, original_park, original_park.id, park.proposal)
        for activity in original_park.activities.all():
            activity.id=None
            activity.proposal_park=park
            activity.save()
            print('new activity', activity, activity.id, park)
            #new_activities_list.append(new_ac)
        for access in original_park.access_types.all():
            access.id=None
            access.proposal_park=park
            access.save()
            print('new access', access, park)
            #new_access_list.append(new_ac)
        for zone in original_park.zones.all():
            original_zone=copy.deepcopy(zone)
            zone.id=None
            zone.proposal_park=park
            zone.save()
            print('new zone',zone)
            for acz in original_zone.park_activities.all():
                acz.id=None
                acz.park_zone=zone
                acz.save()
                print('new zone activity', acz, zone)

    for trail in original_proposal.trails.all():
        original_trail=copy.deepcopy(trail)
        trail.id=None
        trail.proposal=p
        trail.save()

        for section in original_trail.sections.all():
            original_section=copy.deepcopy(section)
            section.id=None
            section.proposal_trail=trail
            section.save()
            print('new section', section, trail)
            for act in original_section.trail_activities.all():
                act.id=None
                act.trail_section=section
                act.save()
                print('new trail activity', act, section)

    try:
        other_details=ProposalOtherDetails.objects.get(proposal=original_proposal)
        new_accreditations=[]
        print('proposal:',original_proposal, original_proposal.other_details.id, other_details.id)
        print('accreditations', other_details.accreditations.all())
        for acc in other_details.accreditations.all():
            acc.id=None
            acc.save()
            new_accreditations.append(acc)
        other_details.id=None
        other_details.proposal=p
        other_details.save()
        for new_acc in new_accreditations:
            new_acc.proposal_other_details=other_details
            new_acc.save()
    except ProposalOtherDetails.DoesNotExist:
        other_details=ProposalOtherDetails.objects.create(proposal=p)

    for vehicle in original_proposal.vehicles.all():
        vehicle.id=None
        vehicle.proposal=p
        vehicle.save()
    for vessel in original_proposal.vessels.all():
        vessel.id=None
        vessel.proposal=p
        vessel.save()

    return p

def duplicate_filming(p):
    original_proposal=copy.deepcopy(p)
    p.id=None
    p.save()
    print ('new proposal',p)

    for park in original_proposal.filming_parks.all():

        original_park=copy.deepcopy(park)
        park.id=None
        park.proposal=p
        park.save()
        for park_document in FilmingParkDocument.objects.filter(filming_park=original_park.id):
            park_document.filming_park = park
            park_document.id = None
            park_document._file.name = u'{}/proposals/{}/filming_park_documents/{}'.format(settings.MEDIA_APP_DIR, p.id, park_document.name)
            park_document.can_delete = True
            park_document.save()

    try:
        other_details=ProposalFilmingOtherDetails.objects.get(proposal=original_proposal)
        other_details.id=None
        other_details.proposal=p
        other_details.save()
        #print('proposal:',original_proposal, original_proposal.filming_other_details.id, other_details.id)
    except ProposalFilmingOtherDetails.DoesNotExist:
        other_details=ProposalFilmingOtherDetails.objects.create(proposal=p)

    try:
        filming_activity=ProposalFilmingActivity.objects.get(proposal=original_proposal)
        filming_activity.id=None
        filming_activity.proposal=p
        filming_activity.save()
    except ProposalFilmingActivity.DoesNotExist:
        filming_activity=ProposalFilmingActivity.objects.create(proposal=p)

    try:
        filming_access=ProposalFilmingAccess.objects.get(proposal=original_proposal)
        filming_access.id=None
        filming_access.proposal=p
        filming_access.save()
    except ProposalFilmingAccess.DoesNotExist:
        filming_access=ProposalFilmingAccess.objects.create(proposal=p)

    try:
        filming_equipment=ProposalFilmingEquipment.objects.get(proposal=original_proposal)
        filming_equipment.id=None
        filming_equipment.proposal=p
        filming_equipment.save()
    except ProposalFilmingEquipment.DoesNotExist:
        filming_equipment=ProposalFilmingEquipment.objects.create(proposal=p)

    # for trail in original_proposal.trails.all():
    #     original_trail=copy.deepcopy(trail)
    #     trail.id=None
    #     trail.proposal=p
    #     trail.save()

    #     for section in original_trail.sections.all():
    #         original_section=copy.deepcopy(section)
    #         section.id=None
    #         section.proposal_trail=trail
    #         section.save()
    #         print('new section', section, trail)
    #         for act in original_section.trail_activities.all():
    #             act.id=None
    #             act.trail_section=section
    #             act.save()
    #             print('new trail activity', act, section)

    for vehicle in original_proposal.vehicles.all():
        vehicle.id=None
        vehicle.proposal=p
        vehicle.save()
    for vessel in original_proposal.vessels.all():
        vessel.id=None
        vessel.proposal=p
        vessel.save()

    return p

def duplicate_event(p):
    original_proposal=copy.deepcopy(p)
    p.id=None
    p.save()
    print ('new proposal',p)

    for park in original_proposal.events_parks.all():

        original_park=copy.deepcopy(park)
        park.id=None
        park.proposal=p
        park.save()
        #copy manytomany field activities_assessor values.
        if original_park.activities_assessor:
            park.activities_assessor.set(original_park.activities_assessor.all())
            park.save()
        for park_document in EventsParkDocument.objects.filter(events_park=original_park.id):
            park_document.events_park = park
            park_document.id = None
            park_document._file.name = u'{}/proposals/{}/events_park_documents/{}'.format(settings.MEDIA_APP_DIR, p.id, park_document.name)
            park_document.can_delete = True
            park_document.save()

    for park in original_proposal.pre_event_parks.all():

        original_park=copy.deepcopy(park)
        park.id=None
        park.proposal=p
        park.save()
        for park_document in PreEventsParkDocument.objects.filter(pre_event_park=original_park.id):
            park_document.pre_event_park = park
            park_document.id = None
            park_document._file.name = u'{}/proposals/{}/pre_event_park_documents/{}'.format(settings.MEDIA_APP_DIR, p.id, park_document.name)
            park_document.can_delete = True
            park_document.save()

    try:
        other_details=ProposalEventOtherDetails.objects.get(proposal=original_proposal)
        other_details.id=None
        other_details.proposal=p
        other_details.save()
        #print('proposal:',original_proposal, original_proposal.filming_other_details.id, other_details.id)
    except ProposalEventOtherDetails.DoesNotExist:
        other_details=ProposalEventOtherDetails.objects.create(proposal=p)

    try:
        event_activity=ProposalEventActivities.objects.get(proposal=original_proposal)
        new_abseiling=[]
        for acc in event_activity.abseiling_climbing_activity_data.all():
            acc.id=None
            acc.save()
            new_abseiling.append(acc)

        event_activity.id=None
        event_activity.proposal=p
        event_activity.save()
        for new_acc in new_abseiling:
            new_acc.event_activities=event_activity
            new_acc.proposal=p
            new_acc.save()
    except ProposalEventActivities.DoesNotExist:
        event_activity=ProposalEventActivities.objects.create(proposal=p)

    try:
        event_vehicle_vessel=ProposalEventVehiclesVessels.objects.get(proposal=original_proposal)
        event_vehicle_vessel.id=None
        event_vehicle_vessel.proposal=p
        event_vehicle_vessel.save()
    except ProposalEventVehiclesVessels.DoesNotExist:
        event_vehicle_vessel=ProposalEventVehiclesVessels.objects.create(proposal=p)

    try:
        event_management=ProposalEventManagement.objects.get(proposal=original_proposal)
        event_management.id=None
        event_management.proposal=p
        event_management.save()
    except ProposalEventManagement.DoesNotExist:
        event_management=ProposalEventManagement.objects.create(proposal=p)

    for vehicle in original_proposal.vehicles.all():
        vehicle.id=None
        vehicle.proposal=p
        vehicle.save()
    for vessel in original_proposal.vessels.all():
        vessel.id=None
        vessel.proposal=p
        vessel.save()

    for trail in original_proposal.events_trails.all():
        original_trail=copy.deepcopy(trail)
        trail.id=None
        trail.proposal=p
        trail.save()
        if original_trail.activities_assessor:
            trail.activities_assessor.set(original_trail.activities_assessor.all())
            trail.save()

        # for section in original_trail.sections.all():
        #     original_section=copy.deepcopy(section)
        #     section.id=None
        #     section.proposal_trail=trail
        #     section.save()
        #     print('new section', section, trail)
        #     for act in original_section.trail_activities.all():
        #         act.id=None
        #         act.trail_section=section
        #         act.save()
        #         print('new trail activity', act, section)


    return p

def searchKeyWords(searchWords, searchProposal, searchApproval, searchCompliance, is_internal= True):
    from commercialoperator.utils import search, search_approval, search_compliance, getChoiceFieldRegex
    from commercialoperator.components.approvals.models import Approval
    from commercialoperator.components.compliances.models import Compliance
    qs = []
    application_types=[ApplicationType.TCLASS, ApplicationType.EVENT, ApplicationType.FILMING]
    if is_internal:
        #proposal_list = Proposal.objects.filter(application_type__name='T Class').exclude(processing_status__in=['discarded','draft'])
        proposal_list = Proposal.objects.filter(application_type__name__in=application_types).exclude(processing_status__in=['discarded','draft'])
        approval_list = Approval.objects.all().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
        compliance_list = Compliance.objects.all()
    if searchWords:
        #convert the search words in to two regex values - one for text one for json values
        search_words_regex = "(?:"+'|'.join(searchWords)+")"
        filter_regex = ".*\".*\":\s\"(\\\\\"|[^\"])*"+search_words_regex+"(\\\\\"|[^\"])*\".*"

        #three searchable fields use choices: accreditation, film_type, and film_purpose
        #so we must convert the search phrase in to the search short word where applicable
        #accreditation
        accreditation_words = getChoiceFieldRegex(searchWords,ProposalAccreditation.ACCREDITATION_TYPE_CHOICES)
        #film type 
        film_type_words = getChoiceFieldRegex(searchWords,ProposalFilmingActivity.FILM_TYPE_CHOICES)
        #film purpose
        film_purpose_words = getChoiceFieldRegex(searchWords,ProposalFilmingActivity.PURPOSE_CHOICES)

        #one particular search value is quite nested - it is faster to run these queries instead of the reverse
        activities = Activity.objects.filter(name__iregex=search_words_regex)
        pts_activities = ProposalTrailSectionActivity.objects.filter(activity__in=activities)
        sections = ProposalTrailSection.objects.filter(trail_activities__in=pts_activities)
        trails = ProposalTrail.objects.filter(sections__in=sections)

        if searchProposal:
            #proposal_list = proposal_list.filter(data__iregex=filter_regex)
            #this below query run is equivalent to the search_words property, except that it retrieves the pertaining proposal records
            #there is a lot here but a lot of time is saved not having to iterate every record every time
            proposal_list = proposal_list.filter(
            (Q(application_type__name=ApplicationType.TCLASS) & 
                (Q(parks__park__name__iregex=search_words_regex))|
                (Q(parks__activities__activity__in=activities))|
                (Q(parks__zones__park_activities__activity__in=activities))|
                (Q(trails__trail__name__iregex=search_words_regex))|
                (Q(vehicles__rego__iregex=search_words_regex))|
                (Q(vessels__spv_no__iregex=search_words_regex))|
                (Q(other_details__other_comments__iregex=search_words_regex))|
                (Q(other_details__mooring__iregex=search_words_regex))|
                (Q(other_details__accreditations__accreditation_type__in=accreditation_words))|
                (Q(trails__in=trails)))| 
            (Q(application_type__name=ApplicationType.EVENT) & 
                (Q(events_parks__park__name__iregex=search_words_regex))|
                (Q(events_parks__event_activities__iregex=search_words_regex))|
                (Q(trails__trail__name__iregex=search_words_regex))|
                (Q(vehicles__rego__iregex=search_words_regex))|
                (Q(vessels__spv_no__iregex=search_words_regex))|
                (Q(trails__in=trails)))| 
            (Q(application_type__name=ApplicationType.FILMING) & 
                (Q(filming_parks__park__name__iregex=search_words_regex))|
                (Q(vehicles__rego__iregex=search_words_regex))|
                (Q(vessels__spv_no__iregex=search_words_regex))|
                (Q(filming_activity__film_type__in=film_type_words))|
                (Q(filming_activity__film_purpose__in=film_purpose_words)))
            ).distinct("id").order_by("-id")

            #this loop now effectively formats the result
            #TODO if pagination can be applied prior, it can save time for all querysets regardless of size
            for p in proposal_list:
                #if p.data:
                if p.search_data:
                    try:
                        #results = search(p.data[0], searchWords)
                        results = search(p.search_data, searchWords)
                        final_results = {}
                        if results:
                            for r in results:
                                for key, value in r.items():
                                    final_results.update({'key': key, 'value': value})
                            res = {
                                'number': p.lodgement_number,
                                'id': p.id,
                                'type': 'Proposal',
                                'applicant': p.applicant,
                                'text': final_results,
                                }
                            qs.append(res)
                    except:
                        raise
        if searchApproval:
            approval_list = approval_list.filter(Q(surrender_details__iregex=filter_regex) | Q(suspension_details__iregex=filter_regex) | Q(cancellation_details__iregex=search_words_regex))
            for a in approval_list:
                try:
                    results = search_approval(a, searchWords)
                    qs.extend(results)
                except:
                    raise
        if searchCompliance:
            compliance_list = compliance_list.filter(Q(text__iregex=search_words_regex) | Q(requirement__free_requirement__iregex=search_words_regex) | Q(requirement__standard_requirement__text__iregex=search_words_regex))
            for c in compliance_list:
                try:
                    results = search_compliance(c, searchWords)
                    qs.extend(results)
                except:
                    raise
    return qs

def search_reference(reference_number):
    from commercialoperator.components.approvals.models import Approval
    from commercialoperator.components.compliances.models import Compliance
    proposal_list = Proposal.objects.all().exclude(processing_status__in=['discarded'])
    approval_list = Approval.objects.all().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
    compliance_list = Compliance.objects.all().exclude(processing_status__in=['future'])
    record = {}
    try:
        result = proposal_list.get(lodgement_number = reference_number)
        record = {  'id': result.id,
                    'type': 'proposal' }
    except Proposal.DoesNotExist:
        try:
            result = approval_list.get(lodgement_number = reference_number)
            record = {  'id': result.id,
                        'type': 'approval' }
        except Approval.DoesNotExist:
            try:
                for c in compliance_list:
                    if c.reference == reference_number:
                        record = {  'id': c.id,
                                    'type': 'compliance' }
            except:
                raise ValidationError('Record with provided reference number does not exist')
    if record:
        return record
    else:
        raise ValidationError('Record with provided reference number does not exist')

from ckeditor.fields import RichTextField
class HelpPage(models.Model):
    HELP_TEXT_EXTERNAL = 1
    HELP_TEXT_INTERNAL = 2
    HELP_TYPE_CHOICES = (
        (HELP_TEXT_EXTERNAL, 'External'),
        (HELP_TEXT_INTERNAL, 'Internal'),
    )

    application_type = models.ForeignKey(ApplicationType)
    content = RichTextField()
    description = models.CharField(max_length=256, blank=True, null=True)
    help_type = models.SmallIntegerField('Help Type', choices=HELP_TYPE_CHOICES, default=HELP_TEXT_EXTERNAL)
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('application_type', 'help_type', 'version')

# --------------------------------------------------------------------------------------
# Filming Models Start
# --------------------------------------------------------------------------------------
class ProposalFilmingActivity(models.Model):
    MOTION_FILM='motion_film'
    PHOTOGRAPHY='photography'
    EDUCATION='education'
    ADVERTISING='advertising'
    FEATURE_FILM='feature_film'
    TOURISM='tourism'
    SOCIAL_MEDIA='social_media'
    DOCUMENTARY='documentary'
    RECREATION='recreation'
    OTHER='other'
    YES='yes'
    NO='no'
    SELL='sell'
    EDITORIAL='editorial'
    FILM_TYPE_CHOICES=(
        (MOTION_FILM,'Motion film'),
        (PHOTOGRAPHY, 'Photography'),
    )
    PURPOSE_CHOICES=(
        (EDUCATION, 'Education'),
        (ADVERTISING, 'Advertising'),
        (FEATURE_FILM, 'Feature film'),
        (RECREATION, 'Recreation'),
        (DOCUMENTARY, 'Documentary'),
        (TOURISM, 'Tourism'),
        (OTHER, 'Other'),
        (SOCIAL_MEDIA, 'Social media/ online content'),
    )
    SPONSORSHIP_CHOICES=(
        (YES, 'Yes'),
        (NO, 'No'),
        (OTHER, 'other')
    )
    FILM_USE_CHOICES=(
        (SELL, 'Sell on to a third pary, e.g. image library, publisher'),
        (EDITORIAL, 'Editorial'),
        (ADVERTISING, 'Advertising'),
        (OTHER, 'Other')
    )

    commencement_date=models.DateField('Commencement Date',blank=True, null=True)
    completion_date=models.DateField('Completion Date',blank=True, null=True)
    previous_contact_person=models.CharField('Previous Contact person', max_length=100, null=True)
    #film_type=models.CharField('Type of Film', max_length=40, choices=FILM_TYPE_CHOICES, null=True, blank=True)
    film_type=MultiSelectField('Type of Film', max_choices=2, max_length=40, choices=FILM_TYPE_CHOICES, null=True, blank=True)
    #film_purpose=models.CharField('Purpose of Film', max_length=40, choices=PURPOSE_CHOICES, null=True, blank=True)
    film_purpose=MultiSelectField('Purpose of Film', max_choices=5, max_length=200, choices=PURPOSE_CHOICES, null=True, blank=True)
    film_purpose_details=models.TextField(blank=True)
    sponsorship=models.CharField('Sponsorship Type', max_length=40, choices=SPONSORSHIP_CHOICES, null=True, blank=True)
    #sponsorship=MultiSelectField('Sponsorship Type', max_choices=3, max_length=120, choices=SPONSORSHIP_CHOICES, null=True, blank=True)
    sponsorship_details=models.TextField(blank=True)
    #film_usage=models.CharField('Film be used', max_length=40, choices=FILM_USE_CHOICES, null=True, blank=True)
    film_usage=MultiSelectField('Film be used',max_choices=4, max_length=160, choices=FILM_USE_CHOICES, null=True, blank=True)
    film_usage_details=models.TextField(blank=True)
    activity_title=models.CharField('Activity title', max_length=100, null=True, blank=True)
    production_description=models.TextField(blank=True, null=True,)
    proposal = models.OneToOneField(Proposal, related_name='filming_activity', null=True)
    #pdswa_location=models.BooleanField('Event location within PDSWA',default=False)

    def __str__(self):
        return '{}'.format(self.activity_title)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def num_filming_days(self):
        return (self.completion_date - self.commencement_date).days + 1

class ProposalFilmingAccess(models.Model):
    proposal = models.OneToOneField(Proposal, related_name='filming_access', null=True)
    track_use=models.BooleanField('Use of Tracks or trails',default=False)
    track_use_details=models.TextField(blank=True)
    off_road=models.BooleanField('Conduct any off-road activity',default=False)
    off_road_details=models.TextField(blank=True)
    road_closure=models.BooleanField('roads to be closed during filming',default=False)
    road_closure_details=models.TextField(blank=True)
    no_of_people=models.CharField('Activity title', max_length=100, blank=True, null=True)
    camp_on_land=models.BooleanField('Camp on CALM land',default=False)
    camp_location=models.TextField('Where',blank=True)
    staff_assistance=models.BooleanField('Need assistance from Department staff',default=False)
    assistance_staff_capacity=models.TextField('Capacity of staff for assistance',blank=True)
    staff_to_film=models.BooleanField('Need Department staff to film',default=False)
    film_staff_capacity=models.TextField('Capacity of staff for filming',blank=True)
    cultural_significance=models.BooleanField('Areas of cultural significance',default=False)
    cultural_significance_details=models.TextField('Cultural significance details',blank=True)


    def __str__(self):
        return '{}'.format(self.proposal)

    class Meta:
        app_label = 'commercialoperator'


class ProposalFilmingEquipment(models.Model):
    vehicle_owned=models.BooleanField('Vehicle Hired on owned',default=False)
    rps_used=models.BooleanField('Use of RPS for filming',default=False)
    rps_used_details=models.TextField('RPA used details', blank=True, null=True)
    rps_overweight=models.BooleanField('Weight of RPS over two kg',default=False)
    num_cameras=models.TextField('Number and type of cameras to be used', blank=True, null=True)
    alteration_required=models.BooleanField('Any alteration required to the area',default=False)
    alteration_required_details=models.TextField('Alteration required details', blank=True, null=True)
    other_equipments=models.TextField('Other equipment', blank=True, null=True)
    proposal = models.OneToOneField(Proposal, related_name='filming_equipment', null=True)

    def __str__(self):
        return '{}'.format(self.num_cameras)

    class Meta:
        app_label = 'commercialoperator'


class ProposalFilmingOtherDetails(models.Model):
    safety_details=models.TextField('Steps taken to ensure safety of others', blank=True, null=True)
    camping_fee_waived = models.BooleanField(default=False)
    fee_waived_num_people = models.SmallIntegerField('For how many people', blank=True, null=True)
    insurance_expiry= models.DateField(blank=True, null=True)
    other_comments=models.TextField('Other comments', blank=True, null=True)
    proposal = models.OneToOneField(Proposal, related_name='filming_other_details', null=True)

    def __str__(self):
        return '{}'.format(self.safety_details)

    class Meta:
        app_label = 'commercialoperator'

class ProposalFilmingParks(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='filming_parks', null=True)
    proposal = models.ForeignKey(Proposal, related_name='filming_parks', null=True)
    park= models.ForeignKey(Park, related_name='filming_proposal')
    feature_of_interest=models.CharField('Feture of interest', max_length=100, blank=True, null=True)
    from_date=models.DateField(blank=True, null=True)
    to_date=models.DateField(blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.proposal)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal', 'park')

    def can_assessor_edit_orig(self,user):
        assessor_group=None
        if self.proposal.processing_status == 'with_district_assessor':
            if self.park.district:
                check_group = DistrictProposalAssessorGroup.objects.filter(
                        district__name=self.park.district.name
                    ).distinct()
                if check_group:
                    assessor_group = check_group[0]
                else:
                    assessor_group = DistrictProposalAssessorGroup.objects.get(default=True)
                return assessor_group in user.districtproposalassessorgroup_set.all()
        elif self.proposal.processing_status == 'with_assessor':
                return self.proposal.can_assess(user)
        else:
            return False

    def can_assessor_edit(self,user):
        assessor_group=None
        allowed_status=['with_district_assessor', 'partially_declined', 'partially_approved']
        if self.proposal.processing_status in allowed_status:
            if self.park.district:
                qs=self.proposal.district_proposals.filter(district__name='Kensington')
                if qs:
                    kens_proposal=qs[0]
                    check_group = DistrictProposalAssessorGroup.objects.filter(
                            district__name='Kensington'
                        ).distinct()
                    if check_group:
                        assessor_group = check_group[0]
                    else:
                        assessor_group = DistrictProposalAssessorGroup.objects.get(default=True)
                    if kens_proposal.processing_status=='with_assessor':
                        return assessor_group in user.districtproposalassessorgroup_set.all()
                    else:
                        return False

                else:

                    check_group = DistrictProposalAssessorGroup.objects.filter(
                            district__name=self.park.district.name
                        ).distinct()
                    if check_group:
                        assessor_group = check_group[0]
                    else:
                        assessor_group = DistrictProposalAssessorGroup.objects.get(default=True)

                    district_proposal=self.proposal.district_proposals.filter(district=self.park.district)
                    if district_proposal:
                        district_proposal=district_proposal[0]
                        if district_proposal.processing_status=='with_assessor':
                            return assessor_group in user.districtproposalassessorgroup_set.all()
                        else:
                            return False
                    else:
                        return False
        elif self.proposal.processing_status == 'with_assessor':
                return self.proposal.can_assess(user)
        else:
            return False

    def add_documents(self, request):
        with transaction.atomic():
            try:
                # save the files
                data = json.loads(request.data.get('data'))
                if not data.get('update'):
                    documents_qs = self.filming_park_documents.filter(input_name='filming_park_doc', visible=True)
                    documents_qs.delete()
                for idx in range(data['num_files']):
                    _file = request.data.get('file-'+str(idx))
                    document = self.filming_park_documents.create(_file=_file, name=_file.name)
                    document.input_name = data['input_name']
                    document.can_delete = True
                    document.save()
                # end save documents
                self.save()
            except:
                raise
        return


class FilmingParkDocument(Document):
    filming_park = models.ForeignKey('ProposalFilmingParks',related_name='filming_park_documents')
    _file = models.FileField(upload_to=update_filming_park_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    class Meta:
        app_label = 'commercialoperator'

    def delete(self):
        if self.can_delete:
            return super(FilmingParkDocument, self).delete()

#Internal Workflow models - Filming application
class DistrictProposalAssessorGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(EmailUser)
    district = models.ForeignKey(District, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "District Assessor Group"
        verbose_name_plural = "District Assessor Group"

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = DistrictProposalAssessorGroup.objects.get(default=True)
        except DistrictProposalAssessorGroup.DoesNotExist:
            default = None

        if self.pk:
            if not self.default and not self.district:
                raise ValidationError('Only default can have no district set for District assessor group. Please specifiy region')
#
        else:
            if default and self.default:
                raise ValidationError('There can only be one default District assessor group')


    @property
    def members_email(self):
        return [i.email for i in self.members.all()]

class DistrictProposalApproverGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(EmailUser)
    district = models.ForeignKey(District, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "District Approver Group"
        verbose_name_plural = "District Approver Group"

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = DistrictProposalApproverGroup.objects.get(default=True)
        except DistrictProposalApproverGroup.DoesNotExist:
            default = None

        if self.pk:
            if not self.default and not self.district:
                raise ValidationError('Only default can have no district set for District assessor group. Please specifiy region')
        else:
            if default and self.default:
                raise ValidationError('There can only be one default district approver group')

    @property
    def members_email(self):
        return [i.email for i in self.members.all()]


class DistrictProposal(models.Model):
    PROCESSING_STATUS_WITH_ASSESSOR = 'with_assessor'
    PROCESSING_STATUS_WITH_REFERRAL = 'with_referral'
    PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS = 'with_assessor_requirements'
    PROCESSING_STATUS_WITH_APPROVER = 'with_approver'
    PROCESSING_STATUS_APPROVED = 'approved'
    PROCESSING_STATUS_DECLINED = 'declined'
    PROCESSING_STATUS_DISCARDED = 'discarded'
    PROCESSING_STATUS_CHOICES=(
                                (PROCESSING_STATUS_WITH_ASSESSOR, 'With Assessor'),
                                (PROCESSING_STATUS_WITH_REFERRAL, 'With Referral'),
                                (PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS, 'With Assessor (Requirements)'),
                                (PROCESSING_STATUS_WITH_APPROVER, 'With Approver'),
                                (PROCESSING_STATUS_DECLINED, 'Declined'),
                                (PROCESSING_STATUS_APPROVED, 'Approved'),
                                (PROCESSING_STATUS_DISCARDED, 'Discarded'),

                                )
    proposal = models.ForeignKey(Proposal, related_name='district_proposals')
    district = models.ForeignKey(District, related_name='proposals')
    proposal_park=models.ManyToManyField(ProposalFilmingParks)
    district_approval = models.ForeignKey('commercialoperator.DistrictApproval',null=True,blank=True)
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_district_proposals_assigned', on_delete=models.SET_NULL)
    assigned_approver = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_district_proposals_approvals', on_delete=models.SET_NULL)
    proposed_issuance_approval = JSONField(blank=True, null=True)
    proposed_decline_status = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.proposal)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def get_processing_status(self):
        return self.get_processing_status_display()

    @property
    def districts_list(self):
        #return self.region.split(',') if self.region else []
        return [self.district.name] if self.district else []

    # @property
    # def parks_list(self):
    #     #return self.region.split(',') if self.region else []
    #     return ProposalFilmingParks.objects.filter(park__district=self.district, proposal=self.proposal) if self.district else None

    @property
    def parks_list(self):
        #return self.region.split(',') if self.region else []
        if self.district:
            if self.district.name=='Kensington':
                return ProposalFilmingParks.objects.filter(proposal=self.proposal)
            else:
                return ProposalFilmingParks.objects.filter(park__district=self.district, proposal=self.proposal)
        return None


    @property
    def district_name(self):
        #return self.region.split(',') if self.region else []
        return self.district.name if self.district else ''

    @property
    def is_kensington_proposal(self):
        #return self.region.split(',') if self.region else []
        return True if self.district and self.district.name=='Kensington' else False

    @property
    def submitter(self):
        return self.proposal.submitter

    @property
    def applicant(self):
        return self.proposal.applicant

    @property
    def permit(self):
        return self.proposal.permit


    @property
    def assessor_group(self):
        # TODO get list of assessor groups based on region and activity
        if self.district:
            try:
                check_group = DistrictProposalAssessorGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    district__name__in=self.districts_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except DistrictProposalAssessorGroup.DoesNotExist:
                pass
        default_group = DistrictProposalAssessorGroup.objects.get(default=True)

        return default_group

    @property
    def approver_group(self):
        # TODO get list of approver groups based on region and activity
        if self.district:
            try:
                check_group = DistrictProposalApproverGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    district__name__in=self.districts_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except DistrictProposalApproverGroup.DoesNotExist:
                pass
        default_group = DistrictProposalApproverGroup.objects.get(default=True)

        return default_group



    def __assessor_group(self):
        # TODO get list of assessor groups based on region and activity
        if self.district:
            try:
                check_group = DistrictProposalAssessorGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    district__name__in=self.districts_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except DistrictProposalAssessorGroup.DoesNotExist:
                pass
        default_group = DistrictProposalAssessorGroup.objects.get(default=True)

        return default_group


    def __approver_group(self):
        # TODO get list of approver groups based on region and activity
        if self.district:
            try:
                check_group = DistrictProposalApproverGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    district__name__in=self.districts_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except DistrictProposalApproverGroup.DoesNotExist:
                pass
        default_group = DistrictProposalApproverGroup.objects.get(default=True)

        return default_group

    @property
    def assessor_recipients(self):
        recipients = []
        assessor_group=self.__assessor_group()
        recipients = assessor_group.members_email
        return recipients

    @property
    def approver_recipients(self):
        recipients = []
        approver_group=self.__approver_group()
        recipients = approver_group.members_email

        return recipients

    def can_assess(self,user):
        #if self.processing_status == 'on_hold' or self.processing_status == 'with_assessor' or self.processing_status == 'with_referral' or self.processing_status == 'with_assessor_requirements':
        if self.processing_status in ['with_assessor', 'with_assessor_requirements']:
            return self.__assessor_group() in user.districtproposalassessorgroup_set.all()
        elif self.processing_status == 'with_approver':
            return self.__approver_group() in user.districtproposalapprovergroup_set.all()
        else:
            return False

    def can_process_requirements(self,user):
        #if self.processing_status == 'on_hold' or self.processing_status == 'with_assessor' or self.processing_status == 'with_referral' or self.processing_status == 'with_assessor_requirements':
        if self.processing_status in ['with_assessor','with_assessor_requirements']:
            return self.__assessor_group() in user.districtproposalassessorgroup_set.all()
        else:
            return False

    @property
    def allowed_district_assessors(self):
        if self.processing_status == 'with_approver':
            group = self.__approver_group()
        else:
            group = self.__assessor_group()
        return group.members.all() if group else []

    def assign_officer(self,request,officer):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not self.can_assess(officer):
                    raise ValidationError('The selected person is not authorised to be assigned to this proposal')
                if self.processing_status == 'with_approver':
                    if officer != self.assigned_approver:
                        self.assigned_approver = officer
                        self.save()
                        # Create a log entry for the proposal
                        self.proposal.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_DISTRICT_APPROVER.format(self.id,self.proposal.id, '{}({})'.format(officer.get_full_name(),officer.email)),request)
                        # Create a log entry for the organisation
                        #applicant_field=getattr(self, self.applicant_field)
                        #applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                else:
                    if officer != self.assigned_officer:
                        self.assigned_officer = officer
                        self.save()
                        # Create a log entry for the proposal
                        self.proposal.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_DISTRICT_ASSESSOR.format(self.id,self.proposal.id, '{}({})'.format(officer.get_full_name(),officer.email)),request)
                        # Create a log entry for the organisation
                        #applicant_field=getattr(self, self.applicant_field)
                        #applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
            except:
                raise

    def unassign(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status == 'with_approver':
                    if self.assigned_approver:
                        self.assigned_approver = None
                        self.save()
                        # Create a log entry for the proposal
                        self.proposal.log_user_action(ProposalUserAction.ACTION_UNASSIGN_DISTRICT_APPROVER.format(self.id),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_DISTRICT_APPROVER.format(self.id, self.proposal.id),request)
                else:
                    if self.assigned_officer:
                        self.assigned_officer = None
                        self.save()
                        # Create a log entry for the proposal
                        self.proposal.log_user_action(ProposalUserAction.ACTION_UNASSIGN_DISTRICT_ASSESSOR.format(self.id, self.proposal.id),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_DISTRICT_ASSESSOR.format(self.id, self.proposal.id),request)
            except:
                raise

    def move_to_status(self,request,status, approver_comment=''):
        if not self.can_assess(request.user):
            raise exceptions.ProposalNotAuthorized()
        if status in ['with_assessor','with_assessor_requirements','with_approver']:
            if self.proposal.can_user_edit:
                raise ValidationError('You cannot change the current status at this time')
            if self.processing_status != status:
                #TODO send email to District Approver group when District proposal is pushed to status with approver
                if self.processing_status =='with_approver':
                    self.approver_comment=''
                    if approver_comment:
                        self.approver_comment = approver_comment
                        self.save()
                    send_district_proposal_approver_sendback_email_notification(request, self)
                self.processing_status = status
                self.save()
                # if status=='with_assessor_requirements':
                #     self.proposal.add_default_requirements()

                # Create a log entry for the proposal
                if self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR:
                    self.proposal.log_user_action(ProposalUserAction.ACTION_BACK_TO_PROCESSING_DISTRICT.format(self.id, self.proposal.id),request)
                elif self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS:
                    self.proposal.log_user_action(ProposalUserAction.ACTION_ENTER_REQUIREMENTS_DISTRICT.format(self.id, self.proposal.id),request)
        else:
            raise ValidationError('The provided status cannot be found.')

    def proposed_decline(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_assessor':
                    raise ValidationError('You cannot propose to decline if it is not with assessor')

                reason = details.get('reason')
                DistrictProposalDeclinedDetails.objects.update_or_create(
                    district_proposal = self,
                    defaults={'officer': request.user, 'reason': reason, 'cc_email': details.get('cc_email',None)}
                )
                self.proposed_decline_status = True
                approver_comment= ''
                self.move_to_status(request,'with_approver', approver_comment)
                # Log proposal action
                self.proposal.log_user_action(ProposalUserAction.ACTION_DISTRICT_PROPOSED_DECLINE.format(self.id, self.proposal.id),request)
                # Log entry for organisation
                applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_DISTRICT_PROPOSED_DECLINE.format(self.id, self.proposal.id),request)

                send_district_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def final_decline(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot decline if it is not with approver')

                proposal_decline, success = DistrictProposalDeclinedDetails.objects.update_or_create(
                    district_proposal = self,
                    defaults={'officer':request.user,'reason':details.get('reason'),'cc_email':details.get('cc_email',None)}
                )
                self.proposed_decline_status = True
                self.processing_status = 'declined'
                #self.customer_status = 'declined'
                self.save()
                proposal=self.proposal
                all_district_proposals=proposal.district_proposals.all().exclude(processing_status='discarded')
                approved_district_proposals=proposal.district_proposals.filter(processing_status='approved')
                declined_district_proposals=proposal.district_proposals.filter(processing_status='declined')
                if proposal.processing_status=='partially_declined':
                    if declined_district_proposals.count() == all_district_proposals.count():
                        proposal.processing_status='declined'
                        proposal.customer_status='declined'
                        proposal.save()
                if proposal.processing_status== 'with_district_assessor':
                    proposal.processing_status='partially_declined'
                    proposal.customer_status='partially_declined'
                    proposal.save()

                self.proposal.log_user_action(ProposalUserAction.ACTION_DISTRICT_DECLINE.format(self.id, self.proposal.id),request)
                # Log entry for organisation
                applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_DISTRICT_DECLINE.format(self.id, self.proposal.id),request)

                send_district_proposal_decline_email_notification(self,request, proposal_decline)
            except:
                raise

    def proposed_approval(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_assessor_requirements':
                    raise ValidationError('You cannot propose for approval if it is not with assessor for requirements')
                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                approver_comment = ''
                self.move_to_status(request,'with_approver', approver_comment)
                self.assigned_officer = None
                self.save()
                # Log proposal action
                self.proposal.log_user_action(ProposalUserAction.ACTION_DISTRICT_PROPOSED_APPROVAL.format(self.id, self.proposal.id),request)
                # Log entry for organisation
                applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_DISTRICT_PROPOSED_APPROVAL.format(self.id, self.proposal.id),request)

                send_district_approver_approve_email_notification(request, self)
            except:
                raise

    def preview_approval(self,request,details):
        from commercialoperator.components.approvals.models import PreviewTempApproval
        with transaction.atomic():
            try:
                if self.processing_status != 'with_approver':
                    raise ValidationError('Licence preview only available when processing status is with_approver. Current status {}'.format(self.processing_status))
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                #if not self.applicant.organisation.postal_address:
                if not self.proposal.applicant_address:
                    raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')
                self.processing_status = 'approved'
                self.save()
                #lodgement_number = self.previous_application.approval.lodgement_number if self.proposal_type in ['renewal', 'amendment'] else None # renewals/amendments keep same licence number
                #lodgement_number = self.proposal.approval.lodgement_number
                if self.proposal.proposal_type in ['renewal', 'amendment'] :
                    lodgement_number = self.proposal.previous_application.approval.lodgement_number
                elif self.proposal.approval:
                    lodgement_number = self.proposal.approval.lodgement_number
                else:    
                    lodgement_number = None # renewals/amendments keep same licence number
                preview_approval = PreviewTempApproval.objects.create(
                    current_proposal = self.proposal,
                    issue_date = timezone.now(),
                    expiry_date = datetime.datetime.strptime(details.get('due_date'), '%d/%m/%Y').date(),
                    start_date = datetime.datetime.strptime(details.get('start_date'), '%d/%m/%Y').date(),
                    #expiry_date = details.get('due_date').strftime('%d/%m/%Y'),
                    #start_date = details.get('start_date').strftime('%d/%m/%Y'),
                    submitter = self.proposal.submitter,
                    #org_applicant = self.applicant if isinstance(self.applicant, Organisation) else None,
                    #proxy_applicant = self.applicant if isinstance(self.applicant, EmailUser) else None,
                    org_applicant = self.proposal.org_applicant,
                    proxy_applicant = self.proposal.proxy_applicant,
                    lodgement_number = lodgement_number
                )

                # Generate the preview document - get the value of the BytesIO buffer
                licence_buffer = preview_approval.generate_doc(request.user, preview=True)

                # clean temp preview licence object
                transaction.set_rollback(True)

                return licence_buffer
            except:
                raise

    def final_approval(self,request,details):
        from commercialoperator.components.approvals.models import Approval, DistrictApproval
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot issue the approval if it is not with an approver')
                #if not self.applicant.organisation.postal_address:
                if not self.proposal.applicant_address:
                    raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')

                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                self.processing_status = 'approved'
                self.save()
                #self.customer_status = 'approved'
                # Log proposal action
                self.proposal.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_DISTRICT.format(self.id, self.proposal.id),request)
                # Log entry for organisation
                applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_DISTRICT.format(self.id, self.proposal.id),request)

                if self.processing_status == 'approved':
                    # TODO if it is an ammendment proposal then check appropriately
                    checking_district_proposal = self
                    checking_proposal = self.proposal

                    district_approval,district_created = DistrictApproval.objects.update_or_create(
                        current_district_proposal = checking_district_proposal,
                        defaults = {
                            'issue_date' : timezone.now(),
                            'expiry_date' : details.get('expiry_date'),
                            'start_date' : details.get('start_date'),

                        }
                    )
                    if self.proposal.proposal_type == 'renewal':
                        if self.proposal.previous_application:
                            previous_approval = self.proposal.previous_application.approval
                            approval,created = Approval.objects.update_or_create(
                                current_proposal = checking_proposal,
                                defaults = {
                                    'issue_date' : timezone.now(),
                                    'expiry_date' : details.get('expiry_date'),
                                    'start_date' : details.get('start_date'),
                                    'submitter': self.proposal.submitter,
                                    #'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                    #'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                    'org_applicant' : self.proposal.org_applicant,
                                    'proxy_applicant' : self.proposal.proxy_applicant,
                                    'lodgement_number': previous_approval.lodgement_number
                                }
                            )
                            if created:
                                previous_approval.replaced_by = approval
                                previous_approval.save()

                    #elif self.proposal_type == 'amendment':
                    if self.proposal.proposal_type == 'amendment':
                        if self.proposal.previous_application:
                            previous_approval = self.proposal.previous_application.approval
                            print('previous approval', previous_approval.id)
                            approval,created = Approval.objects.update_or_create(
                                current_proposal = checking_proposal,
                                defaults = {
                                    'issue_date' : timezone.now(),
                                    'expiry_date' : details.get('expiry_date'),
                                    'start_date' : details.get('start_date'),
                                    'submitter': self.proposal.submitter,
                                    #'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                    #'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                    'org_applicant' : self.proposal.org_applicant,
                                    'proxy_applicant' : self.proposal.proxy_applicant,
                                    'lodgement_number': previous_approval.lodgement_number
                                }
                            )
                            if created:
                                previous_approval.replaced_by = approval
                                previous_approval.save()
                            print('new approval', approval.id)
                    else:
                        approval,created = Approval.objects.update_or_create(
                            current_proposal = checking_proposal,
                            defaults = {
                                'issue_date' : timezone.now(),
                                'expiry_date' : details.get('expiry_date'),
                                'start_date' : details.get('start_date'),
                                'submitter': self.proposal.submitter,
                                #'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                #'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                'org_applicant' : self.proposal.org_applicant,
                                'proxy_applicant' : self.proposal.proxy_applicant,
                                #'extracted_fields' = JSONField(blank=True, null=True)
                            }
                        )

                    print('district created', district_created, district_approval)
                    print('approval created',created, approval)
                    # Generate compliances
                    from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
                    #When first district proposal is created and Approval object is created (not updated) for Amendment proposal, delete all the future compliancs linked to previous application.
                    if district_created:
                        if created:
                            if self.proposal.proposal_type == 'amendment':
                                approval_compliances = Compliance.objects.filter(approval= previous_approval, proposal = self.proposal.previous_application, processing_status='future')
                                if approval_compliances:
                                    for c in approval_compliances:
                                        print ('compliance deleted',c.id)
                                        c.delete()
                        # Log creation
                        # Generate the document
                        approval.generate_doc(request.user)
                        requirement_set=self.district_proposal_requirements.all()
                        self.generate_district_compliances(approval,district_approval, requirement_set, request)                        # send the doc and log in approval and org
                    else:
                        #approval.replaced_by = request.user
                        district_approval.replaced_by = self.district_approval
                        # Generate the document
                        approval.generate_doc(request.user)
                        #Delete the future compliances if Approval is reissued and generate the compliances again.
                        district_approval_compliances = Compliance.objects.filter(district_approval= district_approval, district_proposal = self, proposal = self.proposal, processing_status='future')
                        if district_approval_compliances:
                            for c in district_approval_compliances:
                                c.delete()
                        requirement_set=self.district_proposal_requirements.all()
                        self.generate_district_compliances(approval,district_approval, requirement_set, request)
                        #Log proposal action
                        self.proposal.log_user_action(ProposalUserAction.ACTION_UPDATE_APPROVAL_DISTRICT.format(self.id, self.proposal.id),request)
                        # Log entry for organisation
                        applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UPDATE_APPROVAL_DISTRICT.format(self.id, self.proposal.id),request)
                    self.proposal.approval = approval
                    self.district_approval = district_approval
                    self.save()
                #send Proposal approval email with attachment
                #send_proposal_approval_email_notification(self,request)
                district_approval.lodgement_number= approval.lodgement_number
                district_approval.licence_document= approval.licence_document
                district_approval.save()

                proposal=self.proposal
                all_district_proposals=proposal.district_proposals.all().exclude(processing_status='discarded')
                approved_district_proposals=proposal.district_proposals.filter(processing_status='approved')
                declined_district_proposals=proposal.district_proposals.filter(processing_status='declined')
                if proposal.processing_status=='partially_declined' or proposal.processing_status=='partially_approved' or proposal.processing_status== 'with_district_assessor':
                    if approved_district_proposals.count() == all_district_proposals.count():
                        proposal.processing_status='approved'
                        proposal.customer_status='approved'
                    else:
                        proposal.processing_status='partially_approved'
                        proposal.customer_status='partially_approved'
                # if proposal.processing_status== 'with_district_assessor':

                #     proposal.processing_status='partially_approved'
                #     proposal.customer_status='partially_approved'
                send_district_proposal_approval_email_notification(self, approval, request)
                self.proposal.save(version_comment='Final District Approval: {} for District Proposal: {}'.format(self.proposal.approval.lodgement_number, self.id))
                self.proposal.approval.documents.all().update(can_delete=False)

            except:
                raise

    def generate_district_compliances(self,approval, district_approval, requirement_set, request):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
        #For amendment type of Proposal, check for copied requirements from previous proposal
        if self.proposal.proposal_type == 'amendment':
            try:
                for r in self.proposal.requirements.filter(copied_from__isnull=False, district_proposal__isnull=True):
                    cs=[]
                    cs=Compliance.objects.filter(requirement=r.copied_from, proposal=self.proposal.previous_application, processing_status='due')
                    if cs:
                        if r.is_deleted == True:
                            for c in cs:
                                print('discard proposal compliance', c)
                                c.processing_status='discarded'
                                c.customer_status = 'discarded'
                                c.reminder_sent=True
                                c.post_reminder_sent=True
                                c.save()
            except:
                raise

        if self.proposal.proposal_type == 'amendment':
            try:
                for r in requirement_set.filter(copied_from__isnull=False):
                    cs=[]
                    cs=Compliance.objects.filter(requirement=r.copied_from, processing_status='due')
                    if cs:
                        if r.is_deleted == True:
                            for c in cs:
                                print('discarded compliance', c)
                                c.processing_status='discarded'
                                c.customer_status = 'discarded'
                                c.reminder_sent=True
                                c.post_reminder_sent=True
                                c.save()
                        if r.is_deleted == False:
                            for c in cs:
                                print('not deleted', c)
                                c.district_proposal=self
                                c.proposal= self.proposal
                                c.approval=approval
                                c.district_approval=c.district_approval
                                c.requirement=r
                                c.save()
            except:
                raise
        #requirement_set= self.requirements.filter(copied_from__isnull=True).exclude(is_deleted=True)
        requirement_set= requirement_set.exclude(is_deleted=True)

        #for req in self.requirements.all():
        for req in requirement_set:
            try:
                if req.due_date and req.due_date >= today:
                    current_date = req.due_date
                    #create a first Compliance
                    try:
                        compliance= Compliance.objects.get(requirement = req, due_date = current_date)
                    except Compliance.DoesNotExist:
                        compliance =Compliance.objects.create(
                                    proposal=self.proposal,
                                    district_proposal=self,
                                    due_date=current_date,
                                    processing_status='future',
                                    approval=approval,
                                    district_approval=district_approval,
                                    requirement=req,
                        )
                        compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
                    if req.recurrence:
                        while current_date < approval.expiry_date:
                            for x in range(req.recurrence_schedule):
                            #Weekly
                                if req.recurrence_pattern == 1:
                                    current_date += timedelta(weeks=1)
                            #Monthly
                                elif req.recurrence_pattern == 2:
                                    current_date += timedelta(weeks=4)
                                    pass
                            #Yearly
                                elif req.recurrence_pattern == 3:
                                    current_date += timedelta(days=365)
                            # Create the compliance
                            if current_date <= approval.expiry_date:
                                try:
                                    compliance= Compliance.objects.get(requirement = req, due_date = current_date)
                                except Compliance.DoesNotExist:
                                    compliance =Compliance.objects.create(
                                                proposal=self.proposal,
                                                due_date=current_date,
                                                district_proposal=self,
                                                processing_status='future',
                                                approval=approval,
                                                district_approval=district_approval,
                                                requirement=req,
                                    )
                                    compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
            except:
                raise




class DistrictProposalDeclinedDetails(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='declined_details')
    district_proposal = models.OneToOneField(DistrictProposal)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)
    cc_email = models.TextField(null=True)

    class Meta:
        app_label = 'commercialoperator'


# --------------------------------------------------------------------------------------
# Filming Models End
# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Event Models Start
# --------------------------------------------------------------------------------------

class ProposalEventActivities(models.Model):
    event_name=models.CharField('Event name', max_length=100, blank=True, null=True)
    proposal = models.OneToOneField(Proposal, related_name='event_activity', null=True)
    commencement_date=models.DateField(blank=True, null=True)
    completion_date=models.DateField(blank=True, null=True)
    event_date=models.CharField('Event date', max_length=100, blank=True, null=True)
    pdswa_location=models.BooleanField('Event location within PDSWA',default=False)

    def __str__(self):
        return '{}'.format(self.event_name)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def can_occur(self):
        """ Event can occur if within max_num_months_ahead """
        try:
            if self.proposal.org_applicant.max_num_months_ahead==0 or timezone.now().date() + relativedelta(months=self.proposal.org_applicant.max_num_months_ahead) < self.completion_date:
                return True
        except:
            return True

        return False

class ProposalEventManagement(models.Model):
    num_participants = models.SmallIntegerField('Number of participants expected', blank=True, null=True)
    proposal = models.OneToOneField(Proposal, related_name='event_management', null=True)
    num_spectators = models.SmallIntegerField('Number of spectators expected', blank=True, null=True)
    num_officials = models.SmallIntegerField('Number of officials expected', blank=True, null=True)
    num_vehicles = models.SmallIntegerField('Number of vehicles expected', blank=True, null=True)
    media_involved = models.BooleanField(default=False)
    media_details=models.TextField(blank=True)
    structure_change = models.BooleanField(default=False)
    structure_change_details=models.TextField(blank=True)
    vendor_hired = models.BooleanField(default=False)
    vendor_hired_details=models.TextField(blank=True)
    equipment_details= models.TextField(blank=True)
    toilets_provided = models.BooleanField(default=False)
    toilets_provided_details=models.TextField(blank=True)
    rubbish_removal = models.BooleanField(default=False)
    rubbish_removal_details=models.TextField(blank=True)
    approvals_gained = models.BooleanField(default=False)
    approvals_gained_details=models.TextField(blank=True)
    emergency_plan = models.BooleanField(default=False)
    event_management_plan = models.BooleanField(default=False)
    emergency_response_plan = models.BooleanField(default=False)
    risk_management_plan = models.BooleanField(default=False)
    traffic_management_plan = models.BooleanField(default=False)
    other_info= models.TextField(blank=True)


    def __str__(self):
        return '{}'.format(self.num_participants)

    class Meta:
        app_label = 'commercialoperator'


class ProposalEventVehiclesVessels(models.Model):
    hired_or_owned = models.NullBooleanField(null=True)
    proposal = models.OneToOneField(Proposal, related_name='event_vehicles_vessels', null=True)

    def __str__(self):
        return '{}'.format(self.hired_or_owned)

    class Meta:
        app_label = 'commercialoperator'


class ProposalEventOtherDetails(models.Model):
    training_date= models.DateField(blank=True, null=True)
    insurance_expiry= models.DateField(blank=True, null=True)
    proposal = models.OneToOneField(Proposal, related_name='event_other_details', null=True)
    participants_number = models.CharField(max_length=24,null=True,blank=True)
    officials_number = models.CharField(max_length=24,null=True,blank=True)
    support_vehicle_number = models.CharField(max_length=24,null=True,blank=True)
    other_comments=models.TextField('Other comments', blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.training_date)

    class Meta:
        app_label = 'commercialoperator'

class ProposalEventsParks(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='filming_parks', null=True)
    proposal = models.ForeignKey(Proposal, related_name='events_parks', null=True)
    park= models.ForeignKey(Park, related_name='events_proposal')
    activities_assessor=models.ManyToManyField(Activity, null=True, blank=True)
    event_activities=models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return '{}'.format(self.park)

    class Meta:
        app_label = 'commercialoperator'

    # @property
    # def activities_names(self):
    #     return [a.name for a in self.activities.all()]
    @property
    def activities_assessor_names(self):
        return [a.name for a in self.activities_assessor.all() ] if self.activities_assessor else None


    def add_documents(self, request):
        with transaction.atomic():
            try:
                # save the files
                data = json.loads(request.data.get('data'))
                if not data.get('update'):
                    documents_qs = self.events_park_documents.filter(input_name='events_park_doc', visible=True)
                    documents_qs.delete()
                for idx in range(data['num_files']):
                    _file = request.data.get('file-'+str(idx))
                    document = self.events_park_documents.create(_file=_file, name=_file.name)
                    document.input_name = data['input_name']
                    document.can_delete = True
                    document.save()
                # end save documents
                self.save()
            except:
                raise
        return

class AbseilingClimbingActivity(models.Model):
    proposal = models.ForeignKey(Proposal, related_name='event_abseiling_climbing_activity', null=True)
    event_activities = models.ForeignKey('ProposalEventActivities',related_name='abseiling_climbing_activity_data')
    leader = models.CharField(max_length=255,null=True,blank=True)
    rego_number = models.CharField(max_length=255,null=True,blank=True)
    expiry_date= models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'commercialoperator'


class EventsParkDocument(Document):
    events_park = models.ForeignKey('ProposalEventsParks',related_name='events_park_documents')
    _file = models.FileField(upload_to=update_events_park_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    class Meta:
        app_label = 'commercialoperator'

    def delete(self):
        if self.can_delete:
            return super(EventsParkDocument, self).delete()

class ProposalPreEventsParks(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='filming_parks', null=True)
    proposal = models.ForeignKey(Proposal, related_name='pre_event_parks', null=True)
    park= models.ForeignKey(Park, related_name='pre_event_proposal')
    activities=models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return '{}'.format(self.park)

    class Meta:
        app_label = 'commercialoperator'

    # @property
    # def activities_names(self):
    #     return [a.name for a in self.activities.all()]

    def add_documents(self, request):
        with transaction.atomic():
            try:
                # save the files
                data = json.loads(request.data.get('data'))
                if not data.get('update'):
                    documents_qs = self.pre_event_park_documents.filter(input_name='pre_event_park_doc', visible=True)
                    documents_qs.delete()
                for idx in range(data['num_files']):
                    _file = request.data.get('file-'+str(idx))
                    document = self.pre_event_park_documents.create(_file=_file, name=_file.name)
                    document.input_name = data['input_name']
                    document.can_delete = True
                    document.save()
                # end save documents
                self.save()
            except:
                raise
        return
class PreEventsParkDocument(Document):
    pre_event_park = models.ForeignKey('ProposalPreEventsParks',related_name='pre_event_park_documents')
    _file = models.FileField(upload_to=update_pre_event_park_doc_filename, max_length=512)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    class Meta:
        app_label = 'commercialoperator'

    def delete(self):
        if self.can_delete:
            return super(PreEventsParkDocument, self).delete()

class ProposalEventsTrails(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='filming_parks', null=True)
    proposal = models.ForeignKey(Proposal, related_name='events_trails', null=True)
    trail= models.ForeignKey(Trail, related_name='events_proposal', null=True)
    section= models.ForeignKey(Section, related_name='events_proposal', null=True)
    activities_assessor=models.ManyToManyField(Activity, blank=True, null=True) 
    event_trail_activities=models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return '{}'.format(self.trail)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def activities_assessor_names(self):
        return [a.name for a in self.activities_assessor.all() ] if self.activities_assessor else None


# --------------------------------------------------------------------------------------
# Event Models End
# --------------------------------------------------------------------------------------

import reversion
reversion.register(Referral, follow=['referral_documents', 'assessment'])
reversion.register(ReferralDocument, follow=['referral_document'])

reversion.register(Proposal, follow=['documents', 'onhold_documents','required_documents','qaofficer_documents','comms_logs','other_details', 'parks', 'trails', 'vehicles', 'vessels', 'proposalrequest_set','proposaldeclineddetails', 'proposalonhold', 'requirements', 'referrals', 'qaofficer_referrals', 'compliances', 'referrals', 'approvals', 'park_entries', 'assessment', 'fee_discounts', 'district_proposals', 'filming_parks', 'events_parks', 'pre_event_parks','filming_activity', 'filming_access', 'filming_equipment', 'filming_other_details', 'event_activity', 'event_management', 'event_vehicles_vessels', 'event_other_details','event_abseiling_climbing_activity' ])
reversion.register(ProposalDocument, follow=['onhold_documents'])
reversion.register(ApplicationFeeDiscount)
reversion.register(OnHoldDocument)
reversion.register(ProposalRequest)
reversion.register(ProposalRequiredDocument)
reversion.register(ProposalApplicantDetails)
reversion.register(ProposalActivitiesLand)
reversion.register(ProposalActivitiesMarine)
reversion.register(ProposalOtherDetails, follow=['accreditations'])

reversion.register(ProposalLogEntry, follow=['documents',])
reversion.register(ProposalLogDocument)

#reversion.register(Park, follow=['proposals',])
reversion.register(ProposalPark, follow=['activities','access_types', 'zones'])
reversion.register(ProposalParkAccess)

#reversion.register(AccessType, follow=['proposals','proposalparkaccess_set', 'vehicles'])

#reversion.register(Activity, follow=['proposalparkactivity_set','proposalparkzoneactivity_set', 'proposaltrailsectionactivity_set'])
reversion.register(ProposalParkActivity)

reversion.register(ProposalParkZone, follow=['park_activities'])
reversion.register(ProposalParkZoneActivity)
reversion.register(ParkEntry)

reversion.register(ProposalTrail, follow=['sections'])
reversion.register(Vehicle)
reversion.register(Vessel)
reversion.register(ProposalUserAction)

reversion.register(ProposalTrailSection, follow=['trail_activities'])

reversion.register(ProposalTrailSectionActivity)
reversion.register(AmendmentReason, follow=['amendmentrequest_set'])
reversion.register(AmendmentRequest)
reversion.register(Assessment)
reversion.register(ProposalDeclinedDetails)
reversion.register(ProposalOnHold)
reversion.register(ProposalStandardRequirement, follow=['proposalrequirement_set'])
reversion.register(ProposalRequirement, follow=['compliance_requirement'])
reversion.register(ReferralRecipientGroup, follow=['commercialoperator_referral_groups', 'referral_assessment'])
reversion.register(QAOfficerGroup, follow=['qaofficer_groups'])
reversion.register(QAOfficerReferral)
reversion.register(QAOfficerDocument, follow=['qaofficer_referral_document'])
reversion.register(ProposalAccreditation)
reversion.register(HelpPage)
reversion.register(ChecklistQuestion, follow=['answers'])
reversion.register(ProposalAssessment, follow=['answers'])
reversion.register(ProposalAssessmentAnswer)

#Filming
reversion.register(ProposalFilmingActivity)
reversion.register(ProposalFilmingAccess)
reversion.register(ProposalFilmingEquipment)
reversion.register(ProposalFilmingOtherDetails)
reversion.register(ProposalFilmingParks, follow=['filming_park_documents'])
reversion.register(FilmingParkDocument)
reversion.register(DistrictProposal, follow=['district_compliance', 'district_proposal_requirements', 'district_approvals'])

#Event
reversion.register(ProposalEventActivities, follow=['abseiling_climbing_activity_data'])
reversion.register(ProposalEventManagement)
reversion.register(ProposalEventVehiclesVessels)
reversion.register(ProposalEventOtherDetails)
reversion.register(ProposalEventsParks, follow=['events_park_documents'])
reversion.register(AbseilingClimbingActivity)
reversion.register(EventsParkDocument)
reversion.register(ProposalPreEventsParks, follow=['pre_event_park_documents'])
reversion.register(PreEventsParkDocument)
reversion.register(ProposalEventsTrails)













