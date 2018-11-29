from django.views import generic
from app.models import Attendee, RuleSet, MenuPermission, Booking, Room, \
    MatchLine, PagePermission
import json

from app.views.gbhelper.filter_helper import FilterHelper
import datetime
from django.db.models import Q, F
from django.db import connection
import math
from django.db.models.aggregates import Count
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.helper import HelperData


class UserRule(generic.TemplateView):
    def get_menu_permissions(request):
        ErrorR.ex_time_init()
        my_rule_set = []
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
                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
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

        if total_allotments > 0:
            total_occupancy = math.ceil(total_stay / total_allotments * 100)
        else:
            total_occupancy = 0
        context = {
            "details": result,
            "total_occupancy": total_occupancy
        }
        return context

    def get_filtered_attendee(request, filters, match_condition,matched_attendees=[]):
        event_id = request.session['event_id']
        return FilterHelper.get_attendee_using_filter(event_id, filters, match_condition, matched_attendees=[])

