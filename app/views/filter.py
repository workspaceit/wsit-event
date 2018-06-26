import json
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.http import Http404, HttpResponseForbidden
from django.db.models import Q, Max, F

from app.views.gbhelper.filter_helper import FilterHelper
from app.views.room_view import RoomView
from .common_views import GroupView, EventView, CommonContext
from app.models import Attendee, Tag, Session, Group, RuleSet, SeminarsUsers, Answers, AttendeeTag, UsedRule, Questions, \
    Option, AttendeeGroups, Room, DeviceToken, Booking, MatchLine, SeminarSpeakers, EmailContents, MessageContents, \
    EmailReceivers, MessageReceiversHistory, AttendeeSubmitButton, RegistrationGroupOwner, RegistrationGroups, Orders, \
    CreditOrders, OrderItems
from django.db.models.aggregates import Count, Sum
from app.views.gbhelper.error_report_helper import ErrorR
import time


class FilterView(generic.DetailView):
    def get(self, request):
        return render(request, '')

    @staticmethod
    def recur_filter(request, filters, match_condition,matched_attendees=[]):
        event_id = request.session['event_auth_user']['event_id']
        return FilterHelper.get_attendee_using_filter(event_id, filters, match_condition, matched_attendees=[])
        # main_q = Q()
        # if match_condition == 1:
        #     main_q = Q(id=-11)
        # if len(matched_attendees) == 0:
        #     matched_attendees = []
        # for filter1 in filters:
        #     if isinstance(filter1[0], dict):
        #         if match_condition == '2':
        #             all_attendees_data = Attendee.objects.filter(event_id=event_id,status="registered").values('id')
        #             all_attendee_data = []
        #             for all_att in all_attendees_data:
        #                 all_attendee_data.append(all_att['id'])
        #             if len(matched_attendees) != 0:
        #                 matched_attendees = list(set(matched_attendees) & set(all_attendee_data))
        #             else:
        #                 matched_attendees = all_attendee_data
        #             single_filter = filter1[0]
        #             if single_filter['field']=='1':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     q &= Q(created__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '2':
        #                     q &= ~Q(created__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '3':
        #                     single_filter['values'][0] += ' 23:59:59'
        #                     q &= Q(created__gt=single_filter['values'][0])
        #                 if single_filter['condition'] == '4':
        #                     single_filter['values'][0] += ' 00:00:00'
        #                     q &= Q(created__lt=single_filter['values'][0])
        #                 if single_filter['condition'] == '5':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q &= Q(created__range=(earlier, now))
        #                 if single_filter['condition'] == '6':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q &= ~Q(created__range=(earlier, now))
        #                 if single_filter['condition'] == '7':
        #                     start_date = single_filter['values'][0] + ' 00:00:00'
        #                     end_date = single_filter['values'][1] + ' 23:59:59'
        #                     q &= Q(created__range=(start_date, end_date))
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='2':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     q &= Q(updated__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '2':
        #                     q &= ~Q(updated__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '3':
        #                     single_filter['values'][0] += ' 23:59:59'
        #                     q &= Q(updated__gt=single_filter['values'][0])
        #                 if single_filter['condition'] == '4':
        #                     single_filter['values'][0] += ' 00:00:00'
        #                     q &= Q(updated__lt=single_filter['values'][0])
        #                 if single_filter['condition'] == '5':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q &= Q(updated__range=(earlier, now))
        #                 if single_filter['condition'] == '6':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q &= ~Q(updated__range=(earlier, now))
        #                 if single_filter['condition'] == '7':
        #                     start_date = single_filter['values'][0] + ' 00:00:00'
        #                     end_date = single_filter['values'][1] + ' 23:59:59'
        #                     q &= Q(updated__range=(start_date, end_date))
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='3':
        #                 q = Q()
        #                 attendee_ids = AttendeeGroups.objects.filter(group_id=single_filter['values'][0]).values(
        #                     'attendee_id')
        #                 if single_filter['condition'] == '1':
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     q &= ~Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     new_attende_ids=[]
        #                     for attendee in attendee_ids:
        #                         if not AttendeeGroups.objects.filter(attendee_id=attendee['attendee_id']).exclude(group_id=single_filter['values'][0]).exists():
        #                            new_attende_ids.append(attendee['attendee_id'])
        #                     q &= Q(id__in=new_attende_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='4':
        #                 q = Q()
        #                 attendee_ids = AttendeeTag.objects.filter(tag_id=single_filter['values'][0]).values(
        #                     'attendee_id')
        #                 if single_filter['condition'] == '1':
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     q &= ~Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     new_attende_ids=[]
        #                     for attendee in attendee_ids:
        #                         if not AttendeeTag.objects.filter(attendee_id=attendee['attendee_id']).exclude(tag_id=single_filter['values'][0]).exists():
        #                            new_attende_ids.append(attendee['attendee_id'])
        #                     q &= Q(id__in=new_attende_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='6':
        #                 q = Q()
        #                 attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0]).values(
        #                     'attendee_id')
        #                 if single_filter['condition'] == '1':
        #                     attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                                                                  status='attending').values('attendee_id')
        #                     q &= Q(id__in=attending)
        #                 elif single_filter['condition'] == '2':
        #                     attending_data = SeminarsUsers.objects.filter(Q(Q(session_id=single_filter['values'][0]) & Q(Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))).values('attendee_id')
        #                     q &= ~Q(id__in=attending_data)
        #                 elif single_filter['condition'] == '3':
        #                     attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                                                                 status='in-queue').values('attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '4':
        #                     attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                                                                 status='deciding').values('attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='7':
        #                 q = Q()
        #                 attendees_matches = []
        #                 if single_filter['type'] == 'text' or single_filter['type'] == 'textarea':
        #                     if single_filter['values'][0] == '1':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__icontains=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '2':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value__icontains=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                         # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
        #                         #                                            value__icontains=single_filter['values'][
        #                         #                                                1]).values('user_id')
        #                         #
        #                         # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
        #                         #     id__in=attendees_excludes)
        #                         # q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '3':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '4':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                         # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
        #                         #                                            value=single_filter['values'][1]).values('user_id')
        #                         # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
        #                         #     id__in=attendees_excludes)
        #                         # q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '5':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__istartswith=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '6':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__iendswith=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #
        #                     elif single_filter['values'][0] == '7':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q &= ~Q(id__in=attendees_matches)
        #
        #                     elif single_filter['values'][0]=='8':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                 else:
        #                     if single_filter['values'][0] == '1':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '2':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #                         # attendees_excludes = Answers.objects.filter(
        #                         #     question_id=int(single_filter['condition']),
        #                         #     value=single_filter['values'][1]).values('user_id')
        #                         # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(id__in=attendees_excludes)
        #                         # q &= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '3':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q &= ~Q(id__in=attendees_matches)
        #                         print(q)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q &= Q(id__in=attendees_matches)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #
        #             if single_filter['field']=='8':
        #                 q = Q()
        #                 attendee_ids = DeviceToken.objects.all().values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='9':
        #                 q = Q()
        #                 if single_filter['condition']=='1':
        #                     room_id = single_filter['values'][1]
        #                     # attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
        #                     if single_filter['values'][0]=='1':
        #                         attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = Booking.objects.exclude(room_id=int(room_id)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                         # q &= ~Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='2':
        #
        #                     if single_filter['values'][0] == '1':
        #                         attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     if single_filter['values'][0] == '2':
        #                         attendees = Booking.objects.exclude(check_in__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
        #                         # q &= ~Q(id__in=attendees)
        #                     if single_filter['values'][0] == '3':
        #                         # single_filter['values'][1] += ' 23:59:59'
        #                         attendees = Booking.objects.filter(check_in__gt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '4':
        #                         # single_filter['values'][1] += ' 00:00:00'
        #                         attendees = Booking.objects.filter(check_in__lt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0]== '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     if single_filter['values'][0]== '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.exclude(check_in__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
        #                         # q &= ~Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1]
        #                         end_date = single_filter['values'][2]
        #                         attendees = Booking.objects.filter(check_in__range=(start_date, end_date)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='3':
        #
        #                     if single_filter['values'][0] == '1':
        #                         attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     if single_filter['values'][0] == '2':
        #                         attendees = Booking.objects.exclude(check_out__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
        #                         # q &= ~Q(id__in=attendees)
        #                     if single_filter['values'][0] == '3':
        #                         # single_filter['values'][1] += ' 23:59:59'
        #                         attendees = Booking.objects.filter(check_out__gt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '4':
        #                         # single_filter['values'][1] += ' 00:00:00'
        #                         attendees = Booking.objects.filter(check_out__lt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0]== '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     if single_filter['values'][0]== '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.exclude(check_out__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
        #                         # q &= ~Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1]
        #                         end_date = single_filter['values'][2]
        #                         attendees = Booking.objects.filter(check_out__range=(start_date, end_date)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='4':
        #                     room_number = single_filter['values'][1]
        #
        #                     if single_filter['values'][0]=='1':
        #                         attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = Booking.objects.exclude(room__beds=int(room_number)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
        #                         # q &= ~Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees = Booking.objects.filter(room__beds__gt=int(room_number)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees = Booking.objects.filter(room__beds__lt=int(room_number)).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='5':
        #                     if single_filter['values'][1] == '':
        #                         single_filter['values'][1] = 0
        #                     occupancy_value = int(single_filter['values'][1])
        #
        #
        #                     rooms = Room.objects.all()
        #
        #
        #                     if single_filter['values'][0]=='1':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #
        #                             if occupancy['total_occupancy'] == occupancy_value:
        #                                 selected_rooms.append(room.id)
        #                         # print("------------")
        #                         # print(selected_rooms)
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] != occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                     elif single_filter['values'][0]=='3':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] > occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #                     elif single_filter['values'][0]=='4':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] < occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q &= Q(id__in=attendees)
        #
        #
        #                 if single_filter['condition']=='6':
        #                    value = single_filter['values'][1]
        #                    attendee_ids =[]
        #                    attendees = MatchLine.objects.raw('select m.* from match_line as m where m.match_id in (select n.match_id from match_line as n group by n.match_id having COUNT(*) > 1)')
        #                    for attendee in attendees:
        #                        attendee_ids.append(attendee.booking.attendee.id)
        #
        #                    if single_filter['values'][0]=='1':
        #                       if value == '1':
        #                           q &= Q(id__in=attendee_ids)
        #                       if value == '2':
        #                           q &= ~Q(id__in=attendee_ids)
        #
        #                    elif single_filter['values'][0]=='2':
        #                       if value == '1':
        #                           q &= ~Q(id__in=attendee_ids)
        #                       if value == '2':
        #                           q &= Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='10':
        #                 q = Q()
        #                 attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='11':
        #                 q = Q()
        #                 attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],attendee_id__isnull=False).values('attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='12':
        #                 q = Q()
        #                 attendee_ids = MessageReceiversHistory.objects.filter(receiver__message_content_id=single_filter['condition'],receiver__attendee_id__isnull=False).values('receiver__attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='13':
        #                 q = Q()
        #                 if single_filter['values'][0] == '1':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
        #                    q &= Q(id__in=attendee_ids)
        #
        #                 elif single_filter['values'][0] == '2':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 elif single_filter['values'][0] == '3':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count=int(single_filter['values'][1])).values('attendee_id')
        #                    q &= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '4':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__gt=int(single_filter['values'][1])).values('attendee_id')
        #                    q &= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '5':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__lt=int(single_filter['values'][1])).values('attendee_id')
        #                    q &= Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='14':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                    attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
        #                    q &= Q(id__in=attendee_ids)
        #
        #                 elif single_filter['condition'] == '2':
        #                    attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field'] == '15':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Attendee.objects.filter(registration_group__isnull=False, event_id=event_id,
        #                                                                status="registered").values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
        #                         q &= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group__isnull=True, event_id=event_id,
        #                                                                status="registered").values('id').exclude(id__in=owner_ids)
        #                         q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values(
        #                             'owner_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values(
        #                             'owner_id')
        #                         q &= ~Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     if single_filter['values'][0] == '1':
        #                         value_checker = int(single_filter['values'][1])
        #                         if value_checker > 1:
        #                             value_checker = value_checker - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
        #                             cnt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
        #                             'owner_id')
        #                         q &= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         value_checker = int(single_filter['values'][1])
        #                         if value_checker > 1:
        #                             value_checker = value_checker - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).exclude(
        #                             cnt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
        #                             'owner_id')
        #                         q &= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '3':
        #                         value_checker = int(single_filter['values'][1]) - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
        #                             cnt__gt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
        #                             'owner_id')
        #                         q &= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '4':
        #                         value_checker = int(single_filter['values'][1])
        #                         if value_checker > 1:
        #                             value_checker = value_checker - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
        #                             cnt__lt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
        #                             'owner_id')
        #                         q &= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees, q, event_id)
        #
        #             if single_filter['field'] == '16':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(status=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(status=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(created_at__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(created_at__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '3':
        #                         single_filter['values'][1] += ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(created_at__gt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '4':
        #                         single_filter['values'][1] += ' 00:00:00'
        #                         attendee_ids = Orders.objects.filter(created_at__lt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.filter(created_at__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.exclude(created_at__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1] + ' 00:00:00'
        #                         end_date = single_filter['values'][2] + ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(created_at__range=(start_date, end_date)).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(due_date__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(due_date__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '3':
        #                         single_filter['values'][1] += ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(due_date__gt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '4':
        #                         single_filter['values'][1] += ' 00:00:00'
        #                         attendee_ids = Orders.objects.filter(due_date__lt=single_filter['values'][1]).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.filter(due_date__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.exclude(due_date__range=(earlier, now)).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1] + ' 00:00:00'
        #                         end_date = single_filter['values'][2] + ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(due_date__range=(start_date, end_date)).values('attendee_id')
        #                         q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '4':
        #                     # multiple_attendee_ids = Orders.objects.raw('SELECT o1.id,o1.attendee_id FROM orders o1 JOIN(SELECT order_number,Count(order_number) as order_number_count FROM orders GROUP BY order_number) o2 ON o1.order_number=o2.order_number where o2.order_number_count > 1')
        #                     # attendee_ids = []
        #                     # for attendee in multiple_attendee_ids:
        #                     #    attendee_ids.append(attendee.attendee.id)
        #                     # print(attendee_ids)
        #                     multiple_groups = Orders.objects.values('order_number').annotate(count=Count('order_number')).filter(count__gt=1)
        #                     multiple_groups_no = []
        #                     for order_no in multiple_groups:
        #                         multiple_groups_no.append(order_no['order_number'])
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(order_number__in=multiple_groups_no).values('attendee_id')
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(order_number__in=multiple_groups_no).values('attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '5':
        #                     attendee_ids = []
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '6':
        #                     if single_filter['values'][0]=='1':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').exclude(total_balance=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__gt=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__lt=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='5':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__range=(single_filter['values'][1],single_filter['values'][2]))
        #                         q &= Q(id__in=attendees)
        #                 elif single_filter['condition'] == '7':
        #                     if single_filter['values'][0]=='1':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').exclude(total_cost=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__gt=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__lt=single_filter['values'][1])
        #                         q &= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='5':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__range=(single_filter['values'][1],single_filter['values'][2]))
        #                         q &= Q(id__in=attendees)
        #
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #             if single_filter['field'] == '17':
        #                 q = Q()
        #                 if single_filter['values'][0] == '1':
        #                     attendee_ids = OrderItems.objects.filter(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '2':
        #                     attendee_ids = OrderItems.objects.exclude(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #                 matched_attendees = FilterView.get_matched_attendees(matched_attendees,q,event_id)
        #
        #
        #         elif match_condition == '1':
        #             single_filter = filter1[0]
        #             if single_filter['field']== '1' :
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     q |= Q(created__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '2':
        #                     q |= ~Q(created__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '3':
        #                     single_filter['values'][0] += ' 23:59:59'
        #                     q |= Q(created__gt=single_filter['values'][0])
        #                 if single_filter['condition'] == '4':
        #                     single_filter['values'][0] += ' 00:00:00'
        #                     q |= Q(created__lt=single_filter['values'][0])
        #                 if single_filter['condition'] == '5':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q |= Q(created__range=(earlier, now))
        #                 if single_filter['condition'] == '6':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q |= ~Q(created__range=(earlier, now))
        #                 if single_filter['condition'] == '7':
        #                     start_date = single_filter['values'][0] + ' 00:00:00'
        #                     end_date = single_filter['values'][1] + ' 23:59:59'
        #                     q |= Q(created__range=(start_date, end_date))
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #
        #             if single_filter['field']=='2':
        #                 # need to test again
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     q |= Q(updated__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '2':
        #                     q |= ~Q(updated__startswith=single_filter['values'][0])
        #                 if single_filter['condition'] == '3':
        #                     single_filter['values'][0] += ' 23:59:59'
        #                     q |= Q(updated__gt=single_filter['values'][0])
        #                 if single_filter['condition'] == '4':
        #                     single_filter['values'][0] += ' 00:00:00'
        #                     q |= Q(updated__lt=single_filter['values'][0])
        #                 if single_filter['condition'] == '5':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q |= Q(updated__range=(earlier, now))
        #                 if single_filter['condition'] == '6':
        #                     now = datetime.datetime.now()
        #                     if single_filter['values'][1] == "1":
        #                         days_to_go = int(single_filter['values'][0]) * 1
        #                     elif single_filter['values'][1] == "2":
        #                         days_to_go = int(single_filter['values'][0]) * 7
        #                     elif single_filter['values'][1] == "3":
        #                         days_to_go = int(single_filter['values'][0]) * 30
        #                     earlier = now - datetime.timedelta(days_to_go)
        #                     q |= ~Q(updated__range=(earlier, now))
        #                 if single_filter['condition'] == '7':
        #                     start_date = single_filter['values'][0] + ' 00:00:00'
        #                     end_date = single_filter['values'][1] + ' 23:59:59'
        #                     q |= Q(updated__range=(start_date, end_date))
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='3':
        #                 q = Q()
        #                 attendee_ids = AttendeeGroups.objects.filter(group_id=single_filter['values'][0]).values(
        #                     'attendee_id')
        #                 if single_filter['condition'] == '1':
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     q |= ~Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     new_attende_ids=[]
        #                     for attendee in attendee_ids:
        #                         if not AttendeeGroups.objects.filter(attendee_id=attendee['attendee_id']).exclude(group_id=single_filter['values'][0]).exists():
        #                            new_attende_ids.append(attendee['attendee_id'])
        #                     q |= Q(id__in=new_attende_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='4':
        #                 q = Q()
        #                 attendee_ids = AttendeeTag.objects.filter(tag_id=single_filter['values'][0]).values(
        #                     'attendee_id')
        #                 if single_filter['condition'] == '1':
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     q |= ~Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     new_attende_ids=[]
        #                     for attendee in attendee_ids:
        #                         if not AttendeeTag.objects.filter(attendee_id=attendee['attendee_id']).exclude(tag_id=single_filter['values'][0]).exists():
        #                            new_attende_ids.append(attendee['attendee_id'])
        #                     q |= Q(id__in=new_attende_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='6':
        #                 q = Q()
        #                 attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0]).values(
        #                     'attendee_id')
        #                 if single_filter['condition'] == '1':
        #                     attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                                                                  status='attending').values('attendee_id')
        #                     q |= Q(id__in=attending)
        #                     # q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     # not_attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                     #                                              status='not-attending').values('attendee_id')
        #                     attending_data = SeminarsUsers.objects.filter(Q(Q(session_id=single_filter['values'][0]) & Q(Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))).values('attendee_id')
        #                     # not_attending = Attendee.objects.values('id').exclude(id__in=attending_data)
        #                     # all_not_attending = attendee_ids | not_attending
        #                     q |= ~Q(id__in=attending_data)
        #                 elif single_filter['condition'] == '3':
        #                     attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                                                                 status='in-queue').values('attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '4':
        #                     attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
        #                                                                 status='deciding').values('attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='7':
        #                 q = Q()
        #                 if single_filter['type'] == 'text' or single_filter['type'] == 'textarea':
        #                     if single_filter['values'][0] == '1':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__icontains=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '2':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value__icontains=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                         # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
        #                         #                                             value__icontains=single_filter['values'][
        #                         #                                                 1]).values('user_id')
        #                         #
        #                         # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
        #                         #     id__in=attendees_excludes)
        #                         # q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '3':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '4':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                         # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
        #                         #                                             value=single_filter['values'][1]).values(
        #                         #     'user_id')
        #                         # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
        #                         #     id__in=attendees_excludes)
        #                         # q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '5':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__istartswith=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '6':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__iendswith=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0]=='7':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q |= ~Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0]=='8':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                 else:
        #                     if single_filter['values'][0] == '1':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
        #                                                                    value=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0] == '2':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #                         # attendees_excludes = Answers.objects.filter(
        #                         #     question_id=int(single_filter['condition']),
        #                         #     value=single_filter['values'][1]).values('user_id')
        #                         # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
        #                         #     id__in=attendees_excludes)
        #                         # q |= Q(id__in=attendees_matches)
        #
        #
        #                         # attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
        #                         # q |= Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q |= ~Q(id__in=attendees_matches)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
        #                         q |= Q(id__in=attendees_matches)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='8':
        #                 q = Q()
        #                 attendee_ids = DeviceToken.objects.all().values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='9':
        #                 q = Q()
        #                 if single_filter['condition']=='1':
        #                     room_id = single_filter['values'][1]
        #                     # attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
        #                     if single_filter['values'][0]=='1':
        #                         attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = Booking.objects.exclude(room_id=int(room_id)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                         # q |= ~Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='2':
        #
        #                     if single_filter['values'][0] == '1':
        #                         attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     if single_filter['values'][0] == '2':
        #                         attendees = Booking.objects.exclude(check_in__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
        #                         # q |= ~Q(id__in=attendees)
        #                     if single_filter['values'][0] == '3':
        #                         # single_filter['values'][1] += ' 23:59:59'
        #                         attendees = Booking.objects.filter(check_in__gt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '4':
        #                         # single_filter['values'][1] += ' 00:00:00'
        #                         attendees = Booking.objects.filter(check_in__lt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0]== '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     if single_filter['values'][0]== '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.exclude(check_in__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
        #                         # q |= ~Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '7':
        #                         # start_date = single_filter['values'][1] + ' 00:00:00'
        #                         # end_date = single_filter['values'][2] + ' 23:59:59'
        #                         # change
        #                         start_date = single_filter['values'][1]
        #                         end_date = single_filter['values'][2]
        #                         attendees = Booking.objects.filter(check_in__range=(start_date, end_date)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='3':
        #
        #                     if single_filter['values'][0] == '1':
        #                         attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     if single_filter['values'][0] == '2':
        #                         attendees = Booking.objects.exclude(check_out__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
        #                         # q |= ~Q(id__in=attendees)
        #                     if single_filter['values'][0] == '3':
        #                         # single_filter['values'][1] += ' 23:59:59'
        #                         attendees = Booking.objects.filter(check_out__gt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '4':
        #                         # single_filter['values'][1] += ' 00:00:00'
        #                         attendees = Booking.objects.filter(check_out__lt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                     if single_filter['values'][0]== '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     if single_filter['values'][0]== '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendees = Booking.objects.exclude(check_out__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
        #                         # q |= ~Q(id__in=attendees)
        #
        #                     if single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1]
        #                         end_date = single_filter['values'][2]
        #                         attendees = Booking.objects.filter(check_out__range=(start_date, end_date)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='4':
        #                     room_number = single_filter['values'][1]
        #
        #                     if single_filter['values'][0]=='1':
        #                         attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = Booking.objects.exclude(room__beds=int(room_number)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                         # attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
        #                         # q |= ~Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees = Booking.objects.filter(room__beds__gt=int(room_number)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees = Booking.objects.filter(room__beds__lt=int(room_number)).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='5':
        #                     if single_filter['values'][1] == '':
        #                         single_filter['values'][1] = 0
        #                     occupancy_value = int(single_filter['values'][1])
        #
        #                     rooms = Room.objects.all()
        #
        #
        #                     if single_filter['values'][0]=='1':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] == occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] != occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                     elif single_filter['values'][0]=='3':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] > occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                     elif single_filter['values'][0]=='4':
        #                         selected_rooms=[]
        #                         for room in rooms:
        #                             occupancy = RoomView.find_booking(str(room.id))
        #                             if occupancy['total_occupancy'] < occupancy_value:
        #                                 selected_rooms.append(room.id)
        #
        #
        #                         attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
        #                         q |= Q(id__in=attendees)
        #
        #                 if single_filter['condition']=='6':
        #                    value = single_filter['values'][1]
        #                    attendee_ids =[]
        #                    attendees = MatchLine.objects.raw('select m.* from match_line as m where m.match_id in (select n.match_id from match_line as n group by n.match_id having COUNT(*) > 1)')
        #                    for attendee in attendees:
        #                        attendee_ids.append(attendee.booking.attendee.id)
        #
        #                    if single_filter['values'][0]=='1':
        #                       if value == '1':
        #                           q |= Q(id__in=attendee_ids)
        #                       if value == '2':
        #                           q |= ~Q(id__in=attendee_ids)
        #
        #                    elif single_filter['values'][0]=='2':
        #                       if value == '1':
        #                           q |= ~Q(id__in=attendee_ids)
        #                       if value == '2':
        #                           q |= Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='10':
        #                 q = Q()
        #                 attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='11':
        #                 q = Q()
        #                 attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],attendee_id__isnull=False).values('attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='12':
        #                 q = Q()
        #                 attendee_ids = MessageReceiversHistory.objects.filter(receiver__message_content_id=single_filter['condition'],receiver__attendee_id__isnull=False).values('receiver__attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='13':
        #                 q = Q()
        #                 if single_filter['values'][0] == '1':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
        #                    q |= Q(id__in=attendee_ids)
        #
        #                 elif single_filter['values'][0] == '2':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 elif single_filter['values'][0] == '3':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count=int(single_filter['values'][1])).values('attendee_id')
        #                    q |= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '4':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__gt=int(single_filter['values'][1])).values('attendee_id')
        #                    q |= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '5':
        #                    attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__lt=int(single_filter['values'][1])).values('attendee_id')
        #                    q |= Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='14':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                    attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
        #                    q |= Q(id__in=attendee_ids)
        #
        #                 elif single_filter['condition'] == '2':
        #                    attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field'] == '15':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Attendee.objects.filter(registration_group__isnull=False, event_id=event_id, status="registered").values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
        #                         q |= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group__isnull=True, event_id=event_id, status="registered").values('id').exclude(id__in=owner_ids)
        #                         q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values('owner_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values('owner_id')
        #                         q |= ~Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     if single_filter['values'][0] == '1':
        #                         value_checker = int(single_filter['values'][1])
        #                         if value_checker>1:
        #                             value_checker = value_checker - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15,registration_group__isnull=False).values('registration_group_id').annotate(cnt=Count('registration_group_id')).filter(cnt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values('owner_id')
        #                         q |= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         value_checker = int(single_filter['values'][1])
        #                         if value_checker > 1:
        #                             value_checker = value_checker - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).exclude(
        #                             cnt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values('owner_id')
        #                         q |= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '3':
        #                         value_checker = int(single_filter['values'][1]) - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
        #                             cnt__gt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
        #                             'owner_id')
        #                         q |= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #                     elif single_filter['values'][0] == '4':
        #                         value_checker = int(single_filter['values'][1])
        #                         if value_checker > 1:
        #                             value_checker = value_checker - 1
        #                         groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
        #                             'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
        #                             cnt__lt=value_checker).values('registration_group_id')
        #                         attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
        #                         owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
        #                             'owner_id')
        #                         q |= Q(id__in=attendee_ids)
        #                         q |= Q(id__in=owner_ids)
        #
        #
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees, q, event_id)
        #
        #             if single_filter['field'] == '16':
        #                 q = Q()
        #                 if single_filter['condition'] == '1':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(status=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(status=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '2':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(created_at__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(created_at__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '3':
        #                         single_filter['values'][1] += ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(created_at__gt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '4':
        #                         single_filter['values'][1] += ' 00:00:00'
        #                         attendee_ids = Orders.objects.filter(created_at__lt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.filter(created_at__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.exclude(created_at__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1] + ' 00:00:00'
        #                         end_date = single_filter['values'][2] + ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(created_at__range=(start_date, end_date)).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '3':
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(due_date__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(due_date__startswith=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '3':
        #                         single_filter['values'][1] += ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(due_date__gt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '4':
        #                         single_filter['values'][1] += ' 00:00:00'
        #                         attendee_ids = Orders.objects.filter(due_date__lt=single_filter['values'][1]).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '5':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.filter(due_date__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '6':
        #                         now = datetime.datetime.now()
        #                         if single_filter['values'][2] == "1":
        #                             days_to_go = int(single_filter['values'][1]) * 1
        #                         elif single_filter['values'][2] == "2":
        #                             days_to_go = int(single_filter['values'][1]) * 7
        #                         elif single_filter['values'][2] == "3":
        #                             days_to_go = int(single_filter['values'][1]) * 30
        #                         earlier = now - datetime.timedelta(days_to_go)
        #                         attendee_ids = Orders.objects.exclude(due_date__range=(earlier, now)).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                     elif single_filter['values'][0] == '7':
        #                         start_date = single_filter['values'][1] + ' 00:00:00'
        #                         end_date = single_filter['values'][2] + ' 23:59:59'
        #                         attendee_ids = Orders.objects.filter(due_date__range=(start_date, end_date)).values('attendee_id')
        #                         q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '4':
        #                     # multiple_attendee_ids = Orders.objects.raw('SELECT o1.id,o1.attendee_id FROM orders o1 JOIN(SELECT order_number,Count(order_number) as order_number_count FROM orders GROUP BY order_number) o2 ON o1.order_number=o2.order_number where o2.order_number_count > 1')
        #                     # attendee_ids = []
        #                     # for attendee in multiple_attendee_ids:
        #                     #    attendee_ids.append(attendee.attendee.id)
        #                     # print(attendee_ids)
        #                     multiple_groups = Orders.objects.values('order_number').annotate(count=Count('order_number')).filter(count__gt=1)
        #                     multiple_groups_no = []
        #                     for order_no in multiple_groups:
        #                         multiple_groups_no.append(order_no['order_number'])
        #                     if single_filter['values'][0] == '1':
        #                         attendee_ids = Orders.objects.filter(order_number__in=multiple_groups_no).values('attendee_id')
        #                     elif single_filter['values'][0] == '2':
        #                         attendee_ids = Orders.objects.exclude(order_number__in=multiple_groups_no).values('attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '5':
        #                     attendee_ids = []
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['condition'] == '6':
        #                     if single_filter['values'][0]=='1':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').exclude(total_balance=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__gt=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__lt=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='5':
        #                         attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__range=(single_filter['values'][1],single_filter['values'][2]))
        #                         q |= Q(id__in=attendees)
        #                 elif single_filter['condition'] == '7':
        #                     if single_filter['values'][0]=='1':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='2':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').exclude(total_cost=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='3':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__gt=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='4':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__lt=single_filter['values'][1])
        #                         q |= Q(id__in=attendees)
        #                     elif single_filter['values'][0]=='5':
        #                         attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__range=(single_filter['values'][1],single_filter['values'][2]))
        #                         q |= Q(id__in=attendees)
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #             if single_filter['field'] == '17':
        #                 q = Q()
        #                 if single_filter['values'][0] == '1':
        #                     attendee_ids = OrderItems.objects.filter(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '2':
        #                     attendee_ids = OrderItems.objects.exclude(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #                 matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #     else:
        #         match_condition_inner = filter1[0][0]['matchFor']
        #         if match_condition == '2':
        #             main_q = Q()
        #             total_matched_attendees = FilterView.recur_filter(request, filter1, match_condition_inner)
        #             main_q &= Q(id__in=total_matched_attendees)
        #             matched_attendees = FilterView.get_matched_attendees(matched_attendees,main_q,event_id)
        #             # main_q &= Q(id__in=FilterView.recur_filter(request, filter1, match_condition_inner))
        #         elif match_condition == '1':
        #             main_q = Q(id=-11)
        #             total_matched_attendees = FilterView.recur_filter(request, filter1, match_condition_inner,matched_attendees)
        #             main_q |= Q(id__in=total_matched_attendees)
        #             matched_attendees = FilterView.get_all_matched_attendees(matched_attendees,main_q,event_id)
        #             # main_q |= Q(id__in=FilterView.recur_filter(request, filter1, match_condition_inner))
        # main_q &= Q(event_id=event_id)
        # main_q &= Q(id__in=matched_attendees)
        #
        # total_attendees = Attendee.objects.filter(main_q).values('id')
        # all_attendess = []
        # for att in total_attendees:
        #     all_attendess.append(att['id'])
        # return all_attendess


    def get_filtered_attendees(request, rule_id):
        start_time = time.time()
        attendees=[]
        try:
            rule = RuleSet.objects.get(id=rule_id)
            if rule:
                filters = json.loads(rule.preset)
                q = Q()
                if filters:
                    match_condition = '0'
                    if 'matchFor' in filters[0][0]:
                        match_condition = filters[0][0]['matchFor']
                    elif rule.matchfor:
                        match_condition = rule.matchfor

                    if match_condition == '2':
                        q &= Q(id__in=FilterView.recur_filter(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        q |= Q(id__in=FilterView.recur_filter(request, filters, match_condition))
                    else:
                        q = Q(id=-11)
                    attendees = Attendee.objects.filter(q)
                    # ErrorR.okblue(attendees.query)
                    if rule.is_limit:
                        limit = 0
                        if rule.limit_amount>0:
                            limit=rule.limit_amount
                        import itertools
                        top5 = itertools.islice(attendees, limit)
                        return list(top5)
        except Exception as e:
            ErrorR.efail(e)
            print(len(attendees))
        ErrorR.warn(time.time() - start_time)
        return attendees


    def get_filtered_attendees_count(request, rule_id):
        # attendees=[]
        # try:
        #     rule = RuleSet.objects.get(id=rule_id)
        #     if rule:
        #         filters = json.loads(rule.preset)
        #         q = Q()
        #         if filters:
        #             if 'matchFor' in filters[0][0]:
        #                 match_condition = filters[0][0]['matchFor']
        #             elif rule.matchfor:
        #                 match_condition = rule.matchfor
        #             if match_condition == '2':
        #                 q &= Q(id__in=FilterView.recur_filter(request, filters, match_condition))
        #                 # q &= FilterView.recur_filter(request, filters, match_condition)
        #             elif match_condition == '1':
        #                 q = Q(id=-11)
        #                 q |= Q(id__in=FilterView.recur_filter(request, filters, match_condition))
        #             attendees = Attendee.objects.filter(q)
        #             if rule.is_limit:
        #                 limit = 0
        #                 if rule.limit_amount>0:
        #                     limit=rule.limit_amount
        #                 import itertools
        #                 top5 = itertools.islice(attendees, limit)
        #                 return list(top5)
        # except Exception as e:
        #     ErrorR.efail(e)
        return len(FilterView.get_filtered_attendees(request, rule_id))

    # def get_matched_attendees(matched_attendees,q,event_id):
    #     attendees = Attendee.objects.filter(q).filter(event_id=event_id).values('id')
    #     attendees_array = []
    #     for attendee in attendees:
    #         attendees_array.append(attendee['id'])
    #     # if len(matched_attendees) > 0 and len(attendees_array) > 0:
    #     matched_attendees = list(set(matched_attendees) & set(attendees_array))
    #     # elif len(matched_attendees) == 0:
    #     #     matched_attendees = attendees_array
    #     return matched_attendees
    #
    # def get_all_matched_attendees(matched_attendees,q,event_id):
    #     attendees = Attendee.objects.filter(q).filter(event_id=event_id).values('id')
    #     attendees_array = []
    #     for attendee in attendees:
    #         attendees_array.append(attendee['id'])
    #     # if len(matched_attendees) > 0 and len(attendees_array) > 0:
    #     matched_attendees = list(set(matched_attendees) | set(attendees_array))
    #     # elif len(matched_attendees) == 0:
    #     #     matched_attendees = list(set(matched_attendees + attendees_array))
    #         # matched_attendees = attendees_array
    #     return matched_attendees


    def post(self, request):
        response_data = {}
        filters = json.loads(request.POST.get('filters'))
        rule = request.POST.get('rule_id')
        if rule != '':
            if not (UsedRule.objects.filter(rule_id=rule, user_id=request.session['event_auth_user']['id']).exists()):
                used_rule = UsedRule(rule_id=rule, user_id=request.session['event_auth_user']['id'])
                used_rule.save()
                total_used = UsedRule.objects.filter(user_id=request.session['event_auth_user']['id'])
                if total_used.count() > 3:
                    total_used[0].delete()

        results = FilterView.get_filtered_attendees(request,rule)
        #cubjub need to add limit

        attendee_list = []
        for result in results:
            attendee_list.append(result.as_dict())
        response_data['success'] = 'Filtered'
        response_data['attendees'] = attendee_list
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_filter(request):
        response_data = {}
        if EventView.check_permissions(request, 'filter_permission'):
            filters = request.POST.get('filters')
            preset_name = request.POST.get('preset_name')

            is_limit = False
            if request.POST.get('is_limit')=="1":
                is_limit = True
            limit_amount = request.POST.get('limit_amount')
            main_matchfor = request.POST.get('matchfor')
            # today_date = datetime.now()
            # today_time = today_date.timetuple()
            # today = int(time.mktime(today_time))
            # preset_name = "preset_"+str(today)
            form_data = {
                'name': preset_name,
                'preset': filters,
                'is_limit': is_limit,
                'limit_amount': limit_amount,
                'created_by_id': request.session['event_auth_user']['id']
            }
            if main_matchfor:
                form_data['matchfor'] = main_matchfor
            if 'id' in request.POST:
                group_id = request.POST.get('group_id')
                form_data['group_id' ]= group_id
                rule_id = request.POST.get('id')
                old_filter = RuleSet.objects.get(id=rule_id)
                if old_filter.name == 'quick-filter':
                    form_data['name'] = 'quick-filter'
                if not (RuleSet.objects.filter(name=preset_name,group__event_id=request.session['event_auth_user']['event_id']).exclude(id=rule_id).exists()):
                    RuleSet.objects.filter(id=rule_id).update(**form_data)
                    filter = RuleSet.objects.get(id=rule_id)
                    response_data['filter'] = filter.as_dict()
                    response_data['success'] = 'Attendee Filter Successfully Updated'
                else:
                    response_data['error'] = 'Filter Name Already Exist'
            else:
                event_id=request.session['event_auth_user']['event_id']
                if preset_name == 'quick-filter':
                   type = request.POST.get('type')
                   quick_filter_group = Group.objects.filter(name='temporary-filter',event_id=event_id)

                   if not type:
                       old_filter= RuleSet.objects.filter(name=preset_name,created_by_id=request.session['event_auth_user']['id'],group__event_id=event_id)

                       if old_filter.exists():
                           RuleSet.objects.filter(id=old_filter[0].id).update(**form_data)
                           response_data['success'] = 'Quick Filter Successfully updated'
                           response_data['quick_filter'] = old_filter[0].as_dict()
                       else :
                           if quick_filter_group.exists():
                               form_data['group_id']=quick_filter_group[0].id
                               filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                               form_data["rule_order"] = filter_order
                               quick_filter = RuleSet(**form_data)
                               quick_filter.save()
                               response_data['success'] = 'Quick Filter Successfully saved'
                               response_data['quick_filter'] = quick_filter.as_dict()
                           else:
                               response_data['error'] = 'Quick Filter group not availables'
                   else:
                       if type=="menu":
                          menu_filter = RuleSet.objects.filter(name__contains='menu-filter', group__event_id=event_id).order_by('-id')[:1]
                          if menu_filter.exists():
                             filer_count =  menu_filter[0].name.split("-")[2]
                             new_filter_num = int(filer_count)+1
                             new_filter_name = "menu-filter-"+str(new_filter_num)
                             form_data['name']=new_filter_name
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                          else:
                             form_data['name']="menu-filter-1"
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                       if type=="export":
                          menu_filter = RuleSet.objects.filter(name__contains='export-filter', group__event_id=event_id).order_by('-id')[:1]
                          if menu_filter.exists():
                             filer_count =  menu_filter[0].name.split("-")[2]
                             new_filter_num = int(filer_count)+1
                             new_filter_name = "export-filter-"+str(new_filter_num)
                             form_data['name']=new_filter_name
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                          else:
                             form_data['name']="export-filter-1"
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                       if type=="page":
                         page_filter = RuleSet.objects.filter(name__contains='page-filter', group__event_id=event_id).order_by('-id')[:1]
                         if page_filter.exists():
                            filer_count =  page_filter[0].name.split("-")[2]
                            new_filter_num = int(filer_count)+1
                            new_filter_name = "page-filter-"+str(new_filter_num)
                            form_data['name']=new_filter_name
                            form_data['group_id']=quick_filter_group[0].id
                            filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                            form_data["rule_order"] = filter_order
                            quick_filter = RuleSet(**form_data)
                            quick_filter.save()
                            response_data['success'] = 'Quick Filter Successfully saved'
                            response_data['quick_filter'] = quick_filter.as_dict()

                         else:
                            form_data['name']="page-filter-1"
                            form_data['group_id']=quick_filter_group[0].id
                            filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                            form_data["rule_order"] = filter_order
                            quick_filter = RuleSet(**form_data)
                            quick_filter.save()
                            response_data['success'] = 'Quick Filter Successfully saved'
                            response_data['quick_filter'] = quick_filter.as_dict()





                else:
                    group_id = request.POST.get('group_id')
                    form_data['group_id' ]= group_id
                    filter_order = FilterView.get_filters_order(group_id)
                    form_data["rule_order"] = filter_order
                    if not (RuleSet.objects.filter(name=preset_name, group__event_id=event_id).exists()):
                        rule_set = RuleSet(**form_data)
                        rule_set.save()
                        response_data['filter'] = rule_set.as_dict()
                        response_data['success'] = 'Attendee Filter Successfully Saved'
                    else:
                        response_data['error'] = 'Filter Name Already Exist'



        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_filter(request):
        user_id = request.session['event_auth_user']['id']
        user_rules = RuleSet.objects.filter(created_by_id=user_id)
        context = {
            'user_rules': user_rules
        }
        return render(request, 'attendee/filter_set.html', context)

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'filter_permission'):
            id = request.POST.get('id')
            filter = RuleSet.objects.get(id=id)
            if filter.name == 'quick-filter':
                response_data['warning'] = "You can't delete the Quick Filter"
            else:
                rule = RuleSet.objects.get(id=id)
                rule.delete()
                response_data['success'] = 'Filter Preset Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def filters(request):
        if EventView.check_read_permissions(request, 'filter_permission'):
            # session_groups = GroupView.get_sessionGroup(request)
            # for group in session_groups:
            #     group.sessions = Session.objects.filter(group_id=group.id)
            # tags = Tag.objects.all()
            # attendee_groups = GroupView.get_attendeeGroup(request)
            # filterGroup = GroupView.get_filterGroup(request)
            # for group in filterGroup:
            #     group.filters = RuleSet.objects.filter(group_id=group.id).order_by('rule_order').exclude(name='quick-filter')
            # question_groups = GroupView.get_questionGroup(request)
            # for question_group in question_groups:
            #     question_group.questions = Questions.objects.filter(group_id=question_group.id)
            #     for question in question_group.questions:
            #         if question.type != 'text' and question.type != 'textarea':
            #             question.options = Option.objects.filter(question_id=question.id)
            #
            # hotelGroup = GroupView.get_hotelGroup(request)
            # for group in hotelGroup:
            #     group.slugName = group.name.replace(" ", "_")
            #     group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id).order_by(
            #         'room_order')
            #
            # event_id = request.session['event_auth_user']['event_id']
            # emails = EmailContents.objects.filter(template__event_id=event_id, is_show=1)
            # messages = MessageContents.objects.filter(event_id=event_id, is_show=1)
            # context = {
            #     'filterGroup': filterGroup,
            #     'session_groups': session_groups,
            #     'tags': tags,
            #     'attendee_groups': attendee_groups,
            #     'question_groups': question_groups,
            #     'hotelGroups':hotelGroup,
            #     'emails':emails,
            #     "messages": messages
            # }
            context = {}
            filter_context= CommonContext.get_filter_context(request)
            context.update(filter_context)
            return render(request, 'filter/filter.html', context)

    def search(request):
        search_key = request.POST.get('search_key')
        all_filters_groups = []
        if search_key:
            filters_group = Group.objects.filter(
                Q(type="filter", is_show=1, event_id=request.session['event_auth_user']['event_id']) & (Q(ruleset__name__icontains=search_key))).order_by(
                'group_order').distinct()
        else:
            filters_group = Group.objects.filter(Q(type="filter", is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by('group_order').distinct()
        for group in filters_group:
            group.filters = RuleSet.objects.filter(Q(group_id=group.id) & Q(name__icontains=search_key)).order_by('rule_order')
            group_dict = dict(
                id=group.id,
                name=group.name,
                filters=group.filters
            )
            all_filters_groups.append(group_dict)
        data = {
            'filterGroup': all_filters_groups
        }
        return render(request, 'filter/filter_result.html', data)

    def filter_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        if EventView.check_permissions(request, 'filter_permission'):
            filter_id = request.POST.get('filter_id')
            filter = RuleSet.objects.get(id=filter_id)

            duplicate_existance = RuleSet.objects.filter(name=filter.name + '[Copy]', group__event_id=event_id)
            if duplicate_existance.exists():
                response_data['error'] = 'This export is already make a duplicate.'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            filter.pk = None
            # if '[Copy]' not in session.name:
            filter.name += '[Copy]'
            filter.created_by_id=request.session['event_auth_user']['id']
            filter.save()
            response_data['success'] = "Create duplicate filter Successfully"
            response_data['filter'] = filter.as_dict()
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def set_filters_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'filter_permission'):
            filters_order = json.loads(request.POST.get('filters_order'))
            for filter in filters_order:
                RuleSet.objects.filter(id=filter['filter_id']).update(rule_order=filter['order'])
            response_data['success'] = 'Filters Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def quick_filter_exists(request):
        event_id=request.session['event_auth_user']['event_id']
        admin_id=request.session['event_auth_user']['id']
        response_data ={}
        quick_filter = RuleSet.objects.filter(name='quick-filter',created_by_id=admin_id,group__event_id=event_id)
        if quick_filter.exists():
            response_data['status']= True
            response_data['filter']=quick_filter[0].as_dict()
        else:
            response_data['status']= False

        return HttpResponse(json.dumps(response_data),content_type="application/json")



    def get_filters_order(group_id):
        filter = RuleSet.objects.values('rule_order').filter(group_id = group_id).aggregate(Max('rule_order'))
        if filter['rule_order__max']:
             rule_order = filter['rule_order__max'] + 1
        else:
            rule_order = 1
        return rule_order


class FilterDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return RuleSet.objects.get(pk=pk)
        except RuleSet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        rule = self.get_object(pk)
        response = {
            'success': True,
            'rule': rule.as_dict()
        }
        return HttpResponse(json.dumps(response), content_type='application/json')
