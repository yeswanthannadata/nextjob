from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
class Command(BaseCommand):

    commands = ['sendreport',]
    args = '[command]'
    help = 'Send report'

    def handle(self, *args, **options):


        #reports = Log.objects.filter(date__gt=datetime.today(),date__lt=(datetime.today()+timedelta(days=2)))
        #for report in reports:
        from django.core import mail
        from django.core.mail import send_mail, BadHeaderError
        from django.core.mail import EmailMessage
        from api.models import JD as JobDesTable
        from api.models import StatusType
        from api.models import Candidate
        import datetime

        counts              = {}
        jds                 = JobDesTable.objects.values_list('id', 'job_title')
        selected_option_id  = StatusType.objects.filter(status_field='Selected').values_list(flat=True)[0]
        no_show_option_id   = StatusType.objects.filter(status_field='No Show').values_list(flat=True)[0]
        #closed_option_id    = StatusType.objects.filter(status_field='Closed').values_list(flat=True)[0]
        scheduled_option_id = StatusType.objects.filter(status_field='Scheduled').values_list(flat=True)[0]
        content             = ""
        for jd in jds:

            counts[jd[1]] = {}
            counts[jd[1]]['selected']           = Candidate.objects.filter(status=selected_option_id, jd=jd[0]).count()
            counts[jd[1]]['no_show']            = Candidate.objects.filter(status=no_show_option_id, jd=jd[0]).count()
            #counts[jd[1]]['closed']             = Candidate.objects.filter(status=closed_option_id, jd=jd[0]).count()
            counts[jd[1]]['Scheduled Today']    = Candidate.objects.filter(status=scheduled_option_id, 
                                                                        jd=jd[0], walk_in_date=datetime.datetime.today()).count()
            counts[jd[1]]["Didn't Get Response"]= Candidate.objects.filter(status=scheduled_option_id, 
                                                                        jd=jd[0], walk_in_date__lt=datetime.datetime.today()).count()

        for jd_name in counts:
            content     += "<h3>" + jd_name + "</h3><ul>"

            for section, count in counts[jd_name].items():
                if section == "Didn't Get Response":
                    content += "<li style='color:red'>" + section + " : " + str(count) + "</li>"
                else:
                    content += "<li>" + section + " : " + str(count) + "</li>"

            content     += "</ul>"
        print content

        msg                 = EmailMessage("Report" , content, 'sportsolympictool@gmail.com', ['akhilraj@headrun.com'])
        msg.content_subtype = "html"
        msg.send()
