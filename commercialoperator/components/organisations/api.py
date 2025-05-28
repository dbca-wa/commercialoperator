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
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from ledger_api_client.utils import update_organisation_obj, get_all_organisation

from commercialoperator.components.approvals.serializers import EmailUserSerializer
from commercialoperator.components.organisations.utils import can_admin_org
from commercialoperator.components.permission.permission import organisation_permissions
from commercialoperator.components.segregation.api import LedgerOrganisationFilterBackend
from commercialoperator.components.segregation.decorators import basic_exception_handler
from commercialoperator.components.segregation.utils import (
    filter_organisation_list,
    retrieve_delegate_organisation_ids,
    retrieve_email_user,
    retrieve_organisation_delegate_ids,
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
    allow_external = False  # NOTE: Workaround for allowing organisations to be accessed when validating pins

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request) or self.allow_external:
            return Organisation.objects.all()
        elif is_customer(self.request):
            user_orgs = retrieve_delegate_organisation_ids(user.id)
            return Organisation.objects.filter(organisation_id__in=user_orgs)
        return Organisation.objects.none()

    def get_object(self):
        org_id = self.kwargs.get("pk", None)
        if not org_id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "An Organisation PK is required"},
            )

        is_ledger_org_query = bool(self.request.POST.get("is_ledger_org_query", False))
        if is_ledger_org_query:
            try:
                return self.get_queryset().get(organisation_id=org_id)
            except Organisation.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={
                        "message": f"Organisation with ledger id {org_id} not found not found in COLS"
                    },
                )
        else:
            try:
                return super().get_object()
            except Organisation.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "message": f"Organisation does not exist in COLS.{"Did you attempt to query a ledger organisation in COLS?" if not is_ledger_org_query else ""}"
                    }
                )
            except serializers.ValidationError:
                raise serializers.ValidationError(
                    {"message": "Organisation does not exist"}
                )

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
    @basic_exception_handler
    def contacts_exclude(self, request, *args, **kwargs):
        ledger_organisation_id = kwargs.get("pk", None)
        if not ledger_organisation_id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "An Organisation ID is required"},
            )

        try:
            cols_organisation = Organisation.objects.get(
                organisation_id=ledger_organisation_id
            )
        except Organisation.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": "Organisation not found"},
            )

        contacts = cols_organisation.contacts.exclude(user_status="draft")
        serializer = OrganisationContactSerializer(contacts, many=True)

        return Response(serializer.data)

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def validate_pins(self, request, *args, **kwargs):
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
    @basic_exception_handler
    def unlink_user(self, request, *args, **kwargs):
        self.allow_external = True
        instance = self.get_object()

        user_obj = self.request.user
        user_data = EmailUserSerializer(user_obj.id).data
        serializer = OrgUserAcceptSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        instance.unlink_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
    @basic_exception_handler
    def relink_user(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrgUserAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = EmailUser.objects.get(
            email=serializer.validated_data["email"].lower()
        )
        instance.relink_user(user_obj, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
    @basic_exception_handler
    @transaction.atomic
    def add_comms_log(self, request, *args, **kwargs):
        instance = self.get_object()
        mutable = request.data._mutable
        request.data._mutable = True
        request.data["organisation"] = "{}".format(instance.id)
        request.data["staff_id"] = "{}".format(request.user.id)
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

    @action(
        methods=[
            "POST",
        ],
        detail=False,
    )
    @basic_exception_handler
    def existance(self, request, *args, **kwargs):
        serializer = OrganisationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get("name", None)
        abn = serializer.validated_data.get("abn", None)
        data = Organisation.existance(name, abn)
        # Check request user cannot be relinked to org.
        data.update([("user", request.user.id)])
        data.update([("abn", request.data["abn"])])
        serializer = OrganisationCheckExistSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def update_details(self, request, *args, **kwargs):
        instance = self.get_object()
        if not can_admin_org(instance, request.user.id):
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={
                    "message": "You do not have permission to update this organisation."
                },
            )

        serializer = DetailsSerializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

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

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def update_address(self, request, *args, **kwargs):
        raise NotImplementedError(
            "Updating addresses needs to be implemented in ledger api client"
        )
        instance = self.get_object()
        request.data["organisation_id"] = instance.organisation_id
        return self.update_details(request, *args, **kwargs)

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def upload_id(self, request, *args, **kwargs):
        pass

    @action(
        methods=[
            "GET",
        ],
        detail=False,
        # permission_classes=[IsAuthenticated],
    )
    def organisation_lookup(self, request, *args, **kwargs):
        filtered_organisations = filter_organisation_list(
            self, request, *args, **kwargs
        )
        organisation_ids = [o.organisation_id for o in filtered_organisations]
        organisations = self.get_queryset().filter(organisation_id__in=organisation_ids)

        data_transform = [
            {
                "id": organisation.id,
                "text": f"{organisation.name} (ABN: {organisation.abn})",
                "first_five": organisation.first_five,
            }
            for organisation in organisations
        ]
        return Response({"results": data_transform})

    @action(
        methods=[
            "GET",
        ],
        detail=False,
        # permission_classes=[IsAuthenticated],
    )
    @basic_exception_handler
    def linked_organisation(self, request, *args, **kwargs):
        org_id = request.GET.get("org_id", None)
        if not org_id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "An Organisation ID is required"},
            )
        try:
            org = self.get_queryset().get(organisation_id=org_id)
        except Organisation.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": f"Organisation with ledger id {org_id} not found"},
            )
        else:
            if not organisation_permissions(request, org_id):
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={
                        "message": "You do not have permission to view this organisation."
                    },
                )

        serializer = OrganisationSerializer(org, context={"request": request})

        return Response(serializer.data)


class OrganisationListFilterView(generics.ListAPIView):
    queryset = Organisation.objects.none()
    serializer_class = LedgerOrganisationFilterSerializer
    filter_backends = (LedgerOrganisationFilterBackend,)
    search_fields = (
        "organisation_name",
        "organisation_trading_name",
        "organisation_abn",
    )

    def get_queryset(self):
        org_list = Organisation.objects.all().values_list("organisation_id", flat=True)
        return Organisation.objects.filter(id__in=org_list)

    def list(self, request, *args, **kwargs):
        from commercialoperator.components.segregation.serializers import (
            OrganisationListSerializer,
        )

        organisations = filter_organisation_list(self, request, *args, **kwargs)
        serializer = OrganisationListSerializer(
            organisations, many=True, context={"request": request}
        )

        return Response(serializer.data)


class OrganisationRequestDatatableFilterBackend(DatatablesFilterBackend):
    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        applicant = request.GET.get("filter_applicant", "All")
        if applicant != "All":
            raise serializers.ValidationError("Filtering by applicant is not supported")

        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)

        queryset = super(
            OrganisationRequestDatatableFilterBackend, self
        ).filter_queryset(request, queryset, view)
        setattr(view, "_datatables_total_count", total_count)

        return queryset


class OrganisationRequestsViewSet(viewsets.ModelViewSet):
    http_method_names = ["head", "get", "post", "put", "patch"]

    queryset = OrganisationRequest.objects.none()
    serializer_class = OrganisationRequestSerializer
    filter_backends = (OrganisationRequestDatatableFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    page_size = 10
    ordering = ("lodgement_date",)

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return OrganisationRequest.objects.all()
        elif is_customer(self.request):
            user_org_ids = retrieve_delegate_organisation_ids(user.id)
            user_organisations = Organisation.objects.filter(
                organisation_id__in=user_org_ids
            )
            user_organisation_abns = [org.abn for org in user_organisations]

            # NOTE: Adding organisation requests where the user is a delegate here, on top of being a requester
            return OrganisationRequest.objects.filter(
                Q(abn__in=user_organisation_abns) | Q(requester_id=user)
            )

        return OrganisationRequest.objects.none()

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    @basic_exception_handler
    def linked_organisations(self, request, *args, **kwargs):
        user_id = request.user.id
        qs = self.get_queryset()
        # qs = self.get_queryset().filter(id=1079) # An existing organisation request for testing

        # Ledger organisation ids
        ledger_org_ids = []
        # Get all organisations from ledger in advance to not otherwise query ledger in each loop
        all_organisations_response = get_all_organisation()
        if all_organisations_response.get("status") != status.HTTP_200_OK:
            raise serializers.ValidationError(
                "Error fetching organisations from ledger"
            )
        ledger_organisation_data = all_organisations_response.get("data", [])
        # Retrieve ledger organisation ids by ABN for which there is an organisation request
        organisation_request_abns = [org_req.abn for org_req in qs]
        ledger_org_ids = [
            d["organisation_id"]
            for d in ledger_organisation_data
            if d["organisation_abn"] in organisation_request_abns
        ]
        ledger_org_ids = list(set(ledger_org_ids))
        # Get COLS organisation ids for the ledger organisation ids (there is no abn field in organisation model, so have to take a little detour)
        organisation_ids = Organisation.objects.filter(
            organisation_id__in=ledger_org_ids
        ).values_list("id", flat=True)
        # Of those, get the COLS organisation ids where the user is a delegate
        user_delegate_organisation_ids = [
            oid
            for oid in organisation_ids
            if user_id in retrieve_organisation_delegate_ids(oid)
        ]
        # Get the organisation ABNs for the user delegate organisations
        organisation_abns = [
            org.abn
            for org in Organisation.objects.filter(
                id__in=user_delegate_organisation_ids
            )
        ]

        serializer = OrganisationRequestSerializer(
            qs.filter(abn__in=organisation_abns),
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    @basic_exception_handler
    def datatable_list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = OrganisationRequestDTSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)

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
    @basic_exception_handler
    def assign_request_user(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.assign_to(request.user, request)
        serializer = OrganisationRequestSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def unassign(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.unassign(request)
        serializer = OrganisationRequestSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def accept(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.accept(request)
        serializer = OrganisationRequestSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    @basic_exception_handler
    def amendment_request(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.amendment_request(request)
        serializer = OrganisationRequestSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=[
            "PUT",
        ],
        detail=True,
    )
    @basic_exception_handler
    def reupload_identification_amendment_request(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.reupload_identification_amendment_request(request)
        serializer = OrganisationRequestSerializer(
            instance, partial=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def decline(self, request, *args, **kwargs):
        instance = self.get_object()
        reason = ""
        instance.decline(reason, request)
        serializer = OrganisationRequestSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @basic_exception_handler
    def assign_to(self, request, *args, **kwargs):
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
        serializer = OrganisationRequestSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

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
    @basic_exception_handler
    @transaction.atomic
    def add_comms_log(self, request, *args, **kwargs):
        instance = self.get_object()
        mutable = request.data._mutable
        request.data._mutable = True
        request.data["organisation"] = "{}".format(instance.id)
        request.data["request"] = "{}".format(instance.id)
        request.data["staff_id"] = "{}".format(request.user.id)
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

    @basic_exception_handler
    def create(self, request, *args, **kwargs):
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
                OrganisationRequestUserAction.ACTION_LODGE_REQUEST.format(instance.id),
                request,
            )
            instance.send_organisation_request_email_notification(request)
        return Response(serializer.data)


class OrganisationAccessGroupMembersView(views.APIView):

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
            user_orgs = retrieve_delegate_organisation_ids(user.id)
            return Organisation.objects.filter(organisation_id__in=user_orgs)
        return Organisation.objects.none()
