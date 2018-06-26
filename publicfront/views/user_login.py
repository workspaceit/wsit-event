from django.shortcuts import redirect
from django.views import generic
from app.models import Attendee, Answers


class UserLogin(generic.View):
    def loginUser(request, user_key, *args, **kwargs):
        user = Attendee.objects.filter(secret_key__contains=user_key)
        if user.exists():
            attendee_session = UserLogin.add_attendee_to_session(request, user[0])
        else:
            return "Login Failed"

    def add_attendee_to_session(request, attendee):
        if 'event_user' in request.session:
            del request.session['event_user']
        if 'is_user_login' in request.session:
            del request.session['is_user_login']
        first_name = Answers.objects.filter(question__actual_definition='firstname', user_id=attendee.id)
        last_name = Answers.objects.filter(question__actual_definition='lastname', user_id=attendee.id)
        attending = 'Yes'
        if first_name.exists():
            fname = first_name[0].value
        else:
            fname = attendee.firstname
        if last_name.exists():
            lname = last_name[0].value
        else:
            lname = attendee.lastname
        auth_user = {
            "id": attendee.id,
            "name": fname + ' ' + lname,
            "email": attendee.email,
            "type": attendee.type,
            "attending": attending,
            "avatar": attendee.avatar,
            "secret_key": attendee.secret_key,
            "event_id": attendee.event_id
        }
        return auth_user


class LogoutView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        # request.session.flush()
        if 'event_user' in request.session:
            del request.session['event_user']
        if 'is_user_login' in request.session:
            del request.session['is_user_login']
        return redirect('welcome', event_url=request.session['event_url'])
