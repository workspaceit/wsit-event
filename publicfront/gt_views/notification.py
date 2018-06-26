from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from app.models import Attendee, Locations, Answers, SessionTags, Booking, MatchLine, SeminarsUsers, Session, \
    Group, Notification, Setting, SeminarSpeakers, ActivityHistory, Questions
import json
import base64
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Q
import os
import io
import time
import boto
import base64
from django.core.urlresolvers import reverse
from boto.s3.key import Key
# from .attendee import Mailer
from .mail import MailHelper
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image, ExifTags

scheduler = BackgroundScheduler()
scheduler.add_jobstore('redis')
scheduler.start()
from django.contrib.sessions.models import Session as DjangoSession


class NotificationClass(generic.DetailView):
    def notifications(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                user_id = request.session['event_user']['id']
                notification = Notification.objects.filter(to_attendee_id=user_id, status=0)
                total_seconds = NotificationClass.get_timout(request.session['event_user']['event_id'])
                for nt in notification:

                    first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                        user_id=nt.sender_attendee_id)
                    last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                       user_id=nt.sender_attendee_id)
                    if first_name.exists():
                        nt.sender_attendee.firstname = first_name[0].value
                    if last_name.exists():
                        nt.sender_attendee.lastname = last_name[0].value

                    nt.expire_at = nt.created_at + timedelta(seconds=total_seconds)
                    nt.save()

                new_noty = 0
                if notification.count() > 0:
                    new_noty = notification[notification.count() - 1].id
                context = {
                    "notifications": notification,
                }
                request.session['event_user']['last_noty'] = new_noty
                request.session.modified = True
                return render(request, 'gt/notification/my_notifications.html', context)
            else:
                return redirect('gt-welcome')
        else:
            return redirect('gt-welcome')

    def get_notifications(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                user_id = request.session['event_user']['id']
                searchkey = request.POST.get('key')
                type = request.POST.get('sort_type')
                if type == None:
                    notification = Notification.objects.filter(to_attendee_id=user_id, status=0)
                else:
                    if type == "all":
                        if searchkey:
                            notification = Notification.objects.filter(to_attendee_id=user_id, status=0,
                                                                       message__icontains=searchkey)
                        else:
                            notification = Notification.objects.filter(to_attendee_id=user_id, status=0)
                    else:
                        if type == 'session':
                            notification = Notification.objects.filter(
                                Q(to_attendee_id=user_id, status=0, message__icontains=searchkey) & Q(
                                    Q(type='session') | Q(type='session_attend')))
                        elif type == 'attendee':
                            notification = Notification.objects.filter(
                                Q(to_attendee_id=user_id, status=0, message__icontains=searchkey) & Q(
                                    type='filter_message'))
                        else:
                            notification = Notification.objects.filter(to_attendee_id=user_id, status=0,
                                                                       message__icontains=searchkey, type=type)

                total_seconds = NotificationClass.get_timout(request.session['event_user']['event_id'])
                for nt in notification:
                    if nt.sender_attendee_id != None:
                        first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                            user_id=nt.sender_attendee_id)
                        last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                           user_id=nt.sender_attendee_id)
                        if first_name.exists():
                            nt.sender_attendee.firstname = first_name[0].value
                        if last_name.exists():
                            nt.sender_attendee.lastname = last_name[0].value
                    nt.expire_at = nt.created_at + timedelta(seconds=total_seconds);
                new_noty = 0
                if notification.count() > 0:
                    new_noty = notification[notification.count() - 1].id
                context = {
                    "notifications": notification
                }
                get_data = render_to_string('gt/notification/my_notifications_result.html', context)
                from publicfront.gt_views.common import CommonMenu
                sessions_finished = CommonMenu.get_finished_sessions(request)
                new_sessions_finished = []
                for session in sessions_finished:
                    new_sessions_finished.append(session.session.id)
                evaluate_context = {
                    'sessions_finished': sessions_finished
                }
                evaluate_data = render_to_string('gt/notification/evaluate_result.html', evaluate_context)
                sessions_next_up = CommonMenu.get_nextup_sessions(request)
                new_sessions_next_up = []
                for next_session in sessions_next_up:
                    new_sessions_next_up.append(next_session['id'])
                next_up_context = {
                    'sessions_next_up': sessions_next_up
                }
                next_up_data = render_to_string('gt/notification/next_up_result.html', next_up_context)
                evaluation_message = 'Du har en ny aktivitet att utvärdera'
                next_up_message = 'Du har en aktivitet som startar snart'
                time_now = CommonMenu.getTimezoneNow(request)
                f = '%Y-%m-%d %H:%M:%S'
                now = datetime.strptime(str(time_now).split(".")[0], f)
                show_next_up = False
                if 'new_sessions_next_up' in request.session['event_user']:
                    for next_id in new_sessions_next_up:
                        if next_id not in request.session['event_user']['new_sessions_next_up']:
                            session_info = Session.objects.get(id=int(next_id))
                            start = datetime.strptime(str(session_info.start).split("+")[0], f)
                            if start > now:
                                time = start - now
                                time = str(time).split(':')[1]
                                time = int(time) + 1
                                time = str(time) + ' minuter'
                            else:
                                time = 'now'
                            next_up_message = 'Din aktivitet ' + str(
                                session_info.name) + ' börjar inom ' + time + ' i/på ' + str(
                                session_info.location.name) + ''
                            show_next_up = True
                show_evaluation_message = 1
                show_evaluation = False
                if 'new_sessions_finished' in request.session['event_user']:
                    for evaluate_id in new_sessions_finished:
                        if evaluate_id not in request.session['event_user']['new_sessions_finished']:
                            evaluate_info = Session.objects.get(id=int(evaluate_id))
                            end = datetime.strptime(str(evaluate_info.end).split("+")[0], f)
                            end_1hr = end + timedelta(minutes=60)
                            if now > end_1hr:
                                show_evaluation_message = 0
                            evaluation_message = 'Tyck till om ' + str(evaluate_info.name) + ''
                            show_evaluation = True

                mydata = {
                    'notifications': get_data,
                    'evaluations': evaluate_data,
                    'next_up': next_up_data,
                    'new_noty': new_noty,
                    'new_sessions_finished': new_sessions_finished,
                    'new_sessions_next_up': new_sessions_next_up,
                    'evaluation_message': evaluation_message,
                    'next_up_message': next_up_message,
                    'show_evaluation_message': show_evaluation_message,
                    'show_next_up': show_next_up,
                    'show_evaluation': show_evaluation,
                    'success': True
                }
                request.session['event_user']['last_noty'] = new_noty
                request.session['event_user']['new_sessions_finished'] = new_sessions_finished
                request.session['event_user']['new_sessions_next_up'] = new_sessions_next_up
                request.session.modified = True
                return HttpResponse(json.dumps(mydata), content_type="application/json")
            else:
                mydata = {
                    'success': False
                }
                return HttpResponse(json.dumps(mydata), content_type="application/json")
        else:
            mydata = {
                'success': False
            }
            return HttpResponse(json.dumps(mydata), content_type="application/json")

    def deletenotification(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            id = request.POST.get('id')
            notification = Notification.objects.get(id=id)
            notification.status = 1;
            notification.save()
            response_data = {}
            response_data['status'] = 'success'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_timout(event_id):
        setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
        timeout = setting[0].value
        new_timeout = time.strptime(timeout, "%H:%M")
        total_seconds = timedelta(hours=new_timeout.tm_hour, minutes=new_timeout.tm_min,
                                  seconds=new_timeout.tm_sec).total_seconds()
        return total_seconds
