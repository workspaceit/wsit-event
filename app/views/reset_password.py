import os
import json
import random
import string
import hashlib
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect
from django.contrib import messages

from django.contrib.auth.hashers import make_password
from .mail import MailHelper
from app.models import Users, PasswordResetRequest
from django.conf import settings


class ResetPasswordREquest(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'reset_password/request_reset_password.html', {})

    def post(self, request, *args, **kwargs):
        response_data = {}
        email = request.POST.get('email')
        try:
            users = Users.objects.filter(email=email)
            if users.count() > 0:
                user = users[0]
                # generate hash code and store
                key = ''.join(
                    random.choice(string.ascii_letters + string.digits + string.ascii_letters) for _ in
                    range(10)) + str(datetime.now())
                key = key.encode('utf-8')
                hash_code = hashlib.sha224(key).hexdigest()

                # send mail
                subject = "Event Manager::Password Reset"
                receiver = user.email
                sender_mail = "workspaceinfotech@gmail.com"
                base_url = settings.SITE_URL
                context = {'base_url': base_url, 'key': hash_code}
                template = "reset_password/email.html"
                MailHelper.mail_send(template, context, subject, receiver, sender_mail)
                PasswordResetRequest(user=user, hash_code=hash_code, expired_at=datetime.now()+timedelta(hours=24)).save()
                response_data = {'success': True, 'messages': ['Mail sent to reset password']}
            else:
                response_data = {'success': False, 'errors': ['User does not exist']}

        except Exception:
            response_data = {'success': False, 'errors': ['Something went wrong.']}

        return HttpResponse(json.dumps(response_data), content_type="application/json")


class ResetPassword(TemplateView):

    def get(self, request, *args, **kwargs):
        hash_code = request.GET.get('key')
        try:
            reset_password = PasswordResetRequest.objects.get(hash_code=hash_code)
            if datetime.now() > reset_password.expired_at:
                raise PasswordResetException("expired")
            elif reset_password.already_used:
                raise PasswordResetException("used")
            else:
                user = reset_password.user
                context = {'hash_code': hash_code, 'user_id': user.id}
                return render(request, 'reset_password/reset_password.html', context)
        except ObjectDoesNotExist:
            raise Http404("dsd")
        except PasswordResetException as e:
            print(e.message)
            if e.message == 'expired':
                context = {'message': 'The link is already expired.'}
            elif e.message == 'used':
                context = {'message': 'The link is already used once by you.'}
            return render(request, 'reset_password/reset_password.html', context)

    def post(self, request, *args, **kwargs):
        try:
            hash_code = request.POST.get('key')
            user_id = request.POST.get('uid')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            reset_password = PasswordResetRequest.objects.get(hash_code=hash_code, user__id=user_id)
            user = reset_password.user
            if datetime.now() > reset_password.expired_at:
                raise PasswordResetException("expired")
            elif reset_password.already_used:
                raise PasswordResetException("used")
            if password == confirm_password:
                user.password = make_password(password)
                user.save()
                reset_password.already_used = True
                reset_password.save()
                messages.success(request, 'Your password is changed successfully. You can now login')
                return redirect('login')
            else:
                raise Exception
        except ObjectDoesNotExist:
            raise Http404()
        except PasswordResetException as e:
            if e.message == 'expired':
                context = {'message': 'The link is already expired.'}
            elif e.message == 'used':
                context = {'message': 'The link is already used once by you.'}
            return render(request, 'reset_password/reset_password.html', context)
        except Exception:
            messages.success(request, 'Something went wrong.')
            return redirect('login')


class PasswordResetException(Exception):
    def __init__(self, message):
        self.message = message




