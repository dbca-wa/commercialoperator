import csv
import pytz
from six import StringIO
from django.utils import timezone
from commercialoperator.components.stubs.classes import (
    CashTransaction,
    BpointTransaction,
    BpayTransaction,
    Invoice,
)
from commercialoperator.components.bookings.models import (
    BookingInvoice,
    ApplicationFeeInvoice,
)
from commercialoperator.components.stubs.decorators import basic_exception_handler


@basic_exception_handler
def booking_bpoint_settlement_report(_date):
    bpoint, bpay, cash = [], [], []
    bpoint.extend(
        [
            x
            for x in BpointTransaction.objects.filter(
                created__date=_date, response_code=0, crn1__startswith="0557"
            ).exclude(crn1__endswith="_test")
        ]
    )
    bpay.extend(
        [
            x
            for x in BpayTransaction.objects.filter(
                p_date__date=_date, crn__startswith="0557"
            ).exclude(crn__endswith="_test")
        ]
    )
    cash = CashTransaction.objects.filter(
        created__date=_date, invoice__reference__startswith="0557"
    ).exclude(type__in=["move_out", "move_in"])

    strIO = StringIO()
    fieldnames = [
        "Payment Date",
        "Settlement Date",
        "Confirmation Number",
        "Name",
        "Type",
        "Amount",
        "Invoice",
    ]
    writer = csv.writer(strIO)
    writer.writerow(fieldnames)

    for b in bpoint:
        booking, invoice = None, None
        try:
            invoice = Invoice.objects.get(reference=b.crn1)
            try:
                booking = BookingInvoice.objects.get(
                    invoice_reference=invoice.reference
                ).booking
            except BookingInvoice.DoesNotExist:
                pass

            try:
                application_fee = ApplicationFeeInvoice.objects.get(
                    invoice_reference=invoice.reference
                ).application_fee
            except ApplicationFeeInvoice.DoesNotExist:
                pass

            if booking:
                b_name = "{}".format(booking.proposal.applicant)
                created = timezone.localtime(
                    b.created, pytz.timezone("Australia/Perth")
                )
                settlement_date = (
                    invoice.settlement_date.strftime("%d/%m/%Y")
                    if invoice.settlement_date
                    else ""
                )
                writer.writerow(
                    [
                        created.strftime("%d/%m/%Y %H:%M:%S"),
                        settlement_date,
                        booking.admission_number,
                        b_name.encode("utf-8"),
                        invoice.get_payment_method_display(),
                        invoice.amount,
                        invoice.reference,
                    ]
                )
            elif application_fee:
                b_name = "{}".format(application_fee.proposal.applicant)
                created = timezone.localtime(
                    application_fee.created, pytz.timezone("Australia/Perth")
                )
                settlement_date = (
                    invoice.settlement_date.strftime("%d/%m/%Y")
                    if invoice.settlement_date
                    else ""
                )
                writer.writerow(
                    [
                        created.strftime("%d/%m/%Y %H:%M:%S"),
                        settlement_date,
                        application_fee.proposal.lodgement_number,
                        b_name.encode("utf-8"),
                        invoice.get_payment_method_display(),
                        invoice.amount,
                        invoice.reference,
                    ]
                )
            else:
                writer.writerow(
                    [
                        b.created.strftime("%d/%m/%Y %H:%M:%S"),
                        b.settlement_date.strftime("%d/%m/%Y"),
                        "",
                        "",
                        str(b.action),
                        b.amount,
                        invoice.reference,
                    ]
                )
        except Invoice.DoesNotExist:
            pass

    for b in bpay:
        booking, invoice = None, None
        try:
            invoice = Invoice.objects.get(reference=b.crn)
            try:
                booking = BookingInvoice.objects.get(
                    invoice_reference=invoice.reference
                ).booking
            except BookingInvoice.DoesNotExist:
                pass

            if booking:
                b_name = "{}".format(booking.proposal.applicant)
                created = timezone.localtime(
                    b.created, pytz.timezone("Australia/Perth")
                )
                settlement_date = b.p_date.strftime("%d/%m/%Y")
                writer.writerow(
                    [
                        created.strftime("%d/%m/%Y %H:%M:%S"),
                        settlement_date,
                        booking.admission_number,
                        b_name.encode("utf-8"),
                        invoice.get_payment_method_display(),
                        invoice.amount,
                        invoice.reference,
                    ]
                )
            else:
                writer.writerow(
                    [
                        b.created.strftime("%d/%m/%Y %H:%M:%S"),
                        b.settlement_date.strftime("%d/%m/%Y"),
                        "",
                        "",
                        str(b.action),
                        b.amount,
                        invoice.reference,
                    ]
                )
        except Invoice.DoesNotExist:
            pass

    for b in cash:
        booking, invoice = None, None
        try:
            invoice = b.invoice
            try:
                booking = BookingInvoice.objects.get(
                    invoice_reference=invoice.reference
                ).booking
            except BookingInvoice.DoesNotExist:
                pass

            if booking:
                b_name = "{} {}".format(
                    booking.details.get("first_name", ""),
                    booking.details.get("last_name", ""),
                )
                created = timezone.localtime(
                    b.created, pytz.timezone("Australia/Perth")
                )
                writer.writerow(
                    [
                        created.strftime("%d/%m/%Y %H:%M:%S"),
                        b.created.strftime("%d/%m/%Y"),
                        booking.confirmation_number,
                        b_name.encode("utf-8"),
                        str(b.type),
                        b.amount,
                        invoice.reference,
                    ]
                )
            else:
                writer.writerow(
                    [
                        b.created.strftime("%d/%m/%Y %H:%M:%S"),
                        b.created.strftime("%d/%m/%Y"),
                        "",
                        "",
                        str(b.type),
                        b.amount,
                        invoice.reference,
                    ]
                )
        except Invoice.DoesNotExist:
            pass

    strIO.flush()
    strIO.seek(0)
    return strIO
