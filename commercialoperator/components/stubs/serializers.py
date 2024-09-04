from django.conf import settings
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from rest_framework import serializers

from commercialoperator.components.organisations.models import Organisation
from commercialoperator.components.organisations.utils import can_manage_org
from commercialoperator.components.stubs.models import LedgerOrganisation
from commercialoperator.components.stubs.utils import retrieve_email_user


class EmailUserRoSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "title",
            "organisation",
        )

    def get_id(self, obj):
        return obj

    def get_email(self, obj):
        email_user = retrieve_email_user(obj)
        if email_user:
            return email_user.email
        return None

    def get_first_name(self, obj):
        email_user = retrieve_email_user(obj)
        if email_user:
            return email_user.first_name
        return None

    def get_last_name(self, obj):
        email_user = retrieve_email_user(obj)
        if email_user:
            return email_user.last_name
        return None

    def get_full_name(self, obj):
        email_user = retrieve_email_user(obj)
        if email_user:
            return f"{email_user.first_name} {email_user.last_name}"
        return

    def get_title(self, obj):
        email_user = retrieve_email_user(obj)
        if email_user:
            return email_user.title
        return None

    def get_organisation(self, obj):
        email_user = retrieve_email_user(obj)
        if email_user:
            return email_user.organisation
        return None

    def to_representation(self, instance):
        if settings.DEV_EMAILUSER_REPLACEMENT_ID and not retrieve_email_user(instance):
            # For dev purposes, replace the email user id with the replacement id if the email user does not exist in ledger
            instance = settings.DEV_EMAILUSER_REPLACEMENT_ID
        return super().to_representation(instance)


class OrganisationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="organisation_id", read_only=True)
    pins = serializers.SerializerMethodField(read_only=True)
    delegates = serializers.SerializerMethodField(read_only=True)
    # delegate_organisation_contacts = serializers.ListField(
    #     child=OrganisationContactSerializer(), read_only=True
    # )
    organisation_name = serializers.CharField(read_only=True)
    # contacts = OrganisationContactSerializer(many=True, read_only=True)

    class Meta:
        model = LedgerOrganisation
        fields = (
            "id",
            "organisation_id",
            "organisation_name",
            "organisation_trading_name",
            "organisation_abn",
            "organisation_email",
            # "phone_number",
            "pins",
            "delegates",
            # "delegate_organisation_contacts",
            # "contacts",
            # "address",
        )

    def get_trading_name(self, obj):
        return obj.ledger_organisation_name

    def get_pins(self, obj):
        try:
            user = self.context["request"].user
            org = Organisation.objects.get(organisation_id=obj.organisation_id)
            # Check if the request user is among the first five delegates in the organisation
            if can_manage_org(org, user):
                return {
                    "one": obj.admin_pin_one,
                    "two": obj.admin_pin_two,
                    "three": obj.user_pin_one,
                    "four": obj.user_pin_two,
                }
            else:
                return None
        except KeyError:
            return None

    def get_delegates(self, obj):
        return None

    #     user_delegate_ids = UserDelegation.objects.filter(organisation=obj).values_list(
    #         "user", flat=True
    #     )
    #     return BasicOrganisationContactSerializer(
    #         obj.contacts.filter(
    #             user_status="active",
    #             user_role="organisation_admin",
    #             user__in=user_delegate_ids,
    #         ).order_by("user_role", "first_name"),
    #         many=True,
    #         read_only=True,
    #     ).data


class OrganisationListSerializer(OrganisationSerializer):
    name = serializers.CharField(source="organisation_name", read_only=True)

    class Meta:
        model = LedgerOrganisation
        fields = (
            "id",
            "name",
            "organisation_id",
            "organisation_name",
            "organisation_trading_name",
            "organisation_abn",
            "organisation_email",
            "pins",
            "delegates",
        )
        read_only_fields = fields
        extra_kwargs = {field: {"read_only": True} for field in fields}
