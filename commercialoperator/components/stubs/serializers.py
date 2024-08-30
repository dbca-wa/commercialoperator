from django.conf import settings
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from rest_framework import serializers

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
