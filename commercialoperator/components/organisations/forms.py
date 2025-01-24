from django import forms
from commercialoperator.components.organisations.models import OrganisationAccessGroup

from ledger_api_client.ledger_models import EmailUserRO as EmailUser


class OrganisationAccessGroupAdminForm(forms.ModelForm):
    class Meta:
        model = OrganisationAccessGroup
        fields = [
            # "site",
        ]
