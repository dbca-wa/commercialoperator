from django import forms
from commercialoperator.components.organisations.models import OrganisationAccessGroup

from ledger_api_client.ledger_models import EmailUserRO as EmailUser


class OrganisationAccessGroupAdminForm(forms.ModelForm):
    class Meta:
        model = OrganisationAccessGroup
        fields = [
            # "site",
        ]

    def __init__(self, *args, **kwargs):
        super(OrganisationAccessGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            # Note: adding the members here programmatically does not work yet
            self.fields["members"] = forms.ModelMultipleChoiceField(
                queryset=EmailUser.objects.filter(is_staff=True),
                required=True,
                widget=forms.SelectMultiple,
            )
            # self.fields["members"].queryset = EmailUser.objects.filter(is_staff=True)
