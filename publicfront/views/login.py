from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import generic
from app.models import Attendee, Answers, Elements, EmailContents
from django.contrib.auth.hashers import check_password
from publicfront.views.lang_key import LanguageKey
from publicfront.views.page2 import DynamicPage
import json
from publicfront.views.send_email import UserEmail


class LoginView(generic.View):
    def get(self, request, *args, **kwargs):
        if 'is_user_login' not in request.session:
            return DynamicPage.get_static_page(request, 'default-login-page', True, *args, **kwargs)
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def post(self, request, *args, **kwargs):
        response_data = {}
        email = request.POST.get('user_email')
        password = request.POST.get('user_password')
        event_id = request.session["event_id"]
        try:
            element = Elements.objects.filter(slug="login-form")
            language = LanguageKey.get_lang_key(request, element[0].id)
            users = Attendee.objects.filter(email=email, event_id=event_id)
            # request.session.flush()
            for user in users:
                if check_password(password, user.password):
                    if 'event_user' in request.session:
                        del request.session['event_user']
                    if 'is_user_login' in request.session:
                        del request.session['is_user_login']
                    first_name = Answers.objects.filter(question__actual_definition='firstname', user_id=user.id)
                    last_name = Answers.objects.filter(question__actual_definition='lastname', user_id=user.id)
                    attending = 'Yes'
                    if first_name.exists():
                        fname = first_name[0].value
                    else:
                        fname = user.firstname
                    if last_name.exists():
                        lname = last_name[0].value
                    else:
                        lname = user.lastname
                    auth_user = {
                        "id": user.id,
                        "name": fname + ' ' + lname,
                        "email": user.email,
                        "type": user.type,
                        "attending": attending,
                        "avatar": user.avatar,
                        "secret_key": user.secret_key,
                        "event_id": user.event.id
                    }

                    request.session['event_user'] = auth_user
                    request.session['event_id'] = auth_user['event_id']
                    request.session['is_user_login'] = True
                    response_data['success'] = True
                    response_data['redirect_url'] = '/'
                    response_data['message'] = language['langkey']['login_form_notify_successfull']
                else:
                    response_data['message'] = language['langkey']['login_form_notify_valid_failed']
                    response_data['success'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except ObjectDoesNotExist:
            response_data['message'] = language['langkey']['login_form_notify_valid_failed']
            response_data['success'] = False
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def retrieve_uid(request, *args, **kwargs):
        response_data = {}
        email = request.POST.get('user_email')
        event_id = request.session["event_id"]
        attendee = Attendee.objects.filter(email=email, event_id=event_id)
        element = Elements.objects.filter(slug="request-login")
        language = LanguageKey.get_lang_key(request, element[0].id)
        if attendee.exists():
            if 'send_email_id' in request.POST:
                send_email_id = request.POST.get('send_email_id')
                UserEmail.send_email_to_user(request, send_email_id, attendee[0])
            else:
                send_email_data = EmailContents.objects.filter(name='request-login-confirmation',template__event_id=event_id)
                if send_email_data.exists():
                    send_email_id = send_email_data[0].id
                    # queue = UserEmail.email_connection(request)
                    UserEmail.send_email_to_user(request, send_email_id, attendee[0])
            response_data['message'] = language['langkey']['request_login_notify_success']
            response_data['success'] = True
        else:
            response_data['message'] = language['langkey']['request_login_notify_request']
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")
