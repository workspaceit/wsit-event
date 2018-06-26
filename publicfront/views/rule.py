from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from app.models import Attendee, SeminarsUsers, Answers, RuleSet, MenuPermission, AttendeeGroups, AttendeeTag, \
    DeviceToken, Booking, \
    Room, \
    MatchLine, PagePermission, SeminarSpeakers, EmailReceivers, MessageReceiversHistory, AttendeeSubmitButton, \
    RegistrationGroupOwner, Orders, CreditOrders, OrderItems
import json

from app.views.gbhelper.filter_helper import FilterHelper
from app.views.room_view import RoomView
import datetime
from django.db.models import Q, F
from django.db import connection
import math
from django.db.models.aggregates import Count, Sum
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.helper import HelperData


class UserRule(generic.TemplateView):
    def get_menu_permissions(request):
        ErrorR.ex_time_init()
        my_rule_set = []
        # today_date = datetime.datetime.now()
        today_date= HelperData.getTimezoneNow(request)
        menu_permissions = []
        from django.db.models import Count, Max
        event_id = request.session['event_id']
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            ErrorR.ex_time_init()
            menus_with_rule = MenuPermission.objects.filter(menu__event_id=event_id, menu__is_visible=1,
                menu__start_time__lt=today_date, menu__end_time__gt=today_date).values('rule_id').exclude(rule_id=None)
            rule_list = []
            for menu_rules in menus_with_rule:
                if menu_rules['rule_id'] not in rule_list:
                    rule_list.append(menu_rules['rule_id'])
            # Need to get the rules using menupermission table
            rule_sets = RuleSet.objects.filter(group__event_id=event_id, id__in=rule_list)
            for rule in rule_sets:
                try:
                    filters = json.loads(rule.preset)
                    q = Q()
                    match_condition = '0'
                    if 'matchFor' in filters[0][0]:
                        match_condition = filters[0][0]['matchFor']
                    elif rule.matchfor:
                        match_condition = rule.matchfor
                    if match_condition == '2':
                        # q &= UserRule.get_filtered_attendee(request, filters, match_condition)
                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        # q |= UserRule.get_filtered_attendee(request, filters, match_condition)
                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    else:
                        q = Q(id=-11)
                    attendees = Attendee.objects.filter(q)

                    if attendees.filter(id=attendee_id).count() > 0:
                        my_rule_set.append(rule.id)
                except Exception as e:
                    print(e)
                    pass
            ErrorR.ex_time()

            m_permissions = MenuPermission.objects.filter(
                (Q(rule_id__in=my_rule_set) | Q(rule_id=None)),
                menu__event_id=event_id, menu__level=1, menu__is_visible=1,
                menu__start_time__lt=today_date, menu__end_time__gt=today_date).values('menu_id').annotate(
                id=Max('id')).order_by('menu__rank')
            menu_permissions = []
            for m in m_permissions:
                menu_permissions.extend(MenuPermission.objects.filter(id=m['id']))
        else:
            m_permissions = MenuPermission.objects.filter(menu__allow_unregistered=True, menu__event_id=event_id,
                                                          menu__level=1, menu__is_visible=1,
                                                          menu__start_time__lt=today_date,
                                                          menu__end_time__gt=today_date).values('menu_id').annotate(
                id=Max('id')).order_by('menu__rank')

            menu_permissions = []
            for m in m_permissions:
                menu_permissions.extend(MenuPermission.objects.filter(id=m['id']))
        ErrorR.ex_time()
        context = {
            'my_rule_set': my_rule_set,
            'menu_permissions': menu_permissions
        }
        return context

    def get_page_permissions(request):
        my_rule_set = []
        today_date = datetime.datetime.now()
        page_permissions = []
        from django.db.models import Count, Max
        event_id = request.session['event_id']
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            rule_sets = RuleSet.objects.filter(group__event_id=event_id)
            for rule in rule_sets:
                filters = json.loads(rule.preset)
                q = Q()
                match_condition = '0'
                if 'matchFor' in filters[0][0]:
                    match_condition = filters[0][0]['matchFor']
                elif rule.matchfor:
                    match_condition = rule.matchfor
                if match_condition == '2':
                    q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                elif match_condition == '1':
                    q = Q(id=-11)
                    q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                else:
                    q = Q(id=-11)
                attendees = Attendee.objects.filter(q)

                if attendees.filter(id=attendee_id).count() > 0:
                    my_rule_set.append(rule.id)

            m_permissions = PagePermission.objects.filter(
                (Q(rule_id__in=my_rule_set) | Q(rule_id=None)),
                page__event_id=event_id, page__level=1, page__is_visible=1,
                page__start_time__lt=today_date, page__end_time__gt=today_date).values('page_id').annotate(id=Max('id'))
            page_permissions = []
            for m in m_permissions:
                page_permissions.extend(PagePermission.objects.filter(id=m['id']))
        else:
            m_permissions = PagePermission.objects.filter(page__allow_unregistered=True, page__event_id=event_id,
                                                          page__level=1, page__is_visible=1,
                                                          page__start_time__lt=today_date,
                                                          page__end_time__gt=today_date).values('page_id').annotate(
                id=Max('id'))

            page_permissions = []
            for m in m_permissions:
                page_permissions.extend(PagePermission.objects.filter(id=m['id']))

        return page_permissions

    def find_booking(room_id):
        room = Room.objects.get(id=room_id)
        qry = 'SELECT room_allotments.*, count(bookings.id) as booking FROM room_allotments left outer join bookings on room_allotments.room_id=bookings.room_id and room_allotments.available_date between bookings.check_in and bookings.check_out WHERE room_allotments.room_id=' + room_id + ' group by room_allotments.id'
        cursor = connection.cursor()

        cursor.execute(qry)
        rows = cursor.fetchall()

        result = []
        total_stay = 0
        total_allotments = 0
        for row in rows:
            res = {}
            res['id'] = row[0]
            res['allotments'] = row[1]
            res['available_date'] = str(row[2])
            res['room_id'] = row[3]
            res['booking'] = math.ceil(row[6] / room.beds)
            matched_attendee = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                count_match__gt=1, match__room_id=room_id)
            count_matched_pairs = matched_attendee.filter(match__start_date__lte=res['available_date'],
                                                          match__end_date__gt=res['available_date']).count()
            res['matched_pairs'] = count_matched_pairs
            match_id = []
            if matched_attendee.count() > 0:
                for match in matched_attendee:
                    match_id.append(match['match_id'])
            count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                match_id__in=match_id, booking__check_in__lte=res['available_date'],
                booking__check_out__gt=res['available_date']).exclude(match__start_date__lte=res['available_date'],
                                                                      match__end_date__gt=res['available_date']).count()
            res['matched_singles'] = count_matched_singles
            matched_booking = []
            booking_matched = MatchLine.objects.filter(match_id__in=match_id)
            if booking_matched.exists():
                for booking in booking_matched:
                    matched_booking.append(booking.booking_id)
            count_unmatched_attendee = Booking.objects.filter(room_id=room_id, check_in__lte=res['available_date'],
                                                              check_out__gt=res['available_date']).exclude(
                id__in=matched_booking).count()
            res['unmatched'] = count_unmatched_attendee
            total = count_matched_pairs + count_matched_singles + count_unmatched_attendee
            res['total'] = total
            best_scenario = count_matched_pairs + count_matched_singles + math.ceil(
                count_unmatched_attendee / room.beds)
            res['best_scenario'] = best_scenario
            res['free'] = row[1] - res['total']
            if res['free'] < 0:
                res['free'] = 0
            if res['allotments'] > 0:
                res['occupancy'] = math.ceil(res['total'] / res['allotments'] * 100)
            else:
                res['occupancy'] = 0

            result.append(res)
            total_stay += res['total']
            total_allotments += res['allotments']

        # print(result)
        if total_allotments > 0:
            total_occupancy = math.ceil(total_stay / total_allotments * 100)
        else:
            total_occupancy = 0
        context = {
            "details": result,
            "total_occupancy": total_occupancy
        }
        return context

    # Attendee Needed for this function
    # def get_filtered_attendee(request, filters, match_condition):
    #     event_id = request.session['event_id']
    #
    #     q = Q()
    #     if match_condition == 1:
    #         q = Q(id=-11)
    #     try:
    #         for filter1 in filters:
    #             if isinstance(filter1[0], dict):
    #                 if match_condition == '2':
    #                     single_filter = filter1[0]
    #                     if single_filter['field'] == '1':
    #                         if single_filter['condition'] == '1':
    #                             q &= q & Q(created__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '2':
    #                             q &= ~Q(created__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '3':
    #                             single_filter['values'][0] += ' 23:59:59'
    #                             q &= Q(created__gt=single_filter['values'][0])
    #                         if single_filter['condition'] == '4':
    #                             single_filter['values'][0] += ' 00:00:00'
    #                             q &= Q(created__lt=single_filter['values'][0])
    #                         if single_filter['condition'] == '5':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q &= Q(created__range=(earlier, now))
    #                         if single_filter['condition'] == '6':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q &= ~Q(created__range=(earlier, now))
    #                         if single_filter['condition'] == '7':
    #                             start_date = single_filter['values'][0] + ' 00:00:00'
    #                             end_date = single_filter['values'][1] + ' 23:59:59'
    #                             q &= Q(created__range=(start_date, end_date))
    #                     if single_filter['field'] == '2':
    #                         if single_filter['condition'] == '1':
    #                             q &= q & Q(updated__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '2':
    #                             q &= ~Q(updated__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '3':
    #                             single_filter['values'][0] += ' 23:59:59'
    #                             q &= Q(updated__gt=single_filter['values'][0])
    #                         if single_filter['condition'] == '4':
    #                             single_filter['values'][0] += ' 00:00:00'
    #                             q &= Q(updated__lt=single_filter['values'][0])
    #                         if single_filter['condition'] == '5':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q &= Q(updated__range=(earlier, now))
    #                         if single_filter['condition'] == '6':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q &= ~Q(updated__range=(earlier, now))
    #                         if single_filter['condition'] == '7':
    #                             start_date = single_filter['values'][0] + ' 00:00:00'
    #                             end_date = single_filter['values'][1] + ' 23:59:59'
    #                             q &= Q(updated__range=(start_date, end_date))
    #                     if single_filter['field'] == '3':
    #                         attendee_ids = AttendeeGroups.objects.filter(group_id=single_filter['values'][0]).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q &= Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '2':
    #                             q &= ~Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '3':
    #                             new_attende_ids = []
    #                             for attendee in attendee_ids:
    #                                 if not AttendeeGroups.objects.filter(attendee_id=attendee['attendee_id']).exclude(
    #                                         group_id=single_filter['values'][0]).exists():
    #                                     new_attende_ids.append(attendee['attendee_id'])
    #                             q &= Q(id__in=new_attende_ids)
    #                     if single_filter['field'] == '4':
    #                         attendee_ids = AttendeeTag.objects.filter(tag_id=single_filter['values'][0]).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q &= Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '2':
    #                             q &= ~Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '3':
    #                             new_attende_ids = []
    #                             for attendee in attendee_ids:
    #                                 if not AttendeeTag.objects.filter(attendee_id=attendee['attendee_id']).exclude(
    #                                         tag_id=single_filter['values'][0]).exists():
    #                                     new_attende_ids.append(attendee['attendee_id'])
    #                             q &= Q(id__in=new_attende_ids)
    #
    #                     if single_filter['field'] == '6':
    #                         attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0]).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
    #                                                                      status='attending').values('attendee_id')
    #                             q &= Q(id__in=attending)
    #                         elif single_filter['condition'] == '2':
    #                             attending_data = SeminarsUsers.objects.filter(Q(
    #                                 Q(session_id=single_filter['values'][0]) & Q(
    #                                     Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))).values(
    #                                 'attendee_id')
    #                             q &= ~Q(id__in=attending_data)
    #                         elif single_filter['condition'] == '3':
    #                             attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
    #                                                                         status='in-queue').values('attendee_id')
    #                             q &= Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '4':
    #                             attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
    #                                                                         status='deciding').values('attendee_id')
    #                             q &= Q(id__in=attendee_ids)
    #                     if single_filter['field'] == '7':
    #                         attendees_matches = []
    #                         if single_filter['type'] == 'text' or single_filter['type'] == 'textarea':
    #                             if single_filter['values'][0] == '1':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value__icontains=single_filter['values'][
    #                                                                                1]).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '2':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).exclude(
    #                                     value__icontains=single_filter['values'][1]).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '3':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value=single_filter['values'][1]).values(
    #                                     'user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '4':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).exclude(
    #                                     value=single_filter['values'][1]).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '5':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value__istartswith=single_filter['values'][
    #                                                                                1]).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '6':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value__iendswith=single_filter['values'][
    #                                                                                1]).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #
    #                             elif single_filter['values'][0] == '7':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q &= ~Q(id__in=attendees_matches)
    #
    #                             elif single_filter['values'][0] == '8':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #
    #                         else:
    #                             if single_filter['values'][0] == '1':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value=single_filter['values'][1]).values(
    #                                     'user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '2':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).exclude(
    #                                     value=single_filter['values'][1]).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '3':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q &= ~Q(id__in=attendees_matches)
    #
    #                             elif single_filter['values'][0] == '4':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q &= Q(id__in=attendees_matches)
    #
    #                     if single_filter['field'] == '8':
    #                         attendee_ids = DeviceToken.objects.all().values('attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q &= Q(id__in=attendee_ids)
    #                         else:
    #                             q &= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '9':
    #                         if single_filter['condition'] == '1':
    #                             room_id = single_filter['values'][1]
    #                             attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
    #                             if single_filter['values'][0] == '1':
    #                                 q &= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '2':
    #                                 q &= ~Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '2':
    #
    #                             if single_filter['values'][0] == '1':
    #                                 attendees = Booking.objects.filter(
    #                                     check_in__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '2':
    #                                 attendees = Booking.objects.filter(
    #                                     check_in__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #                             if single_filter['values'][0] == '3':
    #                                 # single_filter['values'][1] += ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_in__gt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '4':
    #                                 # single_filter['values'][1] += ' 00:00:00'
    #                                 attendees = Booking.objects.filter(check_in__lt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '5':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '6':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '7':
    #                                 # start_date = single_filter['values'][1] + ' 00:00:00'
    #                                 # end_date = single_filter['values'][2] + ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_in__range=(start_date, end_date)).values(
    #                                     'attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '3':
    #
    #                             if single_filter['values'][0] == '1':
    #                                 attendees = Booking.objects.filter(
    #                                     check_out__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '2':
    #                                 attendees = Booking.objects.filter(
    #                                     check_out__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #                             if single_filter['values'][0] == '3':
    #                                 # single_filter['values'][1] += ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_out__gt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '4':
    #                                 # single_filter['values'][1] += ' 00:00:00'
    #                                 attendees = Booking.objects.filter(check_out__lt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '5':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_out__range=(earlier, now)).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '6':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_out__range=(earlier, now)).values(
    #                                     'attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '7':
    #                                 # start_date = single_filter['values'][1] + ' 00:00:00'
    #                                 # end_date = single_filter['values'][2] + ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_out__range=(start_date, end_date)).values(
    #                                     'attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '4':
    #                             room_number = single_filter['values'][1]
    #
    #                             if single_filter['values'][0] == '1':
    #                                 attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '2':
    #                                 attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
    #                                 q &= ~Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '3':
    #                                 attendees = Booking.objects.filter(room__beds__gt=int(room_number)).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '4':
    #                                 attendees = Booking.objects.filter(room__beds__lt=int(room_number)).values(
    #                                     'attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '5':
    #                             if single_filter['values'][1] == '':
    #                                 single_filter['values'][1] = 0
    #                             occupancy_value = int(single_filter['values'][1])
    #                             rooms = Room.objects.all()
    #                             if single_filter['values'][0] == '1':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = UserRule.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] == occupancy_value:
    #                                         selected_rooms.append(room.id)
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '2':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = UserRule.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] != occupancy_value:
    #                                         selected_rooms.append(room.id)
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                             elif single_filter['values'][0] == '3':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = UserRule.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] > occupancy_value:
    #                                         selected_rooms.append(room.id)
    #
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                             elif single_filter['values'][0] == '4':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = UserRule.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] < occupancy_value:
    #                                         selected_rooms.append(room.id)
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q &= Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '6':
    #                             value = single_filter['values'][1]
    #                             attendee_ids = []
    #                             attendees = MatchLine.objects.raw(
    #                                 'select m.* from match_line as m where m.match_id in (select n.match_id from match_line as n group by n.match_id having COUNT(*) > 1)')
    #                             for attendee in attendees:
    #                                 attendee_ids.append(attendee.booking.attendee.id)
    #
    #                             if single_filter['values'][0] == '1':
    #                                 if value == '1':
    #                                     q &= Q(id__in=attendee_ids)
    #                                 if value == '2':
    #                                     q &= ~Q(id__in=attendee_ids)
    #
    #                             elif single_filter['values'][0] == '2':
    #                                 if value == '1':
    #                                     q &= ~Q(id__in=attendee_ids)
    #                                 if value == '2':
    #                                     q &= Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '10':
    #                         attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q &= Q(id__in=attendee_ids)
    #                         else:
    #                             q &= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '11':
    #                         attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],
    #                                                                      attendee_id__isnull=False).values('attendee_id')
    #                         if single_filter['values'][0] == '1':
    #                             q &= Q(id__in=attendee_ids)
    #                         else:
    #                             q &= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '12':
    #                         attendee_ids = MessageReceiversHistory.objects.filter(
    #                             receiver__message_content_id=single_filter['condition'],
    #                             receiver__attendee_id__isnull=False).values('receiver__attendee_id')
    #                         if single_filter['values'][0] == '1':
    #                             q &= Q(id__in=attendee_ids)
    #                         else:
    #                             q &= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '13':
    #
    #                         if single_filter['values'][0] == '1':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(
    #                                 button_id=single_filter['condition']).values('attendee_id')
    #                             q &= Q(id__in=attendee_ids)
    #
    #                         elif single_filter['values'][0] == '2':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(
    #                                 button_id=single_filter['condition']).values('attendee_id')
    #                             q &= ~Q(id__in=attendee_ids)
    #
    #                         elif single_filter['values'][0] == '3':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],
    #                                                                                hit_count=int(
    #                                                                                    single_filter['values'][1])).values(
    #                                 'attendee_id')
    #                             q &= Q(id__in=attendee_ids)
    #                         elif single_filter['values'][0] == '4':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],
    #                                                                                hit_count__gt=int(
    #                                                                                    single_filter['values'][1])).values(
    #                                 'attendee_id')
    #                             q &= Q(id__in=attendee_ids)
    #                         elif single_filter['values'][0] == '5':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],
    #                                                                                hit_count__lt=int(
    #                                                                                    single_filter['values'][1])).values(
    #                                 'attendee_id')
    #                             q &= Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '14':
    #
    #                         if single_filter['condition'] == '1':
    #                             attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0]).values('id')
    #                             q &= Q(id__in=attendee_ids)
    #
    #                         elif single_filter['condition'] == '2':
    #                             attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0]).values('id')
    #                             q &= ~Q(id__in=attendee_ids)
    #
    #                 elif match_condition == '1':
    #                     single_filter = filter1[0]
    #                     if single_filter['field'] == '1':
    #                         if single_filter['condition'] == '1':
    #                             q |= Q(created__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '2':
    #                             q |= ~Q(created__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '3':
    #                             single_filter['values'][0] += ' 23:59:59'
    #                             q |= Q(created__gt=single_filter['values'][0])
    #                         if single_filter['condition'] == '4':
    #                             single_filter['values'][0] += ' 00:00:00'
    #                             q |= Q(created__lt=single_filter['values'][0])
    #                         if single_filter['condition'] == '5':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q |= Q(created__range=(earlier, now))
    #                         if single_filter['condition'] == '6':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q |= ~Q(created__range=(earlier, now))
    #                         if single_filter['condition'] == '7':
    #                             start_date = single_filter['values'][0] + ' 00:00:00'
    #                             end_date = single_filter['values'][1] + ' 23:59:59'
    #                             q |= Q(created__range=(start_date, end_date))
    #                     if single_filter['field'] == '2':
    #                         # need to test again
    #
    #                         if single_filter['condition'] == '1':
    #                             q |= Q(updated__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '2':
    #                             q |= ~Q(updated__startswith=single_filter['values'][0])
    #                         if single_filter['condition'] == '3':
    #                             single_filter['values'][0] += ' 23:59:59'
    #                             q |= Q(updated__gt=single_filter['values'][0])
    #                         if single_filter['condition'] == '4':
    #                             single_filter['values'][0] += ' 00:00:00'
    #                             q |= Q(updated__lt=single_filter['values'][0])
    #                         if single_filter['condition'] == '5':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q |= Q(updated__range=(earlier, now))
    #                         if single_filter['condition'] == '6':
    #                             now = datetime.datetime.now()
    #                             if single_filter['values'][1] == "1":
    #                                 days_to_go = int(single_filter['values'][0]) * 1
    #                             elif single_filter['values'][1] == "2":
    #                                 days_to_go = int(single_filter['values'][0]) * 7
    #                             elif single_filter['values'][1] == "3":
    #                                 days_to_go = int(single_filter['values'][0]) * 30
    #                             earlier = now - datetime.timedelta(days_to_go)
    #                             q |= ~Q(updated__range=(earlier, now))
    #                         if single_filter['condition'] == '7':
    #                             start_date = single_filter['values'][0] + ' 00:00:00'
    #                             end_date = single_filter['values'][1] + ' 23:59:59'
    #                             q |= Q(updated__range=(start_date, end_date))
    #                     if single_filter['field'] == '3':
    #                         attendee_ids = AttendeeGroups.objects.filter(group_id=single_filter['values'][0]).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q |= Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '2':
    #                             q |= ~Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '3':
    #                             new_attende_ids = []
    #                             for attendee in attendee_ids:
    #                                 if not AttendeeGroups.objects.filter(attendee_id=attendee['attendee_id']).exclude(
    #                                         group_id=single_filter['values'][0]).exists():
    #                                     new_attende_ids.append(attendee['attendee_id'])
    #                             q |= Q(id__in=new_attende_ids)
    #                     if single_filter['field'] == '4':
    #                         attendee_ids = AttendeeTag.objects.filter(tag_id=single_filter['values'][0]).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q |= Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '2':
    #                             q |= ~Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '3':
    #                             new_attende_ids = []
    #                             for attendee in attendee_ids:
    #                                 if not AttendeeTag.objects.filter(attendee_id=attendee['attendee_id']).exclude(
    #                                         tag_id=single_filter['values'][0]).exists():
    #                                     new_attende_ids.append(attendee['attendee_id'])
    #                             q |= Q(id__in=new_attende_ids)
    #                     if single_filter['field'] == '6':
    #                         attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0]).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
    #                                                                      status='attending').values('attendee_id')
    #                             q |= Q(id__in=attending)
    #                         elif single_filter['condition'] == '2':
    #                             attending_data = SeminarsUsers.objects.filter(Q(
    #                                 Q(session_id=single_filter['values'][0]) & Q(
    #                                     Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))).values(
    #                                 'attendee_id')
    #                             q |= ~Q(id__in=attending_data)
    #                         elif single_filter['condition'] == '3':
    #                             attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
    #                                                                         status='in-queue').values('attendee_id')
    #                             q |= Q(id__in=attendee_ids)
    #                         elif single_filter['condition'] == '4':
    #                             attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
    #                                                                         status='deciding').values('attendee_id')
    #                             q |= Q(id__in=attendee_ids)
    #                     if single_filter['field'] == '7':
    #                         if single_filter['type'] == 'text' or single_filter['type'] == 'textarea':
    #                             if single_filter['values'][0] == '1':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value__icontains=single_filter['values'][
    #                                                                                1]).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '2':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).exclude(
    #                                     value__icontains=single_filter['values'][1]).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '3':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value=single_filter['values'][1]).values(
    #                                     'user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '4':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).exclude(
    #                                     value=single_filter['values'][1]).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '5':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value__istartswith=single_filter['values'][
    #                                                                                1]).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '6':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value__iendswith=single_filter['values'][
    #                                                                                1]).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '7':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q |= ~Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '8':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                         else:
    #                             if single_filter['values'][0] == '1':
    #                                 attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
    #                                                                            value=single_filter['values'][1]).values(
    #                                     'user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '2':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).exclude(
    #                                     value=single_filter['values'][1]).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '3':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q |= ~Q(id__in=attendees_matches)
    #                             elif single_filter['values'][0] == '4':
    #                                 attendees_matches = Answers.objects.filter(
    #                                     question_id=int(single_filter['condition'])).values('user_id')
    #                                 q |= Q(id__in=attendees_matches)
    #
    #                     if single_filter['field'] == '8':
    #                         attendee_ids = DeviceToken.objects.all().values('attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q |= Q(id__in=attendee_ids)
    #                         else:
    #                             q |= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '9':
    #                         if single_filter['condition'] == '1':
    #                             room_id = single_filter['values'][1]
    #                             attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
    #                             if single_filter['values'][0] == '1':
    #                                 q |= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '2':
    #                                 q |= ~Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '2':
    #
    #                             if single_filter['values'][0] == '1':
    #                                 attendees = Booking.objects.filter(
    #                                     check_in__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '2':
    #                                 attendees = Booking.objects.filter(
    #                                     check_in__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #                             if single_filter['values'][0] == '3':
    #                                 # single_filter['values'][1] += ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_in__gt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '4':
    #                                 # single_filter['values'][1] += ' 00:00:00'
    #                                 attendees = Booking.objects.filter(check_in__lt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '5':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '6':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '7':
    #                                 # start_date = single_filter['values'][1] + ' 00:00:00'
    #                                 # end_date = single_filter['values'][2] + ' 23:59:59'
    #                                 # change
    #                                 start_date = single_filter['values'][1]
    #                                 end_date = single_filter['values'][2]
    #                                 attendees = Booking.objects.filter(check_in__range=(start_date, end_date)).values(
    #                                     'attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '3':
    #
    #                             if single_filter['values'][0] == '1':
    #                                 attendees = Booking.objects.filter(
    #                                     check_out__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '2':
    #                                 attendees = Booking.objects.filter(
    #                                     check_out__startswith=single_filter['values'][1]).values('attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #                             if single_filter['values'][0] == '3':
    #                                 # single_filter['values'][1] += ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_out__gt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '4':
    #                                 # single_filter['values'][1] += ' 00:00:00'
    #                                 attendees = Booking.objects.filter(check_out__lt=single_filter['values'][1]).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '5':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_out__range=(earlier, now)).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             if single_filter['values'][0] == '6':
    #                                 now = datetime.datetime.now()
    #                                 if single_filter['values'][2] == "1":
    #                                     days_to_go = int(single_filter['values'][1]) * 1
    #                                 elif single_filter['values'][2] == "2":
    #                                     days_to_go = int(single_filter['values'][1]) * 7
    #                                 elif single_filter['values'][2] == "3":
    #                                     days_to_go = int(single_filter['values'][1]) * 30
    #                                 earlier = now - datetime.timedelta(days_to_go)
    #                                 attendees = Booking.objects.filter(check_out__range=(earlier, now)).values(
    #                                     'attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #
    #                             if single_filter['values'][0] == '7':
    #                                 # start_date = single_filter['values'][1] + ' 00:00:00'
    #                                 # end_date = single_filter['values'][2] + ' 23:59:59'
    #                                 attendees = Booking.objects.filter(check_out__range=(start_date, end_date)).values(
    #                                     'attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '4':
    #                             room_number = single_filter['values'][1]
    #
    #                             if single_filter['values'][0] == '1':
    #                                 attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '2':
    #                                 attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
    #                                 q |= ~Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '3':
    #                                 attendees = Booking.objects.filter(room__beds__gt=int(room_number)).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '4':
    #                                 attendees = Booking.objects.filter(room__beds__lt=int(room_number)).values(
    #                                     'attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '5':
    #                             if single_filter['values'][1] == '':
    #                                 single_filter['values'][1] = 0
    #                             occupancy_value = int(single_filter['values'][1])
    #
    #                             rooms = Room.objects.all()
    #
    #                             if single_filter['values'][0] == '1':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = RoomView.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] == occupancy_value:
    #                                         selected_rooms.append(room.id)
    #
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #                             elif single_filter['values'][0] == '2':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = RoomView.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] != occupancy_value:
    #                                         selected_rooms.append(room.id)
    #
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                             elif single_filter['values'][0] == '3':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = RoomView.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] > occupancy_value:
    #                                         selected_rooms.append(room.id)
    #
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                             elif single_filter['values'][0] == '4':
    #                                 selected_rooms = []
    #                                 for room in rooms:
    #                                     occupancy = RoomView.find_booking(str(room.id))
    #                                     if occupancy['total_occupancy'] < occupancy_value:
    #                                         selected_rooms.append(room.id)
    #
    #                                 attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
    #                                 q |= Q(id__in=attendees)
    #
    #                         if single_filter['condition'] == '6':
    #                             value = single_filter['values'][1]
    #                             attendee_ids = []
    #                             attendees = MatchLine.objects.raw(
    #                                 'select m.* from match_line as m where m.match_id in (select n.match_id from match_line as n group by n.match_id having COUNT(*) > 1)')
    #                             for attendee in attendees:
    #                                 attendee_ids.append(attendee.booking.attendee.id)
    #
    #                             if single_filter['values'][0] == '1':
    #                                 if value == '1':
    #                                     q |= Q(id__in=attendee_ids)
    #                                 if value == '2':
    #                                     q |= ~Q(id__in=attendee_ids)
    #
    #                             elif single_filter['values'][0] == '2':
    #                                 if value == '1':
    #                                     q |= ~Q(id__in=attendee_ids)
    #                                 if value == '2':
    #                                     q |= Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '10':
    #                         attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values(
    #                             'attendee_id')
    #                         if single_filter['condition'] == '1':
    #                             q |= Q(id__in=attendee_ids)
    #                         else:
    #                             q |= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '11':
    #                         attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],
    #                                                                      attendee_id__isnull=False).values('attendee_id')
    #                         if single_filter['values'][0] == '1':
    #                             q |= Q(id__in=attendee_ids)
    #                         else:
    #                             q |= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '12':
    #                         attendee_ids = MessageReceiversHistory.objects.filter(
    #                             receiver__message_content_id=single_filter['condition'],
    #                             receiver__attendee_id__isnull=False).values('receiver__attendee_id')
    #                         if single_filter['values'][0] == '1':
    #                             q |= Q(id__in=attendee_ids)
    #                         else:
    #                             q |= ~Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '13':
    #
    #                         if single_filter['values'][0] == '1':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(
    #                                 button_id=single_filter['condition']).values('attendee_id')
    #                             q |= Q(id__in=attendee_ids)
    #
    #                         elif single_filter['values'][0] == '2':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(
    #                                 button_id=single_filter['condition']).values('attendee_id')
    #                             q |= ~Q(id__in=attendee_ids)
    #
    #                         elif single_filter['values'][0] == '3':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],
    #                                                                                hit_count=int(
    #                                                                                    single_filter['values'][1])).values(
    #                                 'attendee_id')
    #                             q |= Q(id__in=attendee_ids)
    #                         elif single_filter['values'][0] == '4':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],
    #                                                                                hit_count__gt=int(
    #                                                                                    single_filter['values'][1])).values(
    #                                 'attendee_id')
    #                             q |= Q(id__in=attendee_ids)
    #                         elif single_filter['values'][0] == '5':
    #                             attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],
    #                                                                                hit_count__lt=int(
    #                                                                                    single_filter['values'][1])).values(
    #                                 'attendee_id')
    #                             q |= Q(id__in=attendee_ids)
    #
    #                     if single_filter['field'] == '14':
    #
    #                         if single_filter['condition'] == '1':
    #                             attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0]).values('id')
    #                             q |= Q(id__in=attendee_ids)
    #
    #                         elif single_filter['condition'] == '2':
    #                             attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0]).values('id')
    #                             q |= ~Q(id__in=attendee_ids)
    #
    #             else:
    #                 match_condition_inner = filter1[0][0]['matchFor']
    #                 if match_condition == '2':
    #                     q &= UserRule.get_filtered_attendee(request, filter1, match_condition_inner)
    #                 elif match_condition == '1':
    #                     q = Q(id=-11)
    #                     q |= UserRule.get_filtered_attendee(request, filter1, match_condition_inner)
    #         q &= Q(event_id=event_id)
    #     except Exception as e:
    #         ErrorR.efail(e)
    #         q = Q(id=-11)
    #     return q

    def get_filtered_attendee(request, filters, match_condition,matched_attendees=[]):
        event_id = request.session['event_id']
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='10':
        #                 q = Q()
        #                 attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='11':
        #                 q = Q()
        #                 attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],attendee_id__isnull=False).values('attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='12':
        #                 q = Q()
        #                 attendee_ids = MessageReceiversHistory.objects.filter(receiver__message_content_id=single_filter['condition'],receiver__attendee_id__isnull=False).values('receiver__attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q &= Q(id__in=attendee_ids)
        #                 else:
        #                    q &= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees, q, event_id)
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
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
        #             if single_filter['field'] == '17':
        #                 q = Q()
        #                 if single_filter['values'][0] == '1':
        #                     attendee_ids = OrderItems.objects.filter(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '2':
        #                     attendee_ids = OrderItems.objects.exclude(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q &= Q(id__in=attendee_ids)
        #                 matched_attendees = UserRule.get_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='8':
        #                 q = Q()
        #                 attendee_ids = DeviceToken.objects.all().values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='10':
        #                 q = Q()
        #                 attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values('attendee_id')
        #                 if single_filter['condition'] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='11':
        #                 q = Q()
        #                 attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],attendee_id__isnull=False).values('attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='12':
        #                 q = Q()
        #                 attendee_ids = MessageReceiversHistory.objects.filter(receiver__message_content_id=single_filter['condition'],receiver__attendee_id__isnull=False).values('receiver__attendee_id')
        #                 if single_filter['values'][0] == '1':
        #                    q |= Q(id__in=attendee_ids)
        #                 else:
        #                    q |= ~Q(id__in=attendee_ids)
        #
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #             if single_filter['field']=='15':
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees, q, event_id)
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
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #             if single_filter['field'] == '17':
        #                 q = Q()
        #                 if single_filter['values'][0] == '1':
        #                     attendee_ids = OrderItems.objects.filter(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #                 elif single_filter['values'][0] == '2':
        #                     attendee_ids = OrderItems.objects.exclude(rebate_id=single_filter['condition']).values('order__attendee_id')
        #                     q |= Q(id__in=attendee_ids)
        #                 matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,q,event_id)
        #
        #     else:
        #         match_condition_inner = filter1[0][0]['matchFor']
        #         # total_matched_attendees = []
        #         if match_condition == '2':
        #             main_q = Q()
        #             total_matched_attendees = UserRule.get_filtered_attendee(request, filter1, match_condition_inner)
        #             main_q &= Q(id__in=total_matched_attendees)
        #             matched_attendees = UserRule.get_matched_attendees(matched_attendees,main_q,event_id)
        #         elif match_condition == '1':
        #             main_q = Q(id=-11)
        #             total_matched_attendees = UserRule.get_filtered_attendee(request, filter1, match_condition_inner,matched_attendees)
        #             main_q |= Q(id__in=total_matched_attendees)
        #             matched_attendees = UserRule.get_all_matched_attendees(matched_attendees,main_q,event_id)
        # main_q &= Q(event_id=event_id)
        # main_q &= Q(id__in=matched_attendees)
        # # except Exception as e:
        # #     q = Q(id=-11)
        # #     ErrorR.efail(e)
        # #     import traceback
        # #     traceback.print_exc()
        # total_attendees = Attendee.objects.filter(main_q).values('id')
        # all_attendess = []
        # for att in total_attendees:
        #     all_attendess.append(att['id'])
        # return all_attendess

    # def get_matched_attendees(matched_attendees,q,event_id):
    #     attendees = Attendee.objects.filter(q).filter(event_id=event_id,status="registered").values('id')
    #     attendees_array = []
    #     for attendee in attendees:
    #         attendees_array.append(attendee['id'])
    #     matched_attendees = list(set(matched_attendees) & set(attendees_array))
    #     return matched_attendees
    #
    # def get_all_matched_attendees(matched_attendees,q,event_id):
    #     attendees = Attendee.objects.filter(q).filter(event_id=event_id,status="registered").values('id')
    #     attendees_array = []
    #     for attendee in attendees:
    #         attendees_array.append(attendee['id'])
    #     matched_attendees = list(set(matched_attendees) | set(attendees_array))
    #     return matched_attendees

