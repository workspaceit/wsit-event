import os
from django.template.loader import render_to_string
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import generic
from django.views.generic import TemplateView

from app.models import Setting, Attendee, AttendeePasswordResetRequest, EmailContents, Events
from django.http import HttpResponse
from django.conf import settings
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey
from publicfront.views.page2 import DynamicPage
import random
import string
import hashlib
import json
from datetime import datetime, timedelta
import django

from publicfront.views.send_email import UserEmail


class RootEvent(generic.DetailView):
    def get(self, request, *args, **kwargs):
        default_project = Setting.objects.filter(name='default_project')
        base_url = request.build_absolute_uri()
        if default_project.exists():
            return redirect(base_url + default_project[0].value+"/")
        return redirect('http://workspaceit.com/')

    def health(request, *args, **kwargs):
        return render(request, 'public/health.html')

    def bad_request(request):
        print('bad_request')
        return HttpResponse("400")

    def permission_denied(request):
        print('permission_denied')
        return HttpResponse("403")

    def page_not_found(request, *args, **kwargs):
        # if 'event_id' in request.session:
        #     return DynamicPage.get_static_page(request, '404-not-found', True, *args, **kwargs)
        # else:
        print('page_not_found')
        return HttpResponse("404")

    def server_error(request):
        print('server_error')
        return HttpResponse("500")


class RetrivePasswrod(TemplateView):
    def get(self, request, *args, **kwargs):
        st = ''
        try:
            request.session['event_url'] = 'default-project'
            request.session['event_id'] = Events.objects.get(url='default-project').id
            request.session['site_url'] = settings.SITE_URL
            request.session.modified = True
            return DynamicPage.get_static_page(request, 'reset-password-page', True, *args, **kwargs)
        except Exception as e:
            ErrorR.efail(e)
            return HttpResponse(st)

    def post(self, request, *args, **kwargs):
        try:
            request.session['site_url'] = settings.SITE_URL
            request.session.modified = True
            email = request.POST.get('user_email')
            response_data = {}
            if email and email != "":
                userData = Attendee.objects.filter(email=email)
                if userData.exists():
                    if len(userData) > 1:
                        response_data['success'] = True
                        language = LanguageKey.get_lang_key(request, 31)
                        response_data['multiple_event_list'] = render_to_string("public/element/reset_password_all_events.html",{"userData":userData,"csrf_token": django.middleware.csrf.get_token(request), "language": language})
                    else:
                        request.session['event_url'] = userData[0].event.url
                        request.session['event_id'] = userData[0].event_id
                        event_id = request.session['event_id']
                        key = ''.join(
                            random.choice(string.ascii_letters + string.digits + string.ascii_letters) for _ in
                            range(10)) + str(datetime.now())
                        key = key.encode('utf-8')
                        hash_code = hashlib.sha224(key).hexdigest()

                        getAttendeePasswordResetRequest = AttendeePasswordResetRequest.objects.filter(attendee_id=userData[0].id,
                                                                                    already_used=0,
                                                                                    expired_at__gt=datetime.now())
                        if getAttendeePasswordResetRequest.exists():
                            expired_at = datetime.now() + timedelta(hours=1)
                            AttendeePasswordResetRequest.objects.filter(id=getAttendeePasswordResetRequest[0].id).update(expired_at=expired_at, updated_at=datetime.now())
                        else:
                            AttendeePasswordResetRequest(attendee_id=userData[0].id, hash_code=hash_code,
                                                    expired_at=datetime.now() + timedelta(hours=1)).save()
                        email_id = 0
                        email_data = EmailContents.objects.filter(name='reset-password-confirmation',
                                                                  template__event_id=event_id)
                        if email_data.exists():
                            email_id = email_data[0].id
                        if email_id != 0:
                            UserEmail.send_email_reset_password(request, email_id, userData)
                        response_data['success'] = True
                        response_data['message'] = LanguageKey.catch_lang_key(request, 'reset-password',
                                                                              'reset_password_notify_email_send')
                else:
                    response_data['success'] = False
                    response_data['message'] = 'User not exist .'
            else:
                response_data['success'] = False
                response_data['message'] = 'Email send without key'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            ErrorR.efail(e)
            raise Http404

    def sendRetrivePasswrodMailByID(request):
        response_data = {}
        try:
            userData = Attendee.objects.filter(id=request.POST.get('user_id'))
            request.session['event_url'] = userData[0].event.url
            request.session['event_id'] = userData[0].event_id
            event_id = request.session['event_id']
            getAttendeePasswordResetRequest = AttendeePasswordResetRequest.objects.filter(attendee_id=userData[0].id,
                                                                                          already_used=0,
                                                                                          expired_at__gt=datetime.now())
            if getAttendeePasswordResetRequest.exists():
                expired_at = datetime.now() + timedelta(hours=1)
                AttendeePasswordResetRequest.objects.filter(id=getAttendeePasswordResetRequest[0].id).update(
                    expired_at=expired_at, updated_at=datetime.now())

            else:
                key = ''.join(
                    random.choice(string.ascii_letters + string.digits + string.ascii_letters) for _ in
                    range(10)) + str(datetime.now())
                key = key.encode('utf-8')
                hash_code = hashlib.sha224(key).hexdigest()
                AttendeePasswordResetRequest(attendee_id=userData[0].id, hash_code=hash_code,
                                             expired_at=datetime.now() + timedelta(hours=1)).save()
            email_id = 0
            email_data = EmailContents.objects.filter(name='reset-password-confirmation',
                                                      template__event_id=event_id)
            if email_data.exists():
                email_id = email_data[0].id
            if email_id != 0:
                UserEmail.send_email_reset_password(request, email_id, userData)
            response_data['success'] = True
            response_data['message'] = LanguageKey.catch_lang_key(request, 'reset-password',
                                                                  'reset_password_notify_email_send')
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

