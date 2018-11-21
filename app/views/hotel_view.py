from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import generic
from django.http import HttpResponse
import json
from app.models import Hotel, Room, Locations, Group, RoomAllotment, Booking, RequestedBuddy, Attendee, Match, \
    MatchLine, EmailContents, MessageContents
from app.views.export_lambda import ExcelView
from .room_view import RoomView
from .common_views import GroupView, EventView, CommonContext
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import Http404
from django.db.models import Q
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Avg, Max, Min
from .mail import MailHelper
import logging, traceback
from app.views.gbhelper.language_helper import LanguageH


class HotelView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'hotel_permission'):
            hotelGroup = GroupView.get_hotelGroup(request)
            for group in hotelGroup:
                group.slugName = group.name.replace(" ", "_")
                group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id).order_by(
                    'room_order')
                for room in group.rooms:
                    # room.vat = Group.objects.get(id=room.vat_id)
                    # room.occupancy = RoomView.get_occupancy_modified(room)
                    occupancy = RoomView.find_booking(str(room.id))
                    room.occupancy = occupancy['total_occupancy']

            context = {
                "hotelRooms": hotelGroup
            }
            # NearHotelRooms = Room.objects.all().select_related("hotel").filter(hotel__category="Near By Hotels")
            # FarHotelRooms = Room.objects.all().select_related("hotel").filter(hotel__category="Far Away Hotels")
            return render(request, 'hotel/hotel.html', context)

    def post(self, request):
        response_data = {}
        try:
            with transaction.atomic():
                if EventView.check_permissions(request, 'hotel_permission'):
                    form_data = {
                        "group_id": request.POST.get('group'),
                        "location_id": request.POST.get('location'),
                    }
                    rooms = json.loads(request.POST.get('rooms'))
                    # print(rooms)
                    event_id = request.session['event_auth_user']['event_id']
                    current_language_id = LanguageH.get_current_language_id(event_id)
                    default_language_id = current_language_id
                    name_lang = request.POST.get('name_lang')
                    if 'id' in request.POST:
                        current_language_id = request.POST.get('current_language_id')
                        if current_language_id == default_language_id:
                            form_data["name"] = request.POST.get('name')
                        hotel_id = request.POST.get('id')
                        hotel_old = Hotel.objects.get(id=hotel_id)
                        form_data = LanguageH.update_lang(current_language_id, form_data, "name_lang", name_lang,
                                                          hotel_old.name_lang)
                        Hotel.objects.filter(id=hotel_id).update(**form_data)
                        for room in rooms:
                            savedRoom = RoomView.addRoom(request, hotel_id, room)
                            allotments = json.loads(room.get('allotments'))
                            for allotment_data in allotments:
                                start_date = datetime.strptime(allotment_data[0], '%Y-%m-%d')
                                # end_date = datetime.strptime(allotment_data[1], '%Y-%m-%d')
                                # day_count = (end_date - start_date).days + 1

                                allotment_form_data = {
                                    "allotments": allotment_data[1],
                                    "available_date": datetime.strftime(start_date, '%Y-%m-%d'),
                                    "room_id": savedRoom.id
                                }
                                allotment_cost = allotment_data[2]
                                allotment_vat = allotment_data[3]
                                if len(allotment_cost) > 0 and allotment_cost.isdigit():
                                    allotment_form_data['cost'] = allotment_cost
                                if len(allotment_vat) > 0 and allotment_vat.isdigit():
                                    allotment_form_data['vat'] = allotment_vat
                                elif len(allotment_cost) > 0 and allotment_cost.isdigit() and int(allotment_cost) > 0:
                                    print('Allotment cost does not set VAT')
                                    continue

                                allotment = RoomAllotment(**allotment_form_data)
                                allotment.save()
                        hotel_rooms = Room.objects.filter(hotel_id=hotel_id)
                        roomlist = []
                        for room in hotel_rooms:
                            updated_rooms = room.as_dict()
                            occupancy = RoomView.find_booking(str(room.id))
                            updated_rooms['occupancy'] = occupancy['total_occupancy']
                            # updated_rooms['occupancy'] = RoomView.get_occupancy_modified(room)
                            roomlist.append(updated_rooms)
                        response_data['success'] = 'Hotel Update Successfully'
                        response_data['rooms'] = roomlist
                        response_data['name_lang'] = form_data['name_lang']
                        return HttpResponse(json.dumps(response_data), content_type="application/json")

                    else:
                        form_data["name"] = request.POST.get('name')
                        form_data = LanguageH.insert_lang(current_language_id, form_data, "name_lang", name_lang)
                        hotel = Hotel(**form_data)
                        hotel.save()
                        for room in rooms:
                            savedRoom = RoomView.addRoom(request, hotel.id, room)
                            allotments = json.loads(room.get('allotments'))
                            # return
                            for allotment_data in allotments:
                                start_date = datetime.strptime(allotment_data[0], '%Y-%m-%d')
                                # end_date = datetime.strptime(allotment_data[1], '%Y-%m-%d')
                                # day_count = (end_date - start_date).days + 1

                                allotment_form_data = {
                                    "allotments": allotment_data[1],
                                    "available_date": datetime.strftime(start_date, '%Y-%m-%d'),
                                    "room_id": savedRoom.id
                                }
                                allotment_cost = allotment_data[2]
                                allotment_vat = allotment_data[3]
                                if len(allotment_cost) > 0 and allotment_cost.isdigit():
                                    allotment_form_data['cost'] = allotment_cost
                                if len(allotment_vat) > 0 and allotment_vat.isdigit():
                                    allotment_form_data['vat'] = allotment_vat
                                elif len(allotment_cost) > 0 and allotment_cost.isdigit() and int(allotment_cost) > 0:
                                    print('Allotment cost does not set VAT')
                                    continue
                                allotment = RoomAllotment(**allotment_form_data)
                                allotment.save()

                                # for single_date in (start_date + timedelta(n) for n in range(day_count)):
                                #     print(single_date)
                                #     allotment_form_data = {
                                #         "allotments": allotment_data[2],
                                #         "available_date": datetime.strftime(single_date, '%Y-%m-%d'),
                                #         "room_id": savedRoom.id
                                #     }
                                #     allotment = RoomAllotment(**allotment_form_data)
                                #     allotment.save();
                    response_data['success'] = 'Hotel Create Successfully'
                    response_data['name_lang'] = form_data['name_lang']
                else:
                    response_data['error'] = 'You do not have Permission to do this'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as exception:
            print(traceback.print_exc())
            response_data['error'] = 'Something went wrong'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add(request):
        locationGroup = GroupView.get_locationGroup(request)
        for group in locationGroup:
            group.locations = Locations.objects.all().filter(group_id=group.id)
        category = GroupView.get_hotelGroup(request)
        paymentGroup = GroupView.get_paymentGroup(request)
        context = {
            "locationGroup": locationGroup,
            "category": category,
            "paymentGroup": paymentGroup
        }
        return render(request, 'hotel/add.html', context)

    def edit(request):
        return render(request, 'hotel/add.html')

    # @staticmethod
    # def get_common_dates(booking_list):
    #     booking1_check_in = booking_list[0].check_in
    #     booking1_check_out = booking_list[0].check_out
    #     day_count = (booking1_check_out - booking1_check_in).days + 1
    #     booking1_date_list = []
    #     for single_date in (booking1_check_in + timedelta(n) for n in range(day_count)):
    #         booking1_date_list.append(single_date)
    #
    #     booking2_check_in = booking_list[1].check_in
    #     booking2_check_out = booking_list[1].check_out
    #     day_count2 = (booking2_check_out - booking2_check_in).days + 1
    #     booking2_date_list = []
    #     for single_date2 in (booking2_check_in + timedelta(n) for n in range(day_count2)):
    #         booking2_date_list.append(single_date2)
    #
    #     common_dates = list(set(booking1_date_list).intersection(booking2_date_list))
    #     return common_dates

    @transaction.atomic
    def match(request):
        if EventView.check_read_permissions(request, 'hotel_permission'):
            room_id = request.GET.get('room_id')
            # all_matches = Match.objects.all()
            # for match in all_matches:
            #     if match.all_dates == '':
            #         booking_check_in = match.start_date
            #         booking_check_out = match.end_date
            #         day_count = (booking_check_out - booking_check_in).days + 1
            #         all_dates = []
            #         for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
            #                 all_dates.append(str(single_date))
            #         print('all_dates')
            #         print(all_dates)
            #         Match.objects.filter(id=match.id).update(all_dates=json.dumps(all_dates))
            context = RoomView.get_matched_pair(request, room_id)
            common_context = CommonContext.get_all_common_context(request)

            context.update(common_context)
            context['room_id'] = room_id
            hotel_group = GroupView.get_hotelGroup(request)
            for group in hotel_group:
                group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
                for room in group.rooms:
                    # room.vat = Group.objects.get(id=room.vat_id)
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
            event_id = request.session['event_auth_user']['event_id']
            email_lists = EmailContents.objects.filter(template__event_id=event_id, is_show=1).values('id', 'name')
            msg_lists = MessageContents.objects.filter(event_id=event_id, is_show=1).values('id', 'name')
            context['attendee_view_email_lists'] = email_lists
            context['attendee_view_msg_lists'] = msg_lists
            context['hotel_groups'] = hotel_group
            return render(request, 'hotel/match.html', context)

    @transaction.atomic
    def match_partial(request):
        room_id = request.GET.get('room_id')
        context = RoomView.get_matched_pair(request, room_id)
        common_context = CommonContext.get_all_common_context(request)

        context.update(common_context)
        hotel_group = GroupView.get_hotelGroup(request)
        for group in hotel_group:
            group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
            for room in group.rooms:
                # room.vat = Group.objects.get(id=room.vat_id)
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
        context['hotel_groups'] = hotel_group
        return render(request, 'hotel/match_partial.html', context)

    @transaction.atomic
    def pair_up(request):
        booking_ids = json.loads(request.POST.get('bookings'))
        response = HotelView.pair_up_details(request, booking_ids)

        return HttpResponse(json.dumps(response), content_type="application/json")

    @transaction.atomic
    def pair_up_details(request, booking_ids):
        match_buddies = []
        response = {}
        if len(booking_ids) > 1:
            first_booking = Booking.objects.get(pk=booking_ids[0])
            room_id = first_booking.room_id
            beds = first_booking.room.beds
            bookings = Booking.objects.filter(id__in=booking_ids)
            attendee_count = []
            all_pair_up_attendes = []
            for attendee_booking in bookings:
                all_pair_up_attendes.append(attendee_booking)
                if attendee_booking.attendee_id not in attendee_count:
                    attendee_count.append(attendee_booking.attendee_id)
            if len(bookings) <= beds or len(attendee_count) <= beds:
                common_dates = RoomView.get_common_dates(bookings)
                print(common_dates)
                if len(common_dates) > 0:
                    # room distribution checking
                    start_date = min(common_dates)
                    end_date = max(common_dates) + timedelta(days=1)
                    previous_matches_room = Match.objects.filter(Q(room_id=room_id))
                    previous_total = previous_matches_room.count()
                    # min_allotment = RoomAllotment.objects.values('allotments').filter(room_id=room_id, available_date__in=common_dates).aggregate(Min('allotments'))['allotments__min']
                    # print(min_allotment)
                    # if previous_total < min_allotment:
                    check_allotment = RoomView.check_allotment(request, room_id, common_dates)
                    if check_allotment:
                        all_dates = []
                        for my_date in common_dates:
                            all_dates.append(str(my_date))
                        match = Match(room_id=room_id, start_date=start_date, end_date=end_date,
                                      all_dates=json.dumps(all_dates))
                        match.save()
                        for booking in bookings:
                            match_line = MatchLine(match=match, booking_id=booking.id)
                            match_line.save()
                            match_buddies.append(match_line.as_dict())
                        response['success'] = True
                        response['message'] = 'Successfully paired up'
                        if len(match_buddies) > 1:
                            for match_attendee in match_buddies:
                                matchlist = match_buddies[:]
                                matchlist.remove(match_attendee)
                                # HotelView.send_email(request, match_attendee['booking']['attendee'], 'email/match_buddy.html', matchlist)
                        # end room distribution checking
                        context = {
                            'booking_list': all_pair_up_attendes
                        }
                        pair_up_view = render_to_string('hotel/pair_up.html', context)
                        response['view'] = pair_up_view
                    else:
                        response['success'] = False
                        response['message'] = 'Maximum number of paired up for this room given the time range'
                else:
                    response['success'] = False
                    response['message'] = 'No common date(s) to pair up'
            else:
                response['success'] = False
                response['message'] = 'Room capacity exceeds the selected bookings'
        else:
            response['success'] = False
            response['message'] = 'Select at least 2 attendees to pair up'
        return response

    @transaction.atomic
    def break_up(request):
        booking_ids = json.loads(request.POST.get('bookings'))
        response = {}
        if len(booking_ids) > 1:
            bookings = Booking.objects.filter(id__in=booking_ids)
            match_line = MatchLine.objects.filter(booking_id=booking_ids[0])
            for match in match_line:
                match_id = match.match_id
                MatchLine.objects.filter(booking_id__in=booking_ids).delete()
                Match.objects.get(pk=match_id).delete()
                bookings.update(broken_up=True)
            response['success'] = True
            response['message'] = 'Successfully broken up'
            unmatched_bookings_data = []
            unmatched_bookings = Booking.objects.filter(id__in=booking_ids)
            for unmatched_book in unmatched_bookings:
                unmatched_bookings_data.append(unmatched_book)
            response['data'] = render_to_string('hotel/break_up.html',
                                                context={'unmatched_bookings': unmatched_bookings_data})
        else:
            response['success'] = False
            response['message'] = 'Invalid selection'
        return HttpResponse(json.dumps(response), content_type="application/json")

    def check_match(request):
        response = {}
        booking_id = request.POST.get('booking_id')
        room_id = request.POST.get('room_id')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        old_booking = Booking.objects.get(id=booking_id)
        sql = 'select m.* from match_line m where booking_id=' + str(
            booking_id) + ' and (select count(*) from `match_line` n where m.match_id=n.match_id)>1;'
        get_match = MatchLine.objects.raw(
            sql
        )
        booking_matches = []
        match_attendees = ''
        response['status'] = 0
        if len(list(get_match)) > 0:
            matches = MatchLine.objects.filter(match_id=get_match[0].match_id)
            for match in matches:
                booking_matches.append(match.booking_id)
                if match.booking_id != int(booking_id):
                    match_attendees = match_attendees + str(match.booking.attendee.firstname) + ' ' + str(
                        match.booking.attendee.lastname)
                    # if match.id != matches[len(matches)-1].id:
                    #     match_attendees = match_attendees + ' and '
            a_list = []
            all_dates = []
            hotel_info = Room.objects.get(id=int(room_id))
            attendee_name = str(old_booking.attendee.firstname) + ' ' + str(old_booking.attendee.lastname)
            if hotel_info.beds < len(booking_matches):
                response[
                    'message'] = 'This will break the match between ' + attendee_name + ' and ' + match_attendees + ', are you sure you want to continue?'
                response['status'] = 1
            else:
                if len(booking_matches) > 1:
                    booking_list = Booking.objects.filter(id__in=booking_matches)
                    for booking in booking_list:
                        if int(booking_id) == int(booking.id):
                            booking_check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
                            booking_check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
                        else:
                            booking_check_in = booking.check_in
                            booking_check_out = booking.check_out
                        print(booking_check_in)
                        print(booking_check_out)
                        day_count = (booking_check_out - booking_check_in).days
                        print('day_count')
                        print(day_count)
                        booking_date_list = []
                        for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                            booking_date_list.append(single_date)
                            all_dates.append(single_date)
                        a_list.append(booking_date_list)

                    for i in range(0, len(a_list)):
                        for j in range(1, len(a_list)):
                            all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
                hotel_name = str(hotel_info.hotel.name) + '-' + str(hotel_info.description)
                if int(room_id) != int(old_booking.room_id) or len(all_dates) == 0:
                    response[
                        'message'] = 'This will break the match between ' + attendee_name + ' and ' + match_attendees + ', are you sure you want to continue?'
                    response[
                        'date_message'] = 'This will break the match between ' + attendee_name + ' and ' + match_attendees + ', are you sure you want to continue?'
                    response['status'] = 1
                    attendee_booking = {}
                    attendee_booking['check_in'] = check_in
                    attendee_booking['check_out'] = check_out
                    attendee_booking['room_id'] = room_id
                    attendee_booking_available = HotelView.check_available_room(attendee_booking, 0)
                    print("attendee_booking_available")
                    print(attendee_booking_available)
                    if attendee_booking_available:
                        matche_buddy = MatchLine.objects.filter(match_id=get_match[0].match_id).exclude(
                            booking_id=booking_id)
                        buddy_count = 0
                        buddy_availabe = True
                        for buddy in matche_buddy:
                            buddy_count = buddy_count + 1
                            buddy_booking = {}
                            buddy_booking['check_in'] = buddy.booking.check_in.strftime('%Y-%m-%d')
                            buddy_booking['check_out'] = buddy.booking.check_out.strftime('%Y-%m-%d')
                            buddy_booking['room_id'] = room_id
                            buddy_booking_available = HotelView.check_available_room(buddy_booking, buddy_count)
                            if not buddy_booking_available:
                                buddy_availabe = False
                                break
                        if buddy_availabe:
                            response[
                                'message'] = 'You are about to move ' + attendee_name + ' to ' + hotel_name + '. Would you like to move ' + match_attendees + ' to ' + hotel_name + ' as well and match ' + attendee_name + ' and ' + match_attendees + ' there as well?'
                            response['status'] = 2
                elif len(all_dates) == 0:
                    response[
                        'message'] = 'This will break the match between ' + attendee_name + ' and ' + match_attendees + ', are you sure you want to continue?'
                    response['status'] = 1
        response['success'] = True
        return HttpResponse(json.dumps(response), content_type="application/json")

    def check_available_room(booking, buddy_count):
        start_date = datetime.strptime(booking['check_in'], '%Y-%m-%d')
        end_date = datetime.strptime(booking['check_out'], '%Y-%m-%d')
        day_count = (end_date - start_date).days
        room = Room.objects.get(id=booking['room_id'])
        available = True
        for single_date in (start_date + timedelta(n) for n in range(day_count)):
            current_date = datetime.strftime(single_date, '%Y-%m-%d')
            if current_date != str(end_date).split(' ')[0]:
                allotments = RoomAllotment.objects.filter(available_date=current_date, room_id=booking['room_id'])
                if allotments.count():
                    get_bookings = Booking.objects.filter(room_id=booking['room_id'], check_in__lte=current_date,
                                                          check_out__gt=current_date).count()
                    get_bookings = get_bookings + buddy_count
                    total_beds = room.beds * allotments[0].allotments
                    if get_bookings >= total_beds:
                        available = False
                else:
                    available = False
        return available

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            id = request.POST.get('id')
            rooms = RoomView.get_rooms(id)
            for room in rooms:
                deletedRoom = Room.objects.get(id=room.id)
                deletedRoom.delete()
            hotel = Hotel.objects.get(id=id)
            hotel.delete()
            response_data['success'] = 'Hotel Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def search(request):
        search_key = request.POST.get('search_key')
        if search_key:
            hotels_group = Group.objects.filter(
                Q(type="hotel", is_show=1, event_id=request.session['event_auth_user']['event_id']) & (
                    Q(hotel__name__icontains=search_key))).order_by('group_order').distinct()

        else:
            hotels_group = Group.objects.filter(
                Q(type="hotel", is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by(
                'group_order').distinct()
        for group in hotels_group:
            group.slugName = group.name.replace(" ", "_")
            group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id,
                                                                            hotel__name__icontains=search_key).order_by(
                'room_order')
            for room in group.rooms:
                # room.vat = Group.objects.get(id=room.vat_id)
                occupancy = RoomView.find_booking(str(room.id))
                room.occupancy = occupancy['total_occupancy']
        context = {
            "hotelsGroups": hotels_group
        }
        return render(request, 'hotel/hotel_result.html', context)

    def send_email(request, attendee_obj, file_path, matchlist):
        buddies = []
        for match in matchlist:
            buddies.append(match['booking']['attendee']['email'])
        context = {
            "buddies": buddies
        }
        logger = logging.getLogger(__name__)
        subject = "GT-ROOM BUDDY"
        sender_mail = "mahedi@workspaceit.com"
        if attendee_obj['group']['event']['id'] == 11:
            subject = "ROOM BUDDY"
            sender_mail = "mahedi@workspaceit.com"
        logger.debug("-----------------sender Email------------------------")
        logger.debug(sender_mail)
        to = attendee_obj['email']
        MailHelper.mail_send(file_path, context, subject, to, sender_mail)
        return "ok"

    def generate_hotel_report_excel(request):
        hotels = Hotel.objects.filter(group__event_id=request.session['event_auth_user']['event_id'])
        hotel_rows = []
        for hotel in hotels:
            rooms = RoomView.get_rooms(hotel.id)
            for room in rooms:
                hotel_rows.append([str(hotel.name) + " - " + str(room.description)])

                hotel_rows.append(
                    ['Date', 'Allotments', 'Matched Pairs', 'Matched Singles', 'Unmatched', 'Total', 'Best Scenario',
                     'Occupancy', 'Avalible'])
                room_allotments = room.allotment_list
                for allotment in room_allotments['details']:
                    hotel_rows.append([allotment['available_date'], allotment['allotments'], allotment['matched_pairs'],
                                       allotment['matched_singles'], allotment['unmatched'], allotment['total'],
                                       allotment['best_scenario'], str(allotment['occupancy'])+"%", allotment['free']])
        return ExcelView.write_excel(hotel_rows, "Hotel report.xlsx")


class HotelListView(BaseDatatableView):
    model = Hotel
    columns = ['id', 'name', 'category', 'location_id', 'id']
    order_columns = ['id', 'name', 'category', 'location_id', 'id']


class HotelDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            hotel = Hotel.objects.filter(id=pk, group__event_id=self.request.session['event_auth_user']['event_id'])
            if hotel.exists():
                return hotel[0]
            else:
                raise Http404
        except Hotel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if EventView.check_read_permissions(request, 'hotel_permission'):
            hotel = self.get_object(pk)
            rooms = RoomView.get_rooms(pk)
            locationGroup = GroupView.get_locationGroup(request)
            for group in locationGroup:
                group.locations = Locations.objects.all().filter(group_id=group.id)
            category = GroupView.get_hotelGroup(request)
            paymentGroup = GroupView.get_paymentGroup(request)
            context = {
                'hotel': hotel,
                'rooms': rooms,
                'locationGroup': locationGroup,
                'category': category,
                'paymentGroup': paymentGroup
            }
            context.update(LanguageH.get_current_and_all_presets(request))
            return render(request, 'hotel/edit.html', context)


class HotelBooking(generic.DetailView):

    def remove_booking(id):
        attendee_booking = Booking.objects.get(id=id)
        attendee_booking.delete()
        sql = 'SELECT *, count(match_id) as d FROM `match_line` group by match_id having d=1'
        single_match = MatchLine.objects.raw(
            sql
        )
        for match in single_match:
            print('match_id')
            print(match.match_id)
        return True
