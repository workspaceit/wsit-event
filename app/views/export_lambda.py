from django.shortcuts import render, redirect
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
import os
from django.http import HttpResponse
from django.views import generic
from app.models import Attendee,MatchLine, ExportState , Room,Events, Questions, Booking, Answers, RequestedBuddy,Travel,TravelAttendee, Setting, \
    Orders, Group, OrderItems, CreditUsages, Payments, RegistrationGroupOwner
from .common_views import GroupView
import time
import logging
from django.core import serializers
import json
import io
import boto
import datetime
from pytz import timezone
from boto.s3.key import Key
from django.conf import settings
from .filter import FilterView
from django.db.models import Count, Max, F, Sum
import logging
import re
from app.views.gbhelper.export_library import ExportLibrary

class ExcelView(generic.DetailView):

    def export(request,export_type,export_filter_name, qlist, slist, rule_id, uid, rdate, udate, secret, bid, attGroup, attTag, hotel, travel, hotel_columns, economy_columns, include_import_header):

        if 'is_login' not in request.session or not request.session['is_login']:
            return redirect('login')
        else:
            event_id = request.session['event_auth_user']['event_id']
            admin_id = request.session['event_auth_user']['id']
            if export_type == "hotel_view":
                return ExcelView.export_room_dependencies(request, export_filter_name, qlist, rule_id)
            elif export_type == "economy_view":
                return ExcelView.export_as_economy_view(request, rule_id, export_filter_name, qlist, economy_columns)

            attendees = FilterView.get_filtered_attendees(request, rule_id)
            ExportLibrary.prepare_export_data_s3_upload(export_filter_name, qlist, slist, uid, rdate, udate, secret, bid, attGroup,
                                                        attTag, travel, hotel_columns, attendees, economy_columns, include_import_header, event_id, admin_id)

        response = {
                'error': False,
                'message': 'Your file will be available momentarily'
            }
        return HttpResponse(json.dumps(response), content_type="application/json")

    def getTimezoneNow(request, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_auth_user']['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            now = datetime.datetime.now(timezone_active)
            return now

    def urlify(s):
         s = re.sub(r"[^\w\s]", '_', s)
         s = re.sub(r"\s+", '_', s)
         return s

    def export_room_dependencies(request, export_filter_name, qlist, rule_id):
        attendees = FilterView.get_filtered_attendees(request, rule_id)
        questions = []
        question_groups = GroupView.get_questionGroup(request)
        for group in question_groups:
            questions.extend(Questions.objects.filter(group=group, id__in=qlist).order_by('question_order'))

        allAnswers = Answers.objects.filter(question_id__in=questions, user_id__in=attendees)
        all_bookings = Booking.objects.filter(attendee__in=attendees)
        matchlines = MatchLine.objects.filter(booking__in=all_bookings)

        defaultGroup = [
            {'id': "att-uid", "name": "Attendee Id"},
            {'id': "check in", "name": "Check In"},
            {'id': "check out", "name": "Check Out"}
        ]

        max_att_in_a_room = matchlines.values("match_id").annotate(max_att=Count("id")).order_by()

        max_buddy = 1
        if max_att_in_a_room:
            max_att_in_a_room = max_att_in_a_room.latest('max_att')
            max_buddy = max_att_in_a_room['max_att']

        room_list = Room.objects.values("id", "description", "hotel__name", "booking", "booking__matchline__match").filter(booking__id__in=all_bookings).distinct()
        room_list = json.dumps(list(room_list))

        headers = ExcelView.get_room_header(defaultGroup, max_buddy, questions)
        rule_name = ExcelView.urlify(export_filter_name)
        event = Events.objects.get(id=request.session['event_auth_user']['event_id'])
        file_name = 'exported_files/' + event.name + '/' + rule_name + '_' + str(time.strftime("%Y_%m_%d_%H_%M_%S")) + '.xlsx'

        var_list = {
            'headers': json.dumps(headers),
            'file_name': file_name,
            'questions': serializers.serialize('json', questions),
            'answers': serializers.serialize('json', allAnswers),
            'bookings': serializers.serialize('json', all_bookings),
            'matchlines': serializers.serialize('json', matchlines),
            'rooms': room_list,
            'export_as_hotel': True
        }
        ExcelView.upload_data_to_s3(var_list)

        export_state = ExportState(file_name=file_name, status=0, event_id=request.session['event_auth_user']['event_id'],admin_id=request.session['event_auth_user']['id'])
        export_state.save()

        response = {
            'error': False,
            'message': 'Your file will be available momentarily.'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    def upload_data_to_s3(var_list):
        message = json.dumps(var_list)
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        filename_with_path = 'export/data.txt'
        key_name = filename_with_path
        k = Key(bucket)
        k.key = key_name
        if not k.exists():
            key = bucket.new_key(key_name)
            key.set_contents_from_string(message)
            key.set_metadata('Content-Type', 'text/plain')
            key.set_acl('public-read')
            key.make_public()
        else:
            k.set_contents_from_string(message)
            k.set_metadata('Content-Type', 'text/plain')
            k.set_acl('public-read')
            k.make_public()

    def export_as_economy_view(request, rule_id, export_filter_name, question_list, economy_columns):
        event_id = request.session['event_auth_user']['event_id']
        attendees = FilterView.get_filtered_attendees(request, rule_id)
        questions = []
        question_groups = GroupView.get_questionGroup(request)
        for group in question_groups:
            questions.extend(Questions.objects.filter(group=group, id__in=question_list).order_by('question_order'))

        attendee_ids = list(attendees.values_list('id', flat=True))
        attendee_order_numbers = list(Orders.objects.filter(attendee_id__in=attendee_ids).values_list('order_number', flat=True))
        # need to update non filtered attendees because filtered attendee could have non filtered attendee in their group order
        attendee_ids = list(Orders.objects.filter(order_number__in=attendee_order_numbers).values_list('attendee_id', flat=True))
        allAnswers = Answers.objects.filter(question_id__in=questions, user_id__in=attendee_ids)
        order_item_objects = OrderItems.objects.filter(order__order_number__in=attendee_order_numbers).exclude(
            item_type__in=['rebate', 'adjustment']).annotate(value=Sum((F('cost') * F('vat_rate')) / 100)).values(
            'order__order_number', 'vat_rate', 'value')

        if not attendee_order_numbers:
            # produce error in following raw query while a attendee_order_numbers is empty
            attendee_order_numbers = [0]

        query_string = "SELECT id, status, invoice_ref, invoice_date, due_date, vat_amount, rebate_amount, order_number," \
                       "cost, GROUP_CONCAT(attendee_id), SUM(cost) AS net_cost, SUM(vat_amount) AS t_vat, " \
                       "SUM(rebate_amount) AS t_rebate, SUM(cost + vat_amount) AS total_cost FROM orders " \
                       "WHERE cost > 0 AND order_number IN ({}) GROUP BY order_number ORDER BY order_number ASC".format(str(attendee_order_numbers).strip('[]'))

        query_result = Orders.objects.raw(query_string, translations={'GROUP_CONCAT(attendee_id)': 'attendees'})
        attendee_orders = []
        for res in query_result:
            attendee_orders.append(dict(
                order_number=res.order_number, status=res.status,
                invoice_id=res.invoice_ref, invoice_date=str(res.invoice_date) if res.invoice_date else "",
                due_date=str(res.due_date) if res.due_date else "", vat_amount=res.t_vat,
                rebate_amount=res.t_rebate, total_cost_excl_vat=res.net_cost,
                total_cost_incl_vat=res.total_cost, attendees=res.attendees
            ))
        credit_usages = dict()
        credit_usage_objects = CreditUsages.objects.filter(order_number__in=attendee_order_numbers).values(
            'order_number').annotate(total_cost=Sum('cost'))
        for credit_item in credit_usage_objects:
            credit_usages[credit_item['order_number']] = credit_item['total_cost']

        order_payments = Payments.objects.filter(order_number__in=attendee_order_numbers)
        order_vat_percent_sum = dict()
        event_economy_vats = []
        event_economy_vat_count = 1
        if 'vat-xx-percent-sum' in economy_columns:
            vat_objects = Group.objects.filter(event_id=event_id, type='payment').values('name')
            for vat in vat_objects:
                if vat["name"].isdigit():
                    event_economy_vats.append(int(vat["name"]))
            event_economy_vats.sort()
            event_economy_vat_count = len(event_economy_vats)
            for order_item in order_item_objects:
                order_number = order_item["order__order_number"]
                if order_vat_percent_sum.get(order_number):
                    order_vat_percent_sum[order_number][int(order_item['vat_rate'])] += order_item['value']
                else:
                    order_vat_percent_sum[order_number] = dict()
                    for vat in event_economy_vats:
                        order_vat_percent_sum[order_number][vat] = 0
                    order_vat_percent_sum[order_number][int(order_item['vat_rate'])] += order_item['value']

        max_attendee_in_order = 1
        max_order_counter_obj = Orders.objects.filter(order_number__in=attendee_order_numbers, cost__gt=0).values('order_number').annotate(
            total=Count('order_number')).aggregate(max_order_counter=Max('total'))
        if max_order_counter_obj["max_order_counter"]:
            max_attendee_in_order = max_order_counter_obj["max_order_counter"]

        group_details = dict()
        if 'order-group-id' in economy_columns:
            group_members = attendees.filter(registration_group__isnull=False).values('id', 'registration_group__name')
            group_owners = RegistrationGroupOwner.objects.filter(owner_id__in=attendee_ids).values('owner_id', 'group__name')
            for group_member in group_members:
                if group_details.get(group_member['registration_group__name']):
                    group_details[group_member['registration_group__name']].append(group_member['id'])
                else:
                    group_details[group_member['registration_group__name']] = [group_member['id']]
            for group_owner in group_owners:
                if group_details.get(group_owner['group__name']):
                    group_details[group_owner['group__name']].append(group_owner['owner_id'])
                else:
                    group_details[group_owner['group__name']] = [group_owner['owner_id']]

        headers = ExcelView.get_economy_view_header(max_attendee_in_order, economy_columns, questions, event_economy_vats)
        rule_name = ExcelView.urlify(export_filter_name)
        event = Events.objects.get(id=event_id)
        file_name = 'exported_files/' + event.name + '/' + rule_name + '_' + str(
            time.strftime("%Y_%m_%d_%H_%M_%S")) + '.xlsx'
        #
        var_list = {
            'file_name': file_name,
            'headers': json.dumps(headers),
            'economy_columns': economy_columns,
            'attendee_orders': json.dumps(attendee_orders),
            'credit_usages': json.dumps(credit_usages),
            'order_vat_percent_sum': json.dumps(order_vat_percent_sum),
            'order_payments': serializers.serialize('json', order_payments),
            'event_economy_vat_count': event_economy_vat_count,
            'questions': serializers.serialize('json', questions),
            'answers': serializers.serialize('json', allAnswers),
            'group_details': json.dumps(group_details),
            'export_as_economy_view': True
        }

        ExcelView.upload_data_to_s3(var_list)
        export_state = ExportState(file_name=file_name, status=0, event_id=event_id, admin_id=request.session['event_auth_user']['id'])
        export_state.save()

        response = {
            'error': False,
            'message': 'Your file will be available momentarily.'
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_economy_view_header(max_attendee_in_order, economy_columns, questions, event_economy_vats):
        if not economy_columns:
            economy_columns = "order-number,order-status,total-order-sum-incl-vat"
        not_used_header, header = ExportLibrary.get_economy_header(economy_columns, [], [], 1, event_economy_vats)

        for index in range(0, max_attendee_in_order):
            index += 1
            for qus in questions:
                header.append("Attendee {}: {}".format(index, qus.title))

        return header

    def allExportList(request):
        if 'is_login' not in request.session or not request.session['is_login']:
            return redirect('login')
        else:
            start_time = time.time()
            logger = logging.getLogger(__name__)

            travel_list = TravelAttendee.objects.all()
            question_groups = GroupView.get_questionGroup(request)
            questions=[]
            for group in question_groups:
                questions.extend(Questions.objects.filter(group=group))
            travel_groups = GroupView.get_travelGroup(request)
            travels = []
            for group in travel_groups:
                travels.extend(Travel.objects.filter(group=group))
            attendees = Attendee.objects.filter(status="registered")
            req_buddy=RequestedBuddy.objects.all()
            match_lines= MatchLine.objects.all()
            all_bookings = Booking.objects.all()
            all_answers = Answers.objects.filter(question__in=questions)

            return HttpResponse("asdd")

            logger.debug("-----------------Before Loop------------------------")
            logger.debug("--- %s seconds ---" % (time.time() - start_time))
            booking_headers=[{"id":"rbr","name":"Room Buddy Request"},{"id":"rba","name":"Room Buddy Actual"}]
            excel_rows=ExcelView.get_excel_header(questions,travels,booking_headers)
            var_list = {
                'headers' : json.dumps(excel_rows),
                'attendees':serializers.serialize('json', attendees),
                'questions':serializers.serialize('json', questions),
                'answers':serializers.serialize('json', all_answers),
                'travels':serializers.serialize('json', travels),
                'travel_list':serializers.serialize('json', travel_list),
                'bookings':serializers.serialize('json', all_bookings),
                'req_buddy':serializers.serialize('json', req_buddy),
                'matchlines':serializers.serialize('json', match_lines)
            }

            #S3
            message = json.dumps(var_list)

            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            filename_with_path = 'export/data.txt'
            key_name = filename_with_path
            k = Key(bucket)
            k.key = key_name
            if not k.exists():
                key = bucket.new_key(key_name)
                key.set_contents_from_string(message)
                key.set_metadata('Content-Type', 'text/plain')
                key.set_acl('public-read')
                key.make_public()
            else:
                k.set_contents_from_string(message)
                k.set_metadata('Content-Type', 'text/plain')
                k.set_acl('public-read')
                k.make_public()
            #END S3

            logger.debug("-----------------After Save------------------------")
            logger.debug("--- %s seconds ---" % (time.time() - start_time))

            response = {
                'error': False,
                'message': 'Your file will be available momentarily.'
            }
            return HttpResponse(json.dumps(response), content_type="application/json")

    @staticmethod
    def get_excel_header(defaults,questions,sessions,travels, hotels=None, max_booking_number=None, max_actual_room_buddy=None):
        header_row1=[]
        header_row2=[]

        for default in defaults:
            header_row1.append(str(default['id']))
            header_row2.append(default['name'])

        for question in questions:
            header_row1.append("q-"+str(question.id))
            header_row2.append(question.title)

        searchChars = 'ÅÄåäÖö'
        replaceChars = 'AAaaOo'
        trans_table = str.maketrans(searchChars, replaceChars)
        for ssn in sessions:
            header_row1.append("session-"+str(ssn.id))
            header_row2.append((ssn.name).translate(trans_table))

        for travel in travels:
            header_row1.append("travel-"+str(travel.id))
            header_row2.append(travel.name)

        if hotels:
            for max_booking_i in range(0, max_booking_number):
                if 'booking-id-col' in hotels:
                    header_row1.append('h-booking_id')
                    header_row2.append('Booking')
                if 'match-id-col' in hotels:
                    header_row1.append('h-match_id')
                    header_row2.append('Match Id')
                if 'room-id-col' in hotels:
                    # actually room id
                    header_row1.append('h-hotel_id')
                    header_row2.append('Hotel Id')
                if 'hotel-name-col' in hotels:
                    header_row1.append('h-hotel_name')
                    header_row2.append('Hotel Name')
                if 'description-col' in hotels:
                    header_row1.append('h-description')
                    header_row2.append('Description')
                if 'check-in-col' in hotels:
                    header_row1.append('h-check_in')
                    header_row2.append('Check In')
                if 'check-out-col' in hotels:
                    header_row1.append('h-check_out')
                    header_row2.append('Check Out')
                if 'beds-col' in hotels:
                    header_row1.append('h-beds')
                    header_row2.append('Beds')
                if 'location-col' in hotels:
                    header_row1.append('h-location_id')
                    header_row2.append('Location')
                if 'rbr-col' in hotels:
                    header_row1.append('h-rbr')
                    header_row2.append('Room Buddy Requested')
                for i in range(0, max_actual_room_buddy):
                    if 'rba-col' in hotels:
                        header_row1.append('h-rba')
                        header_row2.append('Room Buddy Actual')
                    if 'rba-checkin-col' in hotels:
                        header_row1.append('h-rba_checkin')
                        header_row2.append('Actual Room Buddy Check In')
                    if 'rba-checkout-col' in hotels:
                        header_row1.append('h-rba_checkout')
                        header_row2.append('Actual Room Buddy Check Out')

        header_row=[]
        header_row.append(header_row1)
        header_row.append(header_row2)
        return header_row

    def get_room_header(defaults, max_att, questions):
        header_row2 = ['Hotel Name', 'Description', 'Room ID', 'Match ID', 'Booking ID']

        for i in range(0, max_att):
            for default in defaults:
                header_row2.append("Guest " + str(i + 1) + " " + default['name'])

            for question in questions:
                header_row2.append("Guest " + str(i + 1) + " " + question.title)

        header_row = [header_row2]
        return header_row


    def get_hotel_header(questions):

        header_row1=['booking','match','Attendee Id', 'First Name', 'Last Name', 'Email', 'hotel_id', 'hotel_name',  'Room Description','check_in', 'check_out', 'rbr', 'rba']
        header_row2=['Booking','Match Id','Attendee Id', 'First Name', 'Last Name', 'Email', 'Hotel Id', 'Hotel Name', 'Room Description', 'Check In', 'Check Out', 'Room Buddy Requested', 'Room Buddy Actual']

        for question in questions:
            header_row1.append("q-"+str(question.id))
            header_row2.append(question.title)

        header_row=[]
        header_row.append(header_row1)
        header_row.append(header_row2)
        return header_row


    @staticmethod
    def write_excel(excel_rows,filename="Attendee.xlsx",file_path="attendeeList"):
        # print(excel_rows)
        wb = Workbook()
        ws = wb.active
        for row in excel_rows:
            ws.append(row)
        f = io.BytesIO()
        wb.save(f)
        response = HttpResponse(save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename='+filename
        return response

    def get_answer(attendee_id,questions,answers):
        answered_questions = answers.filter(user_id=attendee_id)
        q_a_list = []
        for question in questions:
            value = ''
            for answer in answered_questions:
                if question.id == answer.question_id:
                    value = answer.value
            # q_a_list.append({'question_id': question.id, 'answer': value})
            q_a_list.append( value)
        return q_a_list

    def get_buddy(buddy_list):
        buddies=''
        for buddy in buddy_list:
            if buddy.email:
                buddies=buddies+buddy.email
            elif buddy.buddy_id:
                # buddies= buddies+buddy.buddy.firstname+" "+ buddy.buddy.lastname
                buddies= buddies+buddy.buddy.email+","
            else :
                buddies = buddies+ ""
        return buddies[:-1]

    def get_actual_buddy(actualBuddyList,booking):
        actualBuddyName=''
        for actualBuddy in actualBuddyList:
            if actualBuddy.booking.attendee_id!=booking.attendee_id:
                actualBuddyName =actualBuddyName + actualBuddy.booking.attendee.email + ","
        return actualBuddyName[:-1]

    def add_sessions(all_sessions,seminar_users,attendee_id):
        sessions=[]
        for session in all_sessions:
            seminar_user = seminar_users.filter(attendee_id=attendee_id,session_id=session.id).last()
            if seminar_user:
                sessions.append( seminar_user.status)
            else:
                sessions.append('')
        return sessions

    def add_travels(all_travels,travel_users,attendee_id):
        travels=[]
        for travel in all_travels:
            traveller = travel_users.filter(attendee_id=attendee_id,travel_id=travel.id).last()
            if traveller:
                travels.append( traveller.status)
            else:
                travels.append('')
        return travels
