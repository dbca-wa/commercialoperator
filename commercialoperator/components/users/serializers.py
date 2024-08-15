from django.conf import settings
from django.db.models import Q
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from commercialoperator.components.stubs.classes import (
    ErsatzAddress as Address,
)  # ledger.accounts.models.Address
from commercialoperator.components.organisations.models import (
    Organisation,
)
from commercialoperator.components.main.models import (
    CommunicationsLogEntry,
    UserSystemSettings,
    Document,
    ApplicationType,
)
from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.organisations.utils import (
    can_admin_org,
    is_consultant,
    is_org_access_member,
)
from commercialoperator.components.stubs.models import (
    EmailUserAction,
    EmailUserLogEntry,
)
from commercialoperator.helpers import in_dbca_domain, is_commercialoperator_admin
from commercialoperator.components.approvals.models import Approval
from rest_framework import serializers
from ledger_api_client.helpers import is_payment_admin
from django.utils import timezone
from datetime import timedelta


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("id", "description", "file", "name", "uploaded_date")


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "line1", "locality", "state", "country", "postcode")


class UserSystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSystemSettings
        fields = ("one_row_per_park",)


class UserOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="organisation.name")
    abn = serializers.CharField(source="organisation.abn")
    email = serializers.SerializerMethodField()
    is_consultant = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    active_proposals = serializers.SerializerMethodField(read_only=True)
    current_event_proposals = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organisation
        fields = (
            "id",
            "name",
            "abn",
            "email",
            "is_consultant",
            "is_admin",
            "active_proposals",
            "current_event_proposals",
        )

    def get_is_admin(self, obj):
        user = EmailUser.objects.get(id=self.context.get("user_id"))
        return can_admin_org(obj, user)

    def get_is_consultant(self, obj):
        user = EmailUser.objects.get(id=self.context.get("user_id"))
        return is_consultant(obj, user)

    def get_email(self, obj):
        email = EmailUser.objects.get(id=self.context.get("user_id")).email
        return email

    def get_active_proposals(self, obj):
        """
        TClass Rules as per email: WGenuit 23/03/2022 12:51pm

        User can apply for the licence type if there is no application for that licence type in status other than (approved, declined, discarded) and
        there is no licence of that licence type in status current or suspended.

        Situations where user cannot apply for the licence type (new, amendment or renewal):
            1. If there is another application from that user for that licence type that is in status Draft, With Assessor, With Referral or With Approver
            2. If there is a licence of that licence type for that user with status Current or Suspended
        """
        _list = []

        today = timezone.localtime(timezone.now()).date()
        for application_type in [ApplicationType.TCLASS]:
            # NOTE: approval__expiry_date__gt=today --> needed in qs because expired (expired and replace_by_id) Migrated licences are showing as 'current'
            qs = (
                Proposal.objects.filter(
                    application_type__name=application_type, org_applicant=obj
                )
                .exclude(
                    Q(processing_status__in=["approved", "declined", "discarded"])
                    & ~Q(
                        approval__status__in=["current", "suspended"],
                        approval__expiry_date__gt=today,
                    )
                )
                .values_list("lodgement_number", flat=True)
            )

            _list.append(dict(application_type=application_type, proposals=qs))

        for application_type in [ApplicationType.FILMING, ApplicationType.EVENT]:
            qs = (
                Proposal.objects.filter(
                    application_type__name=application_type, org_applicant=obj
                )
                .exclude(processing_status__in=["approved", "declined", "discarded"])
                .values_list("lodgement_number", flat=True)
            )
            _list.append(dict(application_type=application_type, proposals=qs))

        return _list

    def get_current_event_proposals(self, obj):
        today = timezone.localtime(timezone.now()).date()
        # Only return the Approvals in last 12 months
        year_date = today - timedelta(days=365)
        _list = []
        # for application_type in ['T Class', 'Filming', 'Event']:
        qs = (
            Approval.objects.filter(
                expiry_date__lte=today,
                expiry_date__gte=year_date,
                current_proposal__application_type__name=ApplicationType.EVENT,
                current_proposal__org_applicant=obj,
            )
            .values(
                "id", "current_proposal", "current_proposal__event_activity__event_name"
            )
            .order_by("id")
        )
        _list.append(dict(application_type=ApplicationType.EVENT, proposals=qs))
        return _list


class UserFilterSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = ("id", "last_name", "first_name", "email", "name")

    def get_name(self, obj):
        return obj.get_full_name()


class UserSerializer(serializers.ModelSerializer):
    commercialoperator_organisations = serializers.SerializerMethodField()
    residential_address = UserAddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    # identification = DocumentSerializer()
    is_department_user = serializers.SerializerMethodField()
    is_payment_admin = serializers.SerializerMethodField()
    system_settings = serializers.SerializerMethodField()
    is_payment_admin = serializers.SerializerMethodField()
    is_commercialoperator_admin = serializers.SerializerMethodField()
    is_org_access_member = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
            "email",
            #'identification',
            "residential_address",
            "phone_number",
            "mobile_number",
            "commercialoperator_organisations",
            "personal_details",
            "address_details",
            "contact_details",
            "full_name",
            "is_department_user",
            "is_payment_admin",
            "is_staff",
            "system_settings",
            "is_commercialoperator_admin",
            "is_org_access_member",
        )

    def get_personal_details(self, obj):
        return True if obj.last_name and obj.first_name else False

    def get_address_details(self, obj):
        return True if obj.residential_address else False

    def get_contact_details(self, obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.phone_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_is_department_user(self, obj):
        if obj.email:
            return in_dbca_domain(obj)
        else:
            return False

    def get_is_payment_admin(self, obj):
        return is_payment_admin(obj)

    def get_commercialoperator_organisations(self, obj):
        commercialoperator_organisations = obj.commercialoperator_organisations
        serialized_orgs = UserOrganisationSerializer(
            commercialoperator_organisations, many=True, context={"user_id": obj.id}
        ).data
        return serialized_orgs

    def get_system_settings(self, obj):
        try:
            user_system_settings = obj.system_settings.first()
            serialized_settings = UserSystemSettingsSerializer(
                user_system_settings
            ).data
            return serialized_settings
        except:
            return None

    def get_is_commercialoperator_admin(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_commercialoperator_admin(request)
        return False

    def get_is_org_access_member(self, obj):
        request = self.context["request"] if self.context else None
        if request:
            return is_org_access_member(request.user)
        return False


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "last_name",
            "first_name",
        )


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "phone_number",
            "mobile_number",
        )

    def validate(self, obj):
        # Mobile and phone number for dbca user are updated from active directory so need to skip these users from validation.
        domain = None
        if obj["email"]:
            domain = obj["email"].split("@")[1]
        if domain in settings.DEPT_DOMAINS:
            return obj
        else:
            if not obj.get("phone_number") and not obj.get("mobile_number"):
                raise serializers.ValidationError(
                    "You must provide a mobile/phone number"
                )
        return obj


class EmailUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source="who.get_full_name")

    class Meta:
        model = EmailUserAction
        fields = "__all__"


class EmailUserCommsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUserLogEntry
        fields = "__all__"


class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=EmailUser.objects.all(), required=False
    )
    documents = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationsLogEntry
        fields = (
            "id",
            "customer",
            "to",
            "fromm",
            "cc",
            "log_type",
            "reference",
            "subject" "text",
            "created",
            "staff",
            "emailuser",
            "documents",
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class EmailUserLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = EmailUserLogEntry
        fields = "__all__"
        read_only_fields = ("customer",)

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]
