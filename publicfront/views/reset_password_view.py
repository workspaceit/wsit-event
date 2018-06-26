import json
import os, sys

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.http import Http404

import random
import string
import hashlib
from datetime import datetime, timedelta
from app.models import Attendee, EmailContents, AttendeePasswordResetRequest
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey
from publicfront.views.page2 import DynamicPage
from publicfront.views.send_email import UserEmail
from django.template.loader import render_to_string


class ResetPasswordPublic(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            resetpass_hash_key = request.GET.get('key')
            if resetpass_hash_key != "":
                userHashCodeData = AttendeePasswordResetRequest.objects.filter(hash_code=resetpass_hash_key,already_used=0,
                                                                       expired_at__gt=datetime.now(),attendee__event_id=request.session['event_id'])
                if userHashCodeData.exists():
                    request.session['reset_have_auth'] = "newpasstrue"
                    request.session['reset_have_auth_user_id'] = userHashCodeData[0].attendee_id
                    request.session['reset_have_auth_hashcode_id'] = userHashCodeData[0].id
                    return DynamicPage.get_static_page(request, 'new-password-page',True, *args, **kwargs)
                else:
                    return DynamicPage.get_static_page(request, '404-not-found', True, *args, **kwargs)
            else:
                return DynamicPage.get_static_page(request, '404-not-found', True, *args, **kwargs)
        except Exception as e:
            ErrorR.efail(e)
            return DynamicPage.get_static_page(request, '404-not-found', True, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            email = request.POST.get('user_email')
            event_id = request.session['event_id']
            response_data = {}
            language = LanguageKey.get_lang_key(request, 31)
            if email and email != "":
                userData = Attendee.objects.filter(email=email, event_id=event_id)
                if userData.exists():
                    if len(userData)>1:
                        response_data['success'] = True
                        response_data['multiple'] = True
                        response_data['message'] = render_to_string("public/element/reset_password_all_events.html", {"userData":userData, "csrf_token": request.POST.get('csrfmiddlewaretoken'), "language": language})
                    else:
                        attendee = userData[0]
                        userHashCodeData = AttendeePasswordResetRequest.objects.filter(attendee_id=attendee.id,already_used=0,
                                                                                       expired_at__gt=datetime.now())
                        if userHashCodeData.exists():
                            expired_at = datetime.now() + timedelta(hours=1)
                            AttendeePasswordResetRequest.objects.filter( id=userHashCodeData[0].id).update(
                                expired_at=expired_at, updated_at=datetime.now())
                        else:
                            key = ''.join(
                                random.choice(string.ascii_letters + string.digits + string.ascii_letters) for _ in
                                range(10)) + str(datetime.now())
                            key = key.encode('utf-8')
                            hash_code = hashlib.sha224(key).hexdigest()
                            AttendeePasswordResetRequest(attendee_id=attendee.id, hash_code=hash_code,
                                                         expired_at=datetime.now() + timedelta(hours=1)).save()
                        email_id = 0
                        if 'email_id' in request.POST:
                            email_id = request.POST.get('email_id')
                        else:
                            email_data = EmailContents.objects.filter(name='reset-password-confirmation',
                                                                      template__event_id=event_id)
                            if email_data.exists():
                                email_id = email_data[0].id
                        if email_id != 0:
                            UserEmail.send_email_reset_password(request, email_id, userData)
                        response_data['success'] = True
                        response_data['multiple'] =False
                        response_data['message'] = LanguageKey.catch_lang_key(request, 'reset-password','reset_password_notify_email_send')
                else:
                    response_data['success'] = False
                    response_data['message'] = 'User not exist .'
            else:
                response_data['success'] = False
                response_data['message'] = 'Email send without key'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            print(e)
            ErrorR.efail(e)
            raise Http404

    def save_new_password(request, *args, **kwargs):
        try:
            response_data={}
            from django.contrib.auth.hashers import make_password
            new_password = request.POST.get('new_password')
            if new_password != "":
                Attendee.objects.filter(id=request.session['reset_have_auth_user_id']).update(
                    password=make_password(new_password))
                AttendeePasswordResetRequest.objects.filter(id=request.session['reset_have_auth_hashcode_id']).update(already_used=1)
                del request.session['reset_have_auth_user_id']
                del request.session['reset_have_auth_hashcode_id']
                response_data['success'] = True
                response_data['location'] = request.session['base_url']+'/attendee-login'
                response_data['message'] = LanguageKey.catch_lang_key(request, 'new-password','new_password_notify_changed')
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            raise Http404
        except Exception as e:
            ErrorR.efail(e)
            raise Http404
