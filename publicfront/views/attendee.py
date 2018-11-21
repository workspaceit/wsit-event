try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from app.models import Users,Setting, Attendee, Session, Group, Room, SeminarsUsers, Questions, Booking, Answers, RequestedBuddy, RoomAllotment, Option,ActivityHistory
import json
from django.db import transaction
from django.views.generic import TemplateView
import string
import random
from datetime import datetime, timedelta
from django.conf import settings
import os
import boto
from boto.s3.key import Key
from pytz import timezone


class AttendeeRegistration(TemplateView):

    def getTimezoneNow(self, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone')
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            now = datetime.now(timezone_active)
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            return now

    def saveAnswers(userId, answer, *args, **kwargs):
        print(answer['answer'])
        if answer['answer'] is "null" or answer['answer'] is None:
            answer['answer'] = ""
        answerExist = Answers.objects.filter(question_id=answer['id'], user_id=userId)
        if answerExist.exists():
            # if answer['answer'] == "":
            #     Answers.objects.filter(question_id=answer['id'], user_id=userId).delete()
            # else:
            old_value = answerExist[0].value
            Answers.objects.filter(question_id=answer['id'], user_id=userId).update(value=answer['answer'])
            if old_value != answer['answer']:
                activity_history = ActivityHistory(attendee_id=userId,activity_type='update', category='question', question_id=answer['id'], old_value=old_value, new_value=answer['answer'], event_id=answerExist[0].question.group.event_id)
                activity_history.save()
            attendeeAnswer = Answers.objects.filter(question_id=answer['id'], user_id=userId)
            return attendeeAnswer[0]
        else:
            # if answer['answer'] != '':
            attendeeAnswer = Answers(value=answer['answer'], question_id=answer['id'], user_id=userId)
            attendeeAnswer.save()
            return attendeeAnswer

    def check_available_room(booking, room_id):
        start_date = datetime.strptime(booking['check_in'], '%Y-%m-%d')
        end_date = datetime.strptime(booking['check_out'], '%Y-%m-%d')
        day_count = (end_date - start_date).days + 1
        room = Room.objects.get(id=room_id)
        available = True
        for single_date in (start_date + timedelta(n) for n in range(day_count)):
            current_date = datetime.strftime(single_date, '%Y-%m-%d')
            allotments = RoomAllotment.objects.filter(available_date=current_date, room_id=room_id)
            if allotments.count():
                get_bookings = Booking.objects.filter(room_id=room_id, check_in__lte=current_date,
                                                      check_out__gte=current_date).count()
                if 'id' in booking:
                    get_bookings = get_bookings - 1
                total_beds = room.beds * allotments[0].allotments
                if get_bookings >= total_beds:
                    available = False
            else:
                available = False
        return available

class AttendeeInfo(generic.DetailView):
    def get(self, request, pk, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee = Attendee.objects.get(id=pk)
            if attendee:
                first_name = Answers.objects.filter(question__actual_definition='firstname', user_id=pk)
                last_name = Answers.objects.filter(question__actual_definition='lastname', user_id=pk)
                bio = Answers.objects.filter(question__title__iexact='bio', user_id=pk)
                if os.environ['ENVIRONMENT_TYPE'] != 'master' and os.environ['ENVIRONMENT_TYPE'] != 'staging' and os.environ['ENVIRONMENT_TYPE'] != 'develop':
                    attendee.avatar = ''
                else:
                    if attendee.avatar != '':
                        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
                        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                        filename = 'public/images/attendee/attendee_' + str(attendee.id) + '.jpg'
                        key_name = filename
                        k = Key(bucket)
                        k.key = key_name
                        if not k.exists():
                           attendee.avatar = ''
                if first_name.exists():
                    attendee.firstname = first_name[0].value
                if last_name.exists():
                    attendee.lastname = last_name[0].value
                if bio.exists():
                    attendee.bio = bio[0].value
                else:
                    attendee.bio = ''
                context ={
                    "attendee": attendee
                }

                return render(request, 'public/attendee/attendee_bio.html', context)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def get_push_notification_status(request, *args, **kwargs):
        response_data = {}
        try:
            if 'secret_key' in request.GET:
                secret_key = request.GET.get('secret_key')
                attendee = Attendee.objects.filter(secret_key=secret_key)
                if attendee.exists():
                    response_data['success'] = True
                    response_data['push_notification_status'] = attendee[0].push_notification_status
                else:
                    response_data['success'] = False
                    response_data['message'] = 'Secret Key is not correct'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['success'] = False
                response_data['message'] = 'Please Login First'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            response_data['success'] = False
            response_data['message'] = 'Something went wrong, Please try again'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def change_push_notification_status(request, *args, **kwargs):
        response_data = {}
        try:
            if 'secret_key' in request.GET:
                secret_key = request.GET.get('secret_key')
                attendee = Attendee.objects.filter(secret_key=secret_key)
                if attendee.exists():
                    if 'push_notification' in request.GET:
                        push_notification_status = request.GET.get('push_notification')
                        if str(push_notification_status) == '1':
                            Attendee.objects.filter(id=attendee[0].id).update(push_notification_status=1)
                            response_data['success'] = True
                            response_data['message'] = 'Attendee Push Notification Status Updated'
                        elif str(push_notification_status) == '0':
                            Attendee.objects.filter(id=attendee[0].id).update(push_notification_status=0)
                            response_data['success'] = True
                            response_data['message'] = 'Attendee Push Notification Status Updated'
                        else:
                            response_data['success'] = False
                            response_data['message'] = 'Please sent the correct key'
                        attendee = Attendee.objects.get(id=attendee[0].id)
                        response_data['push_notification_status'] = attendee.push_notification_status
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                    else:
                        response_data['success'] = False
                        response_data['message'] = 'Please sent the correct status'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data['success'] = False
                    response_data['message'] = 'Secret Key is not correct'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['success'] = False
                response_data['message'] = 'Please Login First'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            response_data['success'] = False
            response_data['message'] = 'Something went wrong, Please try again'
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class AttendeeSearch(generic.DetailView):
    def get(self, request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            return render(request, 'public/attendee/attendee_search.html')
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def post(self, request, *args, **kwargs):
        key =request.POST.get('sort_key')
        searchkey = request.POST.get('key')
        if key == "lastname":
            # attendee_list = Attendee.objects.all().order_by('lastname')
            if searchkey:
                searchkey = "%%%s%%" % searchkey
                #attendee_list = Attendee.objects.raw('select attendees.id,attendees.firstname, attendees.lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where (attendees.firstname like %s or attendees.lastname like %s or answers.value like %s)  order by attendees.lastname',[searchkey,searchkey,searchkey])
                attendee_list = Attendee.objects.raw('select attendees.id,IFNULL((select value from answers where answers.question_id=68 and answers.user_id=attendees.id ),attendees.firstname)as firstname,IFNULL((select value from answers where answers.question_id=69 and answers.user_id=attendees.id ),attendees.lastname)as lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where (select value from answers where answers.question_id=68 and answers.user_id=attendees.id ) like %s or (select value from answers where answers.question_id=69 and answers.user_id=attendees.id ) like %s or answers.value like %s or attendees.firstname like %s or attendees.lastname  like %s order by lastname',[searchkey,searchkey,searchkey,searchkey,searchkey])
            else:
                attendee_list = Attendee.objects.raw('select attendees.id,IFNULL((select value from answers where answers.question_id=68 and answers.user_id=attendees.id ),attendees.firstname)as firstname,IFNULL((select value from answers where answers.question_id=69 and answers.user_id=attendees.id ),attendees.lastname)as lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 order by lastname')
            dataList = []

            if len(list(attendee_list))>0:
                alphabet = attendee_list[0].lastname[0]
                row_data=[]
                for attendee in attendee_list:
                    if attendee.event_id == request.session['event_user']['event_id']:
                        if alphabet.lower() == attendee.lastname[0].lower():
                            row_data.append(attendee)
                        else:
                            dataList.append({"alphabet":alphabet.upper(),"attendees":row_data})
                            row_data=[]
                            alphabet= attendee.lastname[0]
                            row_data.append(attendee)

                dataList.append({"alphabet":alphabet.upper(),"attendees":row_data})
        elif key=="firstname":
            #attendee_list = Attendee.objects.all().order_by('firstname')
            if searchkey:
                searchkey = "%%%s%%" % searchkey
                #attendee_list = Attendee.objects.raw('select attendees.id,attendees.firstname, attendees.lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where attendees.firstname like %s or attendees.lastname like %s or answers.value like %s  order by attendees.firstname',[searchkey,searchkey,searchkey])
                attendee_list = Attendee.objects.raw('select attendees.id,IFNULL((select value from answers where answers.question_id=68 and answers.user_id=attendees.id ),attendees.firstname)as firstname,IFNULL((select value from answers where answers.question_id=69 and answers.user_id=attendees.id ),attendees.lastname)as lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where (select value from answers where answers.question_id=68 and answers.user_id=attendees.id ) like %s or (select value from answers where answers.question_id=69 and answers.user_id=attendees.id ) like %s or answers.value like %s or attendees.firstname like %s or attendees.lastname  like %s order by firstname',[searchkey,searchkey,searchkey,searchkey,searchkey])
            else:
                attendee_list = Attendee.objects.raw('select attendees.id,IFNULL((select value from answers where answers.question_id=68 and answers.user_id=attendees.id ),attendees.firstname)as firstname,IFNULL((select value from answers where answers.question_id=69 and answers.user_id=attendees.id ),attendees.lastname)as lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 order by firstname')
            dataList = []
            if len(list(attendee_list))>0:
                alphabet = attendee_list[0].firstname[0]
                row_data=[]
                for attendee in attendee_list:
                    if attendee.event_id == request.session['event_user']['event_id']:
                        if alphabet.lower() == attendee.firstname[0].lower():
                            row_data.append(attendee)
                        else:
                            dataList.append({"alphabet":alphabet.upper(),"attendees":row_data})
                            row_data=[]
                            alphabet= attendee.firstname[0]
                            row_data.append(attendee)
                dataList.append({"alphabet":alphabet.upper(),"attendees":row_data})
        elif key=="office":
            #attendee_list = Attendee.objects.all().order_by('firstname')
            if searchkey:
                searchkey = "%%%s%%" % searchkey
                #attendee_list = Attendee.objects.raw('select attendees.id,attendees.firstname, attendees.lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where attendees.firstname like %s or attendees.lastname like %s or answers.value like %s  order by office',[searchkey,searchkey,searchkey])
                attendee_list = Attendee.objects.raw('select attendees.id,IFNULL((select value from answers where answers.question_id=68 and answers.user_id=attendees.id ),attendees.firstname)as firstname,IFNULL((select value from answers where answers.question_id=69 and answers.user_id=attendees.id ),attendees.lastname)as lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where (select value from answers where answers.question_id=68 and answers.user_id=attendees.id ) like %s or (select value from answers where answers.question_id=69 and answers.user_id=attendees.id ) like %s or answers.value like %s or attendees.firstname like %s or attendees.lastname  like %s order by office',[searchkey,searchkey,searchkey,searchkey,searchkey])
            else:
                attendee_list = Attendee.objects.raw('select attendees.id,IFNULL((select value from answers where answers.question_id=68 and answers.user_id=attendees.id ),attendees.firstname)as firstname,IFNULL((select value from answers where answers.question_id=69 and answers.user_id=attendees.id ),attendees.lastname)as lastname, answers.value AS office from attendees left join answers on attendees.id=answers.user_id and answers.question_id=56 where answers.value is not NULL order by office')
            dataList = []
            if len(list(attendee_list))>0:
                alphabet = attendee_list[0].office[0]
                row_data=[]
                #dataList[alphabet]
                for attendee in attendee_list:
                    if attendee.event_id == request.session['event_user']['event_id']:
                        if attendee.office:
                            if alphabet.lower() == attendee.office[0].lower():
                                row_data.append(attendee)
                            else:
                                dataList.append({"alphabet":alphabet.upper(),"attendees":row_data})
                                row_data=[]
                                alphabet= attendee.office[0]
                                row_data.append(attendee)

                dataList.append({"alphabet":alphabet.upper(),"attendees":row_data})

        #return HttpResponse(json.dumps(dataList), content_type="application/json")
        return render(request, 'public/attendee/attendee_search_result.html',{"dataList":dataList})


