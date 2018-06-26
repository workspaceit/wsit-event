try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.db import transaction
from django.http import HttpResponse
import json
from app.models import Attendee, ActivityHistory, Questions, Answers, SeminarsUsers, Booking, RequestedBuddy, Session, Room, RoomAllotment, AttendeeTag, Tag
import string
import random
from .mail import MailHelper
from django.db.models import Q
from publicfront.views.attendee import AttendeeRegistration as AttRegistration
import os
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from publicfront.views.user_login import UserLogin
from datetime import datetime, timedelta
from django.core import serializers


class AttendeeRegistration(TemplateView):

    def get(self, request):
        return render(request, 'gt/attendee/registration.html', {})

    @transaction.atomic
    def post(self,request):
        response_data = {}
        form_data = {
            "firstname": request.POST.get('fname'),
            "lastname": request.POST.get('lname'),
            "email": request.POST.get('email'),
            "phonenumber": request.POST.get('phone'),
            "group_id": 83
        }
        event_id = request.POST.get('event_id')
        answers = json.loads(request.POST.get('answers'))
        if not (Attendee.objects.filter(email=form_data['email'], event_id=event_id).exists()):
            form_data["type"] = "user"
            flag = True
            while (flag):
                secret_key = ''.join(
                    random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(40))
                checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
                if checkUniquity < 1:
                    flag = False
            form_data["secret_key"] = secret_key
            password_character = '!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            password = ''.join(
                    random.choice(password_character) for _ in range(6))
            form_data["password"] = make_password(password)
            attendee = Attendee(**form_data)
            try:
                with transaction.atomic():
                    attendee.save()
                    activity = ActivityHistory(attendee_id=attendee.id,activity_type="register",category="event",event_id=event_id)
                    activity.save()
                    for answer in answers:
                        if answer['id'] != 'buddy' and answer['answer'] != '' and answer['answer'] != False:
                            if Questions.objects.filter(id=answer['id']).exists():
                                AttRegistration.saveAnswers(attendee.id, answer)
            except Exception as e:
                response_data = {
                    'error': e
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            AttendeeRegistration.send_email(request, attendee,'gt/email_template/confirmation_email.html')
            response_data['success'] = 'Successfully registered'
            response_data['key'] = secret_key
            login_user = AutoLoginView.auto_login_user(request,secret_key)
            if login_user:
                request.session['event_user'] = login_user
                request.session['is_user_login'] = True
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['error'] = 'Email already exists'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def optional_registration(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            return render(request, 'gt/attendee/middagar_registration.html', {})
        else:
            return redirect('gt-welcome')

    def optional_registration_read(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            return render(request, 'gt/attendee/middagar_registration_read.html', {})
        else:
            return redirect('gt-welcome')

    def saveAnswers(userId, answer):
        if answer['answer'] == True:
            answer['answer'] = 'Yes'
        elif answer['answer'] == False:
            answer['answer'] == 'No'
        answerExist = Answers.objects.filter(question_id=answer['id'], user_id=userId)
        if answerExist.exists():
            if answer['value'] == '':
                answerExist.delete()
            else:
                Answers.objects.filter(question_id=answer['id'], user_id=userId).update(value=answer['answer'])
                attendeeAnswer = Answers.objects.filter(question_id=answer['id'], user_id=userId)
                return attendeeAnswer[0]
        else:
            attendeeAnswer = Answers(value=answer['answer'], question_id=answer['id'], user_id=userId)
            attendeeAnswer.save()
            return attendeeAnswer


    def send_email(request,attendee_obj,file_path):
        print('ok')
        attendee = attendee_obj.id
        att_email= attendee_obj.email
        answerList= Answers.objects.filter(user_id=attendee)
        sessionList= SeminarsUsers.objects.filter(attendee_id=attendee, session__group_id=88)
        bookings = Booking.objects.filter(attendee_id=attendee)
        for booking in bookings:
            buddy_list = []
            # booking.buddy_list = booking.buddies.all()
            requested_buddies = RequestedBuddy.objects.filter(booking_id=booking.id)
            bookings_buddies = {}
            bookings_buddies['booking'] = booking.as_dict()

            for requested_buddy in requested_buddies:
                if requested_buddy.buddy_id:
                    buddy_list.append(requested_buddy.buddy.firstname+" " +requested_buddy.buddy.lastname)
                else:
                    buddy_list.append(requested_buddy.email)
            booking.buddy_list = buddy_list
        print(sessionList.count())
        base_url = 'http://127.0.0.1:8000/'
        context = {
            'answerlist' : answerList,
            'sessions' : sessionList,
            # 'buddies' : buddy_list,
            'base_url': base_url,
            'secret_key': attendee_obj.secret_key,
            # 'group_id': attendee_obj.group_id,
            'group_id': 83,
            'bookings': bookings,
            'att_email': att_email
        }
        print(context)
        subject = "Bekräftelse - Kunskapsveckan och GetTogether"
        sender_mail = "registration@eventdobby.com"
        # if attendee_obj.group.event_id == 11:
        #     subject = "KINGFOMARKET-REGISTRATION"
        #     sender_mail = "kingfomarket@eventdobby.com"

        to = att_email
        MailHelper.mail_send(file_path,context,subject,to,sender_mail)
        return "ok"

    def get_attendees_alt(request):
        response_data = {}
        val = request.POST.get('q')
        if len(val) > 2:
            b_list = []
            my_data = []
            if val != '':
                buddies = RequestedBuddy.objects.filter(exists=False, email=val, booking__attendee__group__event_id=10)
                for buddy in buddies:
                    b_list.append(buddy.booking.attendee.id)
                matched_at = Attendee.objects.values('email', 'id').filter(Q(id__in=b_list))
                if matched_at.count() > 0:
                    print(matched_at.count())
                    for m in matched_at:
                        arr_data_mat = {
                            'id': m['id'],
                            'text': m['email'] + ' (has selected you as preferred room buddy)'
                        }
                        my_data.append(arr_data_mat)
            attendees = Attendee.objects.values('email','id').filter((Q(email__icontains=val, event_id=10)) & (~Q(id__in=b_list)))
            for attendee in attendees:
                arr_data = {
                    'id': attendee['id'],
                    'text': attendee['email']
                }
                my_data.append(arr_data)
        else:
            my_data = []
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    @staticmethod
    def get_participation(request):
        attendee_id = Attendee.objects.get(id=request.session['event_user']['id'])
        answers = []
        sessions = []
        bookings = []
        question_ids = [141, 149, 140, 142, 144, 147, 148]
        session_ids = [145, 146, 147, 148, 149]
        room_ids = [6, 7]
        attendee_answers = Answers.objects.filter(user_id=attendee_id, question_id__in=question_ids)
        attendee_sessions = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id__in=session_ids)
        attendee_bookings = Booking.objects.filter(attendee_id=attendee_id, room_id__in=room_ids)
        for answer in attendee_answers:
            answers.append(answer.as_dict())
        for session in attendee_sessions:
            sessions.append(session.as_dict())
        for booking in attendee_bookings:
            buddies = booking.buddies.all()
            buddy_list = []
            for buddy in buddies:
                buddy_list.append(buddy.as_dict())
            bookings.append({
                'booking': booking.as_dict(),
                'buddies': buddy_list
            })
        response_data = {
            'answers': answers,
            'sessions': sessions,
            'bookings': bookings
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    @transaction.atomic
    def add_participation(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            response_data = {}
            try:
                with transaction.atomic():
                    attendee = Attendee.objects.get(id=request.session['event_user']['id'])
                    if attendee:
                        answers = json.loads(request.POST.get('answers'))
                        attendee_session = json.loads(request.POST.get('sessions'))
                        booking = json.loads(request.POST.get('rooms'))
                        for answer in answers:
                            if answer['id'] != 'buddy' and answer['answer'] != False:
                                if Questions.objects.filter(id=answer['id']).exists():
                                    AttRegistration.saveAnswers(attendee.id, answer)

                        if 'deleted_sessions' in request.POST:
                            deletedSession = json.loads(request.POST.get('deleted_sessions'))
                            for del_session in deletedSession:
                                SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=del_session).delete()
                        if 'deleted_questions' in request.POST:
                            deleted_answers = json.loads(request.POST.get('deleted_questions'))
                            for del_answer in deleted_answers:
                                Answers.objects.filter(user_id=attendee.id, question_id=del_answer).delete()
                        if 'deleted_bookings' in request.POST:
                            deleted_bookings = json.loads(request.POST.get('deleted_bookings'))
                            for del_booking in deleted_bookings:
                                Booking.objects.filter(id=del_booking).delete()

                        for session in attendee_session:
                            session_exist = SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=session)
                            if session_exist.exists():
                                print('ok')
                            else:
                                sessionAttendees = Session.objects.values('max_attendees').get(id=session)
                                bookedFlights = SeminarsUsers.objects.filter(session_id=session).exclude(status='not-attending').count()
                                # bookedFlights = SeminarsUsers.objects.filter(session_id=session, status='attending').count()
                                if sessionAttendees['max_attendees'] > bookedFlights:
                                    attendeeSessions = SeminarsUsers(attendee_id=attendee.id, session_id=session)
                                    attendeeSessions.save()
                                else:
                                    if not session.receive_answer and session.allow_attendees_queue:
                                        seminar_data = {
                                            "attendee_id": attendee.id,
                                            "session_id": session,
                                            "status": "in-queue"
                                        }
                                        all_queue = SeminarsUsers.objects.filter(session_id=session, status='in-queue').order_by('queue_order')
                                        if all_queue.exists():
                                            seminar_data['queue_order'] = all_queue[all_queue.count()-1].queue_order + 1
                                        attendeeSessions = SeminarsUsers(**seminar_data)
                                        attendeeSessions.save()
                                    # error_message = 'Your selected sessions capacity is full'
                                    # raise Exception('')
                                        # adding hotel rooms and requested buddies for attendee
                        for attendee_booking in booking:
                            room_id = attendee_booking['room_id']
                            room_available = AttRegistration.check_available_room(attendee_booking, room_id)
                            if not room_available:
                                error_message = 'Room is not available'
                                raise Exception(error_message)
                            if 'booking_id' in attendee_booking:
                                booking_exist = Booking.objects.filter(id=attendee_booking['booking_id'])
                                booking_id = attendee_booking['booking_id']
                                if booking_exist.exists():
                                    Booking.objects.filter(id=attendee_booking['booking_id']).update(check_in=attendee_booking['check_in'], check_out=attendee_booking['check_out'])
                                    booking_id = booking_exist[0].id
                            else:
                                booking = Booking(attendee_id=attendee.id, room_id=room_id, check_in=attendee_booking['check_in'], check_out=attendee_booking['check_out'])
                                booking.save()
                                booking_id = booking.id
                            buddies = attendee_booking['buddy']
                            if len(buddies) == 0:
                                RequestedBuddy.objects.filter(booking_id=booking_id).delete()
                            for buddy in buddies:
                                buddy_exist = RequestedBuddy.objects.filter(booking_id=booking_id)
                                get_buddy = Attendee.objects.filter(email=buddy, event_id=attendee.event_id)
                                # if buddy.isdigit():
                                if get_buddy.exists():
                                    print(get_buddy[0].id)
                                    if buddy_exist.exists():
                                        RequestedBuddy.objects.filter(booking_id=booking_id).update(buddy_id=get_buddy[0].id, email=None, exists=True)
                                    else:
                                        requested_buddy = RequestedBuddy(booking_id=booking_id, buddy_id=get_buddy[0].id, exists=True, email=None)
                                        requested_buddy.save()
                                    email_attendee = get_buddy[0]
                                    context = {
                                        'message': attendee.firstname +" "+ attendee.lastname +" has chosen you as room buddy, if you have not already, please go register at: <a href='http://www.eventdobby.com/gt'>Eventdobby.com</a>"
                                    }
                                    # subject = "MESSAGE - KINGFOMARKET"
                                    to = email_attendee.email
                                    # MailHelper.mail_send('public/email_template/email_message.html', context, "Room Buddy Request", to)
                                else:
                                    print(buddy)
                                    if buddy_exist.exists():
                                        RequestedBuddy.objects.filter(booking_id=booking_id).update(email=buddy, buddy_id= None, exists=False)
                                    else:
                                        requested_buddy = RequestedBuddy(booking_id=booking_id, exists=False, email=buddy)
                                        requested_buddy.save()
                                    context = {
                                        'message': attendee.firstname +" "+ attendee.lastname +" has chosen you as room buddy, if you have not already, please go register at: <a href='http://www.eventdobby.com/gt'>Eventdobby.com</a>"
                                    }
                                    # subject = "MESSAGE - KINGFOMARKET"
                                    to = buddy
                                    # MailHelper.mail_send('public/email_template/email_message.html', context, "Room Buddy Request", to)
                        response_data['success'] = 'Participation Update Successfully'
                        AttendeeRegistration.send_email(request, attendee,'gt/email_template/confirmation_medverkan.html')
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                    else:
                        return redirect('gt-welcome')
            except Exception as e:
                import os,sys
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                response_data = {
                    'error': str(e)
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return redirect('gt-welcome')



class SenRegistration(TemplateView):
    def get(self, request):
        return render(request, 'gt/attendee/sen_registration.html', {})

    def post(self,request):
        response_data = {}
        form_data = {
            "firstname": request.POST.get('fname'),
            "lastname": request.POST.get('lname'),
            "email": request.POST.get('email'),
            "phonenumber": request.POST.get('phone'),
            "event_id": request.session['event_id']
        }
        event_id = request.POST.get('event_id')
        answers = json.loads(request.POST.get('answers'))
        if not (Attendee.objects.filter(email=form_data['email'], event_id=event_id).exists()):
            form_data["type"] = "user"
            flag = True
            while (flag):
                secret_key = ''.join(
                    random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))
                checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
                if checkUniquity < 1:
                    flag = False
            form_data["secret_key"] = secret_key
            password = ''.join(
                    random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(8))
            form_data["password"] = make_password(password)
            attendee = Attendee(**form_data)
            try:
                with transaction.atomic():
                    attendee.save()
                    activity = ActivityHistory(attendee_id=attendee.id,activity_type="register",category="event",event_id=event_id)
                    activity.save()
                    for answer in answers:
                        if answer['id'] != 'buddy' and answer['answer'] != False:
                            if Questions.objects.filter(id=answer['id']).exists():
                                AttRegistration.saveAnswers(attendee.id, answer)
                    answers = json.loads(request.POST.get('answers'))
                    attendee_session = json.loads(request.POST.get('sessions'))
                    booking = json.loads(request.POST.get('rooms'))

                    tag = Tag.objects.filter(name='Sen anmälan')
                    if tag.exists():
                        attendee_tag = AttendeeTag(attendee_id=attendee.id, tag_id=tag[0].id)
                        attendee_tag.save()
                    else:
                        new_tag = Tag(name='Sen anmälan')
                        new_tag.save()
                        attendee_tag = AttendeeTag(attendee_id=attendee.id, tag_id=new_tag.id)
                        attendee_tag.save()

                    for session in attendee_session:
                        session_exist = SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=session)
                        if session_exist.exists():
                            print('ok')
                        else:
                            sessionAttendees = Session.objects.values('max_attendees').get(id=session)
                            bookedFlights = SeminarsUsers.objects.filter(session_id=session).exclude(status='not-attending').count()
                            if sessionAttendees['max_attendees'] > bookedFlights:
                                attendeeSessions = SeminarsUsers(attendee_id=attendee.id, session_id=session)
                                attendeeSessions.save()
                            else:
                                if not session.receive_answer and session.allow_attendees_queue:
                                    seminar_data = {
                                        "attendee_id": attendee.id,
                                        "session_id": session,
                                        "status": "in-queue"
                                    }
                                    all_queue = SeminarsUsers.objects.filter(session_id=session, status='in-queue').order_by('queue_order')
                                    if all_queue.exists():
                                        seminar_data['queue_order'] = all_queue[all_queue.count()-1].queue_order + 1
                                    attendeeSessions = SeminarsUsers(**seminar_data)
                                    attendeeSessions.save()
                    for attendee_booking in booking:
                        room_id = attendee_booking['room_id']
                        room_available = AttRegistration.check_available_room(attendee_booking, room_id)
                        if not room_available:
                            error_message = 'Room is not available'
                            raise Exception(error_message)
                        if 'booking_id' in attendee_booking:
                            booking_exist = Booking.objects.filter(id=attendee_booking['booking_id'])
                            booking_id = attendee_booking['booking_id']
                            if booking_exist.exists():
                                Booking.objects.filter(id=attendee_booking['booking_id']).update(check_in=attendee_booking['check_in'], check_out=attendee_booking['check_out'])
                                booking_id = booking_exist[0].id
                        else:
                            booking = Booking(attendee_id=attendee.id, room_id=room_id, check_in=attendee_booking['check_in'], check_out=attendee_booking['check_out'])
                            booking.save()
                            booking_id = booking.id
                        buddies = attendee_booking['buddy']
                        if len(buddies) == 0:
                            RequestedBuddy.objects.filter(booking_id=booking_id).delete()
                        for buddy in buddies:
                            buddy_exist = RequestedBuddy.objects.filter(booking_id=booking_id)
                            get_buddy = Attendee.objects.filter(email=buddy, event_id=attendee.event_id)
                            # if buddy.isdigit():
                            if get_buddy.exists():
                                print(get_buddy[0].id)
                                if buddy_exist.exists():
                                    RequestedBuddy.objects.filter(booking_id=booking_id).update(buddy_id=get_buddy[0].id, email=None, exists=True)
                                else:
                                    requested_buddy = RequestedBuddy(booking_id=booking_id, buddy_id=get_buddy[0].id, exists=True, email=None)
                                    requested_buddy.save()
                                email_attendee = get_buddy[0]
                                context = {
                                    'message': attendee.firstname +" "+ attendee.lastname +" has chosen you as room buddy, if you have not already, please go register at: <a href='http://www.eventdobby.com/gt'>Eventdobby.com</a>"
                                }
                                # subject = "MESSAGE - KINGFOMARKET"
                                to = email_attendee.email
                                # MailHelper.mail_send('public/email_template/email_message.html', context, "Room Buddy Request", to)
                            else:
                                print(buddy)
                                if buddy_exist.exists():
                                    RequestedBuddy.objects.filter(booking_id=booking_id).update(email=buddy, buddy_id= None, exists=False)
                                else:
                                    requested_buddy = RequestedBuddy(booking_id=booking_id, exists=False, email=buddy)
                                    requested_buddy.save()
                                context = {
                                    'message': attendee.firstname +" "+ attendee.lastname +" has chosen you as room buddy, if you have not already, please go register at: <a href='http://www.eventdobby.com/gt'>Eventdobby.com</a>"
                                }
                                # subject = "MESSAGE - KINGFOMARKET"
                                to = buddy
                                # MailHelper.mail_send('public/email_template/email_message.html', context, "Room Buddy Request", to)

            except Exception as e:
                import os,sys
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                response_data = {
                    'error': str(e)
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            AttendeeRegistration.send_email(request, attendee,'gt/email_template/confirmation_medverkan.html')
            AttendeeRegistration.send_email(request, attendee,'gt/email_template/confirmation_sen_anmalan.html')
            response_data['success'] = 'Successfully registered'
            response_data['key'] = secret_key
            login_user = AutoLoginView.auto_login_user(request,secret_key)
            if login_user:
                request.session['event_user'] = login_user
                request.session['is_user_login'] = True
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['error'] = 'Email already exists'
            return HttpResponse(json.dumps(response_data), content_type="application/json")


class AutoLoginView(TemplateView):

    def auto_login_user(request,user_key):
        from publicfront.gt_views.login import UserLogin
        login_user = UserLogin.loginUser(request,user_key)
        return login_user



class login(TemplateView):

    def get(self, request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            return redirect('gt-welcome')
        else:
            return render( request, "gt/attendee/login.html", {})

    def post(self, request):
        response_data = {}
        form_data = {
            "email": request.POST.get('email'),
            "password": request.POST.get('password')
        }

        try:
            att = Attendee.objects.get(email=form_data["email"], event_id=request.session['event_id'])
            print (att.password + "     " + make_password(form_data["password"]) + "    " + form_data['password'])
            if check_password(form_data["password"], att.password):
                response_data['key'] = att.secret_key
                login_user = UserLogin.loginUser(request, att.secret_key)
                if login_user != 'Login Failed':
                    request.session['event_user'] = login_user
                    request.session['event_id'] = login_user['event_id']
                    request.session['is_user_login'] = True
                    response_data['success'] = "Login successfully"
                else:
                    response_data['error'] = "Wrong Information"
            else:
                response_data['error'] = "Wrong Information"
        except ObjectDoesNotExist:
            response_data['error'] = 'Wrong Information'

        response_data['success'] = 'Attendee Login Successfully'

        return HttpResponse(json.dumps(response_data), content_type="application/json")