from app.models import Attendee, Events, Questions, Answers, Session, SeminarsUsers, Group, AttendeeGroups, Tag, AttendeeTag, Travel, TravelAttendee,\
    RequestedBuddy, Hotel, Room, Locations, MatchLine, Booking, ExportState, Setting, Orders, OrderItems, Payments, \
    RegistrationGroupOwner, CreditUsages
from app.views.gbhelper.error_report_helper import ErrorR
from django.db.models import Count, Max, Sum, F
from django.core import serializers
from django.conf import settings
from boto.s3.key import Key
import json, boto, re, time
from datetime import datetime
from pytz import timezone


class ExportLibrary:
    def prepare_export_data_s3_upload(export_filter_name, qlist, slist, uid, rdate, udate, secret, bid, attGroup, attTag, travel,
                                      hotel_columns, attendees, economy_columns, include_import_header, event_id, admin_id=None):
        response = {'success': False}
        try:
            # attendees
            question_groups = Group.objects.filter(type="question", is_show=1, event_id=event_id).order_by('group_order')
            questions = []
            for group in question_groups:
                questions.extend(Questions.objects.filter(group=group, id__in=qlist).order_by('question_order'))

            allAnswers_init = Answers.objects.filter(question__in=questions, user__in=attendees)
            allAnswers = []
            for ans_item in allAnswers_init:
                if ans_item.question.type == 'checkbox':
                    ans_item.value = ans_item.value.replace('<br>', ',')
                allAnswers.append(ans_item)

            sessionFilterings = Session.objects.filter(id__in=slist).order_by('group__group_order', 'session_order')
            seminarUsers = SeminarsUsers.objects.filter(attendee__in=attendees, session_id__in=slist)
            all_tags = []
            attendee_tags = []
            attendee_groups = []
            all_groups = []
            travel_list = []
            matchLines = []
            defaultGroup = []
            defaults = {}

            if uid:
                defaultGroup.append({'id': "att-uid", "name": "Attendee Id"})
                defaults['uid'] = True

            # defaultGroup.append({'id': "Checked", "name": "Checked"})

            if rdate:
                defaults['rdate'] = True
                defaultGroup.append({'id': "att-rdate", "name": "Registration Date"})

            if udate:
                defaults['udate'] = True
                defaultGroup.append({'id': "att-udate", "name": "Updated Date"})

            if secret:
                defaults['secret'] = True
                defaultGroup.append({'id': "att-secret", "name": "UID (External)"})

            if bid:
                defaults['bid'] = True
                defaultGroup.append({'id': "att-bid", "name": "BID (Badge)"})

            if attGroup:
                defaults['group'] = True
                defaultGroup.append({'id': "att-group", "name": "Attendee Group"})
                attendee_groups = AttendeeGroups.objects.filter(attendee__in=attendees)
                all_groups = Group.objects.filter(event_id=event_id, is_show=1)

            if attTag:
                defaults['tags'] = True
                defaultGroup.append({'id': "att-tag", "name": "Attendee Tag"})
                attendee_tags = AttendeeTag.objects.filter(attendee__in=attendees)
                all_tags = Tag.objects.filter(event_id=event_id)

            travels = []

            if travel:
                travels = Travel.objects.filter(group__event_id=event_id)
                travel_list = TravelAttendee.objects.filter(travel__in=travels, attendee__in=attendees)

            allBookings = []
            hotelBookings = []
            reqBuddy = []
            rooms = []
            hotels = []
            locations = []
            all_event_attendees = []
            hotel_flag = False
            # if export_type == "hotel_edit":
            # hotel_flag=True
            # hotels= Hotel.objects.filter(group__event_id=event_id)
            # rooms = Room.objects.filter(hotel__in=hotels)
            # hotelBookings = Booking.objects.filter(room__in=rooms)
            # allBookings = Booking.objects.filter(room__in=rooms,attendee__in=attendees)
            # matchLines = MatchLine.objects.filter(booking__room__in=rooms)
            # reqBuddy = RequestedBuddy.objects.filter(booking__in=allBookings)
            # locations=Locations.objects.filter(group__event_id=event_id)
            # headers=ExcelView.get_hotel_header(questions)
            # all_event_attendees= Attendee.objects.filter(event_id=event_id, status="registered")

            max_booking_number = 1
            max_actual_room_buddy = 1
            if hotel_columns:
                hotels = Hotel.objects.filter(group__event_id=event_id)
                rooms = Room.objects.filter(hotel__in=hotels)
                hotelBookings = Booking.objects.filter(room__in=rooms)
                allBookings = Booking.objects.filter(room__in=rooms, attendee__in=attendees)
                matchLines = MatchLine.objects.filter(booking__room__in=rooms)
                reqBuddy = RequestedBuddy.objects.filter(booking__in=allBookings)
                locations = Locations.objects.filter(group__event_id=event_id)
                all_event_attendees = Attendee.objects.filter(event_id=event_id, status="registered")

                max_b_number_obj = Booking.objects.filter(attendee_id__in=attendees).values('attendee_id').annotate(
                    total=Count('attendee_id')).aggregate(max_booking_number=Max('total'))
                if max_b_number_obj['max_booking_number']:
                    max_booking_number = max_b_number_obj['max_booking_number']

                if ('rba-col' in hotel_columns or 'rba-checkin-col' in hotel_columns or 'rba-checkout-col' in hotel_columns) and attendees:
                    match_ids = MatchLine.objects.filter(booking__attendee_id__in=attendees).values('match_id')
                    max_a_room_bud = MatchLine.objects.filter(match_id__in=match_ids).values('match_id').annotate(
                        total=Count('match_id')).aggregate(max_total=Max('total'))
                    if max_a_room_bud['max_total']:
                        max_actual_room_buddy = max_a_room_bud['max_total'] - 1

            max_attendee_orders = 1
            event_economy_vats = []
            event_economy_vat_count = 0
            order_vat_percent_sum = dict()
            credit_usages = dict()
            attendee_orders = []
            order_payments = []
            order_owner_excluded_list = []  # ORDER_NUMBER(order owner) text
            group_details = dict()
            if economy_columns:
                if 'order-group-id' in economy_columns:
                    group_owners = RegistrationGroupOwner.objects.filter(owner_id__in=attendees).values('group_id', 'owner_id', 'group__name')
                    for gw in group_owners:
                        group_details[gw['owner_id']] = dict(name=gw['group__name'], members=[], is_owner=True)

                    member_attendees = attendees.filter(registration_group__isnull=False).values('id', 'registration_group__name')
                    for mem_att in member_attendees:
                        group_details[mem_att['id']] = dict(name=mem_att['registration_group__name'], members=[], is_owner=False)
                        order_owner_excluded_list.append(mem_att['id'])

                if 'order-number' in economy_columns and not order_owner_excluded_list:
                    member_attendees = attendees.filter(registration_group__isnull=False).values('id')
                    order_owner_excluded_list = [item['id'] for item in member_attendees]

                attendee_orders = Orders.objects.filter(attendee_id__in=attendees, cost__gt=0)
                attendee_order_numbers = attendee_orders.values('order_number')
                order_payments = Payments.objects.filter(order_number__in=attendee_order_numbers)
                max_order_counter_obj = attendee_orders.values('attendee_id').annotate(total=Count(
                    'attendee_id')).aggregate(max_order_counter=Max('total'))
                if max_order_counter_obj["max_order_counter"]:
                    max_attendee_orders = max_order_counter_obj["max_order_counter"]
                if "vat-xx-percent-sum" in economy_columns:
                    vat_objects = Group.objects.filter(event_id=event_id, type='payment').values('name')
                    for vat in vat_objects:
                        if vat["name"].isdigit():
                            event_economy_vats.append(int(vat["name"]))
                    event_economy_vats.sort()
                    event_economy_vat_count = len(event_economy_vats)

                    order_item_objects = OrderItems.objects.filter(order__order_number__in=attendee_order_numbers).exclude(
                        item_type__in=['rebate', 'adjustment']).annotate(value=Sum((F('cost') * F('vat_rate')) / 100)).values(
                        'order__order_number', 'vat_rate', 'value')
                    for order_item in order_item_objects:
                        order_number = order_item["order__order_number"]
                        if order_vat_percent_sum.get(order_number):
                            order_vat_percent_sum[order_number][int(order_item['vat_rate'])] += order_item['value']
                        else:
                            order_vat_percent_sum[order_number] = dict()
                            for vat in event_economy_vats:
                                order_vat_percent_sum[order_number][vat] = 0
                            order_vat_percent_sum[order_number][int(order_item['vat_rate'])] += order_item['value']

                credit_usage_objects = CreditUsages.objects.filter(order_number__in=attendee_order_numbers).values('order_number').annotate(total_cost=Sum('cost'))
                for credit_item in credit_usage_objects:
                    credit_usages[credit_item['order_number']] = credit_item['total_cost']

            headers = ExportLibrary.get_excel_header(defaultGroup, questions, sessionFilterings, travels, hotel_columns,
                                                     max_booking_number, max_actual_room_buddy, economy_columns, max_attendee_orders,
                                                     event_economy_vats, include_import_header)

            rule_name = ExportLibrary.urlify(export_filter_name)
            event = Events.objects.get(id=event_id)
            public_checker = ''
            if admin_id:
                time_with_timezone = ExportLibrary.getTimezoneNow(event_id)
                file_name = 'exported_files/' + event.name + '/' + rule_name + '_' + str(time_with_timezone.strftime("%Y_%m_%d_%H_%M_%S")) + '.xlsx'
            else:
                public_checker = str(time.time())
                file_name = 'exported_files/' + event.name + '/attendee_' + public_checker + '.xlsx'

            var_list = {
                'headers': json.dumps(headers),
                'file_name': file_name,
                'defaults': json.dumps(defaults),
                'attendees': serializers.serialize('json', attendees),
                'tags': serializers.serialize('json', all_tags),
                'attendee_tags': serializers.serialize('json', attendee_tags),
                'attendee_groups': serializers.serialize('json', attendee_groups),
                'all_groups': serializers.serialize('json', all_groups),
                'questions': serializers.serialize('json', questions),
                'answers': serializers.serialize('json', allAnswers),
                'sessions': serializers.serialize('json', sessionFilterings),
                'seminar_users': serializers.serialize('json', seminarUsers),
                'travels': serializers.serialize('json', travels),
                'travel_list': serializers.serialize('json', travel_list),
                'bookings': serializers.serialize('json', allBookings),
                'rooms': serializers.serialize('json', rooms),
                'hotels': serializers.serialize('json', hotels),
                'locations': serializers.serialize('json', locations),
                'req_buddy': serializers.serialize('json', reqBuddy),
                'matchlines': serializers.serialize('json', matchLines),
                'hotelBookings': serializers.serialize('json', hotelBookings),
                'all_event_attendees': serializers.serialize('json', all_event_attendees),
                'hotel_columns': hotel_columns,
                'max_booking_number': max_booking_number,
                'max_actual_room_buddy': max_actual_room_buddy,
                'hotel_flag': hotel_flag,
                'public_checker': public_checker,
                'export_as_hotel': False,
                'economy_columns': economy_columns,
                'attendee_orders': serializers.serialize('json', attendee_orders),
                'order_payments': serializers.serialize('json', order_payments),
                'order_vat_percent_sum': json.dumps(order_vat_percent_sum),
                'credit_usages': json.dumps(credit_usages),
                'max_attendee_orders': max_attendee_orders,
                'event_economy_vat_count': event_economy_vat_count,
                'group_details': json.dumps(group_details),
                'order_owner_excluded_list': json.dumps(order_owner_excluded_list)
            }

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

            if admin_id:
                export_state = ExportState(file_name=file_name, status=0, event_id=event_id, admin_id=admin_id)
                export_state.save()

            response['success'] = True
            response['public_checker'] = public_checker
        except Exception as ex:
            print('Error occurred to prepare_export_s3_upload')
            ErrorR.efail(ex)
        return response

    def urlify(s):
        s = re.sub(r"[^\w\s]", '_', s)
        s = re.sub(r"\s+", '_', s)
        return s

    def getTimezoneNow(event_id, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone', event_id=event_id)
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            now = datetime.now(timezone_active)
            # print(now.strftime('%Y-%m-%d_%H-%M-%S'))
            return now

    def get_excel_header(defaults, questions, sessions, travels, hotels, max_booking_number,
                         max_actual_room_buddy, economy_columns, max_attendee_orders, event_economy_vats, include_import_header):
        header_row1 = []
        header_row2 = []

        for default in defaults:
            header_row1.append(str(default['id']))
            header_row2.append(default['name'])

        for question in questions:
            header_row1.append("q-" + str(question.id))
            header_row2.append(question.title)

        searchChars = 'ÅÄåäÖö'
        replaceChars = 'AAaaOo'
        trans_table = str.maketrans(searchChars, replaceChars)
        for ssn in sessions:
            header_row1.append("session-" + str(ssn.id))
            header_row2.append((ssn.name).translate(trans_table))

        for travel in travels:
            header_row1.append("travel-" + str(travel.id))
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

        header_row1, header_row2 = ExportLibrary.get_economy_header(economy_columns, header_row1, header_row2, max_attendee_orders, event_economy_vats)
        if include_import_header:
            header_row = [header_row1, header_row2]
        else:
            header_row = [header_row2]
        return header_row

    def get_economy_header(economy_columns, header_row1, header_row2, max_attendee_orders, event_economy_vats):
        if economy_columns:
            for i in range(0, max_attendee_orders):
                if 'order-number' in economy_columns:
                    header_row1.append('e-order_number')
                    header_row2.append('Order Number')
                if 'order-status' in economy_columns:
                    header_row1.append('e-order_status')
                    header_row2.append('Order Status')
                if 'invoice-id' in economy_columns:
                    header_row1.append('e-invoice_id')
                    header_row2.append('Invoice ID')
                if 'invoice-date' in economy_columns:
                    header_row1.append('e-invoice_date')
                    header_row2.append('Invoice Date')
                if 'due-date' in economy_columns:
                    header_row1.append('e-due_date')
                    header_row2.append('Due Date')
                if 'transaction-id' in economy_columns:
                    header_row1.append('e-transaction_id')
                    header_row2.append('Transaction ID')
                if 'transaction-date' in economy_columns:
                    header_row1.append('e-transaction_date')
                    header_row2.append('Transaction Date')
                if 'paid-by-card-invoice' in economy_columns:
                    header_row1.append('e-paid_by')
                    header_row2.append('Paid by Card / Invoice')
                if 'vat-xx-percent-sum' in economy_columns:
                    for vat in event_economy_vats:
                        header_row1.append('e-vat_xx_percent_sum')
                        header_row2.append("{}%".format(vat))
                if 'vat-total-sum' in economy_columns:
                    header_row1.append('e-vat_total_sum')
                    header_row2.append('VAT Total Sum')
                if 'rebate-sum' in economy_columns:
                    header_row1.append('e-rebate_sum')
                    header_row2.append('Rebate Sum')
                if 'credit-usage' in economy_columns:
                    header_row1.append('e-credit_usage')
                    header_row2.append('Credit Usage')
                if 'total-order-sum-excl-vat' in economy_columns:
                    header_row1.append('e-total_sum_excl_vat')
                    header_row2.append('Total Order Sum excl. VAT')
                if 'total-order-sum-incl-vat' in economy_columns:
                    header_row1.append('e-total_sum_incl_vat')
                    header_row2.append('Total Order Sum incl. VAT')
                if 'order-group-id' in economy_columns:
                    header_row1.append('e-order_group_id')
                    header_row2.append('Order Group ID')
        return header_row1, header_row2
