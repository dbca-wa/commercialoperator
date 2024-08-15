import traceback
import json
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers
from rest_framework.decorators import detail_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from commercialoperator.components.proposals.models import ProposalUserAction

from commercialoperator.components.proposals.models import (
    ProposalEventsParks,
    AbseilingClimbingActivity,
    PreEventsParkDocument,
    ProposalPreEventsParks,
    ProposalEventsTrails,
)
from commercialoperator.components.proposals.serializers_event import (
    ProposalEventsParksSerializer,
    SaveProposalEventsParksSerializer,
    AbseilingClimbingActivitySerializer,
    ProposalPreEventsParksSerializer,
    SaveProposalPreEventsParksSerializer,
    ProposalEventsTrailsSerializer,
    SaveProposalEventsTrailsSerializer,
)

from commercialoperator.helpers import is_customer, is_internal

import logging

logger = logging.getLogger(__name__)


class ProposalEventsParksViewSet(viewsets.ModelViewSet):
    queryset = ProposalEventsParks.objects.none()
    serializer_class = ProposalEventsParksSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ProposalEventsParks.objects.all().order_by("id")
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return ProposalEventsParks.objects.filter(
                Q(proposal_id__org_applicant_id__in=user_orgs)
                | Q(proposal_id__submitter=user)
            ).order_by("id")
        return ProposalEventsParks.objects.none()

    @detail_route(methods=["post"])
    def edit_park(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SaveProposalEventsParksSerializer(
                instance, data=json.loads(request.data.get("data"))
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # instance.add_documents(request)
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_EDIT_EVENT_PARK.format(instance.id), request
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            # instance = self.get_object()
            serializer = SaveProposalEventsParksSerializer(
                data=json.loads(request.data.get("data"))
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            # instance.add_documents(request)
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_CREATE_EVENT_PARK.format(instance.id), request
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ]
    )
    @renderer_classes((JSONRenderer,))
    def delete_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            EventsParkDocument.objects.get(id=request.data.get("id")).delete()
            return Response(
                [
                    dict(id=i.id, name=i.name, _file=i._file.url)
                    for i in instance.filming_park_documents.all()
                ]
            )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class AbseilingClimbingActivityViewSet(viewsets.ModelViewSet):
    queryset = AbseilingClimbingActivity.objects.none()
    serializer_class = AbseilingClimbingActivitySerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return AbseilingClimbingActivity.objects.all().order_by("id")
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return AbseilingClimbingActivity.objects.filter(
                Q(proposal_id__org_applicant_id__in=user_orgs)
                | Q(proposal_id__submitter=user)
            ).order_by("id")
        return AbseilingClimbingActivity.objects.none()

    @detail_route(methods=["post"])
    def edit_abseiling_climbing(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = AbseilingClimbingActivitySerializer(
                instance, data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_EDIT_ABSEILING_CLIMBING_ACTIVITY.format(
                    instance.id
                ),
                request,
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ProposalPreEventsParksViewSet(viewsets.ModelViewSet):
    queryset = ProposalPreEventsParks.objects.none()
    serializer_class = ProposalPreEventsParksSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ProposalPreEventsParks.objects.all().order_by("id")
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return ProposalPreEventsParks.objects.filter(
                Q(proposal_id__org_applicant_id__in=user_orgs)
                | Q(proposal_id__submitter=user)
            ).order_by("id")
        return ProposalPreEventsParks.objects.none()

    @detail_route(methods=["post"])
    def edit_park(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SaveProposalPreEventsParksSerializer(
                instance, data=json.loads(request.data.get("data"))
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance.add_documents(request)
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_EDIT_PRE_EVENT_PARK.format(instance.id),
                request,
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            # instance = self.get_object()
            serializer = SaveProposalPreEventsParksSerializer(
                data=json.loads(request.data.get("data"))
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            instance.add_documents(request)
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_CREATE_PRE_EVENT_PARK.format(instance.id),
                request,
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ]
    )
    @renderer_classes((JSONRenderer,))
    def delete_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            PreEventsParkDocument.objects.get(id=request.data.get("id")).delete()
            return Response(
                [
                    dict(id=i.id, name=i.name, _file=i._file.url)
                    for i in instance.pre_event_park_documents.all()
                ]
            )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ProposalEventsTrailsViewSet(viewsets.ModelViewSet):
    queryset = ProposalEventsTrails.objects.none()
    serializer_class = ProposalEventsTrailsSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ProposalEventsTrails.objects.all().order_by("id")
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return ProposalEventsTrails.objects.filter(
                Q(proposal_id__org_applicant_id__in=user_orgs)
                | Q(proposal_id__submitter=user)
            ).order_by("id")
        return ProposalEventsTrails.objects.none()

    @detail_route(methods=["post"])
    def edit_trail(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SaveProposalEventsTrailsSerializer(
                instance, data=json.loads(request.data.get("data"))
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # instance.add_documents(request)
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_EDIT_EVENT_PARK.format(instance.id), request
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            # instance = self.get_object()
            serializer = SaveProposalEventsTrailsSerializer(
                data=json.loads(request.data.get("data"))
            )
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            # instance.add_documents(request)
            instance.proposal.log_user_action(
                ProposalUserAction.ACTION_CREATE_EVENT_PARK.format(instance.id), request
            )
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
