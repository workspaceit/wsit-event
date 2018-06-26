from django.shortcuts import redirect
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Answers, SeminarsUsers, SeminarSpeakers, Attendee, Notification
import json
from django.db.models import Q
import os
import re
import boto
from boto.s3.key import Key
from django.conf import settings


class ExportSession(generic.DetailView):
    def get(self, request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            user_id = request.session['event_user']['id']
            allSession = SeminarSpeakers.objects.filter(speaker_id=user_id)
            context = []
            for session in allSession:
                context.extend([{'session_id': session.session.id, 'session_name': session.session.name}])

            user_id = request.session['event_user']['id']
            attendee = Attendee.objects.get(id=user_id)
            if os.environ['ENVIRONMENT_TYPE'] != 'master' and os.environ['ENVIRONMENT_TYPE'] != 'staging' and os.environ['ENVIRONMENT_TYPE'] != 'develop':
                attendee.avatar = ''
            else:
                if attendee.avatar != '':
                    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                    filename = 'public/images/attendee/attendee_' + str(attendee.id) + '.jpg'
                    key_name = filename
                    k = Key(bucket)
                    k.key = key_name
                    if not k.exists():
                        attendee.avatar = ''
            first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                                        user_id=user_id)
            last_name = Answers.objects.filter(question__actual_definition='lastname',
                                               user_id=user_id)
            attending_status = 'No'
            bio = Answers.objects.filter(question__title__iexact='bio', user_id=user_id)
            attending = Answers.objects.filter(question_id=154, user_id=user_id)
            if attending.exists():
                attending_status = attending[0].value
            if first_name.exists():
                fname = first_name[0].value
            else:
                fname = attendee.firstname
            if last_name.exists():
                lname = last_name[0].value
            else:
                lname = attendee.lastname


            type = attendee.type
            speakers = SeminarSpeakers.objects.filter(speaker_id = attendee.id)
            notification = Notification.objects.filter(to_attendee_id=attendee.id,status=0)
            new_noty = 0
            if notification.count() > 0:
                new_noty = notification[notification.count()-1].id
            if speakers.exists():
                type = "speaker"
            data = {
                'cntx': context,
                'user_info': attendee,
                'first_name': fname,
                'last_name': lname,
                'bio': bio
            }
            auth_user = {
                "id": attendee.id,
                "name": fname+' '+lname,
                "email": attendee.email,
                "type": type,
                "attending": attending_status,
                "avatar": attendee.avatar,
                "secret_key": attendee.secret_key,
                'last_noty': new_noty,
                "event_id": attendee.event.id
            }
            request.session['event_user'] = auth_user

            return render(request, 'public/session/export_session.html', data)
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def getDesiredAttList(request, *args, **kwargs):
        response_data = {}
        firstname = ''
        lastname = ''
        office = ''
        status = ''
        email = ''
        attending = 0
        inCue = 0
        response_data = {}
        response_data['datas'] = []
        sessionId = request.POST.get('sessionId')
        sessionType = request.POST.get('sessionType')
        if sessionType == 'both':
            session = SeminarsUsers.objects.filter(session_id=sessionId).exclude(status='not-attending')
        else:
            session = SeminarsUsers.objects.filter(session_id=sessionId, status=sessionType)

        for att in session:
            att_answer = Answers.objects.filter(Q(user_id=att.attendee_id) & (
            Q(question__actual_definition='firstname') | Q(question__actual_definition='lastname') | Q(question__actual_definition='email') | Q(question_id=156)))
            for ans in att_answer:
                if ans.question.actual_definition == 'firstname':
                    firstname = ans.value
                if ans.question.actual_definition == 'lastname':
                    lastname = ans.value
                if ans.question_id == 156:
                    office = ans.value
                if ans.question.actual_definition == 'email':
                    email = ans.value
            if firstname == '':
                firstname = att.attendee.firstname
            if lastname == '':
                lastname = att.attendee.lastname
            if email == '':
                email = att.attendee.email
            status = att.status
            if status == 'in-queue':
                status = 'In Queue'
            response_data['datas'].append([firstname, lastname, email, office, status])

        attending = SeminarsUsers.objects.filter(session_id=sessionId, status='attending').count()
        inCue = SeminarsUsers.objects.filter(session_id=sessionId, status='in-queue').count()

        response_data['status'] = 'Success'
        response_data['attending'] = attending
        response_data['cue'] = inCue
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def export_for_speaker(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            session_id = request.GET.get('session_id')
            session_type = request.GET.get('session_type')
            header = ['First Name', 'Last Name', 'Phone', 'Email', 'Office', 'Status']
            wb = Workbook()
            excelSheet = [[]]
            excelSheet.append(wb.active)
            user_id = request.session['event_user']['id']
            allSession = SeminarSpeakers.objects.filter(speaker_id=user_id, session_id=session_id)
            firstname = ''
            lastname = ''
            email = ''
            phone = ''
            office = ''
            status = ''
            i = 0
            try:
                for session in allSession:
                    sName = session.session.name
                    sName = re.sub('[^A-Za-z0-9 ]+', '', sName)
                    if len(sName) > 30:
                        sName = sName[:30]
                    if i > 0:

                        excelSheet.append(wb.create_sheet(i, sName))
                    elif i == 0:
                        excelSheet[1].title = sName
                    i = i + 1
                    excelSheet[i].append(header)
                    if session_type == 'both':
                        session = SeminarsUsers.objects.filter(Q(session_id=session.session.id) & (Q(status='attending') | Q(status='in-queue')))
                    else:
                        session = SeminarsUsers.objects.filter(session_id=session.session.id, status=session_type)
                    for att in session:
                        att_answer = Answers.objects.filter(Q(user_id=att.attendee_id) & (
                        Q(question__actual_definition='firstname') | Q(question__actual_definition='lastname') | Q(
                            question__actual_definition='email') | Q(question__actual_definition='phone') | Q(
                            question_id=156)))
                        for ans in att_answer:
                            if ans.question.actual_definition == 'firstname':
                                firstname = ans.value
                            if ans.question.actual_definition == 'lastname':
                                lastname = ans.value
                            if ans.question.actual_definition == 'email':
                                email = ans.value
                            if ans.question.actual_definition == 'phone':
                                phone = ans.value
                            if ans.question_id == 156:
                                office = ans.value

                            if firstname == '':
                                firstname = att.attendee.firstname
                            if lastname == '':
                                lastname = att.attendee.lastname
                            if email == '':
                                email = att.attendee.email
                            if phone == '':
                                phone = att.attendee.phonenumber
                        status = att.status
                        excelSheet[i].append([firstname, lastname, phone, email, office, status])
                if not os.path.exists("SpeakersExport"):
                    os.makedirs("SpeakersExport")
                wb.save("SpeakersExport/Attending Users.xlsx")
                response = HttpResponse(save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="Attending Users.xls"'
                return response
            except Exception as e:
                return HttpResponse(json.dumps(['Exception ' + str(e)]), content_type="application/json")
        else:
            return HttpResponse(json.dumps({}), content_type="application/json")
