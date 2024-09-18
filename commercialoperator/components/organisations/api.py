import traceback
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import renderer_classes, action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.utils import update_organisation_obj

from commercialoperator.components.organisations.utils import can_admin_org
from commercialoperator.components.stubs.api import LedgerOrganisationFilterBackend
from commercialoperator.components.stubs.utils import (
    filter_organisation_list,
    retrieve_email_user,
)
from commercialoperator.helpers import is_customer, is_internal
from commercialoperator.components.organisations.models import (
    Organisation,
    OrganisationContact,
    OrganisationRequest,
    OrganisationRequestUserAction,
    OrganisationContact,
    OrganisationAccessGroup,
    # ledger_organisation,
)

from commercialoperator.components.organisations.serializers import (
    OrganisationSerializer,
    OrganisationAddressSerializer,
    DetailsSerializer,
    SaveDiscountSerializer,
    OrganisationRequestSerializer,
    OrganisationRequestDTSerializer,
    OrganisationContactSerializer,
    OrganisationCheckSerializer,
    OrganisationPinCheckSerializer,
    OrganisationRequestActionSerializer,
    OrganisationActionSerializer,
    OrganisationRequestCommsSerializer,
    OrganisationCommsSerializer,
    OrgUserAcceptSerializer,
    MyOrganisationsSerializer,
    OrganisationCheckExistSerializer,
    LedgerOrganisationFilterSerializer,
    OrganisationLogEntrySerializer,
    OrganisationRequestLogEntrySerializer,
)


class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.none()
    serializer_class = OrganisationSerializer
    allow_external = False  # TODO: review this - workaround for allowing organisations to be accessed when validating pins

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request) or self.allow_external:
            return Organisation.objects.all()
        elif is_customer(self.request):
            # org_contacts = OrganisationContact.objects.filter(is_admin=True).filter(email=user.email) #TODO: is there a better way than email?
            # user_admin_orgs = [org.organisation.id for org in org_contacts]
            # return Organisation.objects.filter(id__in=user_admin_orgs)
            return user.commercialoperator_organisations.all()
        return Organisation.objects.none()

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def contacts(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationContactSerializer(
                instance.contacts.exclude(user_status="pending"), many=True
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def contacts_linked(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = OrganisationContactSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def contacts_exclude(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.contacts.exclude(user_status="draft")
            serializer = OrganisationContactSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def validate_pins(self, request, *args, **kwargs):
        try:
            self.allow_external = True
            instance = self.get_object()
            serializer = OrganisationPinCheckSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ret = instance.validate_pins(
                serializer.validated_data["pin1"],
                serializer.validated_data["pin2"],
                request,
            )

            if ret == None:
                # user has already been to this organisation - don't add again
                data = {"valid": ret}
                return Response({"valid": "User already exists"})

            data = {"valid": ret}
            if data["valid"]:
                # Notify each Admin member of request.
                instance.send_organisation_request_link_notification(request)
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def accept_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.accept_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def accept_declined_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.accept_declined_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def decline_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.decline_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def unlink_user(self, request, *args, **kwargs):
        try:
            self.allow_external = True
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.unlink_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def make_admin_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.make_admin_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def make_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.make_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def make_consultant(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.make_consultant(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def suspend_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.suspend_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def reinstate_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.reinstate_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def relink_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data["email"].lower()
            )
            instance.relink_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = OrganisationActionSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    #    @action(methods=['GET',])
    #    def applications(self, request, *args, **kwargs):
    #        try:
    #            instance = self.get_object()
    #            qs = instance.org_applications.all()
    #            serializer = BaseApplicationSerializer(qs,many=True)
    #            return Response(serializer.data)
    #        except serializers.ValidationError:
    #            print(traceback.print_exc())
    #            raise
    #        except ValidationError as e:
    #            print(traceback.print_exc())
    #            raise serializers.ValidationError(repr(e.error_dict))
    #        except Exception as e:
    #            print(traceback.print_exc())
    #            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = OrganisationCommsSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                mutable = request.data._mutable
                request.data._mutable = True
                request.data["organisation"] = "{}".format(instance.id)
                request.data["staff"] = "{}".format(request.user.id)
                request.data._mutable = mutable
                serializer = OrganisationLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=False,
    )
    def existance(self, request, *args, **kwargs):
        try:
            serializer = OrganisationCheckSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = Organisation.existance(serializer.validated_data["abn"])
            # Check request user cannot be relinked to org.
            data.update([("user", request.user.id)])
            data.update([("abn", request.data["abn"])])
            serializer = OrganisationCheckExistSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def update_details(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not can_admin_org(instance, request.user.id):
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={
                        "message": "You do not have permission to update this organisation."
                    },
                )
            # Note: Calling this function doesn't update the ledger name, trading name, email entries.
            response_ledger = update_organisation_obj(request.data)
            response_ledger_status = response_ledger.get("status", None)
            if not response_ledger_status == status.HTTP_200_OK:
                return Response(
                    status=response_ledger_status,
                    data=response_ledger.get("message", None),
                )

            cache.delete(
                settings.CACHE_KEY_LEDGER_ORGANISATION.format(instance.organisation_id)
            )

            serializer = DetailsSerializer(
                instance, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            if is_internal(request) and "apply_application_discount" in request.data:
                data = request.data
                if not data["apply_application_discount"]:
                    data["application_discount"] = 0
                if not data["apply_licence_discount"]:
                    data["licence_discount"] = 0

                if data["application_discount"] == 0:
                    data["apply_application_discount"] = False
                if data["licence_discount"] == 0:
                    data["apply_licence_discount"] = False

                if (
                    is_internal(request)
                    and "charge_once_per_year" in request.data
                    and request.data.get("charge_once_per_year")
                ):
                    DD = int(request.data.get("charge_once_per_year").split("/")[0])
                    MM = int(request.data.get("charge_once_per_year").split("/")[1])
                    YYYY = timezone.now().year  # set to current year
                    data["charge_once_per_year"] = "{}-{}-{}".format(YYYY, MM, DD)
                else:
                    data["charge_once_per_year"] = None

                serializer = SaveDiscountSerializer(instance, data=data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()

            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            print(e.get_full_details())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            if hasattr(e, "message"):
                raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def update_address(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            request.data["organisation_id"] = instance.organisation_id
            return self.update_details(request, *args, **kwargs)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def upload_id(self, request, *args, **kwargs):
        pass


class OrganisationListFilterView(generics.ListAPIView):
    """https://cop-internal.dbca.wa.gov.au/api/filtered_organisations?search=Org1"""

    queryset = Organisation.objects.none()
    serializer_class = LedgerOrganisationFilterSerializer
    # filter_backends = (filters.SearchFilter,)
    filter_backends = (LedgerOrganisationFilterBackend,)
    search_fields = (
        # "name",
        # "trading_name",
        "organisation_name",
        "organisation_trading_name",
    )

    def get_queryset(self):
        org_list = Organisation.objects.all().values_list("organisation_id", flat=True)
        return Organisation.objects.filter(id__in=org_list)

    def list(self, request, *args, **kwargs):
        from commercialoperator.components.stubs.serializers import (
            OrganisationListSerializer,
        )

        organisations = filter_organisation_list(self, request, *args, **kwargs)
        serializer = OrganisationListSerializer(
            organisations, many=True, context={"request": request}
        )

        return Response(serializer.data)


class OrganisationRequestsViewSet(viewsets.ModelViewSet):
    queryset = OrganisationRequest.objects.none()
    serializer_class = OrganisationRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return OrganisationRequest.objects.all()
        elif is_customer(self.request):
            return user.organisationrequest_set.all()
        return OrganisationRequest.objects.none()

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def datatable_list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        try:
            serializer = OrganisationRequestDTSerializer(qs, many=True)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
        else:
            return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def get_pending_requests(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(
                requester=request.user, status="with_assessor"
            )
            serializer = OrganisationRequestDTSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def get_amendment_requested_requests(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(
                requester=request.user, status="amendment_requested"
            )
            serializer = OrganisationRequestDTSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_to(request.user, request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            # print(traceback.print_exc())
            # raise serializers.ValidationError(repr(e.error_dict))
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.amendment_request(request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "PUT",
        ],
        detail=True,
    )
    def reupload_identification_amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reupload_identification_amendment_request(request)
            serializer = OrganisationRequestSerializer(instance, partial=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            reason = ""
            instance.decline(reason, request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get("user_id", None)
            user = None
            if not user_id:
                raise serializers.ValiationError("A user id is required")
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError(
                    "A user with the id passed in does not exist"
                )
            instance.assign_to(user, request)
            serializer = OrganisationRequestSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = OrganisationRequestActionSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = OrganisationRequestCommsSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                mutable = request.data._mutable
                request.data._mutable = True
                request.data["organisation"] = "{}".format(instance.id)
                request.data["request"] = "{}".format(instance.id)
                request.data["staff"] = "{}".format(request.user.id)
                request.data._mutable = mutable
                serializer = OrganisationRequestLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["requester"] = request.user
            if request.data["role"] == "consultant":
                # Check if consultant can be relinked to org.
                data = Organisation.existance(request.data["abn"])
                data.update([("user", request.user.id)])
                data.update([("abn", request.data["abn"])])
                existing_org = OrganisationCheckExistSerializer(data=data)
                existing_org.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.log_user_action(
                    OrganisationRequestUserAction.ACTION_LODGE_REQUEST.format(
                        instance.id
                    ),
                    request,
                )
                instance.send_organisation_request_email_notification(request)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class OrganisationAccessGroupMembers(views.APIView):

    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        members = []
        if is_internal(request):
            group = OrganisationAccessGroup.objects.first()
            if group:
                for m in group.all_members:
                    emailuser = retrieve_email_user(m)
                    if emailuser:
                        full_name = f"{emailuser.first_name} {emailuser.last_name}"
                        members.append(
                            {
                                "name": full_name,
                                "id": m,
                            }
                        )
            else:
                for m in EmailUser.objects.filter(
                    is_superuser=True, is_staff=True, is_active=True
                ):
                    emailuser = retrieve_email_user(m)
                    if emailuser:
                        full_name = f"{emailuser.first_name} {emailuser.last_name}"
                        members.append({"name": full_name, "id": m.id})
        return Response(members)


class OrganisationContactViewSet(viewsets.ModelViewSet):
    serializer_class = OrganisationContactSerializer
    queryset = OrganisationContact.objects.none()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return OrganisationContact.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return OrganisationContact.objects.filter(Q(organisation_id__in=user_orgs))
        return OrganisationContact.objects.none()

    def destroy(self, request, *args, **kwargs):
        """delete an Organisation contact"""
        num_admins = (
            self.get_object().organisation.contacts.filter(is_admin=True).count()
        )
        org_contact = self.get_object().organisation.contacts.get(id=kwargs["pk"])
        if num_admins == 1 and org_contact.is_admin:
            raise serializers.ValidationError(
                "Cannot delete the last Organisation Admin"
            )
        return super(OrganisationContactViewSet, self).destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "contact_form" in request.data.get("user_status"):
            serializer.save(user_status="contact_form")
        else:
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyOrganisationsViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.none()
    serializer_class = MyOrganisationsSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Organisation.objects.all()
        elif is_customer(self.request):
            return user.commercialoperator_organisations.all()
        return Organisation.objects.none()
