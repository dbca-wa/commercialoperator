import traceback
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from django_countries import countries
from rest_framework import viewsets, serializers, generics, views
from rest_framework.decorators import renderer_classes
from rest_framework.decorators import action as detail_route
from rest_framework.decorators import action as list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from commercialoperator.components.stubs.models import EmailUserAction
from commercialoperator.components.stubs.classes import Address

from commercialoperator.components.users.serializers import (
    UserSerializer,
    UserFilterSerializer,
    UserAddressSerializer,
    ContactSerializer,
    EmailUserActionSerializer,
    EmailUserCommsSerializer,
    EmailUserLogEntrySerializer,
    UserSystemSettingsSerializer,
)
from commercialoperator.components.organisations.serializers import (
    OrganisationRequestDTSerializer,
)
from commercialoperator.components.main.models import UserSystemSettings
from commercialoperator.helpers import is_customer, is_internal

# class DepartmentUserList(views.APIView):
#     renderer_classes = [JSONRenderer,]
#     def get(self, request, format=None):
#         data = cache.get('department_users')
#         if not data:
#             retrieve_department_users()
#             data = cache.get('department_users')
#         return Response(data)

#         serializer  = UserSerializer(request.user)


class GetCountries(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        country_list = []
        for country in list(countries):
            country_list.append({"name": country.name, "code": country.code})
        return Response(country_list)


class GetProfile(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


from rest_framework import filters


class UserListFilterView(generics.ListAPIView):
    """https://cop-internal.dbca.wa.gov.au/api/filtered_users?search=russell"""

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return EmailUser.objects.all()
        elif is_customer(self.request):
            qs = EmailUser.objects.filter(Q(id=user.id))
            return qs
        return EmailUser.objects.none()

    queryset = get_queryset
    serializer_class = UserFilterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("email", "first_name", "last_name")


class UserViewSet(viewsets.ModelViewSet):
    queryset = EmailUser.objects.none()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return EmailUser.objects.all()
        elif is_customer(self.request):
            qs = EmailUser.objects.filter(Q(id=user.id))
            return qs
        return EmailUser.objects.none()

    #    @detail_route(methods=['POST',])
    #    def update_personal(self, request, *args, **kwargs):
    #        try:
    #            instance = self.get_object()
    #            serializer = PersonalSerializer(instance,data=request.data)
    #            serializer.is_valid(raise_exception=True)
    #            instance = serializer.save()
    #            serializer = UserSerializer(instance)
    #            return Response(serializer.data);
    #        except serializers.ValidationError:
    #            print(traceback.print_exc())
    #            raise
    #        except ValidationError as e:
    #            print(traceback.print_exc())
    #            raise serializers.ValidationError(repr(e.error_dict))
    #        except Exception as e:
    #            print(traceback.print_exc())
    #            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def update_contact(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ContactSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
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

    # @detail_route(methods=['POST',])
    # def update_address(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         serializer = UserAddressSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         address, created = Address.objects.get_or_create(
    #             line1 = serializer.validated_data['line1'],
    #             locality = serializer.validated_data['locality'],
    #             state = serializer.validated_data['state'],
    #             country = serializer.validated_data['country'],
    #             postcode = serializer.validated_data['postcode'],
    #             user = instance
    #         )
    #         instance.residential_address = address
    #         instance.save()
    #         serializer = UserSerializer(instance)
    #         return Response(serializer.data);
    #     except serializers.ValidationError:
    #         print(traceback.print_exc())
    #         raise
    #     except ValidationError as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(repr(e.error_dict))
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def update_address(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if instance.residential_address:
                address = Address.objects.filter(id=instance.residential_address.id)
                total_addresses = address.count()
                if total_addresses > 0:
                    residential_address = Address.objects.get(id=address[0].id)
                    residential_address.locality = serializer.validated_data["locality"]
                    residential_address.state = serializer.validated_data["state"]
                    residential_address.country = serializer.validated_data["country"]
                    residential_address.postcode = serializer.validated_data["postcode"]
                    residential_address.line1 = serializer.validated_data["line1"]
                    residential_address.save()
                    instance.residential_address = residential_address
            else:
                address = Address.objects.create(
                    line1=serializer.validated_data["line1"],
                    locality=serializer.validated_data["locality"],
                    state=serializer.validated_data["state"],
                    country=serializer.validated_data["country"],
                    postcode=serializer.validated_data["postcode"],
                    user=instance,
                )
                address.save()
                instance.residential_address = address
                instance.save()

            with transaction.atomic():
                instance.save()
                serializer = UserSerializer(instance)
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

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def update_system_settings(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # serializer = UserSystemSettingsSerializer(data=request.data)
            # serializer.is_valid(raise_exception=True)
            user_setting, created = UserSystemSettings.objects.get_or_create(
                user=instance
            )
            serializer = UserSystemSettingsSerializer(user_setting, data=request.data)
            serializer.is_valid(raise_exception=True)
            # instance.residential_address = address
            serializer.save()
            instance = self.get_object()
            serializer = UserSerializer(instance)
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

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def upload_id(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.upload_identification(request)
            with transaction.atomic():
                instance.save()
                instance.log_user_action(
                    EmailUserAction.ACTION_ID_UPDATE.format(
                        "{} {} ({})".format(
                            instance.first_name, instance.last_name, instance.email
                        )
                    ),
                    request,
                )
            serializer = UserSerializer(instance, partial=True)
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

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def pending_org_requests(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationRequestDTSerializer(
                instance.organisationrequest_set.filter(status="with_assessor"),
                many=True,
                context={"request": request},
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

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = EmailUserActionSerializer(qs, many=True)
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

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = EmailUserCommsSerializer(qs, many=True)
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

    @detail_route(
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
                request.data["emailuser"] = "{}".format(instance.id)
                request.data["staff"] = "{}".format(request.user.id)
                request.data._mutable = mutable
                serializer = EmailUserLogEntrySerializer(data=request.data)
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

    @list_route(
        methods=[
            "GET",
        ]
    )
    def get_department_users(self, request, *args, **kwargs):
        try:
            search_term = request.GET.get("term", "")
            # serializer = UserSerializer(
            #        staff,
            #        many=True
            #        )
            # return Response(serializer.data)
            data = (
                self.get_queryset()
                .filter(is_staff=True)
                .filter(
                    Q(first_name__icontains=search_term)
                    | Q(last_name__icontains=search_term)
                )
                .values("email", "first_name", "last_name")[:10]
            )
            data_transform = [
                {
                    "id": person["email"],
                    "text": person["first_name"] + " " + person["last_name"],
                }
                for person in data
            ]
            return Response({"results": data_transform})
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
