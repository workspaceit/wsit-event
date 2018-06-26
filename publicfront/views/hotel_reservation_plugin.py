import json
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render
from app.views.attendee_view import AttendeeView
from app.views.room_view import RoomView

from app.models import Attendee, ElementsAnswers, Room, Booking, ActivityHistory, RequestedBuddy, RoomAllotment, \
    MatchLine
from django.db.models import Q

from publicfront.views.lang_key import LanguageKey
from django.db.models.functions import Concat
from django.db.models import Value
from app.views.gbhelper.economy_library import EconomyLibrary


class HotelReservationPlugin:
    def buddy_list(request, *args, **kwargs):
        search_key = request.POST.get('q')
        event_id = request.session['event_id']
        # callback_id = request.GET.get('$callback')
        # search_key = request.GET.get('$filter')
        # try:
        #     search_key = eval(search_key.split('(')[1].split(',')[0]).strip()
        # except:
        #     search_key = search_key.split('(')[1].split(',')[0] + "'"
        #     search_key = eval(search_key).strip()

        match_line_attendee = MatchLine.objects.filter(booking__attendee__event_id=event_id).values('booking__attendee')
        match_line_attendee = [m_l_att['booking__attendee'] for m_l_att in match_line_attendee]

        if 'is_user_login' in request.session and request.session['is_user_login'] == True:
            # attendees = Attendee.objects.filter(Q(event_id=event_id) & Q(status="registered") & (
            #     Q(firstname__icontains=search_key) | Q(lastname__icontains=search_key) | Q(
            #         email__istartswith=search_key))).exclude(id__in=match_line_attendee).exclude(id=request.session['event_user']['id'])
            attendees = Attendee.objects.annotate(text=Concat('firstname', Value(' '), 'lastname')).filter(Q(event_id=event_id) & Q(
                status="registered") & (Q(firstname__icontains=search_key) | Q(lastname__icontains=search_key) | Q(text__icontains=search_key)))\
                .exclude(id__in=match_line_attendee).exclude(id=request.session['event_user']['id']).values('id', 'text')
        else:
            # attendees = Attendee.objects.filter(Q(event_id=event_id) & Q(status="registered") & (
            #     Q(firstname__icontains=search_key) | Q(lastname__icontains=search_key) | Q(
            #         email__istartswith=search_key))).exclude(id__in=match_line_attendee)
            attendees = Attendee.objects.annotate(text=Concat('firstname', Value(' '), 'lastname')).filter(Q(event_id=event_id) & Q(status="registered") & (
                Q(firstname__icontains=search_key) | Q(lastname__icontains=search_key) | Q(text__icontains=search_key)))\
                .exclude(id__in=match_line_attendee).values('id', 'text')

        # main_data = [{'id': att['id'], 'name': att['text']} for att in attendees]
        # data = {
        #     'd': {
        #         'results': main_data,
        #         '__count': len(main_data)
        #     }
        # }

        data = json.dumps({ "results": list(attendees)})
        # data = callback_id + '(' + json.dumps(data) + ')'
        return HttpResponse(data, content_type='application/json')

    def get_partial_allow_element(request, *args, **kwargs):
        context = {}
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        user_id = request.POST.get('user_id')
        context['box_id'] = box_id
        if user_id:
            context['uid_text'] = '-u{}'.format(user_id)
        else:
            context['uid_text'] = ''
        partial_counter = request.POST.get('partial_counter')
        try:
            element_answers = ElementsAnswers.objects.filter(box_id=box_id, page_id=page_id)
        except:
            pass

        if element_answers:
            for answer in element_answers:
                if answer.element_question.question_key == 'hotel_reservation_default_check_in_date':
                    context['default_check_in_date'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_default_check_out_date':
                    context['default_check_out_date'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_hotel_groups':
                    hotel_group = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_force_hotel_room_type':
                    context['force_hotel_room_type'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_name':
                    context['optional_field_name'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_description':
                    context['optional_field_description'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_location':
                    context['optional_field_location'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_cost_excl_vat':
                    context['optional_field_cost_excl_vat'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_cost_incl_vat':
                    context['optional_field_cost_incl_vat'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_vat_percent':
                    context['optional_field_vat_percent'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_vat_amount':
                    context['optional_field_vat_amount'] = eval(answer.answer)

            hotel_info = []
            economy_currency_lang = LanguageKey.catch_lang_key_multiple(request, 'economy', ['economy_txt_currency'])
            context['currency_text'] = economy_currency_lang['langkey']['economy_txt_currency']
            if hotel_group and context['force_hotel_room_type'] == 'do-not-force':
                hotel_rooms = Room.objects.filter(hotel__group__in=json.loads(hotel_group)).order_by('hotel__group__group_order','room_order')
                for h_room_item in hotel_rooms:
                    room_obj = h_room_item
                    h_room_item = LanguageKey.get_room_data_by_language(request, h_room_item)
                    result = RoomView.find_booking(str(h_room_item.id))
                    result_oc = True if result['total_occupancy'] > 99 else False
                    # room_allotments = RoomAllotment.objects.filter(room_id=h_room_item.id)
                    # room_allotmentsDates = [ra.available_date.strftime("%Y-%m-%d") for ra in room_allotments]
                    room_allotmentsDates = []
                    for ra in result['details']:
                        if ra['occupancy'] < 100:
                            room_allotmentsDates.append(ra['available_date'])

                    # adding 1 extra date for more than allotment 1 check-out date
                    if room_allotmentsDates:
                        extra_date = datetime.strptime(room_allotmentsDates[-1], '%Y-%m-%d')
                        extra_date = extra_date + timedelta(days=1)
                        extra_date = extra_date.strftime('%Y-%m-%d')
                        room_allotmentsDates.append(extra_date)
                    else:
                        result_oc = True

                    hotel_info.append(
                        {'id': h_room_item.id, 'hotel': h_room_item.hotel.name, 'description': h_room_item.description,
                         'beds': h_room_item.beds,
                         'location': h_room_item.hotel.location.name, 'occupancy': result_oc,
                         'available_dates': json.dumps(room_allotmentsDates),
                         'cost_excl_vat': room_obj.cost_excluded_vat(), 'cost_incl_vat': room_obj.cost_included_vat(),
                         'vat_percentage': room_obj.vat, 'vat_amount': room_obj.get_vat_amount()
                         })

                context['hotel_info'] = hotel_info
            else:
                hotel_room = Room.objects.filter(id=context['force_hotel_room_type'])[0]
                context['force_hotel_room_selection'] = True
                room_obj = hotel_room
                hotel_room = LanguageKey.get_room_data_by_language(request, hotel_room)
                result = RoomView.find_booking(str(hotel_room.id))
                result_oc = True if result['total_occupancy'] == 100 else False
                # room_allotments = RoomAllotment.objects.filter(room_id=hotel_room.id)
                # room_allotmentsDates = [ra.available_date.strftime("%Y-%m-%d") for ra in room_allotments]
                room_allotmentsDates = []
                for ra in result['details']:
                    if ra['occupancy'] < 100:
                        room_allotmentsDates.append(ra['available_date'])

                # adding 1 extra date for more than allotment 1 check-out date
                if room_allotmentsDates:
                    extra_date = datetime.strptime(room_allotmentsDates[-1], '%Y-%m-%d')
                    extra_date = extra_date + timedelta(days=1)
                    extra_date = extra_date.strftime('%Y-%m-%d')
                    room_allotmentsDates.append(extra_date)
                else:
                    result_oc = True

                context['hotel_info'] = [
                    {'id': hotel_room.id, 'hotel': hotel_room.hotel.name, 'description': hotel_room.description,
                     'beds': hotel_room.beds,
                     'location': hotel_room.hotel.location.name, 'occupancy': result_oc,
                     'available_dates': json.dumps(room_allotmentsDates),
                     'cost_excl_vat': room_obj.cost_excluded_vat(), 'cost_incl_vat': room_obj.cost_included_vat(),
                     'vat_percentage': room_obj.vat, 'vat_amount': room_obj.get_vat_amount()
                     }]
        else:
            return HttpResponse('false', content_type='application/json')

        # it's for partial allow counter. Which is needed for diff. to classes and ids
        context['partial_counter'] = partial_counter
        context['language'] = LanguageKey.catch_lang_key_obj(request, "hotel-reservation")
        return render(request, 'public/element/hotel_res_partial_allow_element.html', context)

    def make_reservation(user_status, user_id, event_id, hotel_stays, order_number=None):
        response = dict(result=False, order_number=None)
        if user_status == 'exist':
            existig_bookings = Booking.objects.filter(attendee_id=user_id)
            existig_bookings2 = [b for b in existig_bookings]
            if existig_bookings:
                booking_ids = [b.room.id for b in existig_bookings2]
            else:
                booking_ids = []

            room_id_list = [int(r_id['hotelroomid']) if r_id['hotelroomid'].isdigit() else 0 for r_id in hotel_stays]
            # else 0, here 0 doesn't effect anything

            for booking_room_id in booking_ids:
                if booking_room_id not in room_id_list:
                    delete_booking = existig_bookings2[booking_ids.index(booking_room_id)]
                    print('delete booking {}'.format(str(delete_booking.id)))
                    delete_booking_id = delete_booking.id
                    delete_booking_room_id = delete_booking.room_id
                    del_book_allotments_dates = [delete_booking.check_in + timedelta(n) for n in
                                                 range(0, (delete_booking.check_out - delete_booking.check_in).days)]
                    delete_booking.delete()
                    order_detail = EconomyLibrary.get_order_id(user_id, 'hotel', delete_booking_room_id, delete_booking_id)
                    if order_detail:
                        EconomyLibrary.remove_item_from_order(event_id, user_id, order_detail['order_id'], delete_booking_room_id,
                                                              delete_booking_id, None, del_book_allotments_dates)

        for index, stay in enumerate(hotel_stays):
            print(stay)
            room_id = stay.get("hotelroomid")
            if room_id == 'no-hotel':
                continue
            room_id = int(room_id)
            check_in = stay["checkin"]
            check_out = stay["checkout"]
            buddies = stay["buddyids"]

            if room_id > 0:
                booking_info = {'check_in': check_in, 'check_out': check_out, 'room_id': room_id}
                available = AttendeeView.check_available_room(user_id, booking_info)
                print('available: {}'.format(available))
                print('******************')
                try:
                    if user_status == 'new':
                        if available:
                            order_place_result = HotelReservationPlugin.make_booking(user_id, order_number, room_id, check_in, check_out, event_id, buddies, index)
                            if order_place_result:
                                response['result'] = True
                                response['order_number'] = order_place_result
                        else:
                            print('Room is not available for stay ' + str(index + 1))
                            response['result'] = False
                            return response
                    elif user_status == 'exist':
                        if room_id in booking_ids:
                            remove_item_index = booking_ids.index(room_id)
                            existig_booking = existig_bookings2[remove_item_index]

                            previous_booking_day_count = (existig_booking.check_out - existig_booking.check_in).days
                            new_booking_day_count = (datetime.strptime(check_out, '%Y-%m-%d') - datetime.strptime(check_in, '%Y-%m-%d')).days
                            old_check_in = existig_booking.check_in
                            old_check_out = existig_booking.check_out
                            existig_booking.check_in = check_in
                            existig_booking.check_out = check_out
                            existig_booking.save()
                            booking_ids.pop(remove_item_index)
                            existig_bookings2.pop(remove_item_index)

                            RequestedBuddy.objects.filter(booking_id=existig_booking.id).delete()
                            for buddy in buddies:
                                if buddy.isdigit():
                                    try:
                                        requested_buddy = RequestedBuddy(booking_id=existig_booking.id, buddy_id=buddy)
                                        requested_buddy.save()
                                    except:
                                        pass
                                else:
                                    buddy_array = buddy.split(' ')
                                    attendee_id = 0
                                    if len(buddy_array) > 1:
                                        attendees = Attendee.objects.filter(firstname__startswith=buddy_array[0], event_id=event_id,status="registered")
                                        for attendee in attendees:
                                            if attendee.firstname + ' '+ attendee.lastname == buddy:
                                                attendee_id = attendee.id

                                    if attendee_id == 0:
                                        requested_buddy = RequestedBuddy(booking_id=existig_booking.id, exists=False,
                                                                         email=buddy)
                                    else:
                                        requested_buddy = RequestedBuddy(booking_id=existig_booking.id, buddy_id=attendee_id)
                                        requested_buddy.save()
                                    requested_buddy.save()

                            str_date_to_date = lambda value: datetime.strptime(value, '%Y-%m-%d').date()
                            new_check_in = str_date_to_date(check_in)
                            new_check_out = str_date_to_date(check_out)
                            old_booking_dates = HotelReservationPlugin.get_date_list(old_check_in, old_check_out)
                            new_booking_dates = HotelReservationPlugin.get_date_list(new_check_in, new_check_out)
                            new_extra_booking_dates = list(set(new_booking_dates) - set(old_booking_dates))
                            if previous_booking_day_count != new_booking_day_count:
                                day_difference = 0
                                if new_booking_day_count > previous_booking_day_count:
                                    day_difference = new_booking_day_count - previous_booking_day_count

                                EconomyLibrary.update_hotel_cost(event_id, user_id, room_id, new_booking_day_count, day_difference, existig_booking.id, None, new_extra_booking_dates)
                            else:
                                if old_check_in != new_check_in or old_check_out != new_check_out:
                                    EconomyLibrary.update_hotel_for_allotment(event_id, user_id, room_id, existig_booking.id, old_booking_dates, new_booking_dates)
                        else:
                            if available:
                                order_place_result = HotelReservationPlugin.make_booking(user_id, order_number, room_id, check_in, check_out, event_id, buddies, index)
                                if order_place_result:
                                    response['result'] = True
                                    response['order_number'] = order_place_result
                            else:
                                print('Room is not available for stay ' + str(index + 1))
                                response['result'] = False
                                return response
                except Exception as e:
                    from app.views.gbhelper.error_report_helper import ErrorR
                    ErrorR.efail(e)
                    response['result'] = False
                    return response
            else:
                print('Room not selected for stay ' + str(index + 1))
                response['result'] = False
                return response

        if user_status == 'exist':
            for eb in existig_bookings2:
                if eb.id:
                    eb_room_id = eb.room_id
                    eb_booking_id = eb.id
                    del_book_allotments_dates = HotelReservationPlugin.get_date_list(eb.check_in, eb.check_out)
                    eb.delete()
                    order_detail = EconomyLibrary.get_order_id(user_id, 'hotel', eb_room_id, eb_booking_id)
                    if order_detail:
                        EconomyLibrary.remove_item_from_order(event_id, user_id, order_detail['order_id'], eb.room_id,
                                                              eb_booking_id, None, del_book_allotments_dates)

        response['result'] = True
        return response

    def make_booking(user_id, order_number, room_id, check_in, check_out, event_id, buddies, index):
        booking = Booking(attendee_id=user_id, room_id=room_id, check_in=check_in, check_out=check_out)
        booking.save()
        activity_history = ActivityHistory(attendee_id=user_id, activity_type='register',
                                           category='room', room_id=room_id, event_id=event_id)
        activity_history.save()
        for buddy in buddies:
            if buddy.isdigit():
                try:
                    requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                    requested_buddy.save()
                except:
                    pass
            else:
                requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False, email=buddy)
                requested_buddy.save()
        print('Success for allow ' + str(index + 1))

        booking_day_count = (datetime.strptime(booking.check_out, '%Y-%m-%d') - datetime.strptime(booking.check_in, '%Y-%m-%d')).days
        print('Got order_number {}'.format(order_number))
        result = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='hotel', item_id=room_id, order_number=order_number, booking_day_count=booking_day_count, booking_id=booking.id)
        if result == None:
            raise Exception('error in economy for hotel')
        elif result:
            return result.get('order_number')

    def get_date_list(check_in, check_out):
        return [check_in + timedelta(n) for n in range(0, (check_out - check_in).days)]
