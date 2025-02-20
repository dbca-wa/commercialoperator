from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse

from urllib.parse import quote_plus as urlquote_plus

from commercialoperator.components.bookings.models import ApplicationFee
from reversion.middleware import RevisionMiddleware
from reversion.views import _request_creates_revision

import hashlib
import re

from commercialoperator.components.proposals.models import Proposal
from commercialoperator.helpers import is_internal

CHECKOUT_PATH = re.compile("^/ledger/checkout/checkout")


class FirstTimeNagScreenMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            or not request.method == "GET"
            or "api" in request.path
            or "admin" in request.path
            or "static" in request.path
        ):
            return self.get_response(request)

        if (
            request.user.first_name
            and request.user.last_name
            and request.user.residential_address_id
            or (request.user.phone_number or request.user.mobile_number)
        ):
            return self.get_response(request)

        path_ft = reverse("first_time")
        path_logout = reverse("accounts:logout")
        if request.path not in (path_ft, path_logout):
            return redirect(
                reverse("first_time")
                + "?next="
                + urlquote_plus(request.get_full_path())
            )


class BookingTimerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "cols_app_invoice" in request.session:
            try:
                application_fee = ApplicationFee.objects.get(
                    pk=request.session["cols_app_invoice"]
                )
            except:
                # no idea what object is in self.request.session['ps_booking'], ditch it
                del request.session["cols_app_invoice"]

                # Note: changed to returning response instead of just returning
                return self.get_response(request)
            if application_fee.payment_type != ApplicationFee.PAYMENT_TYPE_TEMPORARY:
                # booking in the session is not a temporary type, ditch it
                del request.session["cols_app_invoice"]

        # Note: changed to returning response instead of just returning
        return self.get_response(request)


class RevisionOverrideMiddleware(RevisionMiddleware):
    """
    Wraps the entire request in a revision.

    override venv/lib/python2.7/site-packages/reversion/middleware.py
    """

    # exclude ledger payments/checkout from revision - hack to overcome basket (lagging status) issue/conflict with reversion
    def request_creates_revision(self, request):
        return (
            _request_creates_revision(request)
            and "checkout" not in request.get_full_path()
        )


# NOTE: I copied this class from mooringlicensing, but not sure we even need it in cols for future payments
# So I commented it out for now
# class PaymentSessionMiddleware(object):

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def process_view(self, request, view_func, view_args, view_kwargs):

#         redirect_path = 'internal' if is_internal(request) else 'external'

#         if (request.user.is_authenticated 
#         and (CHECKOUT_PATH.match(request.path)
#         or request.path.startswith("/ledger-api/process-payment") 
#         or request.path.startswith('/ledger-api/payment-details'))):
#             if 'payment_model' in request.session and 'payment_pk' in request.session:
#                 if request.path.startswith("/ledger-api/process-payment"):

#                     checkouthash =  hashlib.sha256(str(str(request.session["payment_model"])+str(request.session["payment_pk"])).encode('utf-8')).hexdigest() 
#                     checkouthash_cookie = request.COOKIES.get('checkouthash')
#                     # validation_cookie = request.COOKIES.get(request.POST['payment-csrfmiddlewaretoken']) # Commented out

#                     if request.session['payment_model'] == "proposal":
#                         proposal_count = Proposal.objects.filter(pk=request.session['payment_pk']).count()
#                     # elif request.session['payment_model'] == "dcv_permit":
#                     #     proposal_count = DcvPermit.objects.filter(pk=request.session['payment_pk']).count()
#                     # elif request.session['payment_model6'] == "dcv_admission":
#                     #     proposal_count = DcvAdmission.objects.filter(pk=request.session['payment_pk']).count()
#                     # elif request.session['payment_model'] == "sticker":  
#                     #     proposal_count = StickerActionDetail.objects.filter(pk=request.session['payment_pk']).count()
#                     else:
#                         proposal_count = 0

#                     # if checkouthash_cookie != checkouthash or checkouthash_cookie != validation_cookie or proposal_count == 0:
#                     if checkouthash_cookie != checkouthash or proposal_count == 0:
#                         url_redirect = reverse(redirect_path)
#                         response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
#                         return response
#                     else:
#                         return self.get_response(request)
#             else:
#                  if request.path.startswith("/ledger-api/process-payment"):
#                     url_redirect = reverse(redirect_path)
#                     response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
#                     return response
                 
#         return None


#     def __call__(self, request):
        
#         response= self.get_response(request)
#         redirect_path = 'internal' if is_internal(request) else 'external'
        
#         if (request.user.is_authenticated 
#         and (CHECKOUT_PATH.match(request.path)
#         or request.path.startswith("/ledger-api/process-payment") 
#         or request.path.startswith('/ledger-api/payment-details'))):
#             if 'payment_model' in request.session and 'payment_pk' in request.session:
#                 try:
#                     if request.session['payment_model'] == "proposal":
#                         proposal_count = Proposal.objects.get(pk=request.session['payment_pk'])
#                     # elif request.session['payment_model'] == "dcv_permit":
#                     #     proposal_count = DcvPermit.objects.get(pk=request.session['payment_pk'])
#                     # elif request.session['payment_model'] == "dcv_admission":
#                     #     proposal_count = DcvAdmission.objects.get(pk=request.session['payment_pk'])
#                     # elif request.session['payment_model'] == "sticker":  
#                     #     proposal_count = StickerActionDetail.objects.get(pk=request.session['payment_pk'])
#                     else:
#                         proposal_count = 0

#                 except Exception as e:
#                     del request.session['payment_model']
#                     del request.session['payment_pk']
#                     return response

#                 if request.path.startswith("/ledger-api/process-payment"):
                    
#                     if "payment_pk" not in request.session:
#                          url_redirect = reverse(redirect_path)
#                          response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
#                          return response    

#                     checkouthash =  hashlib.sha256(str(str(request.session["payment_model"])+str(request.session["payment_pk"])).encode('utf-8')).hexdigest() 
#                     checkouthash_cookie = request.COOKIES.get('checkouthash')
#                     validation_cookie = request.COOKIES.get(request.POST['payment-csrfmiddlewaretoken'])

#                     if request.session['payment_model'] == "proposal":
#                         proposal_count = Proposal.objects.filter(pk=request.session['payment_pk']).count()
#                     # elif request.session['payment_model'] == "dcv_permit":
#                     #     proposal_count = DcvPermit.objects.filter(pk=request.session['payment_pk']).count()
#                     # elif request.session['payment_model'] == "dcv_admission":
#                     #     proposal_count = DcvAdmission.objects.filter(pk=request.session['payment_pk']).count()
#                     # elif request.session['payment_model'] == "sticker":  
#                     #     proposal_count = StickerActionDetail.objects.filter(pk=request.session['payment_pk']).count()
#                     else:
#                         proposal_count = 0

#                     if checkouthash_cookie != checkouthash or checkouthash_cookie != validation_cookie or proposal_count == 0:                         
#                          url_redirect = reverse(redirect_path)
#                          response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
#                          return response                                                                                                 
#             else:
#                  if request.path.startswith("/ledger-api/process-payment"):
#                     url_redirect = reverse(redirect_path)
#                     response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
#                     return response

#             # force a redirect if in the checkout
#             if ('payment_pk' not in request.session or 'payment_model' not in request.session) and CHECKOUT_PATH.match(request.path):
#                 url_redirect = reverse(redirect_path)
#                 response = HttpResponse("<script> window.location='"+url_redirect+"';</script> <center><div class='container'><div class='alert alert-primary' role='alert'><a href='"+url_redirect+"'> Redirecting please wait: "+url_redirect+"</a><div></div></center>")
#                 return response
                
#         return response
