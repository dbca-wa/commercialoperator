import json

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.decorators import action as list_route

from commercialoperator.components.bookings.models import (
    Booking,
    ParkBooking,
    BookingInvoice,
)
from commercialoperator.components.bookings.serializers import (
    BookingSerializer,
    ParkBookingSerializer,
    DTParkBookingSerializer,
    OverdueBookingInvoiceSerializer,
)
from commercialoperator.components.bookings.utils import (
    bind_booking,
    get_invoice_properties_all,
)
from commercialoperator.components.organisations.models import Organisation
from commercialoperator.components.stubs.utils import retrieve_delegate_organisation_ids
from commercialoperator.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from commercialoperator.components.proposals.api import ProposalFilterBackend


class BookingPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    # renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Booking.objects.all().exclude(
                booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )
        elif is_customer(self.request):
            ledger_user_orgs = retrieve_delegate_organisation_ids(user)
            cols_org_ids = Organisation.objects.filter(
                organisation_id__in=ledger_user_orgs
            ).values_list("id", flat=True)

            return Booking.objects.filter(
                Q(proposal__org_applicant_id__in=cols_org_ids)
                | Q(proposal__submitter_id=user.id)
            ).exclude(booking_type=Booking.BOOKING_TYPE_TEMPORARY)
        return Booking.objects.none()

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def bookings_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/booking_paginated/bookings_external/?format=datatables&draw=1&length=2
        """

        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = BookingSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Booking.objects.all().exclude(
                booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return Booking.objects.filter(
                Q(proposal__org_applicant_id__in=user_orgs)
                | Q(proposal__submitter=user)
            ).exclude(booking_type=Booking.BOOKING_TYPE_TEMPORARY)
        return Booking.objects.none()


class OverdueBookingInvoiceViewSet(viewsets.ModelViewSet):
    queryset = BookingInvoice.objects.none()
    serializer_class = OverdueBookingInvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            bi = BookingInvoice.objects.all().exclude(
                booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )

            # NOTE: [Booking and BookingInvoice] Check if overdue invoices for internal can still be returned this way in segregated COLS
            # from ledger_api_client.ledger_models import Invoice
            # from ledger_api_client.utils import Order
            # # payment_status
            # invoice_properties_all = get_invoice_properties_all()
            # invoice_properties_all[0]["invoice"]
            # [inv_prop for inv_prop in invoice_properties_all if inv_prop.get("invoice", {}).get("payment_status") in ("unpaid", "partially_paid")]
            # Invoice.objects.last()
            # Order.objects.get(number="100088")

            return [inv for inv in bi if inv.overdue]
        elif is_customer(self.request):
            ledger_org_ids = retrieve_delegate_organisation_ids(user)
            cols_org_ids = Organisation.objects.filter(
                organisation_id__in=ledger_org_ids
            ).values_list("id", flat=True)

            bi = BookingInvoice.objects.filter(
                Q(booking__proposal__org_applicant_id__in=cols_org_ids)
                | Q(booking__proposal__submitter_id=user.id)
            ).exclude(booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY)
            return [inv for inv in bi if inv.overdue]
        return BookingInvoice.objects.none()


class ParkBookingViewSet(viewsets.ModelViewSet):
    queryset = ParkBooking.objects.none()
    serializer_class = ParkBookingSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ParkBooking.objects.all().exclude(
                booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return ParkBooking.objects.filter(
                Q(booking__proposal__org_applicant_id__in=user_orgs)
                | Q(booking__proposal__submitter=user)
            ).exclude(booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY)
        return ParkBooking.objects.none()


class ParkBookingPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    # renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = ParkBooking.objects.none()
    serializer_class = DTParkBookingSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ParkBooking.objects.all().exclude(
                booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return ParkBooking.objects.filter(
                Q(booking__proposal__org_applicant_id__in=user_orgs)
                | Q(booking__proposal__submitter=user)
            ).exclude(booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY)
        return ParkBooking.objects.none()

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def park_bookings(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/booking_paginated/bookings_external/?format=datatables&draw=1&length=2
        """

        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTParkBookingSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)

# NOTE: [Booking and Booking Invoice] I added this to the API as callable method to the complete_booking url pattern
def complete_booking(request, booking_hash, booking_id):
    jsondata = {"status": "error completing booking"}
    if booking_hash:
        try:
            booking = Booking.objects.get(id=booking_id, booking_hash=booking_hash)
            basket = Basket.objects.filter(
                status="Submitted",
                booking_reference=settings.BOOKING_PREFIX + "-" + str(booking.id),
            ).order_by("-id")[:1]
            if basket.count() > 0:
                pass
            else:
                raise ValidationError("Error unable to find basket")

            bind_booking(booking, basket)
            jsondata = {"status": "success"}
        except Exception as e:
            print("EXCEPTION")
            print(e)
            jsondata = {"status": "error binding"}
    response = HttpResponse(json.dumps(jsondata), content_type="application/json")
    return response


# from django.views.decorators.http import require_http_methods
# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
# @require_http_methods(['POST'])
# def create_booking(request, *args, **kwargs):
#     # NOTE: Temporary dummy for testing
#     return HttpResponse(
#         json.dumps({"status": "success", "message": "Dummy Test Booking created"}),
#         content_type="application/json",
#     )
