import json
import pytz
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Q
from rest_framework import serializers
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from datetime import datetime
import re
import os
import csv
import xlsxwriter
import uuid

from commercialoperator.settings import MAX_NUM_ROWS_MODEL_EXPORT

def remove_html_tags(text):

    if text is None:
        return None

    HTML_TAGS_WRAPPED = re.compile(r'<[^>]+>.+</[^>]+>')
    HTML_TAGS_NO_WRAPPED = re.compile(r'<[^>]+>')

    text = HTML_TAGS_WRAPPED.sub('', text)
    text = HTML_TAGS_NO_WRAPPED.sub('', text)
    return text

def remove_script_tags(text):

    if text is None:
        return None

    SCRIPT_TAGS_WRAPPED = re.compile(r'(?i)<script[^>]+>.+</script[^>]+>')
    SCRIPT_TAGS_NO_WRAPPED = re.compile(r'(?i)<script[^>]+>')

    text = SCRIPT_TAGS_WRAPPED.sub('', text)
    text = SCRIPT_TAGS_NO_WRAPPED.sub('', text)

    ATTR_BLACKLIST = ['onresize','onvolumechange','onsuspend','onpopstate','onbeforeunload','oncontextmenu',
        'ondragstart','oncuechange','onselect','onafterprint','onmouseover','ondragleave','onstorage',
        'onbeforeprint','onhashchange','onabort','ondragover','onwaiting','onclick','onmousemove','onkeyup',
        'onmousedown','ononline','onsearch','onprogress','onfocus','onmouseup','onplaying','onstalled','oninvalid',
        'ontimeupdate','onkeypress','onseeked','onreset','onwheel','onemptied','oninput','onpagehide','onpause',
        'onloadeddata','onseeking','onunload','onpageshow','onerror','ondrop','oncanplay','oncopy','onended','oncut',
        'onsubmit','ondrag','onblur','ondragend','onplay','onratechange','onloadedmetadata','oncanplaythrough',
        'ondurationchange','onchange','ondblclick','onmousewheel','onpaste','onload','onscroll','onkeydown',
        'ontoggle','onmouseout','onoffline','onloadstart','ondragenter']
    ATTR_BLACKLIST_STR=('|').join(ATTR_BLACKLIST)

    HTML_TAGS_WITH_ATTR_WRAPPED = re.compile(r'(?i)<[^>]+('+ATTR_BLACKLIST_STR+')[\\s]*=[^>]+>.+</[^>]+>')
    HTML_TAGS_WITH_ATTR_NO_WRAPPED = re.compile(r'(?i)<[^>]+('+ATTR_BLACKLIST_STR+')[\\s]*=[^>]+>')

    text = HTML_TAGS_WITH_ATTR_WRAPPED.sub('', text)
    text = HTML_TAGS_WITH_ATTR_NO_WRAPPED.sub('', text)

    return text

def is_json(value):
    try:
        json.loads(value)
    except:
        return False
    return True

def sanitise_fields(instance, exclude=[], error_on_change=[]):
    if hasattr(instance,"__dict__"):
        for i in instance.__dict__:
            #remove html tags for all string fields not in the exclude list
            if not i in exclude and (isinstance(instance.__dict__[i], dict)):
                instance.__dict__[i] = sanitise_fields(instance.__dict__[i])
            
            elif isinstance(instance.__dict__[i], list) and not i in exclude:
                for j in range(0, len(instance.__dict__[i])):
                    check = instance.__dict__[i][j]
                    if isinstance(instance.__dict__[i][j],str):
                        instance.__dict__[i][j] = remove_html_tags(instance.__dict__[i][j])
                    elif isinstance(instance.__dict__[i][j], list) or isinstance(instance.__dict__[i][j], dict):
                        instance.__dict__[i][j] = sanitise_fields(instance.__dict__[i][j])
                    if i in error_on_change and check != instance.__dict__[i][j]:
                        raise serializers.ValidationError("html tags included in field")
            
            elif isinstance(instance.__dict__[i], str) and not i in exclude:
                check = instance.__dict__[i]
                setattr(instance, i, remove_html_tags(instance.__dict__[i]))
                if i in error_on_change and check != instance.__dict__[i]:
                    #only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                    raise serializers.ValidationError("html tags included in field")
            elif isinstance(instance.__dict__[i], str) and i in exclude:
                check = instance.__dict__[i]
                #even though excluded, we still check to remove script tags
                setattr(instance, i, remove_script_tags(instance.__dict__[i]))
                if i in error_on_change and check != instance.__dict__[i]:
                    #only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                    raise serializers.ValidationError("script tags included in field")
            elif (isinstance(instance.__dict__[i], list) or isinstance(instance.__dict__[i], dict)) and i in exclude:
                #if we have reached this point, it means we have a json object with fields that are allowed to contain tags
                #we'll use . notation to identify sub fields that should be carried over to the exclude and error on change lists
                #NOTE: to allow sub fields to be sanitised, the parent field should be included in both lists required for their respective children
                sub_exclude_list = list(filter(lambda e:e.startswith(i+"."), exclude))
                exclude_list = list(map(lambda e:e.replace(i+".","",1), sub_exclude_list))
                #NOTE: a sub error on change list will require the parent field to be in the exclude list, to reach this point (but not necessarily in the error_on_change list)
                sub_error_on_change_list = list(filter(lambda e:e.startswith(i+"."), error_on_change))
                error_on_change_list = list(map(lambda e:e.replace(i+".","",1), sub_error_on_change_list))

                if isinstance(instance.__dict__[i], dict):
                    check = instance.__dict__[i]
                    instance.__dict__[i] = sanitise_fields(instance.__dict__[i], exclude=exclude_list, error_on_change=error_on_change_list)
                    if i in error_on_change and check != instance.__dict__[i]:
                        raise serializers.ValidationError("html tags included in field")
                elif isinstance(instance.__dict__[i], list):
                    for j in range(0, len(instance.__dict__[i])):
                        check = instance.__dict__[i][j]
                        if isinstance(instance.__dict__[i][j],str):
                            #strings in an excluded list will be treated as excluded
                            instance.__dict__[i][j] = remove_script_tags(instance.__dict__[i][j])
                        elif isinstance(instance.__dict__[i][j], list) or isinstance(instance.__dict__[i][j], dict):
                            instance.__dict__[i][j] = sanitise_fields(instance.__dict__[i][j], exclude=exclude_list, error_on_change=error_on_change_list)
                        if i in error_on_change and check != instance.__dict__[i][j]:
                            raise serializers.ValidationError("html tags included in field")
    else:
        remove_keys = []
        for i in instance:
            #for dicts we also check the keys - they are removed completely if not sanitary (should not change keys)
            original_key = i
            if isinstance(original_key, str):
                sanitised_key = remove_html_tags(i)
                if original_key != sanitised_key:
                    remove_keys.append(original_key)
                    continue

            #remove html tags for all string fields not in the exclude list
            if not i in exclude and (isinstance(instance[i], dict)):
                instance[i] = sanitise_fields(instance[i])

            elif isinstance(instance[i], list) and not i in exclude:
                for j in range(0, len(instance[i])):
                    check = instance[i][j]
                    if isinstance(instance[i][j],str):
                        instance[i][j] = remove_html_tags(instance[i][j])
                    elif isinstance(instance[i][j], list) or isinstance(instance[i][j], dict):
                        instance[i][j] = sanitise_fields(instance[i][j])
                    if i in error_on_change and check != instance[i][j]:
                        raise serializers.ValidationError("html tags included in field")

            else:
                if isinstance(instance[i], str) and not i in exclude:
                    check = instance[i]
                    instance[i] = remove_html_tags(instance[i])
                    if i in error_on_change and check != instance[i]:
                        #only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                        raise serializers.ValidationError("html tags included in field")
                elif isinstance(instance[i], str) and i in exclude:
                    #even though excluded, we still check to remove script tags
                    instance[i] = remove_script_tags(instance[i])
                    if i in error_on_change and check != instance[i]:
                        #only fields that cannot be allowed to change through sanitisation just before saving will throw an error
                        raise serializers.ValidationError("script tags included in field")
                elif (isinstance(instance[i], list) or isinstance(instance[i], dict)) and i in exclude:
                    #if we have reached this point, it means we have a json object with fields that are allowed to contain tags
                    #we'll use . notation to identify sub fields that should be carried over to the exclude and error on change lists
                    #NOTE: to allow sub fields to be sanitised, the parent field should be included in both lists required for their respective children
                    sub_exclude_list = list(filter(lambda e:e.startswith(i+"."), exclude))
                    exclude_list = list(map(lambda e:e.replace(i+".","",1), sub_exclude_list))
                    #NOTE: a sub error on change list will require the parent field to be in the exclude list, to reach this point (but not necessarily in the error_on_change list)
                    sub_error_on_change_list = list(filter(lambda e:e.startswith(i+"."), error_on_change))
                    error_on_change_list = list(map(lambda e:e.replace(i+".","",1), sub_error_on_change_list))

                    if isinstance(instance[i], dict):
                        check = instance[i]
                        instance[i] = sanitise_fields(instance[i], exclude=exclude_list, error_on_change=error_on_change_list)
                        if i in error_on_change and check != instance[i]:
                            raise serializers.ValidationError("script tags included in field")
                    elif isinstance(instance[i], list):                        
                        for j in range(0, len(instance[i])):
                            check = instance[i][j]
                            if isinstance(instance[i][j],str):
                                #strings in an excluded list will be treated as excluded
                                instance[i][j] = remove_script_tags(instance[i][j])
                            elif isinstance(instance[i][j], list) or isinstance(instance[i][j], dict):
                                instance[i][j] = sanitise_fields(instance[i][j], exclude=exclude_list, error_on_change=error_on_change_list)
                            if i in error_on_change and check != instance[i][j]:
                                raise serializers.ValidationError("script tags included in field")
                    
        for i in remove_keys:
            del instance[i]
    return instance

def file_extension_valid(file, whitelist, model):
    _, extension = os.path.splitext(file)
    extension = extension.replace(".", "").lower()

    check = whitelist.filter(name=extension).filter(
        Q(model="all") | Q(model__iexact=model)
    )
    valid = check.exists()

    return valid

def check_file(file, model_name):
    from commercialoperator.components.main.models import FileExtensionWhitelist

    # check if extension in whitelist
    cache_key = settings.CACHE_KEY_FILE_EXTENSION_WHITELIST
    whitelist = cache.get(cache_key)
    if whitelist is None:
        whitelist = FileExtensionWhitelist.objects.all()
        cache.set(cache_key, whitelist, settings.CACHE_TIMEOUT_2_HOURS)

    valid = file_extension_valid(str(file), whitelist, model_name)

    if not valid:
        # Get the file extension for more informative error message
        _, extension = os.path.splitext(str(file))
        extension = extension.replace(".", "").lower() if extension else "unknown"
        
        # Get supported extensions for this model
        supported_extensions = whitelist.filter(
            Q(model="all") | Q(model__iexact=model_name)
        ).values_list("name", flat=True).distinct()
        
        if supported_extensions:
            ext_list = ", ".join(sorted(supported_extensions))
            raise serializers.ValidationError(
                f"File type '.{extension}' is not supported. Supported file types are: {ext_list}"
            )
        else:
            raise serializers.ValidationError(
                f"File type '.{extension}' is not supported. Please check the file format and try again."
            )

    

def get_department_user(email):
    if (EmailUser.objects.filter(email__iexact=email.strip()) and 
            EmailUser.objects.get(email__iexact=email.strip()).is_staff):
        return True
    return False

def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return _date.astimezone(local_tz)

def check_db_connection():
    """  check connection to DB exists, connect if no connection exists """
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception as e:
        connection.connect()

def csvExportData(model, header, columns):
    
    csv_file = str(settings.BASE_DIR)+'/tmp/{}_{}_{}.csv'.format(model,uuid.uuid4(),int(datetime.now().timestamp()*100000))
    with open(csv_file, 'w', newline='') as new_file:
        writer = csv.writer(new_file)
        writer.writerow(header)
        for i in columns:
            writer.writerow(i)
    return csv_file

def excelExportData(model, header, columns):
    excel_file = str(settings.BASE_DIR)+'/tmp/{}_{}_{}.xlsx'.format(model,uuid.uuid4(),int(datetime.now().timestamp()*100000))
    workbook = xlsxwriter.Workbook(excel_file) 
    worksheet = workbook.add_worksheet("{} Report".format(model.capitalize()))
    format = workbook.add_format()

    col = 0 
    row = 0

    col_lens = [0]*len(header)

    for i in header:
        worksheet.write(row, col, str(i), format)
        col_lens[col] = len(str(i))+2
        worksheet.set_column(col, col, col_lens[col])
        col += 1
    col = 0 
    row += 1
    for i in columns:
        for j in i:
            worksheet.write(row, col, str(j), format)
            if len(str(j)) > col_lens[col]:
                col_lens[col] = len(str(j))+2
                worksheet.set_column(col, col, col_lens[col])
            col += 1
        col = 0
        row += 1

    workbook.close() 

    return excel_file

def getProposalExport(filters, num):
    from commercialoperator.components.proposals.models import Proposal

    qs = Proposal.objects.order_by("-lodgement_date")
    if filters:
        #lodged_on_from
        if "lodged_on_from" in filters and filters["lodged_on_from"]:
            qs = qs.filter(lodgement_date__gte=filters["lodged_on_from"])
        #lodged_on_to
        if "lodged_on_to" in filters and filters["lodged_on_to"]:
            qs = qs.filter(lodgement_date__lte=filters["lodged_on_to"])

    return qs[:num]


def getApprovalExport(filters, num):
    from commercialoperator.components.approvals.models import Approval

    qs = Approval.objects.order_by("-start_date")

    if filters:
        if "start_date_from" in filters and filters["start_date_from"]:
            qs = qs.filter(start_date__gte=filters["start_date_from"])

        if "start_date_to" in filters and filters["start_date_to"]:
            qs = qs.filter(start_date__lte=filters["start_date_to"])

    return qs[:num]



def getComplianceExport(filters, num):
    from commercialoperator.components.compliances.models import Compliance

    qs = Compliance.objects.order_by("-due_date")

    if filters:
        if "due_date_from" in filters and filters["due_date_from"]:
            qs = qs.filter(due_date__gte=filters["due_date_from"])

        if "due_date_to" in filters and filters["due_date_to"]:
            qs = qs.filter(due_date__lte=filters["due_date_to"])

    return qs[:num]



def getOrganisationRequestExport(filters, num):
    from commercialoperator.components.organisations.models import OrganisationRequest

    qs = OrganisationRequest.objects.order_by("-lodgement_date")

    if filters:
        if "lodged_on_from" in filters and filters["lodged_on_from"]:
            qs = qs.filter(lodgement_date__gte=filters["lodged_on_from"])

        if "lodged_on_to" in filters and filters["lodged_on_to"]:
            qs = qs.filter(lodgement_date__lte=filters["lodged_on_to"])

    return qs[:num]



def getBookingExport(filters, num):
    from commercialoperator.components.bookings.models import ParkBooking

    qs = ParkBooking.objects.order_by("-arrival")

    if filters:
        if "arrival_date_from" in filters and filters["arrival_date_from"]:
            qs = qs.filter(arrival__gte=filters["arrival_date_from"])

        if "arrival_date_to" in filters and filters["arrival_date_to"]:
            qs = qs.filter(arrival__lte=filters["arrival_date_to"])

    return qs[:num]


def exportModelData(model, filters, num_records):

    if not num_records:
        num_records = MAX_NUM_ROWS_MODEL_EXPORT
    else:
        num_records = min(num_records, MAX_NUM_ROWS_MODEL_EXPORT)

    if model == "proposal":
        return getProposalExport(filters, num_records)
    elif model == "approval":
        return getApprovalExport(filters, num_records)
    elif model == "compliance":
        return getComplianceExport(filters, num_records)
    elif model == "organisationrequest":
        return getOrganisationRequestExport(filters, num_records)
    elif model == "booking":
        return getBookingExport(filters, num_records)
    else:
        return


def getProposalExportFields(data):

    header = ["Number", "Licence Type", "Submitter", "Applicant", "Status", "Lodged On", "Assigned Officer", "Event Name", "Invoice Reference"]

    columns = list(
        data.values_list(
            "lodgement_number",
            "proposal_type",
            "submitter_id",
            "org_applicant__property_cache__name",
            "proxy_applicant_id",
            "processing_status",
            "lodgement_date",
            "assigned_officer_id",
            "fee_invoice_reference"
        )
    )

    user_ids = {
        proposal[i]
        for proposal in columns
        for i in (2, 4, 7)
        if proposal[i] is not None
    }

    email_users = EmailUser.objects.filter(id__in=user_ids)
    
    user_map = {
        user.id: f"{user.first_name} {user.last_name}".strip()
        for user in email_users
    }

    columns = list(map(lambda proposal: (
        proposal[0],
        proposal[1].replace("_"," "),
        user_map.get(proposal[2]),
        proposal[3] if proposal[3] else user_map.get(proposal[4]) if user_map.get(proposal[4]) else user_map.get(proposal[2]),
        proposal[5].replace("_"," "),
        proposal[6] if proposal[6] else "",
        user_map.get(proposal[7]) if user_map.get(proposal[7]) else "",
        proposal[8] if proposal[8] else "",
    ),columns))

    return header, columns

def getApprovalExportFields(data):
    
    header = ["Number", "Application", "Licence Type", "Holder", "Status", "Start Date", "Expiry Date", "Event Name"]
              
    columns = list(
        data.values_list(
            "lodgement_number",
            "current_proposal__lodgement_number",
            "current_proposal__proposal_type",
            "submitter_id",
            "org_applicant__property_cache__name",
            "proxy_applicant_id",
            "status",
            "start_date",
            "expiry_date",
            "current_proposal__event_activity__event_name",
        )
    )

    user_ids = {
        proposal[i]
        for proposal in columns
        for i in (3, 5)
        if proposal[i] is not None
    }

    email_users = EmailUser.objects.filter(id__in=user_ids)
    
    user_map = {
        user.id: f"{user.first_name} {user.last_name}".strip()
        for user in email_users
    }

    columns = list(map(lambda approval: (
        approval[0],
        approval[1],
        approval[2].replace("_"," "),
        approval[4] if approval[4] else user_map.get(approval[5]) if user_map.get(approval[5]) else user_map.get(approval[3]),
        approval[6].replace("_"," "),
        approval[7],
        approval[8],
        approval[9],
    ),columns))

    return header, columns

def getComplianceExportFields(data):
    
    header = ["Number", "Licence", "Licence Type", "Holder", "Status", "Due Date", "Assigned To", "Event Name"]
              
    columns = list(
        data.values_list(
            "lodgement_number",
            "approval__lodgement_number",
            "proposal__proposal_type",
            "proposal__submitter_id",
            "proposal__org_applicant__property_cache__name",
            "proposal__proxy_applicant_id",
            "processing_status",
            "due_date",
            "assigned_to",
        )
    )

    user_ids = {
        proposal[i]
        for proposal in columns
        for i in (3, 5, 8)
        if proposal[i] is not None
    }

    email_users = EmailUser.objects.filter(id__in=user_ids)
    
    user_map = {
        user.id: f"{user.first_name} {user.last_name}".strip()
        for user in email_users
    }

    columns = list(map(lambda compliance: (
        
    ),columns))

    return header, columns

def getOrganisationRequestExportFields(data):

    header = ["Number"]
              
    columns = list(
        data.values_list(
            "id",
        )
    )

    return header, columns

def getBookingExportFields(data):
    
    header = ["Number"]
              
    columns = list(
        data.values_list(
            "id",
        )
    )

    return header, columns

def formatExportData(model, data, format):
    
    
    if model == "proposal":
        header, columns = getProposalExportFields(data)
    elif model == "approval":
        header, columns = getApprovalExportFields(data)
    elif model == "compliance":
        header, columns = getComplianceExportFields(data)
    elif model == "organisationrequest":
        header, columns = getOrganisationRequestExportFields(data)
    elif model == "booking":
        header, columns = getBookingExportFields(data)
    else:
        return


    if os.path.isdir(str(settings.BASE_DIR)+'/tmp/') is False:
        os.makedirs(str(settings.BASE_DIR)+'/tmp/')

    if format == "excel":
        file_name = excelExportData(model, header, columns)
        file_buffer = None
        with open(file_name, 'rb') as f:
            file_buffer = f.read()    
        return ('Commercial Operator - {} Report.xlsx'.format(model.capitalize()), file_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        file_name =  csvExportData(model, header, columns)
        file_buffer = None
        with open(file_name, 'rb') as f:
            file_buffer = f.read()    
        return ('Commercial Operator - {} Report.csv'.format(model.capitalize()), file_buffer, 'application/csv')