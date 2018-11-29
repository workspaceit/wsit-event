from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.views import generic
from app.models import Users, Attendee, Tag, Session, Room, SeminarsUsers, Questions, Booking, Answers, \
    RequestedBuddy, RoomAllotment, AttendeeTag, UsedRule, RuleSet, TravelAttendee, Travel, ActivityHistory, \
    CurrentFilter, Setting, MatchLine, Match, AttendeeGroups, EmailContents, \
    MessageHistory, Notification, \
    Elements, DeletedAttendee, DeletedHistory, MessageContents, PresetEvent, Presets, RegistrationGroupOwner, \
    RegistrationGroups, Orders, Payments, EmailReceivers, EmailReceiversHistory, MessageReceivers, \
    OrderItems, CreditOrders
import json
from datetime import datetime, timedelta
from django.http import Http404
from django.views.generic import TemplateView
from django.db.models import Sum

from app.views.email_content_view import EmailContentDetailView
from app.views.gbhelper.common_helper import CommonHelper
from app.views.gbhelper.pdf_generator import EconomyPDFGenerator
from app.views.language_view import LanguageView
from app.views.message_view import MessageView, MessageReceiversView
from app.views.room_view import RoomView
from .question_view import QuestionView
from .common_views import AnswerView, GroupView, CommonContext, TimeDetailView
from django.db.models import Q
from django.db import transaction
import string
import random
from django.contrib.auth.hashers import make_password
from django.db.models.functions import Concat
import logging
from .mail import MailHelper
from django.db.models import Value
from publicfront.views.profile import SessionDetail
from .general_view import General
from .email_view import EmailView
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.gbhelper.economy_library import EconomyLibrary
from .common_views import EventView

class AttendeeView(TemplateView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'attendee_permission'):
            session_groups = GroupView.get_sessionGroup(request)
            for group in session_groups:
                group.sessions = Session.objects.all().filter(group_id=group.id)
            travel_groups = GroupView.get_travelGroup(request)
            for group in travel_groups:
                group.travels = Travel.objects.all().filter(group_id=group.id)
            hotel_group = GroupView.get_hotelGroup(request)
            filter_group = GroupView.get_filterGroup(request)
            for group in hotel_group:
                group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
                for room in group.rooms:
                    room_allotments = RoomView.find_booking(str(room.id))
                    date_allotments = []
                    for allotments in room_allotments['details']:
                        if allotments['occupancy'] < 100:
                            date_allotments.append(str(allotments['available_date']))
                    if len(date_allotments) > 0:
                        new_date = datetime.strptime(date_allotments[-1], "%Y-%m-%d") + timedelta(days=1)
                        new_allotments = str(new_date).split(' ')[0]
                        date_allotments.append(new_allotments)
                    room.allotment = json.dumps(date_allotments)
            last_used_rules = UsedRule.objects.filter(user_id=request.session['event_auth_user']['id'])
            filter_groups = GroupView.get_filterGroup(request)
            for group in filter_groups:
                group.filters = RuleSet.objects.filter(group_id=group.id).exclude(name='quick-filter')
            search_key = ""
            if 'search_key' in request.GET:
                search_key = request.GET.get('search_key')
            last_filter = CurrentFilter.objects.filter(admin_id=request.session['event_auth_user']['id'], table_type='attendee',
                                                       event_id=request.session['event_auth_user']['event_id'])
            visible_columns = ''
            last_active_filter = ''
            show_entries = 10
            sorted_column = 1
            sorting_order = 'asc'
            if last_filter.count() > 0:
                if last_filter[0].show_rows is not None:
                    show_entries = last_filter[0].show_rows
                if last_filter[0].visible_columns is not None:
                    visible_columns = last_filter[0].visible_columns
                if last_filter[0].filter is not None:
                    last_active_filter = last_filter[0].filter.id
                if last_filter[0].sorting_order is not None:
                    sorting_order = last_filter[0].sorting_order
                if last_filter[0].sorted_column is not None:
                    sorted_column = last_filter[0].sorted_column
                    if visible_columns != '':
                        vis_cols_list = json.loads(visible_columns)
                        if sorted_column not in vis_cols_list:
                            sorted_column = 1

            common_context = CommonContext.get_all_common_context(request)
            common_context['hotel_groups'] = hotel_group

            event_id = request.session['event_auth_user']['event_id']
            quick_filter = RuleSet.objects.filter(name='quick-filter',
                                                  created_by_id=request.session['event_auth_user']['id'],
                                                  group__event_id=event_id)
            quick_filter_id = ''
            if quick_filter.exists():
                quick_filter_id = quick_filter[0].id
            email_lists = EmailContents.objects.filter(template__event_id=event_id, is_show=1).values('id', 'name')
            msg_lists = MessageContents.objects.filter(event_id=event_id, is_show=1).values('id', 'name')
            context = {
                'last_used_rules': last_used_rules,
                'filter_group': filter_group,
                'search_key': search_key,
                'rule_groups': filter_groups,
                'visible_columns': visible_columns,
                'last_active_filter': last_active_filter,
                'show_entries': show_entries,
                'sorting_order': sorting_order,
                'sorted_column': sorted_column,
                'quick_filter_id': quick_filter_id,
                'attendee_view_email_lists': email_lists,
                'attendee_view_msg_lists': msg_lists
            }
            context.update(common_context)
            filter_context = CommonContext.get_filter_context(request)
            context.update(filter_context)
            return render(request, 'attendee/attendee.html', context)

    def post(self, request):
        if EventView.check_permissions(request, 'attendee_permission'):
            try:
                with transaction.atomic():
                    response_data = {}
                    event_id = request.session['event_auth_user']['event_id']
                    admin_id = request.session['event_auth_user']['id']
                    form_data = {
                        "firstname": request.POST.get('fname'),
                        "lastname": request.POST.get('lname'),
                        "email": request.POST.get('email'),
                        "phonenumber": request.POST.get('phonenumber'),
                        "event_id": request.session['event_auth_user']['event_id']
                    }
                    if form_data["firstname"] == "" or form_data["firstname"] == "Empty":
                        form_data["firstname"] = ''
                    if form_data["lastname"] == "" or form_data["lastname"] == "Empty":
                        form_data["lastname"] = ''
                    if form_data["email"] == "" or form_data["email"] == "Empty":
                        form_data["email"] = ''
                    if form_data["phonenumber"] == "" or form_data["phonenumber"] == "Empty":
                        form_data["phonenumber"] = ''
                    answers = json.loads(request.POST.get('answers'))
                    attendee_session = json.loads(request.POST.get('attendee_session'))
                    attendee_travel = json.loads(request.POST.get('attendee_travel'))
                    attendee_tags = json.loads(request.POST.get('attendee_tags'))
                    attendee_groups = json.loads(request.POST.get('attendee_groups'))
                    event_id = request.session['event_auth_user']['event_id']

                    if 'id' in request.POST:
                        if "password" in request.POST:
                            form_data["password"] = request.POST.get('password')
                            if form_data["password"] != '' and form_data["password"] != None and form_data[
                                "password"] != 'changed password':
                                form_data["password"] = make_password(form_data["password"])
                        user_id = request.POST.get('id')
                        push_notification_status = request.POST.get('push_notification_status')
                        form_data['push_notification_status'] = False
                        if push_notification_status == "True":
                            form_data['push_notification_status'] = True
                        run = True
                        email_multiple_exist = Attendee.objects.filter(email=form_data['email'], event_id=event_id).exclude(id=user_id).exists()
                        if email_multiple_exist:
                            allow_same_email_multiple_registration = CommonHelper.get_allow_same_email_multiple_registration(event_id)
                            if not allow_same_email_multiple_registration:
                                run = False

                        if run:
                            form_data["updated"] = datetime.now()
                            Attendee.objects.filter(id=user_id).update(**form_data)
                            deleted_groups = AttendeeGroups.objects.filter(attendee_id=user_id).exclude(group_id__in=attendee_groups).delete()
                            new_attendee_groups = []
                            for group in attendee_groups:
                                if not (AttendeeGroups.objects.filter(attendee_id=user_id, group_id=group).exists()):
                                    attendee_group = AttendeeGroups(attendee_id=user_id, group_id=group)
                                    new_attendee_groups.append(attendee_group)
                            AttendeeGroups.objects.bulk_create(new_attendee_groups)

                            tag_exist = []
                            new_attendee_tags = []
                            for tag in attendee_tags:
                                if tag.isdigit():
                                    tag_exist.append(tag)
                                    if not (AttendeeTag.objects.filter(attendee_id=user_id, tag_id=tag).exists()):
                                        attendee_tag = AttendeeTag(attendee_id=user_id, tag_id=tag)
                                        new_attendee_tags.append(attendee_tag)
                                else:
                                    new_tag = Tag(name=tag, event_id=event_id)
                                    new_tag.save()
                                    attendee_tag = AttendeeTag(attendee_id=user_id, tag_id=new_tag.id)
                                    new_attendee_tags.append(attendee_tag)
                                    tag_exist.append(new_tag.id)
                            AttendeeTag.objects.bulk_create(new_attendee_tags)
                            deleted_tag = AttendeeTag.objects.filter(attendee_id=user_id).exclude(
                                tag_id__in=tag_exist).delete()
                            new_questions_answer = []
                            questions_activity = []
                            answers_deleted = []
                            for answer in answers:
                                save_answers = AnswerView.saveAnswers(request, user_id, answer)
                                if 'deleted_questions' in save_answers:
                                    answers_deleted.append(save_answers['deleted_questions'])
                                if 'new_questions_answer' in save_answers:
                                    new_questions_answer.append(save_answers['new_questions_answer'])
                                if 'questions_activity' in save_answers:
                                    questions_activity.append(save_answers['questions_activity'])
                            Answers.objects.bulk_create(new_questions_answer)
                            ActivityHistory.objects.bulk_create(questions_activity)
                            Answers.objects.filter(id__in=answers_deleted).delete()
                            for session in attendee_session:

                                x_session = SeminarsUsers.objects.filter(attendee_id=user_id,
                                                                         session_id=session['id']).last()
                                if not x_session:

                                    test_session = General.testSession(user_id, session['id'])
                                    if test_session['valid']:
                                        attendeeSessions = SeminarsUsers(attendee_id=user_id, session_id=session['id'])
                                        attendeeSessions.save()
                                        activity_history = ActivityHistory(attendee_id=user_id,
                                                                           admin_id=request.session['event_auth_user'][
                                                                               'id'],
                                                                           activity_type='update', category='session',
                                                                           session_id=session['id'],
                                                                           old_value='Not Answered',
                                                                           new_value='Attending',
                                                                           event_id=request.session['event_auth_user'][
                                                                               'event_id'])
                                        activity_history.save()
                                        element = Elements.objects.filter(slug="messages")
                                        language = EmailContentDetailView.get_lang_key(request, element[0].id)
                                        msg = language['langkey']['messages_notify_session_attend'].replace('{session}',"{session_id:"+str(attendeeSessions.session.id)+"}")
                                        notify = Notification(type="session_attend", message=msg, status=0,
                                                              to_attendee_id=user_id)
                                        notify.save()

                                        # # create a order
                                        event_id = request.session['event_auth_user']['event_id']
                                        admin_id=request.session['event_auth_user']['id']
                                        EconomyLibrary.place_order(event_id,user_id,'session',session['id'],admin_id)
                                    else:
                                        if "is_queue" in test_session:
                                            attendeeSessions = SeminarsUsers(attendee_id=user_id, session_id=session['id'],
                                                                             status='in-queue')
                                            attendeeSessions.save()
                                            activity_history = ActivityHistory(attendee_id=user_id,
                                                                               admin_id=request.session['event_auth_user'][
                                                                                   'id'],
                                                                               activity_type='update', category='session',
                                                                               session_id=session['id'],
                                                                               old_value='Not Answered',
                                                                               new_value='In Queue',
                                                                               event_id=request.session['event_auth_user'][
                                                                                   'event_id'])
                                            activity_history.save()
                                            response_data[
                                                'warning'] = 'The session you tried to add is full and therefor has been added to In Queue Attendee'

                                        else:
                                            response_data['warning'] = test_session['reason']
                                else:
                                    test_session = General.testSession(user_id, session['id'])
                                    if test_session['valid']:
                                        x_session.status = "attending"
                                        x_session.save()
                                        element = Elements.objects.filter(slug="messages")
                                        language = EmailContentDetailView.get_lang_key(request, element[0].id)
                                        msg = language['langkey']['messages_notify_session_attend'].replace('{session}',"{session_id:"+str(x_session.session.id)+"}")
                                        notify = Notification(type="session_attend", message=msg, status=0,
                                                              to_attendee_id=user_id)
                                        notify.save()
                                        activity_history = ActivityHistory(attendee_id=user_id,
                                                                           admin_id=request.session['event_auth_user'][
                                                                               'id'],
                                                                           activity_type='update', category='session',
                                                                           session_id=session['id'],
                                                                           old_value='Not Attending',
                                                                           new_value='Attending',
                                                                           event_id=request.session['event_auth_user'][
                                                                               'event_id'])
                                        activity_history.save()
                                        EconomyLibrary.place_order(event_id, user_id, 'session', session['id'], admin_id)
                                    else:
                                        if "is_queue" in test_session:

                                            x_session.status = "in-queue"
                                            x_session.save()

                                            activity_history = ActivityHistory(attendee_id=user_id,
                                                                               admin_id=request.session['event_auth_user'][
                                                                                   'id'],
                                                                               activity_type='update', category='session',
                                                                               session_id=session['id'],
                                                                               old_value='Not Attending',
                                                                               new_value='In Queue',
                                                                               event_id=request.session['event_auth_user'][
                                                                                   'event_id'])
                                            activity_history.save()
                                            response_data[
                                                'warning'] = 'The session you tried to add is full and therefor has been added to In Queue Attendee'

                                        else:
                                            response_data[
                                                'warning'] = 'The attendee is already registered (or in queue) for the session you’re trying to add'

                            for travel in attendee_travel:
                                travelAttendees = Travel.objects.values('max_attendees').get(id=travel['id'])
                                bookedFlights = TravelAttendee.objects.filter(travel_id=travel['id'],
                                                                              status='attending').count()
                                if travelAttendees['max_attendees'] > bookedFlights:
                                    attendeeTravels = TravelAttendee(attendee_id=user_id, travel_id=travel['id'])
                                    attendeeTravels.save()
                                    activity_history = ActivityHistory(attendee_id=user_id,
                                                                       admin_id=request.session['event_auth_user']['id'],
                                                                       activity_type='update', category='travel',
                                                                       travel_id=travel['id'], old_value='Not Answered',
                                                                       new_value='Attending',
                                                                       event_id=request.session['event_auth_user'][
                                                                           'event_id'])
                                    activity_history.save()

                            # adding hotel rooms and requested buddies for attendee
                            attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
                            for attendee_booking in attendee_bookings:
                                available_allotments = []
                                allotments = RoomAllotment.objects.filter(room_id=attendee_booking['room_id'])
                                for allotment in allotments:
                                    available_allotments.append(str(allotment.available_date))
                                newCheckOut = datetime.strptime(attendee_booking['check_out'], "%Y-%m-%d") - timedelta(
                                    days=1)
                                newCheckOutDate = str(newCheckOut).split(' ')[0]
                                if attendee_booking['check_in'] in available_allotments and newCheckOutDate in available_allotments:
                                    if attendee_booking['exists'] == 1:
                                        try:
                                            with transaction.atomic():
                                                room_available = AttendeeView.check_available_room(user_id, attendee_booking)
                                                if not room_available:
                                                    response_data['error'] = 'Those Rooms are not available'
                                                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                                                booking_data = {
                                                    'attendee_id': user_id,
                                                    'room_id': attendee_booking['room_id'],
                                                    'check_in': attendee_booking['check_in'],
                                                    'check_out': attendee_booking['check_out']
                                                }
                                                r = RequestedBuddy.objects.filter(booking_id=attendee_booking['id']).delete()
                                                old_booking = Booking.objects.get(id=attendee_booking['id'])
                                                old_booking_data = {
                                                    'attendee_id': user_id,
                                                    'room_id': old_booking.room_id,
                                                    'check_in': old_booking.check_in,
                                                    'check_out': old_booking.check_out
                                                }
                                                sql = 'select m.* from match_line m where booking_id=' + str(attendee_booking[
                                                                                                                 "id"]) + ' and (select count(*) from `match_line` n where m.match_id=n.match_id)>1;'
                                                get_match = MatchLine.objects.raw(
                                                    sql
                                                )
                                                booking_matches = []
                                                if len(list(get_match)) > 0:
                                                    matches = MatchLine.objects.filter(match_id=get_match[0].match_id)
                                                    for match in matches:
                                                        booking_matches.append(match.booking_id)

                                                    Booking.objects.filter(id=attendee_booking['id']).update(**booking_data)
                                                    if int(old_booking_data['room_id']) != int(booking_data['room_id']):
                                                        AttendeeView.remove_hotel_order_item(event_id, user_id, old_booking_data['room_id'], attendee_booking['id'], admin_id, old_booking_data['check_in'], old_booking_data['check_out'])
                                                        AttendeeView.place_hotel_order(event_id, user_id, booking_data, attendee_booking['id'], admin_id)
                                                    else:
                                                        AttendeeView.update_hotel_order(event_id, user_id, booking_data, old_booking_data, attendee_booking['id'], admin_id)

                                                    common_dates = AttendeeView.get_booking_common_dates(booking_matches)
                                                    if str(old_booking.room_id) != str(attendee_booking['room_id']) or len(common_dates) == 0:
                                                        if 'status' in attendee_booking:
                                                            if attendee_booking['status'] == '2':
                                                                from app.views.hotel_view import HotelView
                                                                attendee_booking_available = HotelView.check_available_room(booking_data, 0)
                                                                if attendee_booking_available:
                                                                    matche_buddy = MatchLine.objects.filter(
                                                                        match_id=get_match[0].match_id).exclude(
                                                                        booking_id=attendee_booking['id'])
                                                                    buddy_count = 0
                                                                    buddy_availabe = True
                                                                    for buddy in matche_buddy:
                                                                        buddy_count = buddy_count + 1
                                                                        buddy_booking = {}
                                                                        buddy_booking['check_in'] = buddy.booking.check_in.strftime('%Y-%m-%d')
                                                                        buddy_booking['check_out'] = buddy.booking.check_out.strftime('%Y-%m-%d')
                                                                        buddy_booking['room_id'] = attendee_booking['room_id']
                                                                        buddy_booking_available = HotelView.check_available_room(buddy_booking, buddy_count)
                                                                        if not buddy_booking_available:
                                                                            buddy_availabe = False
                                                                            break
                                                                    if buddy_availabe:
                                                                        all_dates = []
                                                                        for my_date in common_dates:
                                                                            all_dates.append(str(my_date))
                                                                        end_date = max(common_dates) + timedelta(days=1)
                                                                        updated_match = Match.objects.filter(
                                                                            id=get_match[0].match_id).update(
                                                                            start_date=min(common_dates),
                                                                            end_date=end_date,
                                                                            all_dates=json.dumps(all_dates),
                                                                            room_id=attendee_booking['room_id'])
                                                                        for buddy in matche_buddy:
                                                                            Booking.objects.filter(id=buddy.booking_id).update(room_id=attendee_booking['room_id'])
                                                                            buddy_booking_data = {
                                                                                'room_id': attendee_booking['room_id'],
                                                                                'check_in': str(buddy.booking.check_in),
                                                                                'check_out': str(buddy.booking.check_out)
                                                                            }
                                                                            if int(old_booking_data['room_id']) != int(booking_data['room_id']):
                                                                                # there will be no update for buddy booking order, but order will place because when room is changed
                                                                                AttendeeView.remove_hotel_order_item(event_id, buddy.booking.attendee_id, old_booking_data['room_id'], buddy.booking_id, admin_id, buddy.booking.check_in, buddy.booking.check_out)
                                                                                AttendeeView.place_hotel_order(event_id, buddy.booking.attendee_id, buddy_booking_data, buddy.booking_id, admin_id)

                                                                        booking = Booking.objects.get(id=attendee_booking['id'])
                                                                    else:
                                                                        response_data['warning'] = 'Hotel Change are not possible'
                                                                        Booking.objects.filter(id=attendee_booking['id']).update(**old_booking_data)
                                                                        booking = Booking.objects.get(id=attendee_booking['id'])
                                                                        raise Exception('rollback hotel order changes')
                                                                else:
                                                                    response_data['warning'] = 'Hotel Change are not possible'
                                                                    Booking.objects.filter(id=attendee_booking['id']).update(**old_booking_data)
                                                                    booking = Booking.objects.get(id=attendee_booking['id'])
                                                                    raise Exception('rollback hotel order changes')
                                                            else:
                                                                temp_booking_id =attendee_booking['id']
                                                                bbb = Booking.objects.filter(id=attendee_booking['id']).first()
                                                                bbb_room_id = bbb.room_id
                                                                bbb_check_in = bbb.check_in
                                                                bbb_check_out = bbb.check_out
                                                                bbb.delete()
                                                                booking = Booking(**booking_data)
                                                                booking.save()
                                                                if int(bbb_room_id) != int(booking_data['room_id']):
                                                                    AttendeeView.remove_hotel_order_item(event_id, user_id, bbb_room_id, attendee_booking['id'], admin_id, bbb_check_in, bbb_check_out)
                                                                    AttendeeView.place_hotel_order(event_id, user_id, booking_data, booking.id, admin_id)
                                                                else:
                                                                    AttendeeView.update_hotel_order(event_id, user_id, booking_data, old_booking_data, attendee_booking['id'], admin_id, booking.id)

                                                                AttendeeView.add_booking_history(request, user_id, booking.room_id, 'register')
                                                        else:
                                                            bbb = Booking.objects.filter(id=attendee_booking['id']).first()
                                                            bbb_room_id = bbb.room_id
                                                            bbb_check_in = bbb.check_in
                                                            bbb_check_out = bbb.check_out
                                                            bbb.delete()
                                                            booking = Booking(**booking_data)
                                                            booking.save()
                                                            if int(bbb_room_id) != int(booking_data['room_id']):
                                                                AttendeeView.remove_hotel_order_item(event_id, user_id, bbb_room_id, attendee_booking['id'], admin_id, bbb_check_in, bbb_check_out)
                                                                AttendeeView.place_hotel_order(event_id, user_id, booking_data, booking.id, admin_id)
                                                            else:
                                                                AttendeeView.update_hotel_order(event_id, user_id, booking_data, old_booking_data, attendee_booking['id'], admin_id, booking.id)

                                                            AttendeeView.add_booking_history(request, user_id, booking.room_id, 'register')
                                                    elif len(common_dates) > 0:
                                                        all_dates = []
                                                        for my_date in common_dates:
                                                            all_dates.append(str(my_date))
                                                        end_date = max(common_dates) + timedelta(days=1)
                                                        updated_match = Match.objects.filter(id=get_match[0].match_id).update(
                                                            start_date=min(common_dates), end_date=end_date,
                                                            all_dates=json.dumps(all_dates))
                                                        booking = Booking.objects.get(id=attendee_booking['id'])
                                                    else:
                                                        booking_new = Booking.objects.filter(id=attendee_booking['id']).update(**booking_data)
                                                        booking = Booking.objects.get(id=attendee_booking['id'])
                                                else:
                                                    bbb = Booking.objects.get(id=attendee_booking['id'])
                                                    bbb_check_in = bbb.check_in
                                                    bbb_check_out = bbb.check_out
                                                    Booking.objects.filter(id=attendee_booking['id']).update(**booking_data)
                                                    booking = Booking.objects.get(id=attendee_booking['id'])
                                                    if int(booking_data['room_id']) != int(old_booking_data['room_id']):
                                                        AttendeeView.remove_hotel_order_item(event_id, user_id, old_booking_data['room_id'], attendee_booking['id'], admin_id, bbb_check_in, bbb_check_out)
                                                        AttendeeView.place_hotel_order(event_id, user_id, booking_data, attendee_booking['id'], admin_id)
                                                    else:
                                                        AttendeeView.update_hotel_order(event_id, user_id, booking_data, old_booking_data, attendee_booking['id'], admin_id)
                                                buddies = attendee_booking['room_buddies']
                                                if booking.room.beds > len(buddies):
                                                    for buddy in buddies:
                                                        if buddy.isdigit():
                                                            requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                                                            requested_buddy.save()
                                                        else:
                                                            requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False, email=buddy)
                                                            requested_buddy.save()

                                        except Exception as exce:
                                            ErrorR.efail(exce)
                                    else:
                                        room_available = AttendeeView.check_available_room(user_id, attendee_booking)
                                        if not room_available:
                                            response_data['error'] = 'Those Rooms are not available'
                                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                                        booking = Booking(attendee_id=user_id, room_id=attendee_booking['room_id'],
                                                          check_in=attendee_booking['check_in'],
                                                          check_out=attendee_booking['check_out'])
                                        booking.save()
                                        AttendeeView.add_booking_history(request,user_id,attendee_booking['room_id'],'register')
                                        buddies = attendee_booking['room_buddies']
                                        if booking.room.beds > len(buddies):
                                            for buddy in buddies:
                                                if buddy.isdigit():
                                                    requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                                                    requested_buddy.save()
                                                else:
                                                    requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False,
                                                                                     email=buddy)
                                                    requested_buddy.save()

                                        booking_day_count = (datetime.strptime(booking.check_out, '%Y-%m-%d') - datetime.strptime(booking.check_in, '%Y-%m-%d')).days
                                        result = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='hotel', item_id=attendee_booking['room_id'], booking_day_count=booking_day_count, admin_id=admin_id, booking_id=booking.id)
                                        if result == None:
                                            raise Exception('error in economy for hotel')
                                else:
                                    response_data['warning'] = 'The date you inserted for hotel booking are invalid'

                            response_data['success'] = 'Attendee Update Successfully'
                            send_mail = request.POST.get('send_mail')
                            updated_attendee = Attendee.objects.get(id=user_id)
                            updated_answers = []
                            all_answers = Answers.objects.filter(user_id=user_id)
                            check_for_distinct_question = []
                            answer_exists = []
                            for answer in all_answers:
                                if answer.question_id not in check_for_distinct_question:
                                    updated_answers.append(answer.as_dict())
                                    answer_exists.append(answer.question_id)
                                    check_for_distinct_question.append(answer.question_id)
                            all_questions = Questions.objects.filter(
                                group__event_id=request.session['event_auth_user']['event_id'])
                            for qs in all_questions:
                                if qs.id not in answer_exists:
                                    get_dict = dict(
                                        id='',
                                        user=updated_attendee.as_dict(),
                                        question=qs.as_dict(),
                                        value='N/A'
                                    )
                                    updated_answers.append(get_dict)
                            response_data['updated_answers'] = updated_answers
                            tags = AttendeeTag.objects.filter(attendee_id=user_id)
                            taglist = ""
                            for tag in tags:
                                taglist += tag.tag.name + ", "

                            if len(taglist) > 0:
                                taglist = taglist[:-2]

                            response_data['tag_list'] = taglist
                            groups = AttendeeGroups.objects.filter(attendee_id=user_id)
                            grouplist = ""
                            for group_item in groups:
                                grouplist += group_item.group.name + ", "

                            if len(grouplist) > 0:
                                grouplist = grouplist[:-2]

                            response_data['group_list'] = grouplist

                            att_orders = Orders.objects.filter(attendee_id=user_id).values('order_number', 'invoice_ref')
                            temp_order_invoice_ids = ', '.join(att_or['invoice_ref'] for att_or in list(filter(lambda a_o: a_o['invoice_ref'], att_orders)))
                            response_data['invoice_ids'] = temp_order_invoice_ids

                            att_payments = Payments.objects.filter(order_number__in=[a_o['order_number'] for a_o in att_orders]).values('transaction')
                            temp_order_paymnet_trans = ', '.join(att_pymnt['transaction'] for att_pymnt in list(filter(lambda a_p: a_p['transaction'], att_payments)))
                            response_data['transaction_ids'] = temp_order_paymnet_trans

                            if RegistrationGroupOwner.objects.filter(owner_id=user_id).exists():
                                group_info = EconomyLibrary.get_group_registration_info(user_id)
                                att_orders_temp = Orders.objects.filter(attendee_id__in=group_info['grp-atts']).values(
                                    'order_number')
                                att_order_numbers = []
                                att_orders = []
                                for att_o_items in att_orders_temp:
                                    if att_o_items['order_number'] not in att_order_numbers:
                                        att_order_numbers.append(att_o_items['order_number'])
                                        att_orders.append(att_o_items)

                                temp_order_data = ', '.join(
                                    str(att_order['order_number']) + ' (order owner)' for att_order in att_orders)
                                response_data['order_numbers'] = temp_order_data
                            else:
                                if Attendee.objects.get(id=user_id).registration_group:
                                    temp_order_numbers = ', '.join(str(att_order['order_number']) for att_order in att_orders)
                                else:
                                    temp_order_numbers = ', '.join(str(att_order['order_number']) + "(order owner)" for att_order in att_orders)
                                response_data['order_numbers'] = temp_order_numbers

                            # Send Mail to attendee
                            if send_mail == 'true':
                                logger = logging.getLogger(__name__)
                                email_settings = Setting.objects.filter(name='attendee_edit_confirmation',
                                                                        event_id=updated_attendee.event_id)
                                if email_settings.exists():
                                    email_content = EmailContents.objects.filter(id=int(email_settings[
                                                                                            0].value))  # there will be different email content depend on update attendee or registration
                                    if email_content.exists():
                                        email_content = email_content[0]
                                        logger.debug('-----------Send email-----------------------')
                                        logger.debug(request.session['event_auth_user']['event_id'])
                                        EmailView.add_or_update_email_receivers(updated_attendee, email_content.id, request.session['event_auth_user']['id'])
                                        message_history = MessageHistory(subject=email_content.subject, message='N/A',
                                                                         admin_id=request.session['event_auth_user']['id'],
                                                                         type='mail')
                                        message_history.save()
                                        activity_history = ActivityHistory(attendee_id=updated_attendee.id,
                                                                           admin_id=request.session['event_auth_user'][
                                                                               'id'],
                                                                           activity_type='message', category='message',
                                                                           message_id=message_history.id,
                                                                           event_id=request.session['event_auth_user'][
                                                                               'event_id'])
                                        activity_history.save()
                                        EmailView.send_email(request, updated_attendee, email_content)

                            send_custom = request.POST.get('send_custom')
                            send_custom_type = request.POST.get('send_custom_type')
                            send_custom_value = request.POST.get('send_custom_value')
                            if send_custom == 'true' and send_custom_type != '' and send_custom_value != '':
                                if send_custom_type == 'email':
                                    email_content = EmailContents.objects.filter(id=int(send_custom_value))
                                    if email_content.exists():
                                        receiver = EmailReceivers.objects.filter(attendee_id=updated_attendee.id, email_content_id=send_custom_value, is_show=1).first()
                                        if receiver:
                                            EmailReceivers.objects.filter(id=receiver.id).update(status='sent', last_received=datetime.now())
                                        else:
                                            receiver_form = {
                                                'firstname': updated_attendee.firstname,
                                                'lastname': updated_attendee.lastname,
                                                'email': updated_attendee.email,
                                                'status': 'sent',
                                                'added_by_id': request.session['event_auth_user']['id'],
                                                'email_content_id': send_custom_value,
                                                'attendee_id': updated_attendee.id,
                                                'is_show': 1,
                                            }
                                            receiver = EmailReceivers(**receiver_form)
                                            receiver.save()
                                        message_history = MessageHistory(subject=email_content[0].subject, message='N/A',
                                                                         admin_id=request.session['event_auth_user']['id'],
                                                                         type='mail')
                                        message_history.save()
                                        activity_history = ActivityHistory(attendee_id=updated_attendee.id,
                                                                           admin_id=request.session['event_auth_user']['id'],
                                                                           activity_type='message', category='message',
                                                                           message_id=message_history.id,
                                                                           event_id=request.session['event_auth_user']['event_id'])
                                        activity_history.save()
                                        receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
                                        receiver_history.save()
                                        EmailView.send_email(request, updated_attendee, email_content[0])
                                elif send_custom_type == 'message':
                                    token_count = updated_attendee.devicetoken_set.all().count()
                                    if updated_attendee.phonenumber or token_count > 0:
                                        message_content = MessageContents.objects.filter(id=int(send_custom_value))
                                        if message_content.exists():
                                            exist_receiver = MessageReceivers.objects.filter(attendee_id=updated_attendee.id, message_content_id=send_custom_value, is_show=1)
                                            if exist_receiver.exists():
                                                MessageReceivers.objects.filter(id=exist_receiver[0].id).update(status='sent', last_received=datetime.now())
                                                receiver = exist_receiver[0]
                                            else:
                                                receiver_form = {
                                                    'firstname': updated_attendee.firstname,
                                                    'lastname': updated_attendee.lastname,
                                                    'mobile_phone': updated_attendee.phonenumber,
                                                    'status': 'sent',
                                                    'added_by_id': request.session['event_auth_user']['id'],
                                                    'message_content_id': send_custom_value,
                                                    'attendee_id': updated_attendee.id,
                                                    'is_show': 1,
                                                }
                                                receiver = MessageReceivers(**receiver_form)
                                                receiver.save()
                                            MessageReceiversView.send_message_to_single_receiver(request, receiver, message_content[0])

                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            response_data['error'] = 'email already Exist'
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                    else:
                        attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
                        run = True
                        email_multiple_exist = Attendee.objects.filter(email=form_data['email'], event_id=event_id).exists()
                        if email_multiple_exist:
                            allow_same_email_multiple_registration = CommonHelper.get_allow_same_email_multiple_registration(event_id)
                            if not allow_same_email_multiple_registration:
                                run = False
                        if run:
                            current_language = LanguageView.get_current_preset(request)
                            form_data['language_id'] = current_language.preset_id
                            form_data["type"] = "user"
                            if "password" in request.POST:
                                form_data["password"] = request.POST.get('password')
                            else:
                                form_data["password"] = ""
                            form_data["password"] = make_password(form_data["password"])
                            flag = True

                            setting_uid_length = Setting.objects.filter(name='uid_length', event_id=event_id)
                            if setting_uid_length:
                                uid_length = int(setting_uid_length[0].value)
                            else:
                                uid_length = 16

                            while (flag):
                                secret_key = ''.join(
                                    random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
                                    range(uid_length))
                                checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
                                if checkUniquity < 1:
                                    flag = False

                            bid_flag = True
                            while (bid_flag):
                                badge_key = ''.join(
                                    random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _
                                    in
                                    range(uid_length))
                                checkUniquity = Attendee.objects.filter(bid__contains=badge_key).count()
                                if checkUniquity < 1:
                                    bid_flag = False
                            form_data["secret_key"] = secret_key
                            form_data["bid"] = badge_key
                            attendee = Attendee(**form_data)
                            attendee.save()
                            grouplist = ""
                            new_attendee_groups = []
                            for group in attendee_groups:
                                if not (AttendeeGroups.objects.filter(attendee_id=attendee.id, group_id=group).exists()):
                                    attendee_group = AttendeeGroups(attendee_id=attendee.id, group_id=group)
                                    new_attendee_groups.append(attendee_group)
                                    grouplist += attendee_group.group.name + ", "
                            AttendeeGroups.objects.bulk_create(new_attendee_groups)
                            tag_list = ""
                            new_attendee_tags = []
                            for tag in attendee_tags:
                                if tag.isdigit():
                                    attendee_tag = AttendeeTag(attendee_id=attendee.id, tag_id=tag)
                                    new_attendee_tags.append(attendee_tag)
                                    tag_list += attendee_tag.tag.name + ", "
                                else:
                                    new_tag = Tag(name=tag, event_id=event_id)
                                    new_tag.save()
                                    attendee_tag = AttendeeTag(attendee_id=attendee.id, tag_id=new_tag.id)
                                    new_attendee_tags.append(attendee_tag)
                                    tag_list += tag + ", "
                            AttendeeTag.objects.bulk_create(new_attendee_tags)
                            new_questions_answer = []
                            questions_activity = []
                            answers_deleted = []
                            for answer in answers:
                                save_answers = AnswerView.saveAnswers(request, attendee.id, answer)
                                if 'deleted_questions' in save_answers:
                                    answers_deleted.append(save_answers['deleted_questions'])
                                if 'new_questions_answer' in save_answers:
                                    new_questions_answer.append(save_answers['new_questions_answer'])
                                if 'questions_activity' in save_answers:
                                    questions_activity.append(save_answers['questions_activity'])
                            Answers.objects.bulk_create(new_questions_answer)
                            ActivityHistory.objects.bulk_create(questions_activity)
                            Answers.objects.filter(id__in=answers_deleted).delete()
                            # adding sessions for attendee
                            for session in attendee_session:
                                test_session = General.testSession(attendee.id, session['id'])
                                if test_session['valid']:
                                    attendeeSessions = SeminarsUsers(attendee_id=attendee.id, session_id=session['id'])
                                    attendeeSessions.save()
                                    activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                       admin_id=request.session['event_auth_user']['id'],
                                                                       activity_type='update', category='session',
                                                                       session_id=session['id'], old_value='Not Answered',
                                                                       new_value='Attending',
                                                                       event_id=request.session['event_auth_user'][
                                                                           'event_id'])
                                    activity_history.save()
                                    element = Elements.objects.filter(slug="messages")
                                    language = EmailContentDetailView.get_lang_key(request, element[0].id)
                                    msg = language['langkey']['messages_notify_session_attend'].replace('{session}',"{session_id:"+str(attendeeSessions.session.id)+"}")
                                    notify = Notification(type="session_attend", message=msg, status=0,
                                                          to_attendee_id=attendee.id)
                                    notify.save()
                                    result = EconomyLibrary.place_order(event_id, attendee.id, 'session', session['id'], admin_id)
                                    if result:
                                        response_data['order_number'] = result['order_number']

                                else:
                                    if "is_queue" in test_session:
                                        attendeeSessions = SeminarsUsers(attendee_id=attendee.id, session_id=session['id'],
                                                                         status='in-queue')
                                        attendeeSessions.save()
                                        activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                           admin_id=request.session['event_auth_user'][
                                                                               'id'],
                                                                           activity_type='update', category='session',
                                                                           session_id=session['id'],
                                                                           old_value='Not Answered',
                                                                           new_value='In Queue',
                                                                           event_id=request.session['event_auth_user'][
                                                                               'event_id'])
                                        response_data[
                                            'warning'] = 'The session you tried to add is full and therefor has been added to In Queue Attendee'

                                    else:
                                        response_data['warning'] = test_session['reason']

                            for travel in attendee_travel:
                                travelAttendees = Travel.objects.values('max_attendees').get(id=travel['id'])
                                bookedFlights = TravelAttendee.objects.filter(travel_id=travel['id'],
                                                                              status='attending').count()
                                if travelAttendees['max_attendees'] > bookedFlights:
                                    attendeeTravels = TravelAttendee(attendee_id=attendee.id, travel_id=travel['id'])
                                    attendeeTravels.save()
                                    activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                       admin_id=request.session['event_auth_user']['id'],
                                                                       activity_type='update', category='travel',
                                                                       travel_id=travel['id'], old_value='Not Answered',
                                                                       new_value='Attending',
                                                                       event_id=request.session['event_auth_user'][
                                                                           'event_id'])
                                    activity_history.save()

                            # adding hotel rooms and requested buddies for attendee
                            for attendee_booking in attendee_bookings:
                                room_available = AttendeeView.check_available_room(attendee.id, attendee_booking)
                                if not room_available:
                                    response_data['error'] = 'Those Rooms are not available'
                                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                                booking = Booking(attendee_id=attendee.id, room_id=attendee_booking['room_id'],
                                                  check_in=attendee_booking['check_in'],
                                                  check_out=attendee_booking['check_out'])
                                booking.save()
                                activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                   admin_id=request.session['event_auth_user']['id'],
                                                                   activity_type='register', category='room',
                                                                   room_id=attendee_booking['room_id'],
                                                                   event_id=request.session['event_auth_user']['event_id'])
                                activity_history.save()
                                buddies = attendee_booking['room_buddies']
                                if booking.room.beds > len(buddies):
                                    for buddy in buddies:
                                        if buddy.isdigit():
                                            requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                                            requested_buddy.save()
                                        else:
                                            requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False,
                                                                             email=buddy)
                                            requested_buddy.save()

                                booking_day_count = (datetime.strptime(booking.check_out, '%Y-%m-%d') - datetime.strptime(booking.check_in, '%Y-%m-%d')).days
                                result = EconomyLibrary.place_order(event_id=event_id, user_id=attendee.id, item_type='hotel', item_id=attendee_booking['room_id'], booking_day_count=booking_day_count, admin_id=admin_id, booking_id=booking.id)
                                if result == None:
                                    raise Exception('error in economy for hotel')
                                elif result:
                                    response_data['order_number'] = result['order_number']
                            response_data['success'] = 'Attendee Create Successfully'

                            updated_answers = []
                            all_answers = Answers.objects.filter(user_id=attendee.id)
                            check_for_distinct_question = []
                            answer_exists = []
                            for answer in all_answers:
                                if answer.question_id not in check_for_distinct_question:
                                    updated_answers.append(answer.as_dict())
                                    answer_exists.append(answer.question_id)
                                    check_for_distinct_question.append(answer.question_id)
                            all_questions = Questions.objects.filter(
                                group__event_id=request.session['event_auth_user']['event_id'])
                            for qs in all_questions:
                                if qs.id not in answer_exists:
                                    get_dict = dict(
                                        id='',
                                        user=attendee.as_dict(),
                                        question=qs.as_dict(),
                                        value='N/A'
                                    )
                                    updated_answers.append(get_dict)
                            response_data['updated_answers'] = updated_answers

                            if len(tag_list) > 0:
                                tag_list = tag_list[:-2]

                            response_data['tag_list'] = tag_list
                            if len(grouplist) > 0:
                                grouplist = grouplist[:-2]

                            response_data['group_list'] = grouplist
                            # Send Mail to attendee
                            send_mail = request.POST.get('send_mail')
                            if send_mail == 'true':
                                logger = logging.getLogger(__name__)
                                email_settings = Setting.objects.filter(name='attendee_add_confirmation',
                                                                        event_id=attendee.event_id)
                                if email_settings.exists():
                                    email_content = EmailContents.objects.filter(id=int(email_settings[
                                                                                            0].value))  # there will be different email content depend on update attendee or registration
                                    if email_content.exists():
                                        email_content = email_content[0]
                                        logger.debug('-----------Send email-----------------------')
                                        logger.debug(request.session['event_auth_user']['event_id'])
                                        EmailView.add_or_update_email_receivers(attendee, email_content.id,request.session['event_auth_user']['id'])
                                        message_history = MessageHistory(subject=email_content.subject, message='N/A',
                                                                         admin_id=request.session['event_auth_user']['id'],
                                                                         type='mail')
                                        message_history.save()
                                        activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                           admin_id=request.session['event_auth_user'][
                                                                               'id'],
                                                                           activity_type='message', category='message',
                                                                           message_id=message_history.id,
                                                                           event_id=request.session['event_auth_user'][
                                                                               'event_id'])
                                        activity_history.save()
                                        EmailView.send_email(request, attendee, email_content)
                            send_custom = request.POST.get('send_custom')
                            send_custom_type = request.POST.get('send_custom_type')
                            send_custom_value = request.POST.get('send_custom_value')
                            if send_custom == 'true' and send_custom_type != '' and send_custom_value != '':
                                if send_custom_type == 'email':
                                    email_content = EmailContents.objects.filter(id=int(send_custom_value))
                                    if email_content.exists():
                                        receiver = EmailReceivers.objects.filter(attendee_id=attendee.id,
                                                                                 email_content_id=send_custom_value,
                                                                                 is_show=1).first()
                                        if receiver:
                                            EmailReceivers.objects.filter(id=receiver.id).update(status='sent',
                                                                                              last_received=datetime.now())
                                        else:
                                            receiver_form = {
                                                'firstname': attendee.firstname,
                                                'lastname': attendee.lastname,
                                                'email': attendee.email,
                                                'status': 'sent',
                                                'added_by_id': request.session['event_auth_user']['id'],
                                                'email_content_id': send_custom_value,
                                                'attendee_id': attendee.id,
                                                'is_show': 1,
                                            }
                                            receiver = EmailReceivers(**receiver_form)
                                            receiver.save()
                                        message_history = MessageHistory(subject=email_content[0].subject,
                                                                         message='N/A',
                                                                         admin_id=request.session['event_auth_user'][
                                                                             'id'],
                                                                         type='mail')
                                        message_history.save()
                                        activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                           admin_id=request.session['event_auth_user'][
                                                                               'id'],
                                                                           activity_type='message', category='message',
                                                                           message_id=message_history.id,
                                                                           event_id=request.session['event_auth_user'][
                                                                               'event_id'])
                                        activity_history.save()
                                        receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
                                        receiver_history.save()
                                        EmailView.send_email(request, attendee, email_content[0])
                                elif send_custom_type == 'message':
                                    token_count = attendee.devicetoken_set.all().count()
                                    if attendee.phonenumber or token_count > 0:
                                        message_content = MessageContents.objects.filter(id=int(send_custom_value))
                                        if message_content.exists():
                                            exist_receiver = MessageReceivers.objects.filter(
                                                attendee_id=attendee.id, message_content_id=send_custom_value,
                                                is_show=1)
                                            if exist_receiver.exists():
                                                MessageReceivers.objects.filter(id=exist_receiver[0].id).update(
                                                    status='sent', last_received=datetime.now())
                                                receiver = exist_receiver[0]
                                            else:
                                                receiver_form = {
                                                    'firstname': attendee.firstname,
                                                    'lastname': attendee.lastname,
                                                    'mobile_phone': attendee.phonenumber,
                                                    'status': 'sent',
                                                    'added_by_id': request.session['event_auth_user']['id'],
                                                    'message_content_id': send_custom_value,
                                                    'attendee_id': attendee.id,
                                                    'is_show': 1,
                                                }
                                                receiver = MessageReceivers(**receiver_form)
                                                receiver.save()
                                            MessageReceiversView.send_message_to_single_receiver(request, receiver,
                                                                                                 message_content[0])

                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        else:
                            response_data['error'] = 'email already Exist'
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
            except Exception as e:
                ErrorR.efail(e)
                response_data = {}
                response_data['error'] = e
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data = {}
            response_data['error'] = 'You do not have Permission to do this'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def place_hotel_order(event_id, user_id, booking_data, booking_id, admin_id):
        booking_day_count = (datetime.strptime(booking_data['check_out'], '%Y-%m-%d') - datetime.strptime(booking_data['check_in'], '%Y-%m-%d')).days
        result = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='hotel', item_id=booking_data['room_id'], booking_day_count=booking_day_count, admin_id=admin_id, booking_id=booking_id)
        if result == None:
            # result can also be False, but we need to raise Exception when result is None
            raise Exception('error in economy for hotel')

    def update_hotel_order(event_id, user_id, booking_data, old_booking_data, old_booking_id, admin_id, new_booking_id=None):
        previous_booking_day_count = (old_booking_data['check_out'] - old_booking_data['check_in']).days
        new_check_in = datetime.strptime(booking_data['check_in'], '%Y-%m-%d')
        new_check_out = datetime.strptime(booking_data['check_out'], '%Y-%m-%d')
        new_booking_day_count = (new_check_out - new_check_in).days
        old_booking_dates = AttendeeView.get_date_list(old_booking_data['check_in'], old_booking_data['check_out'])
        new_booking_dates = AttendeeView.get_date_list(new_check_in, new_check_out)
        new_extra_booking_dates = list(set(new_booking_dates) - set(old_booking_dates))
        if previous_booking_day_count != new_booking_day_count or new_booking_id:
            day_difference = 0
            if new_booking_day_count > previous_booking_day_count:
                day_difference = new_booking_day_count - previous_booking_day_count

            EconomyLibrary.update_hotel_cost(event_id, user_id, booking_data['room_id'], new_booking_day_count, day_difference, old_booking_id, new_booking_id, new_extra_booking_dates, admin_id)
        elif old_booking_data['check_in'] != new_check_in or old_booking_data['check_out'] != new_check_out:
                EconomyLibrary.update_hotel_for_allotment(event_id, user_id, booking_data['room_id'], old_booking_id, old_booking_dates, new_booking_dates, admin_id)

    def get_date_list(check_in, check_out):
        return [check_in + timedelta(n) for n in range(0, (check_out - check_in).days)]

    def remove_hotel_order_item(event_id, user_id, room_id, booking_id, admin_id, check_in, check_out):
        order_info = EconomyLibrary.get_order_id(user_id, 'hotel', room_id, booking_id)
        if order_info:
            booking_allotment_dates = [check_in + timedelta(n) for n in range(0, (check_out - check_in).days)]
            EconomyLibrary.remove_item_from_order(event_id, user_id, order_info['order_id'], room_id, booking_id, admin_id, booking_allotment_dates)

    @transaction.atomic
    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'attendee_permission'):
            id = request.POST.get('id')
            admin_id = request.session['event_auth_user']['id']
            event_id = request.session['event_auth_user']['event_id']
            attendee = Attendee.objects.get(id=id)

            # before deleting attendee, we need to delete attendee's Orders and Payments,
            # Orders will be auto deleted but payments will not where we have to delete payments manually,
            # If attendee is group owner and the group have group order of other group member then system
            # need to prevent deletion and provide a message that the owner have group order of other members,
            # And when group member will delete then if the attendee has any pending/paid order then it's cost
            # will create credit order to group orders credit [group owner credit].

            if attendee.registration_group:
                result = AttendeeView.activities_before_delete_remove_group_attendee(id, event_id, admin_id)
                if not result['valid']:
                    response_data["warn"] = result['msg']
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                if RegistrationGroupOwner.objects.filter(owner_id=id).exists():
                    # group owner
                    group_info = EconomyLibrary.get_group_registration_info(id)
                    group_attendee_order_numbers = Orders.objects.filter(attendee_id__in=group_info['grp-atts']).values('order_number')
                    if group_attendee_order_numbers.count() > Orders.objects.filter(attendee_id=id).count():
                        # group members have order
                        response_data["warn"] = "Group members have orders, owner can't be deleted."
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                    else:
                        Payments.objects.filter(order_number__in=group_attendee_order_numbers).delete()
                        RegistrationGroups.objects.filter(id=group_info['group_id']).delete()

                else:
                    # not group attendee
                    attendee_order_numbers = Orders.objects.filter(attendee_id=id).values('order_number')
                    Payments.objects.filter(order_number__in=attendee_order_numbers).delete()

            # response_data["warn"] = "something wrong"
            # return HttpResponse(json.dumps(response_data), content_type="application/json")
            new_activity_history = ActivityHistory(attendee_id=id,
                                                   admin_id=request.session['event_auth_user']['id'],
                                                   activity_type='delete', category='event',
                                                   event_id=request.session['event_auth_user']['event_id'])
            new_activity_history.save()

            delete_att = DeletedAttendee(firstname=attendee.firstname, lastname=attendee.lastname, email=attendee.email,
                                         phonenumber=attendee.phonenumber, event_id=attendee.event_id,
                                         deleted_by_id=admin_id)
            delete_att.save()
            delete_att_histories = []
            old_history = ActivityHistory.objects.filter(attendee_id=attendee.id)
            for activity in old_history:
                history = DeletedHistory(attendee_id=delete_att.id, admin_id=activity.admin_id,
                                         activity_type=activity.activity_type,
                                         category=activity.category, message_id=activity.message_id,
                                         session_id=activity.session_id,
                                         question_id=activity.question_id, travel_id=activity.travel_id,
                                         room_id=activity.room_id,
                                         old_value=activity.old_value, new_value=activity.new_value,
                                         event_id=activity.event_id,
                                         created=activity.created, activity_message=activity.activity_message)
                delete_att_histories.append(history)
            DeletedHistory.objects.bulk_create(delete_att_histories)
            attendee.delete()
            response_data['success'] = 'Attendee Deleted Successfully'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['error'] = 'You do not have Permission to do this'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def activities_before_delete_remove_group_attendee(id, event_id, admin_id, attendee_remove=None):
        """ attendee_remove=True when group attendee get removed from registration group,
            so we have to delete attendee orders manually """
        response_data = dict(msg='', valid=True)
        try:
            attendee_orders = Orders.objects.filter(attendee_id=id)
            for order in attendee_orders:
                total_credit_value = 0
                total_credit_value_incl_vat = 0
                if order.status in ['paid', 'pending']:
                    order_items = OrderItems.objects.filter(order_id=order.id).exclude(item_type='rebate')
                    for order_item in order_items:
                        credit_value = order_item.cost
                        credit_value_incl_vat = order_item.get_total_cost()
                        rebate_item_list = OrderItems.objects.filter(order_id=order_item.order_id, item_type='rebate',
                                                                     rebate_for_item_type=order_item.item_type,
                                                                     rebate_for_item_id=order_item.item_id)
                        for rebate_item in rebate_item_list:
                            if not rebate_item.applied_on_open_order and not rebate_item.rebate_is_deleted:
                                credit_value -= rebate_item.rebate_amount
                                credit_value_incl_vat -= rebate_item.rebate_amount - order_item.get_rebate_vat_amount(
                                    rebate_item.rebate_amount)
                            elif rebate_item.applied_on_open_order and rebate_item.rebate_is_deleted:
                                credit_value += rebate_item.rebate_amount
                                credit_value_incl_vat += rebate_item.rebate_amount + order_item.get_rebate_vat_amount(
                                    rebate_item.rebate_amount)

                        total_credit_value += credit_value
                        total_credit_value_incl_vat += credit_value_incl_vat
                    # we have to add attendee's credit_orders to total_credit_value
                    credit_orders = CreditOrders.objects.filter(order_id=order.id, status='open')
                    for credit_order in credit_orders:
                        total_credit_value += credit_order.cost_excluding_vat
                        total_credit_value_incl_vat += credit_order.cost_including_vat

                    # now we have to add this total_credit_value to order_owner's credit_order
                    owner_open_credit_order = EconomyLibrary.get_group_owner_open_credit_order(id, order.order_number, event_id, admin_id)
                    if not owner_open_credit_order:
                        response_data["msg"] = "Attendee belongs to a registration group and the group does not have group owner, which caused an error."
                        response_data['valid'] = False
                        return response_data
                    else:
                        owner_open_credit_order.cost_excluding_vat += total_credit_value
                        owner_open_credit_order.cost_including_vat += total_credit_value_incl_vat
                        owner_open_credit_order.save()

                if order.status == 'paid':
                    # delete payment that does not include other attendee's payment
                    # few line earlier, we return the execution with warning, which will not effect this payment deletion block,
                    # because, if any order has payment that order will execute warning/return codes before coming here
                    order_number_other_order = Orders.objects.filter(order_number=order.order_number).exclude(attendee_id=id).aggregate(total=Sum('cost'))
                    if order_number_other_order['total'] in [None, 0]:
                        Payments.objects.filter(order_number=order.order_number).delete()
                        if order_number_other_order['total'] == 0:
                            # payment is deleted and still there is 0 cost order to order owner which status='paid' which
                            # will cause an error(due to get payment date) to get balance table, that's why status turn to 'pending'
                            Orders.objects.filter(order_number=order.order_number).exclude(attendee_id=id).update(status='pending')
                if attendee_remove:
                    msg = 'Delete order {0}, while attendee is removed from group.'.format(order.order_number)
                    ActivityHistory(attendee_id=id, admin_id=admin_id, activity_message=msg,
                                    activity_type='delete', category='order', event_id=event_id).save()
                    order.delete()
        except Exception as ex:
            ErrorR.efail(ex)
            response_data['valid'] = False
            response_data['msg'] = "Something went wrong."

        return response_data

    @staticmethod
    def get_booking_common_dates(bookings):
        a_list = []
        all_dates = []
        if len(bookings) > 1:
            booking_list = Booking.objects.filter(id__in=bookings)
            for booking in booking_list:
                booking_check_in = booking.check_in
                booking_check_out = booking.check_out
                day_count = (booking_check_out - booking_check_in).days
                booking_date_list = []
                for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                    booking_date_list.append(single_date)
                    all_dates.append(single_date)
                a_list.append(booking_date_list)

            for i in range(0, len(a_list)):
                for j in range(1, len(a_list)):
                    all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
        return all_dates

    def resetAttendee(request):
        response_data = {}
        if EventView.check_permissions(request, 'attendee_permission'):
            id = request.POST.get('id')

            attendee = Attendee.objects.get(id=id)
            answers = Answers.objects.filter(question__group__event_id=request.session['event_auth_user']['event_id'],
                                             user_id=id)
            for answer in answers:
                if answer.question.default_answer_status == 'empty' and answer.question.actual_definition is None:
                    answer.delete()
                elif answer.question.default_answer_status == 'set':
                    if answer.question.actual_definition == 'firstname':
                        attendee.firstname = answer.question.default_answer
                        attendee.save()
                    elif answer.question.actual_definition == 'lastname':
                        attendee.lastname = answer.question.default_answer
                        attendee.save()
                    elif answer.question.actual_definition == 'email':
                        continue
                    elif answer.question.actual_definition == 'phone':
                        attendee.phonenumber = answer.question.default_answer
                        attendee.save()

                    answer.value = answer.question.default_answer
                    answer.value = answer.value.replace('&quot;', '"').replace("&apos;", "'")
                    answer.save()

            sessions = SeminarsUsers.objects.filter(session__group__event_id=request.session['event_auth_user']['event_id'],
                                                    attendee_id=id)
            for ssn in sessions:
                if ssn.session.default_answer_status == 'empty':
                    ssn.delete()
                elif ssn.session.default_answer_status == 'set':
                    ssn.value = ssn.session.default_answer
                    ssn.save()

            travels = TravelAttendee.objects.filter(travel__group__event_id=request.session['event_auth_user']['event_id'],
                                                    attendee_id=id)
            for travel in travels:
                if travel.travel.default_answer_status == 'empty':
                    travel.delete()
                elif travel.travel.default_answer_status == 'set':
                    travel.value = travel.travel.default_answer
                    travel.save()

            event_id = request.session['event_auth_user']['event_id']
            default_group = Setting.objects.filter(name='default_group', event_id=event_id)
            if default_group:
                default_groups = json.loads(default_group[0].value)
                for group in default_groups:
                    att_group = AttendeeGroups(group_id=int(group), attendee_id=attendee.id)
                    att_group.save()

            attendee_tags = AttendeeTag.objects.filter(attendee_id=attendee.id).delete()
            default_tags = Setting.objects.filter(name='default_tag', event_id=event_id)

            if default_tags:
                default_tags = json.loads(default_tags[0].value)
                for tag in default_tags:
                    att_tag = AttendeeTag(attendee_id=attendee.id, tag_id=tag)
                    att_tag.save()

            attendee_bookings = Booking.objects.filter(attendee_id=attendee.id)

            for booking in attendee_bookings:
                if booking.room.keep_hotel == 0:
                    booking.delete()

            response_data['success'] = 'Attendee Reset Successfully'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['error'] = 'You do not have Permission to do this'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_speakers(request):
        response_data = {}
        val = request.POST.get('q')
        attendees = Attendee.objects.annotate(full_name=Concat('firstname', Value(' '), 'lastname')).filter(
            full_name__istartswith=val, event_id=request.session['event_auth_user']['event_id'], status="registered")
        my_data = []
        for attendee in attendees:
            arr_data = {}
            arr_data['id'] = attendee.id
            arr_data['text'] = attendee.firstname + ' ' + attendee.lastname
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def attendee_order(request,user_id):
        response_data={}
        event_id = request.session['event_auth_user']['event_id']
        economy_data = EconomyLibrary.get_order_tables(user_id, event_id)
        if economy_data['order_type'] == 'attendee-order':
            attendee_order = economy_data['order_list']
        else:
            attendee_order = []

        context={
            'orders':attendee_order,
            'order_table_type': 'attendee-order',
            'request':request,
            'date_format':CommonHelper.get_python_date_format(request)
        }
        html = render_to_string("attendee/attendee_order.html",context)
        response_data["html"]=html
        return HttpResponse(json.dumps(response_data),content_type="application/json")

    def group_order(request, user_id):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        economy_data = EconomyLibrary.get_order_tables(user_id, event_id)
        if economy_data['order_type'] == 'group-order':
            group_order = economy_data['order_list']
        else:
            group_order = []

        context = {
            'orders': group_order,
            'order_table_type': 'group-order',
            'request':request,
            'date_format': CommonHelper.get_python_date_format(request)
        }
        html = render_to_string("attendee/attendee_order.html", context)
        response_data["html"] = html
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def attendee_balance(request, user_id):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        balance = EconomyLibrary.get_balance_tables(user_id,  event_id)
        context = {
            'balance_tables': balance,
            'date_format':CommonHelper.get_python_date_format(request)
        }
        html = render_to_string("attendee/attendee_balance.html", context)
        response_data["html"] = html
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def change_order_status(request):
        response_data={}
        if EventView.check_permissions(request, 'economy_permission'):
            try:
                order_number = request.POST.get('order_number')
                status = request.POST.get('status')
                user_id = request.POST.get('user_id')
                admin_id =request.session['event_auth_user']['id']
                event_id =request.session['event_auth_user']['event_id']

                result = EconomyLibrary.change_order_status(order_number,status,event_id,user_id,admin_id)
                if result.get('status_changed'):
                    response_data['status'] = True
                    response_data['current_order_status'] = result['status']
                    response_data['message'] = "Order status changed successfully."
                else:
                    response_data['status'] = False
                    response_data['message'] = "Order can't be changed."
            except Exception as e:
                ErrorR.efail(e)
                response_data['status']= False
                response_data['message']= "Something went wrong. Please try again"
        else:
            response_data['message'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add_rebate_to_order(request):
        response_data = {}
        order_number = request.POST.get('order_number')
        user_id = request.POST.get('user_id')
        order_id = request.POST.get('order_id')
        admin_id = request.session['event_auth_user']['id']
        rebate_id = request.POST.get('rebate_id')
        result = EconomyLibrary.apply_rebate(user_id, order_id, rebate_id, None, None, admin_id)
        if result['result']:
            response_data['status'] = True
            response_data['download_flag'] = result['download_credit_invoice']
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def remove_rebate_from_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'economy_permission'):
            order_id = request.POST.get('order_id')
            rebate_id = request.POST.get('rebate_id')
            rebate_for_item_id = request.POST.get('rebate_for_item_id')
            rebate_for_item_type = request.POST.get('rebate_for_item_type')
            user_id = request.POST.get('user_id')
            admin_id = request.session['event_auth_user']['id']
            event_id = request.session['event_auth_user']['event_id']
            result = EconomyLibrary.remove_rebate_from_order(order_id,user_id,rebate_id,rebate_for_item_type,rebate_for_item_id,event_id,admin_id)
            if result:
                response_data['status'] = True
                response_data["message"] = "Rebate Delete successfully"
        else:
            response_data['status'] = False
            response_data['message'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def change_order_item_cost(request):
        response = dict(success=False, canceled_order=False, message="Something wrong!")
        try:
            event_id = request.session['event_auth_user']['event_id']
            admin_id = request.session['event_auth_user']['id']
            order_item_id = request.POST.get('order_item_id')
            new_cost = request.POST.get('new_cost')
            if order_item_id.isdigit() and new_cost.replace('.', '').isdigit():
                new_cost = float(new_cost)
                if new_cost > 0:
                    response = EconomyLibrary.admin_change_order_item_cost(order_item_id, new_cost, event_id, admin_id)
        except Exception as ex:
            ErrorR.efail(ex)
        return JsonResponse(response)

    def admin_pdf_request(request):
        if EventView.check_read_permissions(request, 'economy_permission'):
            try:
                event_id = request.session['event_auth_user']['event_id']
                attendee_id = request.GET.get('uid')
                data_action = request.GET.get('data')
                order_number = request.GET.get('order_number')
                if data_action == 'order-invoice':
                    response = EconomyPDFGenerator.get_order_invoice(request,event_id, order_number, attendee_id)
                elif data_action == 'receipt':
                    response = EconomyPDFGenerator.get_receipt(request, event_id, order_number, attendee_id)
                elif data_action == 'credit-invoice':
                    response = EconomyPDFGenerator.get_credit_invoice(request, event_id, order_number, attendee_id)
                else:
                    response = HttpResponse('Something went wrong.')
            except Exception as e:
                ErrorR.efail(e)
                response = HttpResponse('Something went wrong.')
            return response

    def delete_session(request):
        response_data = {}
        try:
            id = request.POST.get('id')
            attendee_session = SeminarsUsers.objects.get(id=id)
            attendee_id = attendee_session.attendee_id
            session_id = attendee_session.session_id
            attendee_session.delete()
            seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id, status='not-attending')
            seminar_attendee.save()
            activity_history = ActivityHistory(attendee_id=attendee_id,
                                               admin_id=request.session['event_auth_user']['id'],
                                               activity_type='update', category='session', session_id=session_id,
                                               old_value='Attending', new_value='Not Attending',
                                               event_id=request.session['event_auth_user']['event_id'])
            activity_history.save()
            request.session['event_id'] = request.session['event_auth_user']['event_id']

            order_detail = EconomyLibrary.get_order_id(attendee_id,'session',session_id)
            if order_detail:
                admin_id=request.session['event_auth_user']['id']
                event_id=request.session['event_auth_user']['event_id']
                result = EconomyLibrary.remove_item_from_order(event_id,attendee_id,order_detail['order_id'],session_id,admin_id)
                response_data['download_flag'] = result['download_applicable']
                response_data['attendee_id'] = attendee_id
                response_data['order_number'] = order_detail['order_number']

            try:
                current_language = PresetEvent.objects.filter(
                    event_id=request.session['event_auth_user']['event_id']).first()
                language_id = current_language.preset.id
            except:
                current_language = Presets.objects.get(id=6)
                language_id = current_language.preset.id
            request.session['language_id'] = language_id
            request.session.modified = True
            ErrorR.okblue("Notify start")
            SessionDetail.notify_queue_user(request, session_id)
            response_data['success'] = True
            response_data['message'] = 'Attendees Session Deleted Successfully'
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
            response_data['message'] = 'Something went wron. Please try again'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_travel(request):
        response_data = {}
        try:
            id = request.POST.get('id')
            attendee_travel = TravelAttendee.objects.get(id=id)
            attendee_id = attendee_travel.attendee_id
            travel_id = attendee_travel.travel_id
            attendee_travel.delete()
            travel_attendee = TravelAttendee(attendee_id=attendee_id, travel_id=travel_id, status='not-attending')
            travel_attendee.save()
            activity_history = ActivityHistory(attendee_id=attendee_id,
                                               admin_id=request.session['event_auth_user']['id'],
                                               activity_type='update', category='travel', travel_id=travel_id,
                                               old_value='Attending', new_value='Not Attending',
                                               event_id=request.session['event_auth_user']['event_id'])
            activity_history.save()
            response_data['success'] = True
            response_data['message'] = 'Attendees Travel Deleted Successfully'
        except Exception as e:
            print(e)
            response_data['success'] = False
            response_data['message'] = 'Something went wron. Please try again'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_booking(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        admin_id = request.session['event_auth_user']['id']
        id = request.POST.get('id')
        attendee_booking = Booking.objects.get(id=id)
        room_id = attendee_booking.room_id
        attendee_id = attendee_booking.attendee_id
        attendee_booking_id = attendee_booking.id
        check_in = attendee_booking.check_in
        check_out = attendee_booking.check_out
        attendee_booking.delete()
        activity_history = ActivityHistory(attendee_id=attendee_id, admin_id=admin_id, activity_type='delete', category='room', room_id=room_id, event_id=request.session['event_auth_user']['event_id'])
        activity_history.save()
        AttendeeView.remove_hotel_order_item(event_id, attendee_id, room_id, attendee_booking_id, admin_id, check_in, check_out)
        response_data['success'] = 'Attendees Booking Deleted Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_attendees(request):
        response_data = {}
        val = request.POST.get('q')
        current_attendee_id = request.POST.get('current_attendee')
        attendees = Attendee.objects.annotate(full_name=Concat('firstname', Value(' '), 'lastname')).filter(
            full_name__istartswith=val, event_id=request.session['event_auth_user']['event_id'],
            status="registered").exclude(
            id=current_attendee_id)
        my_data = []
        for attendee in attendees:
            arr_data = {
                'id': attendee.id,
                'text': attendee.firstname + ' ' + attendee.lastname
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_multiple_attendee(request):
        attendees = json.loads(request.POST.get('attendee_ids'))
        attendee_list = []
        attList = '0'
        for attendee in attendees:
            user = Attendee.objects.get(id=attendee['id'])
            attendee_list.append(user.as_dict())
            attList = attList + "," + attendee['id']
        attList = attList[2:]
        question_groups = []
        questionGroup = GroupView.get_questionGroup(request)
        for group in questionGroup:
            group.questions = Questions.objects.all().filter(group_id=group.id)
            question_list = []
            data = QuestionView.get_Questions(request, group.questions)
            for question in data:
                answer_list = []
                for attendee in attendee_list:
                    answers = Answers.objects.filter(user_id=attendee['id']).filter(
                        question_id=question['question']['id'])
                    for answer in answers:
                        answer_list.append(answer.as_dict())
                question['answers'] = answer_list
            question_list.append(data)
            q_obj = {
                'group': group.as_dict(),
                'questions': question_list
            }
            question_groups.append(q_obj)
        all_attendee_groups = GroupView.get_attendeeGroup(request)
        attendee_groups = []
        for group in all_attendee_groups:
            attendee_groups.append(group.as_dict())
        data = {'attendees': attendee_list, 'question_groups': question_groups, 'attendee_groups': attendee_groups}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def update_multiple_attendee(request):
        response_data = {}
        attendees = json.loads(request.POST.get('attendees'))
        answers = json.loads(request.POST.get('answers'))
        attendee_session = json.loads(request.POST.get('attendee_session'))
        attendee_travel = json.loads(request.POST.get('attendee_travel'))
        updated_attendee = []
        group_id = request.POST.get('role')
        attendee_tags = json.loads(request.POST.get('attendee_tags'))
        event_id = request.session['event_auth_user']['event_id']
        for attendee in attendees:
            attendee_id = attendee['id']
            for answer in answers:
                AnswerView.saveAnswers(request, attendee_id, answer)

            form_data = {}
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            king_email = request.POST.get('king_email')
            mobile_phone = request.POST.get('mobile_phone')
            if first_name != '' and first_name != 'Empty' and first_name != '[Multiple Values]':
                form_data['firstname'] = first_name
            if last_name != '' and last_name != 'Empty' and last_name != '[Multiple Values]':
                form_data['lastname'] = last_name
            if king_email != '' and king_email != 'Empty' and king_email != '[Multiple Values]':
                form_data['email'] = king_email
            if mobile_phone != '' and mobile_phone != 'Empty' and mobile_phone != '[Multiple Values]':
                form_data['phonenumber'] = mobile_phone
            if group_id != '' and group_id != 'Empty' and group_id != '[Multiple Values]':
                form_data['group_id'] = group_id
            Attendee.objects.filter(id=attendee_id).update(**form_data)
            for tag in attendee_tags:
                if tag.isdigit():
                    if not (AttendeeTag.objects.filter(attendee_id=attendee_id, tag_id=tag).exists()):
                        attendee_tag = AttendeeTag(attendee_id=attendee_id, tag_id=tag)
                        attendee_tag.save()
                else:
                    tag_exist = Tag.objects.filter(name=tag, event_id=event_id)
                    if tag_exist.exists():
                        tag_id = tag_exist[0].id
                    else:
                        new_tag = Tag(name=tag, event_id=event_id)
                        new_tag.save()
                        tag_id = new_tag.id
                    attendee_tag = AttendeeTag(attendee_id=attendee_id, tag_id=tag_id)
                    attendee_tag.save()
            for session in attendee_session:
                sessionAttendees = Session.objects.values('max_attendees').get(id=session['id'])
                bookedSessions = SeminarsUsers.objects.filter(session_id=session['id'], status='attending').count()
                if sessionAttendees['max_attendees'] > bookedSessions:
                    x_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session['id'])
                    if not x_session:
                        attendeeSessions = SeminarsUsers(attendee_id=attendee_id, session_id=session['id'])
                        attendeeSessions.save()
                        activity_history = ActivityHistory(attendee_id=attendee_id,
                                                           admin_id=request.session['event_auth_user']['id'],
                                                           activity_type='update', category='session',
                                                           session_id=session['id'], old_value='Not Answered',
                                                           new_value='Attending',
                                                           event_id=request.session['event_auth_user']['event_id'])
                        activity_history.save()
                else:
                    response_data[
                        'warning'] = 'The session you tried to add is full and therefor has not been added to the attendee'

            for travel in attendee_travel:
                attendeeTravels = TravelAttendee(attendee_id=attendee_id, travel_id=travel['id'])
                attendeeTravels.save()

                # adding hotel rooms and requested buddies for attendee
                attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
                for attendee_booking in attendee_bookings:
                    if attendee_booking['exists'] == 1:
                        room_available = AttendeeView.check_available_room(attendee.id, attendee_booking)
                        if not room_available:
                            response_data['error'] = 'Those Rooms are not available'
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        booking_data = {
                            'room_id': attendee_booking['room_id'],
                            'check_in': attendee_booking['check_in'],
                            'check_out': attendee_booking['check_out']
                        }
                        booking = Booking.objects.filter(id=attendee_booking['id']).update(**booking_data)
                        r = RequestedBuddy.objects.filter(booking_id=attendee_booking['id']).delete()
                        buddies = attendee_booking['room_buddies']
                        for buddy in buddies:
                            if buddy.isdigit():
                                requested_buddy = RequestedBuddy(booking_id=attendee_booking['id'], buddy_id=buddy)
                                requested_buddy.save()
                            else:
                                requested_buddy = RequestedBuddy(booking_id=attendee_booking['id'], exists=False,
                                                                 email=buddy)
                                requested_buddy.save()
                    else:
                        room_available = AttendeeView.check_available_room(attendee.id, attendee_booking)
                        if not room_available:
                            response_data['error'] = 'Those Rooms are not available'
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        booking = Booking(attendee_id=attendee_id, room_id=attendee_booking['room_id'],
                                          check_in=attendee_booking['check_in'],
                                          check_out=attendee_booking['check_out'])
                        booking.save()
                        buddies = attendee_booking['room_buddies']
                        for buddy in buddies:
                            if buddy.isdigit():
                                requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                                requested_buddy.save()
                            else:
                                requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False, email=buddy)
                                requested_buddy.save()

            updated_answers = []
            all_answers = Answers.objects.filter(user_id=attendee_id)
            for answer in all_answers:
                updated_answers.append(answer.as_dict())
            attendee_answers = {
                'attendee_id': attendee_id,
                'updated_answers': updated_answers
            }
            updated_attendee.append(attendee_answers)
        response_data['success'] = 'Multiple Attendee Question Update Successfully'
        response_data['updated_answers'] = updated_attendee
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def check_available_room(user_id, booking):
        start_date = datetime.strptime(booking['check_in'], '%Y-%m-%d')
        end_date = datetime.strptime(booking['check_out'], '%Y-%m-%d')
        day_count = (end_date - start_date).days
        room = Room.objects.get(id=booking['room_id'])
        available = True
        if day_count < 1:
            available = False

        user_bookings = Booking.objects.filter(attendee_id=user_id).exclude(
            id=booking['id']) if 'id' in booking else Booking.objects.filter(attendee_id=user_id)
        date_list = []
        for u_b in user_bookings:
            u_b_date_diff = (u_b.check_out - u_b.check_in).days
            for u_b_item in range(0, u_b_date_diff):
                u_b_date = datetime.strftime(u_b.check_in + timedelta(u_b_item), '%Y-%m-%d').split(' ')[0]
                if u_b_date not in date_list:
                    date_list.append(u_b_date)

        for single_date in (start_date + timedelta(n) for n in range(day_count)):
            current_date = datetime.strftime(single_date, '%Y-%m-%d')
            # if 'id' not in booking and current_date in date_list:
            if current_date in date_list:
                # only for new booking
                available = False

            if current_date != str(end_date).split(' ')[0]:
                allotments = RoomAllotment.objects.filter(available_date=current_date, room_id=booking['room_id'])
                if allotments.count():
                    get_bookings = Booking.objects.filter(room_id=booking['room_id'], check_in__lte=current_date,
                                                          check_out__gt=current_date).count()
                    if 'id' in booking:
                        get_bookings = get_bookings - 1
                    total_beds = room.beds * allotments[0].allotments
                    if get_bookings >= total_beds:
                        available = False
                else:
                    available = False

        return available

    def check_unique_secret_key(request):
        secret_key = request.POST["secret_key"]
        checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
        if checkUniquity < 1:
            return HttpResponse("false")
        else:
            return HttpResponse("true")

    def add_booking_history(request,attendee_id,room_id,activity):
        activity_history = ActivityHistory(attendee_id=attendee_id,admin_id=request.session['event_auth_user']['id'],activity_type=activity, category='room',room_id=room_id,event_id=request.session['event_auth_user']['event_id'])
        activity_history.save()
        return ''


class AttendeeDetailView(generic.DetailView):
    assign_session_write_access = False
    assign_travel_write_access = False
    assign_hotel_write_access = False

    def get_object(self, pk):
        try:
            return Attendee.objects.filter(id=pk)
        except Users.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
            allAnswers = user[0].answers_set.all()
            answer_list = []
            for answer in allAnswers:
                answer_list.append(answer.as_dict())
            attendee = user[0].as_dict()
            attendee['created'] = attendee['created'].split(".")[0]
            attendee['updated'] = attendee['updated'].split(".")[0]
            attendee['created'] = TimeDetailView.utc_to_local(request, attendee['created'])
            attendee['updated'] = TimeDetailView.utc_to_local(request, attendee['updated'])
            attendee['created'] = str(CommonHelper.get_formated_date(request,attendee['created']))
            attendee['updated'] = str(CommonHelper.get_formated_date(request,attendee['updated']))
            question_groups = []
            questionGroup = GroupView.get_questionGroup(request)
            for group in questionGroup:
                group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
                question_list = []
                data = QuestionView.get_Questions(request, group.questions)
                question_list.append(data)
                q_obj = {
                    'group': group.as_dict(),
                    'questions': question_list
                }

                question_groups.append(q_obj)

            all_attendee_groups = GroupView.get_attendeeGroup(request)
            attendee_groups = []
            for group in all_attendee_groups:
                attendee_groups.append(group.as_dict())

            travels = Travel.objects.filter(travel_bound='outbound',
                                            group__event_id=request.session['event_auth_user']['event_id'])
            outbound_flights = []
            for flight in travels:
                outbound_flights.append(flight.as_dict())

            homebound_travels = Travel.objects.filter(travel_bound='homebound',
                                                      group__event_id=request.session['event_auth_user']['event_id'])
            homebound_flights = []
            for home_travel in homebound_travels:
                homebound_flights.append(home_travel.as_dict())
            # AttendeeDetailView.homebound_flights=homebound_flights


            tag_list = []
            attendee_tags = AttendeeTag.objects.filter(attendee_id=pk)
            for tag in attendee_tags:
                tag_list.append(tag.as_dict())
            group_list = []
            selected_groups = AttendeeGroups.objects.filter(attendee_id=pk)
            for selected_group in selected_groups:
                group_list.append(selected_group.group_id)

            is_part_of_group = False
            if user[0].registration_group:
                is_part_of_group = True
            else:
                if RegistrationGroupOwner.objects.filter(owner_id=user[0].id).exists():
                    is_part_of_group = True

            data = {
                'success': True,
                'user': attendee,
                'question_groups': question_groups,
                'answers': answer_list,
                'attendee_groups': attendee_groups,
                'attendee_tags': tag_list,
                'attendee_selected_groups': group_list,
                'outbound_flights': outbound_flights,
                'homebound_flights': homebound_flights,
                'datepicker_date_format':CommonHelper.get_datepicker_date_format(request),
                'timezone':CommonHelper.get_timezone(request),
                'moment_date_format':CommonHelper.get_moment_date_format(request),
                'is_part_of_group': is_part_of_group
            }
            return HttpResponse(json.dumps(data), content_type='application/json')
        except Exception as e:
            import traceback
            traceback.print_exc()
            data = {
                'success': False
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

    def default_answer(request, format=None):
        event_id = request.session['event_auth_user']['event_id']
        question_groups = []
        questionGroup = GroupView.get_questionGroup(request)
        question_group = questionGroup
        for group in question_group:
            group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
            question_list = []
            data = QuestionView.get_Questions(request, group.questions)
            question_list.append(data)
            q_obj = {
                'group': group.as_dict(),
                'questions': question_list

            }
            question_groups.append(q_obj)
        all_attendee_groups = GroupView.get_attendeeGroup(request)
        attendee_groups = []
        for group in all_attendee_groups:
            attendee_groups.append(group.as_dict())

        context = {
            'current_admin': request.session['event_auth_user']
        }

        sessions = Session.objects.filter(group__event_id=event_id)
        travels = Travel.objects.filter(group__event_id=event_id)
        options = [
            {'id': 'attending', 'value': 'Attending'},
            {'id': 'in-queue', 'value': 'In Queue'},
            {'id': 'not-attending', 'value': 'Not Attending'}
        ]
        sessionWithOption = []
        for session in sessions:
            sessionWithOption.append({'session': session.as_dict(), 'options': options})
        travelWithOption = []
        for travel in travels:
            travelWithOption.append({'session': travel.as_dict(), 'options': options})

        tag_list = []
        tags = Setting.objects.filter(name='default_tag', event_id=event_id)
        if tags:
            all_tags = Tag.objects.filter(id__in=json.loads(tags[0].value))
            for tag in all_tags:
                tag_list.append(tag.as_dict())

        default_group = Setting.objects.filter(name='default_group', event_id=event_id)
        if default_group:
            default_group = default_group[0].value
        else:
            default_group = 0

        data = {
            'question_groups': question_groups,
            'attendee_groups': attendee_groups,
            'sessions': sessionWithOption,
            'travels': travelWithOption,
            'attendee_tags': tag_list,
            'default_selected_group': default_group,
            'datepicker_date_format': CommonHelper.get_datepicker_date_format(request)
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_history(request, user_id):
        type = request.GET.get('type')
        activity_history = None
        if not type:
            activity_history = ActivityHistory.objects.filter(attendee_id=user_id,
                                                          event_id=request.session['event_auth_user'][
                                                              'event_id']).order_by('-created')
        else:
            selected_category = ['rebate','order','order_item','credit_order', 'credit_usage', 'payment']
            activity_history = ActivityHistory.objects.filter(category__in=selected_category,attendee_id=user_id,
                                                              event_id=request.session['event_auth_user'][
                                                                  'event_id']).order_by('-created')

        context = {
            'activity_history': activity_history,
            'current_admin': request.session['event_auth_user'],
            'date_format':CommonHelper.get_python_date_format(request)+' H:i'
        }
        from django.template.loader import render_to_string
        html = render_to_string('attendee/history.html', context)
        return HttpResponse(html)

    def get_hotels(request, user_id):
        bookings = Booking.objects.filter(attendee_id=user_id)
        booking_list = []
        for booking in bookings:
            requested_buddies = RequestedBuddy.objects.filter(booking_id=booking.id)
            bookings_buddies = {}
            bookings_buddies['booking'] = booking.as_dict()
            buddy_list = []

            for requested_buddy in requested_buddies:
                if requested_buddy.buddy_id:
                    buddy_list.append(requested_buddy.as_dict())
                else:
                    buddy_list.append(requested_buddy.as_dict_alt())

            bookings_buddies['buddies'] = buddy_list
            actual_buddies = MatchLine.objects.filter(booking_id=booking.id)
            actual_buddy_list = []
            if actual_buddies.exists():
                for actual_buddie in actual_buddies:
                    match_lines = MatchLine.objects.filter(match_id=actual_buddie.match_id).exclude(
                        booking__attendee_id=user_id)
                    for match_line in match_lines:
                        actual_buddy_list.append(match_line.as_dict())

            bookings_buddies['actual_buddies'] = actual_buddy_list
            booking_list.append(bookings_buddies)

        assign_hotel_write_access = False
        if "assign_hotel_permission" in request.session['admin_permission']['content_permission'] and \
                        request.session['admin_permission']['content_permission']['assign_hotel_permission'][
                            'access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            assign_hotel_write_access = True
        data = {
            'bookings_buddies': booking_list,
            'assign_hotel_write_access': assign_hotel_write_access
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_sessions(request, user_id):
        attendee_sessions = SeminarsUsers.objects.filter(
            Q(attendee_id=user_id) & Q(Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))

        session_list = []
        for session in attendee_sessions:
            session_list.append(session.as_dict())
        assign_session_write_access = False
        if "assign_session_permission" in request.session['admin_permission']['content_permission'] and \
                        request.session['admin_permission']['content_permission']['assign_session_permission'][
                            'access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            assign_session_write_access = True
        data = {
            'attendee_sessions': session_list,
            'assign_session_write_access': assign_session_write_access

        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_travels(request, user_id):
        attendee_travels = TravelAttendee.objects.filter(attendee_id=user_id, status='attending')

        travel_list = []
        for travel in attendee_travels:
            travel_list.append(travel.as_dict())
        assign_travel_write_access = False
        if "assign_travel_permission" in request.session['admin_permission']['content_permission'] and \
                        request.session['admin_permission']['content_permission']['assign_travel_permission'][
                            'access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            assign_travel_write_access = True
        data = {
            'attendee_travels': travel_list,
            'assign_travel_write_access': assign_travel_write_access,
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def attendeeInfo(request, pk):
        questionGroup = GroupView.get_questionGroup(request)
        context = {
            'questionGroup': questionGroup
        }
        return render(request, 'attendee/attendee_info.html', context)


class GroupRegistrationDetail(generic.DetailView):
    def get_group_registrations(request, user_id):
        try:
            response_data = {}
            attendee = Attendee.objects.get(id=user_id)
            owner = RegistrationGroupOwner.objects.filter(owner_id=user_id)
            group_id = None
            if attendee.registration_group_id:
                group_id = attendee.registration_group_id
            elif owner.exists():
                group_id = owner[0].group_id
            if group_id:
                registration_group_attendees = Attendee.objects.filter(registration_group_id=group_id)
                registration_group_owner = RegistrationGroupOwner.objects.get(group_id=group_id)
                response_data['registration_group_attendees'] = registration_group_attendees
                response_data['registration_group_owner'] = registration_group_owner
                response_data['has_group'] = True
            else:
                response_data['has_group'] = False
            response_data['request'] = request
            registration_group_html = render_to_string('attendee/group_registration.html', response_data)
        except Exception as e:
            ErrorR.efail(e)
            registration_group_html = ''
        return HttpResponse(registration_group_html)

    def get_group_registration_attendee_search(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        excluded_attendees = []
        attendee_id = int(request.POST.get('attendee_id'))
        excluded_attendees.append(attendee_id)
        attendee_owners = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values('owner_id')
        excluded_attendees.extend([item['owner_id'] for item in attendee_owners])
        all_group_attendees = Attendee.objects.filter(registration_group__isnull=False, event_id=event_id).values('id')
        excluded_attendees.extend([item['id'] for item in all_group_attendees])
        attendee_list = []
        val = request.POST.get('q')
        attendees = Attendee.objects.annotate(fullname=Concat('firstname', Value(' '), 'lastname')).filter(
            fullname__icontains=val, event_id=event_id).exclude(id__in=excluded_attendees)
        for attendee in attendees:
            attendee_data = {}
            attendee_data['id'] = attendee.id
            attendee_data['text'] = attendee.firstname + ' ' + attendee.lastname
            attendee_list.append(attendee_data)
        response_data['results'] = attendee_list
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def add_group_registration_attendee(request):
        response_data = {}
        try:
            event_id = request.session['event_auth_user']['event_id']
            admin_id = request.session['event_auth_user']['id']
            owner_id = int(request.POST.get('owner_id'))
            response_data['success'] = True
            activity_history = []
            if 'group_id' in request.POST:
                group_id = int(request.POST.get('group_id'))
                response_data['message'] = "Attendee added to group successfully"
            else:
                group_name = 'registration-group-' + str(owner_id)
                new_group = RegistrationGroups(name=group_name, event_id=event_id)
                new_group.save()
                group_id = new_group.id
                group_owner = RegistrationGroupOwner(group_id=group_id, owner_id=owner_id)
                group_owner.save()
                activity_history.append(ActivityHistory(attendee_id=owner_id,
                                                       admin_id=admin_id,
                                                       activity_type='update', category='registration_group',
                                                       registration_group_id=group_id, new_value='as Order owner',
                                                       event_id=event_id))
                response_data['message'] = "Group is created and Attendee added successfully"
            attendees = json.loads(request.POST.get('attendees'))
            for attendee_id in attendees:
                att_id = int(attendee_id)
                if not RegistrationGroupOwner.objects.filter(owner_id=att_id).exists():
                    attendee = Attendee.objects.get(id=att_id)
                    if attendee.registration_group_id:

                        GroupRegistrationDetail.delete_empty_group(request,attendee.registration_group_id,attendee.id)
                        activity_history.append(ActivityHistory(attendee_id=att_id,
                                                       admin_id=admin_id,
                                                       activity_type='delete', category='registration_group',
                                                       registration_group_id=attendee.registration_group_id,
                                                       event_id=event_id))
                    attendee.registration_group_id = group_id
                    attendee.save()
                    activity_history.append(ActivityHistory(attendee_id=att_id, admin_id=admin_id,
                                                       activity_type='update', category='registration_group',
                                                       registration_group_id=group_id, new_value='as Attendee', event_id=event_id))
                    # after adding to group, we need to merge newly added attendee's order to group order if both orders are open
                    attendee_orders = Orders.objects.filter(attendee_id=att_id, status='open')
                    for order in attendee_orders:
                        group_info = EconomyLibrary.get_group_registration_info(att_id)
                        group_info['grp-atts'].remove(att_id)
                        group_open_order = Orders.objects.filter(attendee_id__in=group_info['grp-atts'], status='open')
                        if group_open_order.exists():
                            old_order_number = order.order_number
                            order.order_number = group_open_order[0].order_number
                            order.save()
                            activity_msg = 'Order {0} is changed to {1}, because attendee added to registration group and open order {0} merged to group open order {1}.'.format(old_order_number, order.order_number)
                            EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, att_id, admin_id)

            ActivityHistory.objects.bulk_create(activity_history)
            registration_group_attendees = Attendee.objects.filter(registration_group_id=group_id)
            registration_group_owner = RegistrationGroupOwner.objects.get(group_id=group_id)
            context = {}
            context['registration_group_attendees'] = registration_group_attendees
            context['registration_group_owner'] = registration_group_owner
            context['has_group'] = True
            response_data['group_html'] = render_to_string('attendee/group_registration.html', context)
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
            response_data['message'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def delete_group_registration_attendee(request):
        response_data = {}
        if EventView.check_permissions(request, 'group_registration_permission'):
            try:
                group_id = int(request.POST.get('group_id'))
                attendee_id = int(request.POST.get('attendee_id'))
                event_id = request.session['event_auth_user']['event_id']
                admin_id = request.session['event_auth_user']['id']
                result = AttendeeView.activities_before_delete_remove_group_attendee(attendee_id, event_id, admin_id, True)
                if not result['valid']:
                    raise Exception(result['msg'])
                Attendee.objects.filter(id=attendee_id).update(registration_group_id=None)
                activity_history = ActivityHistory(attendee_id=attendee_id,
                                                           admin_id=admin_id,
                                                           activity_type='delete', category='registration_group',
                                                           registration_group_id=group_id,
                                                           event_id=event_id)
                activity_history.save()
                delete_empty = GroupRegistrationDetail.delete_empty_group(request,group_id)
                response_data['success'] = True
                response_data['is_empty'] = delete_empty['deleted']
                response_data['message'] = "Attendee Deleted from Group Registration"
            except Exception as e:
                ErrorR.efail(e)
                response_data['success'] = False
                response_data['message'] = "Something went wrong. Please try again"
        else:
            response_data['success'] = False
            response_data['message'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def delete_empty_group(request,group_id,attendee_id=None):
        response = {}
        response['deleted'] = False
        try:
            event_id = request.session['event_auth_user']['event_id']
            admin_id = request.session['event_auth_user']['id']
            if not Attendee.objects.filter(registration_group_id=group_id).exclude(id=attendee_id).exists():
                RegistrationGroups.objects.filter(id=group_id).update(is_show=0)
                owner = RegistrationGroupOwner.objects.filter(group_id=group_id)
                if owner.exists():
                    activity_history = ActivityHistory(attendee_id=owner[0].owner_id,
                                                               admin_id=admin_id,
                                                               activity_type='delete', category='registration_group',
                                                               registration_group_id=group_id,
                                                               event_id=event_id)
                    activity_history.save()
                RegistrationGroupOwner.objects.filter(group_id=group_id).delete()
                response['deleted'] = True
        except Exception as e:
            ErrorR.efail(e)
            response['deleted'] = False
        return response