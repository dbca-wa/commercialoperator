from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone
from ledger_api_client.ledger_models import Invoice
from rest_framework import viewsets
from rest_framework.decorators import action as list_route
from rest_framework.response import Response
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from commercialoperator.components.bookings.models import (
    Booking,
    BookingInvoice,
    ParkBooking,
)
from commercialoperator.components.main.models import Park
from commercialoperator.components.main.serializers import ParkFilterSerializer
from commercialoperator.components.bookings.serializers import (
    BookingSerializer,
    DTParkBookingSerializer,
    OverdueBookingInvoiceSerializer,
)
from commercialoperator.components.proposals.api import ProposalFilterBackend
from commercialoperator.components.segregation.utils import (
    retrieve_delegate_organisation_ids,
)
from commercialoperator.helpers import is_internal


def payment_methods_for_bookings(queryset):
    latest_invoice = BookingInvoice.objects.filter(booking_id=OuterRef("pk")).order_by(
        "-pk"
    )
    bookings = queryset.order_by().annotate(
        latest_invoice_id=Subquery(latest_invoice.values("pk")[:1]),
        latest_invoice_reference=Subquery(
            latest_invoice.values("invoice_reference")[:1]
        ),
    )
    references = set()
    methods = set()
    for booking_type, invoice_id, reference in bookings.values_list(
        "booking_type", "latest_invoice_id", "latest_invoice_reference"
    ).distinct():
        if invoice_id is None and booking_type == Booking.BOOKING_TYPE_MONTHLY_INVOICING:
            methods.add(Invoice.PAYMENT_METHOD_MONTHLY_INVOICING)
        elif reference:
            references.add(reference)

    methods.update(
        Invoice.objects.filter(reference__in=references)
        .values_list("payment_method", flat=True)
        .distinct()
    )
    return [
        {"name": name, "value": str(value)}
        for value, name in Invoice.PAYMENT_METHOD_CHOICES
        if value in methods
    ]


def payment_method_queryset(view, queryset):
    if not view.request.GET.get("payment_method"):
        return view.filter_queryset(queryset)
    view.exclude_payment_method_filter = True
    try:
        return view.filter_queryset(queryset)
    finally:
        view.exclude_payment_method_filter = False


class BookingPaginatedViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    page_size = 10
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Booking.objects.all().exclude(
                booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )
        else:
            cols_org_ids = retrieve_delegate_organisation_ids(user)

            return Booking.objects.filter(
                Q(proposal__org_applicant_id__in=cols_org_ids)
                | Q(proposal__submitter_id=user.id)
            ).exclude(booking_type=Booking.BOOKING_TYPE_TEMPORARY)

    @list_route(methods=["GET"], detail=False)
    def parks_with_bookings(self, request, *args, **kwargs):
        parks = Park.objects.filter(
            bookings__booking__in=self.get_queryset()
        ).distinct()
        serializer = ParkFilterSerializer(parks, many=True)
        return Response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def bookings_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)
        """

        queryset = self.get_queryset()
        method_queryset = payment_method_queryset(self, queryset)
        qs = (
            self.filter_queryset(queryset)
            if request.GET.get("payment_method")
            else method_queryset
        )

        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = BookingSerializer(
            result_page, context={"request": request}, many=True
        )
        response = self.paginator.get_paginated_response(serializer.data)
        response.data["payment_methods"] = payment_methods_for_bookings(method_queryset)
        return response


class OverdueBookingInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookingInvoice.objects.none()
    serializer_class = OverdueBookingInvoiceSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            bi = BookingInvoice.objects.exclude(
                booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY
            ).filter(
                (
                    Q(property_cache__payment_status="Unpaid")
                    | Q(property_cache__payment_status="Partially Paid")
                )
                & Q(deferred_payment_date__lt=timezone.now().date())
            )

            return bi
        else:
            cols_org_ids = retrieve_delegate_organisation_ids(user)

            bi = (
                BookingInvoice.objects.filter(
                    Q(booking__proposal__org_applicant_id__in=cols_org_ids)
                    | Q(booking__proposal__submitter_id=user.id)
                )
                .exclude(booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY)
                .filter(
                    (
                        Q(property_cache__payment_status="Unpaid")
                        | Q(property_cache__payment_status="Partially Paid")
                    )
                    & Q(deferred_payment_date__lt=timezone.now().date())
                )
            )
            return bi


class ParkBookingPaginatedViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    page_size = 10
    queryset = ParkBooking.objects.none()
    serializer_class = DTParkBookingSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ParkBooking.objects.all().exclude(
                booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY
            )
        else:
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            return ParkBooking.objects.filter(
                Q(booking__proposal__org_applicant_id__in=user_orgs)
                | Q(booking__proposal__submitter=user)
            ).exclude(booking__booking_type=Booking.BOOKING_TYPE_TEMPORARY)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def park_bookings(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)
        """

        queryset = self.get_queryset()
        method_queryset = payment_method_queryset(self, queryset)
        qs = (
            self.filter_queryset(queryset)
            if request.GET.get("payment_method")
            else method_queryset
        )

        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTParkBookingSerializer(
            result_page, context={"request": request}, many=True
        )
        response = self.paginator.get_paginated_response(serializer.data)
        bookings = Booking.objects.filter(
            pk__in=method_queryset.order_by().values("booking_id")
        )
        response.data["payment_methods"] = payment_methods_for_bookings(bookings)
        return response
