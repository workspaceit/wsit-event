from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.generic import TemplateView
from app.models import Attendee, Answers
from publicfront.gt_views.attendee import AttendeeRegistration as AttRegistration
from django.http import HttpResponse
import json

class UserLogin(TemplateView):

    def get(self, request):
        if 'uid' in request.GET:
            print(request.GET.get('uid'))
            user_key = request.GET.get('uid')
            login_user = UserLogin.loginUser(request,user_key)
            if login_user:
                request.session['event_user'] = login_user
                request.session['is_user_login'] = True
                return redirect('gt-welcome')
            else:
                return redirect('gt-welcome')

        else:
            return redirect('gt-welcome')


    def loginUser(request,user_key):
        user = Attendee.objects.filter(secret_key=user_key)
        if user.exists():
            request.session.flush()
            first_name = Answers.objects.filter(question__actual_definition='firstname', user_id=user[0].id)
            last_name = Answers.objects.filter(question__actual_definition='lastname', user_id=user[0].id)
            # attending = 'No'
            # if user[0].group.name != "Not Attending":
            attending = 'Yes'
            if first_name.exists():
                fname = first_name[0].value
            else:
                fname = user[0].firstname
            if last_name.exists():
                lname = last_name[0].value
            else:
                lname = user[0].lastname
            auth_user = {
                    "id": user[0].id,
                    "name": fname+' '+lname,
                    "email": user[0].email,
                    "type": user[0].type,
                    "attending": attending,
                    "avatar": user[0].avatar,
                    "secret_key": user[0].secret_key,
                    "event_id": user[0].event.id
                }
            return auth_user
        else:
            return False


class LoginView(generic.DetailView):
    def get(self, request):
        return render(request, 'gt/attendee/sign_in.html', {})
    def post(self,request):
        email = request.POST.get('email')
        attendee = Attendee.objects.filter(email=email, event_id=10)
        response_data = {}
        if attendee.exists():
            AttRegistration.send_email(request, attendee[0], 'gt/email_template/confirmation_email.html')
            response_data['success'] = "An Email sent to you with activation url"
        else:
            response_data['error'] = "Email not Exists"
        return HttpResponse(json.dumps(response_data), content_type="application/json")



class LogoutView(generic.DetailView):
    def get(self, request):
        request.session.flush()
        return redirect('gt-welcome')






