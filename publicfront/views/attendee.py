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
from app.models import Attendee, Room, Booking, Answers, RoomAllotment, ActivityHistory
import json
from django.views.generic import TemplateView
from datetime import datetime, timedelta
from django.conf import settings
import os
import boto
from boto.s3.key import Key
from pytz import timezone


class AttendeeRegistration(TemplateView):

    def saveAnswers(userId, answer, *args, **kwargs):
        if answer['answer'] is "null" or answer['answer'] is None:
            answer['answer'] = ""
        answerExist = Answers.objects.filter(question_id=answer['id'], user_id=userId)
        if answerExist.exists():
            old_value = answerExist[0].value
            Answers.objects.filter(question_id=answer['id'], user_id=userId).update(value=answer['answer'])
            if old_value != answer['answer']:
                activity_history = ActivityHistory(attendee_id=userId,activity_type='update', category='question', question_id=answer['id'], old_value=old_value, new_value=answer['answer'], event_id=answerExist[0].question.group.event_id)
                activity_history.save()
            attendeeAnswer = Answers.objects.filter(question_id=answer['id'], user_id=userId)
            return attendeeAnswer[0]
        else:
            attendeeAnswer = Answers(value=answer['answer'], question_id=answer['id'], user_id=userId)
            attendeeAnswer.save()
            return attendeeAnswer

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


