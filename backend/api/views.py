import json
import MySQLdb
import datetime
from dateutil import parser as date_parser
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse as OrigHttpResponse

from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.views import logout

from src import *
from file_import import *
from django.db.models import Q
from models import JD as JobDesTable
from models import Agent
from models import SPOC
from models import Candidate
from models import StatusType

from auth.decorators import loginRequired
from common.utils import getHttpResponse as HttpResponse
from common.decorators import allowedMethods

SOH_XL_HEADERS = ['FName', 'LName','Mobile','MailId','JDId','AgentId','ScheduledDate']
SOH_XL_MAN_HEADERS = ['FName', 'LName','Mobile','MailId','JDId','AgentId','ScheduledDate']
customer_data = {}

@loginRequired
@allowedMethods(["GET"])
def jds(request):

    user_group = request.user.groups.values_list('name',flat=True)
    user_id = request.user.id

    if 'Admin' in user_group:

        try:
            jdObjs = JobDesTable.objects.values('id','job_title','location','candidates_req','min_experience',
                     'max_experience','job_description','company','min_salary','max_salary','start_date','end_date','status');
        except:
            return  HttpResponse('No Jds are added to this user','1')

    elif user_group[0] == "SPOC":
        spoc_obj = SPOC.objects.filter(name=user_id).values_list('id', flat=True)
        try:
            jdObjs   = JobDesTable.objects.filter(SPOC=spoc_obj[0]).values('id','job_title','location',
            'candidates_req','min_experience','max_experience','job_description','company','min_salary',
            'max_salary','start_date','end_date','status')
        except:
            return HttpResponse('No Jds are added to this SPOC','1')


    else:
        try:
            agent_obj = Agent.objects.filter(name=user_id).values_list('id', flat=True)
            jdObjs    = JobDesTable.objects.filter(agent=agent_obj[0]).values('id','job_title',
                        'location','candidates_req','min_experience','max_experience','job_description','company',
                        'min_salary','max_salary','start_date','end_date','status', 'agent')
        except:
            return HttpResponse('No Jds are added to this Agent','1')

    resp_data = []
    for jdObj in jdObjs:
        jd = jdObj["job_title"]
        li = JobDesTable.objects.filter(job_title=jd).values_list('id')
        scheduled_sta_id = StatusType.objects.get(status_field='Scheduled').id
        selected_sta_id = StatusType.objects.get(status_field='Selected').id
        sch_count = Candidate.objects.filter(jd_id__in=li,status=scheduled_sta_id).count()
        pass_count = Candidate.objects.filter(jd_id__in=li,status=selected_sta_id).count()
        locationObj = Location.objects.filter(id=jdObj["location"]).values_list('name', flat=True)
        print locationObj[0]
        resp_data.append({"id": jdObj["id"], "name": jdObj["job_title"], "location": locationObj[0], 
            "candidates_req": jdObj["candidates_req"],"min_experience":jdObj["min_experience"], 
            "max_experience":jdObj["max_experience"],"job_description":jdObj["job_description"],
            "company":jdObj["company"],"min_salary":jdObj["min_salary"],"max_salary":jdObj["max_salary"],
            "start_date":jdObj["start_date"].strftime('%m/%d/%Y'),"end_date":jdObj["end_date"].strftime('%m/%d/%Y'),
            "status":jdObj["status"],"scheduled":sch_count,"interview_pass":pass_count})

    return HttpResponse(resp_data)


def status(request):
    can_status = request.POST.get('status')
    can_id = request.POST.get('can_id')
    status_id_of_request = StatusType.objects.filter(status_field=can_status)#.values_list('id')
    status_update = Candidate.objects.filter(id=can_id)[0]#.status=status_id_of_request
    status_update.status=status_id_of_request[0]
    status_update.save()

    return OrigHttpResponse("success")

@loginRequired
@allowedMethods(["GET"])
def candidate_status_dropdown(request):
    user_group = request.user.groups.values_list('name',flat=True)
    if user_group[0] == "SPOC":
        resp_data = []
        status_obj = StatusType.objects.filter(is_spoc=True).values_list('status_field', flat=True)
        for status_option in status_obj:
            resp_data.append(status_option)
    else:
        print "dropdown"
        resp_data = []
        status_obj = StatusType.objects.values_list('status_field', flat=True)
        for status_option in status_obj:
            resp_data.append(status_option)
        print resp_data

    return HttpResponse(resp_data)

@loginRequired
@allowedMethods(["GET"])
def candidates(request):
    resp_data = []

    if request.user.is_authenticated():
        #jd          = request.GET.get('jd').split('-')[0]
        jd           = request.GET.get('jd')
        user_group  = request.user.groups.values_list('name',flat=True)
        user_id     = request.user.id
        user_name   = request.user.username
        session_key = request.GET.get('session_key')
        filter_date = request.GET.get('filter_date')
        filter_type = request.GET.get('date_type')
        if filter_date == 'null':
            filter_date = ''

        if filter_date:

            filter_date = date_parser.parse(filter_date.replace(' GMT ',' GMT+').replace('India Standard Time', 'IST'))
            filter_date = date_parser.parse('-'.join(str(filter_date).split('-')[:-1]))
            filter_date_end = filter_date + datetime.timedelta(hours = 23,minutes = 59,seconds = 59)

        if 'Admin' in user_group:

            if filter_date:
                print filter_type
                if filter_type == 'scheduled':
                    candidate_list = Candidate.objects.filter(jd_id=jd, walk_in_date__range=[filter_date, filter_date_end])
                else:
                    candidate_list = Candidate.objects.filter(jd_id=jd, created_at__range=(filter_date, filter_date_end))

            else :
                candidate_list  =  Candidate.objects.filter(jd_id=jd)

        elif user_group[0] == "SPOC":
            satus_id_list   = StatusType.objects.filter(is_spoc=True).values_list('id', flat= True)
            spoc_id         = SPOC.objects.filter(name_id= user_id).values_list('id', flat= True) #take SPOC id
            jd_list         = JobDesTable.objects.filter(id=jd, SPOC= spoc_id).values_list('id')

            if filter_date :
                if filter_type == 'scheduled':
                    candidate_list  = Candidate.objects.filter(jd_id__in= jd_list,status_id__in= satus_id_list, \
                                      walk_in_date__range=(filter_date, filter_date_end))
                else:
                    candidate_list  = Candidate.objects.filter(jd_id__in= jd_list,status_id__in= satus_id_list, \
                                        created_at__range=(filter_date, filter_date_end))

            else :
                candidate_list  = Candidate.objects.filter(jd_id__in= jd_list,status_id__in= satus_id_list)

        else:
            agent_id        = Agent.objects.filter(name_id=user_id).values_list('id', flat=True) #take agent id

            if filter_date :
                if filter_type == 'scheduled':
                    candidate_list  = Candidate.objects.filter(jd_id__in=jd_list, agent_id=agent_id, \
                                      walk_in_date__range = (filter_date, filter_date_end))
                else:
                    candidate_list  = Candidate.objects.filter(jd_id__in=jd_list, agent_id=agent_id, \
                                        created_at__range=(filter_date, filter_date_end))

            else :
                candidate_list  = Candidate.objects.filter(jd_id=jd, agent_id=agent_id)

        for candidate in candidate_list:
            resp_data.append({"id":candidate.id, "name": candidate.fname + "  " + candidate.lname,
            "walk_in_date": candidate.walk_in_date.strftime('%m/%d/%Y'), "status": candidate.status.status_field,
            "mobile_number":candidate.mobile_number, "email_id":candidate.email_id, "location":candidate.location,
            "agent_name": str(candidate.agent.name), "created_at": candidate.created_at.strftime('%m/%d/%Y'), 
            "remarks" : candidate.remarks})
        print resp_data

    return OrigHttpResponse(json.dumps(resp_data),'application/json')

def add_candidate(request):

    if request.user.is_authenticated():
        user_id = request.user.id
        fname   = request.GET.get('fname')
        lname   = request.GET.get('lname')
        date    = request.GET.get('date')
        date    = date.replace('India Standard Time', 'IST')
        #jd_name = request.GET.get('jd').split('-')[0]
        jd = request.GET.get('jd')
        email   = request.GET.get('email')
        mobile  = request.GET.get('mobile')
        remarks = request.GET.get('remarks')
        if remarks:
            pass
        else:
            remarks = "New"
        date    = date_parser.parse(date.replace(' GMT ',' GMT+'))
        date    = date_parser.parse('-'.join(str(date).split('-')[:-1]))
        agent_id        = Agent.objects.filter(name_id = user_id).values_list('id', flat= True)[0]

        new_can = Candidate(jd_id = jd, location="",fname = fname,lname = lname,walk_in_date = date,email_id = email,
                  mobile_number = mobile,status_id = 21,agent_id = agent_id, remarks = remarks)
        try:
            new_can.save()
        except:
            traceback.print_exc()
            return HttpResponse("Duplicate Mobile number","1")
        data = {'status':'success'}

    else:
        data = {'status':'failed'}

    return HttpResponse(data)

@loginRequired
@allowedMethods(["POST"])
def delete_candidate(request):

    id_to_delete = request.POST.get('id_to_delete_json')
    id_to_delete = json.loads(id_to_delete)
    Candidate.objects.filter(id__in=id_to_delete['id_to_delete']).delete()

    data = {'status':'success'}
    return HttpResponse(data)

@loginRequired
@allowedMethods(["POST", "GET"])
def status_log(request):

    from collections import OrderedDict

    status_change   = {}
    candidate_id    = request.GET.get('id')
    status_objs     = Status.objects.filter(candidate_id=candidate_id).all()#.order_by('-modified_at')

    for status_obj in status_objs:
        status_change[str(status_obj.status.status_field)]                 = {}
        #status_change[str(status_obj.status.status_field)]['created_at']   = status_obj.created_at.strftime('%m/%d/%Y')
        status_change[str(status_obj.status.status_field)]['modified_at']  = status_obj.modified_at.strftime('%m/%d/%Y')
        status_change[str(status_obj.status.status_field)]['agent']        = str(status_obj.agent.name)
        status_change[str(status_obj.status.status_field)]['remarks']      = status_obj.remarks

    status_change = OrderedDict(sorted(status_change.items(), key=lambda kv: kv[1]['modified_at'], reverse=True))

    return OrigHttpResponse(json.dumps(status_change),'application/json')


#@loginRequired
#@allowedMethods(["GET"])
def bulk_update(request):
    first_name = request.get('fname')
    last_name  = request.get('lname')
    mobile     = request.get('mobile')
    mobile     = int(float(mobile))
    walkin_date= request.get('walkindate')
    jd_id      = request.get('jdid')
    jd_id      = int(float(jd_id))
    mail_id    = request.get('mailid')
    agent_id   = request.get('agentid')
    agent_id   = int(float(agent_id))
    new_can    = Candidate(jd_id=jd_id, fname=first_name, lname=last_name, mobile_number=mobile, walk_in_date=walkin_date,
                 email_id=mail_id, agent_id=agent_id, status_id=21, location='', remarks='New')
    try:
        new_can.save()
    except:
        return 'Duplicate Mobile number'

def update_candidate(request):

    if request.user.is_authenticated():
        can_id  = request.GET.get('id')
        fname   = request.GET.get('fname')
        lname   = request.GET.get('lname')
        date    = request.GET.get('date')
        date    = date.replace('India Standard Time', 'IST')
        print type(date)
        mobile  = request.GET.get('mobile')
        email   = request.GET.get('email')
        status  = request.GET.get('status')
        data    = {}
        if str(date) != "null":
            date    = date_parser.parse(date.replace(' GMT ',' GMT+'))
            date    = date_parser.parse('-'.join(str(date).split('-')[:-1]))
        else:
            date = ''
        status_id_of_request = StatusType.objects.filter(status_field=status.replace('_', ' '))
        remarks = request.GET.get('remarks')
        if remarks:
            pass
        else:
            remarks = "New"

        can_sta = Candidate.objects.filter(id=can_id)[0]
        if fname:
            can_sta.fname = fname
            data['fname'] = fname
        if lname:
            can_sta.lname = lname
            data['lname'] =lname
        if mobile:
            can_sta.mobile_number = mobile
            data['mobile'] = mobile
        if email:
            can_sta.email_id = email
            data['email'] = email
        if remarks:
            can_sta.remarks = remarks
            data['remarks']  = remarks
        if status:
            can_sta.status = status_id_of_request[0]
            data['status'] = status
        if date:
            can_sta.walk_in_date = date
        can_sta.save()
    return HttpResponse(data)



def excel_upload(request):
        fname = request.FILES['myfile']
        var = fname.name.split('.')[-1].lower()
        if var not in ['xls', 'xlsx', 'xlsb']:
                return HttpResponse("Invalid File")
        else:
                try:
                        open_book = open_workbook(filename=None, file_contents=fname.read())
                        open_sheet = open_book.sheet_by_index(0)
                except:
                        return HttpResponse("Invalid File")
                sheet_headers = validate_sheet(open_sheet, request)
                for row_idx in range(1, open_sheet.nrows):
                        for column, col_idx in sheet_headers:
                                cell_data = get_cell_data(open_sheet, row_idx, col_idx)
                                if column == 'fname':
                                        customer_data['fname'] = ''.join(cell_data)
                                if column == 'lname':
                                        customer_data['lname'] = ''.join(cell_data)
                                if column == 'mobile':
                                        customer_data['mobile'] = ''.join(cell_data)
                                if column == 'mailid':
                                        customer_data['mailid'] = ''.join(cell_data)
                                if column == 'jdid':
                                        customer_data['jdid'] = ''.join(cell_data)
                                if column == 'agentid':
                                        customer_data['agentid'] = ''.join(cell_data)
                                if column == 'scheduleddate':
                                        #cell_data = format_date(cell_data)
                                        cell_data = xlrd.xldate_as_tuple(int(cell_data.split('.')[0]), 0)
                                        cell_data ='%s-%s-%s' % (cell_data[0], cell_data[1], cell_data[2])
                                        customer_data['walkindate'] = ''.join(cell_data)
                        var = bulk_update(customer_data)
                        if var == 'Duplicate Mobile number':
                            return HttpResponse("Duplicate Mobile number",'1')

        return HttpResponse("Hello")

def get_order_of_headers(open_sheet, Default_Headers, mandatory_fileds=[]):
    indexes, sheet_indexes = {}, {}
    sheet_headers = open_sheet.row_values(0)
    lower_sheet_headers = [i.lower() for i in sheet_headers]
    if not mandatory_fileds:
        mandatory_fileds = Default_Headers

    max_index = len(sheet_headers)
    is_mandatory_available = set([i.lower() for i in mandatory_fileds]) - set([j.lower() for j in sheet_headers])
    for ind, val in enumerate(Default_Headers):
        val = val.lower()
        if val in lower_sheet_headers:
            ind_sheet = lower_sheet_headers.index(val)
            sheet_indexes.update({val: ind_sheet})
        else:
            ind_sheet = max_index
            max_index += 1
        #comparing with lower case for case insensitive
        #Change the code as declare *_XL_HEADEERS and *_XL_MAN_HEADERS
        indexes.update({val: ind_sheet})
    return is_mandatory_available, sheet_indexes, indexes

def get_cell_data(open_sheet, row_idx, col_idx):
    try:
        cell_data = open_sheet.cell(row_idx, col_idx).value
        cell_data = str(cell_data)
        if isinstance(cell_data, str):
            cell_data = cell_data.strip()
    except IndexError:
        cell_data = ''
    return cell_data

def format_date(cell_data):
    if not cell_data: return ''
    cell_data = xlrd.xldate_as_tuple(int(cell_data), 0)
    cell_data ='%s-%s-%s' % (cell_data[0], cell_data[1], cell_data[2])

    return date

def validate_sheet(open_sheet, request):
    sheet_headers = []
    #brand_channels = bran_chan_func(request)
    if open_sheet.nrows > 0:
        is_mandatory_available, sheet_headers, all_headers = get_order_of_headers(open_sheet, SOH_XL_HEADERS, SOH_XL_MAN_HEADERS)
        sheet_headers = sorted(sheet_headers.items(), key=lambda x: x[1])
        all_headers = sorted(all_headers.items(), key=lambda x: x[1])
        if is_mandatory_available:
            status = ["Fields are not available: %s" % (", ".join(list(is_mandatory_available)))]
            index_status.update({1: status})
            return "Failed", status

    else:
        status = "Number of Rows: %s" % (str(open_sheet.nrows))
        index_status.update({1: status})
    return sheet_headers

