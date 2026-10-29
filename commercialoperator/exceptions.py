from rest_framework.exceptions import APIException, PermissionDenied


class ReferralNotAuthorized(PermissionDenied):
    default_detail = "You are not authorised to work on this referral"
    default_code = "referral_not_authorized"


class ProposalNotAuthorized(PermissionDenied):
    default_detail = "You are not authorised to work on this proposal"
    default_code = "proposal_not_authorized"


class ReferralCanNotSend(PermissionDenied):
    default_detail = "You can only send referrals sent from an assessor"
    default_code = "referral_level_send_unauthorized"


class ProposalReferralCannotBeSent(PermissionDenied):
    default_detail = (
        "Referrals can only be sent if it is in the right processing status"
    )
    default_code = "proposal_referral_cannot_be_sent"


class ProposalNotComplete(APIException):
    status_code = 400
    default_detail = "The proposal is not complete"
    default_code = "proposal_incoplete"


class ProposalMissingFields(APIException):
    status_code = 400
    default_detail = "The proposal has missing required fields"
    default_code = "proposal_missing_fields"


class LedgerException(Exception):
    """Base exception for Ledger-related errors."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class LedgerApiFailureException(LedgerException):
    """Raised when a call to Ledger fails or times out."""


class LedgerMalformedApiResponseException(LedgerException):
    """Raised when a call to Ledger does not return the expected format."""


class CreateFutureInvoiceFailedException(LedgerException):
    """Raised when process_create_future_invoice does not return a 200 response."""
