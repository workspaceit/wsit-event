from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Room, Group, Hotel, Booking, RoomAllotment, MatchLine, Attendee, Match, RequestedBuddy
from django.http import Http404
import json
from .common_views import GroupView, EventView
from django.db.models import Max
from datetime import datetime, timedelta
from django.db import connection
import math
from django.db.models.aggregates import Count
from django.db.models import Q
import logging
from app.views.gbhelper.language_helper import LanguageH


class RoomView(generic.DetailView):
    def get(self, request):
        return render(request, '')

    def post(self, request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            form_data = {
                "beds": request.POST.get('bed'),
                "cost": request.POST.get('cost') if request.POST.get('cost') else 0,
                "vat": request.POST.get('vat') if request.POST.get('vat') else None,
                "pay_whole_amount": True if request.POST.get('pay_whole_hotel_amount') == 'true' else False
            }
            event_id = request.session['event_auth_user']['event_id']
            current_language_id = LanguageH.get_current_language_id(event_id)
            default_language_id = current_language_id
            description_lang = request.POST.get('description_lang')
            if 'id' in request.POST:
                current_language_id = request.POST.get('current_language_id')
                if current_language_id == default_language_id:
                    form_data["description"] = request.POST.get('description')
                room_id = request.POST.get('id')
                room_old = Room.objects.get(id=room_id)
                form_data = LanguageH.update_lang(current_language_id, form_data, "description_lang", description_lang,
                                                  room_old.description_lang)
                Room.objects.filter(id=room_id).update(**form_data)

                allotments = json.loads(request.POST.get('allotments'))
                for allotment_data in allotments:
                    # start_date = datetime.strptime(allotment_data[0], '%Y-%m-%d')
                    # end_date = datetime.strptime(allotment_data[1], '%Y-%m-%d')
                    # day_count = (end_date - start_date).days + 1
                    #
                    # for single_date in (start_date + timedelta(n) for n in range(day_count)):
                    # print(single_date)
                    #
                    #
                    allotment_form_data = {
                        "allotments": allotment_data[1],
                        "available_date": str(allotment_data[0]),
                        "room_id": room_id
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

                # update_allotment_datas
                allotment_update_res = []
                updateble_allotments = json.loads(request.POST.get('update_allotment_datas'))
                for allotment_data in updateble_allotments:
                    allotment_cost = 0
                    allotment_vat = None
                    if len(allotment_data[2]) > 0 and allotment_data[2].isdigit():
                        allotment_cost = allotment_data[2]
                    if len(allotment_data[3]) > 0 and allotment_data[3].isdigit():
                        allotment_vat = allotment_data[3]
                    elif allotment_cost:
                        print('Allotment cost does not has VAT.')
                        #continue
                    allotment_update_res.append(
                        RoomView.allotment_update_with_conditions(int(allotment_data[0]), int(allotment_data[1]),
                                                                  "update", allotment_cost, allotment_vat))

                response_data['allotment_update_result'] = allotment_update_res
                hotel_room = Room.objects.get(id=room_id)
                room = hotel_room.as_dict()
                occupancy = RoomView.find_booking(str(room_id))
                room['occupancy'] = occupancy['total_occupancy']
                response_data['success'] = 'Room Update Successfully'
                response_data['room'] = room
                return HttpResponse(json.dumps(response_data), content_type="application/json")

        else:
            response_data['error'] = 'You do not have Permission to do this'
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def addRoom(request, hotelId, room):
        room_order = RoomView.get_rooms_order(hotelId)
        form_data = {
            "description": room['description'],
            "beds": room['bed'],
            "cost": room.get('cost') if room.get('cost') else 0,
            "vat": room.get('vat') if room.get('vat') else None,
            "pay_whole_amount": room.get('pay_whole_hotel_amount'),
            "hotel_id": hotelId,
            "room_order": room_order,
        }
        event_id = request.session['event_auth_user']['event_id']
        current_language_id = LanguageH.get_current_language_id(event_id)
        form_data = LanguageH.insert_lang(current_language_id, form_data, "description_lang",
                                          room['description'].replace("'", "&apos;").replace('"', "&quot;"))
        room = Room(**form_data)
        room.save()
        return room

    def get_rooms(hotelId):
        try:
            rooms = Room.objects.filter(hotel_id=hotelId)
            for room in rooms:
                # room.vat = Group.objects.get(id=room.vat_id)
                room.allotments = RoomAllotment.objects.filter(room_id=room.id)
                # room.occupancy = RoomView.get_occupancy_modified(room)
                occupancy = RoomView.find_booking(str(room.id))
                room.occupancy = occupancy['total_occupancy']
                room.allotment_list = occupancy
            return rooms
        except Room.DoesNotExist:
            raise Http404

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            id = request.POST.get('id')
            is_booked = Booking.objects.filter(room_id=id).count()
            if is_booked:
                response_data['error'] = 'This Room is in booking List'
            else:
                room = Room.objects.get(id=id)
                room.delete()
                response_data['success'] = 'Room Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def set_rooms_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            rooms_order = json.loads(request.POST.get('rooms_order'))
            for room in rooms_order:
                Room.objects.filter(id=room['room_id']).update(room_order=room['order'])
            response_data['success'] = 'Room Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_rooms_order(hotelId):
        group = Hotel.objects.values('group_id').get(id=hotelId)
        room = Room.objects.values('room_order').select_related("hotel").filter(
            hotel__group_id=group['group_id']).aggregate(Max('room_order'))
        if room['room_order__max']:
            room_order = room['room_order__max'] + 1
        else:
            room_order = 1
        return room_order

    def get_occupancy(room):
        currentDate = datetime.now()
        allotments = RoomAllotment.objects.filter(available_date=currentDate).filter(room_id=room.id)
        occupancy = 0
        if allotments.exists():
            total_bookings = Booking.objects.filter(check_in__lte=currentDate, check_out__gte=currentDate).filter(
                room_id=room.id).count()
            occupancy = (total_bookings / (allotments[0].allotments * room.beds)) * 100
        return occupancy

    def get_occupancy_modified(room):
        room_id = str(room.id)
        qry = 'SELECT room_allotments.*, count(bookings.id) as booking FROM room_allotments left outer join bookings on room_allotments.room_id=bookings.room_id and room_allotments.available_date between bookings.check_in and bookings.check_out WHERE room_allotments.room_id=' + room_id + ' group by room_allotments.id'
        cursor = connection.cursor()

        cursor.execute(qry)
        rows = cursor.fetchall()
        total = 0
        for row in rows:
            res = {}
            res['id'] = row[0]
            res['allotments'] = row[1]
            res['available_date'] = str(row[2])

            matched_attendee = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                count_match__gt=1, match__room_id=room_id)
            count_matched_pairs = matched_attendee.filter(match__start_date__lte=res['available_date'],
                                                          match__end_date__gt=res['available_date']).count()
            match_id = []
            if matched_attendee.count() > 0:
                for match in matched_attendee:
                    match_id.append(match['match_id'])

            count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                match_id__in=match_id, booking__check_in__lte=res['available_date'],
                booking__check_out__gt=res['available_date']).exclude(match__start_date__lte=res['available_date'],
                                                                      match__end_date__gt=res['available_date']).count()

            matched_booking = []
            booking_matched = MatchLine.objects.filter(match_id__in=match_id)
            if booking_matched.exists():
                for booking in booking_matched:
                    matched_booking.append(booking.booking_id)

            count_unmatched_attendee = Booking.objects.filter(room_id=room_id, check_in__lte=res['available_date'],
                                                              check_out__gt=res['available_date']).exclude(
                id__in=matched_booking).count()
            total += count_matched_pairs + count_matched_singles + count_unmatched_attendee
        return total

    def delete_allotment(request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            id = request.POST.get('id')
            allotment = RoomAllotment.objects.get(id=id)
            current_date = allotment.available_date
            booking_count = Booking.objects.filter(room_id=allotment.room_id, check_in__lte=current_date,
                                                   check_out__gt=current_date).count()
            #
            # is_booked = Booking.objects.filter(room_id=allotment.room_id).count()
            if booking_count > 0:
                # allotment_form_data = {
                # "allotments": booking_count
                #     }
                # RoomAllotment.objects.filter(id=id).update(**allotment_form_data)
                # response_data['new_allotment'] = booking_count
                response_data['error'] = 'This Room is in booking List. Allotment could not be deleted'

            else:
                allotment.delete()
                response_data['success'] = 'Allotment Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def update_allotment(request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            id = request.POST.get('id')
            action_amount = int(request.POST.get('allotment_amount'))
            action = request.POST.get('action')
            response_data = RoomView.allotment_update_with_conditions(id, action_amount, action)
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def edit_allotment(request):
        response_data = {}
        if EventView.check_permissions(request, 'hotel_permission'):
            id = request.POST.get('pk')
            action_amount = int(request.POST.get('value'))
            action = request.POST.get('name')
            response_data = RoomView.allotment_update_with_conditions(id, action_amount, action)
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def allotment_update_with_conditions(id, action_amount, action, cost, vat):
        response_data = {}
        allotment = RoomAllotment.objects.get(id=id)
        room = Room.objects.get(id=allotment.room_id)
        current_date = allotment.available_date
        booking_count = Booking.objects.filter(room_id=allotment.room_id, check_in__lte=current_date,
                                               check_out__gte=current_date).count()
        book_amount = math.ceil(booking_count / room.beds)
        if action == "remove":
            amount = allotment.allotments - action_amount
        if action == "update":
            amount = action_amount
        if amount <= 0 and book_amount == 0:
            allotment.delete()
            response_data['success'] = 'Date : ' + str(allotment.available_date) + '. Allotment Deleted Successfully'
        if amount >= book_amount:
            allotment_form_data = {
                "allotments": amount
            }
            if cost:
                allotment_form_data['cost'] = cost
            else:
                allotment_form_data['cost'] = 0
            if vat:
                allotment_form_data['vat'] = vat
            else:
                allotment_form_data['vat'] = None
            RoomAllotment.objects.filter(id=id).update(**allotment_form_data)
            response_data['success_update'] = 'Date : ' + str(allotment.available_date) + '. Allotment has been updated'
            response_data['new_allotment'] = amount
            response_data['booking'] = book_amount
            response_data['free'] = response_data['new_allotment'] - response_data['booking']

        if amount < book_amount:
            allotment_form_data = {
                "allotments": book_amount
            }
            if cost and vat:
                allotment_form_data['cost'] = cost
                allotment_form_data['vat'] = vat
            RoomAllotment.objects.filter(id=id).update(**allotment_form_data)
            response_data['error'] = 'Date : ' + str(allotment.available_date) + '. Room in the Booking List'
            response_data['new_allotment'] = book_amount
            response_data['booking'] = book_amount
            response_data['free'] = response_data['new_allotment'] - response_data['booking']

        return response_data

    def find_booking(room_id):
        # current_date=allotment.available_date
        # get_bookings = Booking.objects.filter(room_id=allotment.room_id,check_in__lte=current_date, check_out__gte=current_date).count()
        #
        # return get_bookings
        room = Room.objects.get(id=room_id)
        qry = 'SELECT room_allotments.*, count(bookings.id) as booking FROM room_allotments left outer join bookings on room_allotments.room_id=bookings.room_id and room_allotments.available_date >= bookings.check_in and room_allotments.available_date < bookings.check_out WHERE room_allotments.room_id=' + str(
            room_id) + ' group by room_allotments.id order by room_allotments.available_date'
        # qry = 'SELECT room_allotments.*, count(bookings.id) as booking FROM room_allotments left outer join bookings on room_allotments.room_id=bookings.room_id and room_allotments.available_date between bookings.check_in and bookings.check_out WHERE room_allotments.room_id=' + room_id + ' group by room_allotments.id'
        cursor = connection.cursor()

        cursor.execute(qry)
        rows = cursor.fetchall()
        result = []
        total_stay = 0
        total_allotments = 0
        for row in rows:
            # print(row)
            res = {}
            res['id'] = row[0]
            res['allotments'] = row[1]
            res['available_date'] = str(row[2])
            res['room_id'] = row[3]
            res['cost'] = str(row[4])
            res['vat'] = str(row[5])
            res['booking'] = math.ceil(row[6] / room.beds)
            matched_attendee = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                count_match__gt=1, match__room_id=room_id)
            count_matched_pairs = matched_attendee.filter(match__start_date__lte=res['available_date'],
                                                          match__end_date__gt=res['available_date']).count()

            # count_matched_pairs2 = matched_attendee.filter(match__start_date__lte=res['available_date'], match__end_date__gt=res['available_date'])
            # print(count_matched_pairs2.query)
            # count_matched_pairs = matched_attendee.filter(match__all_dates__icontains=res['available_date']).count()
            # count_matched_pairs = matched_attendee.filter(booking__check_in__lte=res['available_date'], booking__check_out__gt=res['available_date']).count()
            # if count_matched_pairs > 0:

            # print('count_matched_pairs')
            # print(res['available_date'])
            # print(count_matched_pairs)
            res['matched_pairs'] = count_matched_pairs
            match_id = []
            if matched_attendee.count() > 0:
                for match in matched_attendee:
                    match_id.append(match['match_id'])
            count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                match_id__in=match_id, booking__check_in__lte=res['available_date'],
                booking__check_out__gt=res['available_date']).exclude(match__start_date__lte=res['available_date'],
                                                                      match__end_date__gt=res['available_date']).count()

            # count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match = Count('match_id')).filter(match_id__in=match_id,booking__check_in__lte=res['available_date'], booking__check_out__gt=res['available_date']).exclude(match__all_dates__icontains=res['available_date']).count()
            # count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match = Count('match_id')).filter(match_id__in=match_id,booking__check_in__lte=res['available_date'], booking__check_out__gte=res['available_date']).exclude(booking__check_in__lte=res['available_date'], booking__check_out__gt=res['available_date']).count()
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
            # if total > res['allotments']:
            #     total = res['allotments']
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
        # return HttpResponse(json.dumps(result), content_type="application/json")

    def get_matched_pair(request, room_id):
        sql = ' select mat.* from matches mat where (mat.id NOT IN( select match_line.match_id from match_line)) or (mat.id IN( select match_line.match_id from match_line group by match_line.match_id having Count(match_line.match_id) = 1))'
        delete_unused_matches = Match.objects.raw(
            sql
        )
        logger = logging.getLogger(__name__)
        for delete_match in delete_unused_matches:
            Match.objects.filter(id=delete_match.id).delete()
            logger.debug("-----------------'Delete Match'------------------------" + str(delete_match.id))
        rooms_with_multiple_beds = Room.objects.values('id').filter(beds__gt=1)
        bookings_matched = MatchLine.objects.values('booking_id').filter(booking__room_id=room_id)
        # remove_bookings_matched = MatchLine.objects.values('booking_id').annotate(count_match_id=Count('match_id')).filter(count_match_id=1)
        # bookings_matched = bookings_matched.exclude(id__in=remove_bookings_matched)
        bookings = Booking.objects.filter(room_id=room_id,
                                          broken_up=False).exclude(id__in=bookings_matched)
        matched_list = []
        already_matched_booking = []
        for booking in bookings:
            if booking.id not in already_matched_booking:
                beds = booking.room.beds
                if beds > 1:
                    pair_bookings = RoomView.check_pair_bookings(request, booking, room_id, already_matched_booking)
                    if len(pair_bookings) > 1 and len(pair_bookings) == beds:
                        common_dates = RoomView.get_booking_common_dates(pair_bookings)
                        if len(common_dates) > 0:
                            for booking_id in pair_bookings:
                                already_matched_booking.append(booking_id)
                            matched_list.append(pair_bookings)
                    else:
                        print('conflict')
                        print(len(pair_bookings))
        matched_bookings = []
        for match_list in matched_list:
            matched_bookings.append(Booking.objects.filter(id__in=match_list, room_id=room_id))
        # insert matched bookings to matches table
        for booking_list in matched_bookings:
            if booking_list:
                match_buddies = []
                common_dates = RoomView.get_common_dates(booking_list)
                if len(common_dates) > 0:
                    all_dates = []
                    for my_date in common_dates:
                        all_dates.append(str(my_date))
                    end_date = max(common_dates) + timedelta(days=1)
                    match = Match(room_id=booking_list[0].room_id, start_date=min(common_dates), end_date=end_date,
                                  all_dates=json.dumps(all_dates))
                    match.save()
                    for booking in booking_list:
                        match_line = MatchLine(match=match, booking_id=booking.id)
                        match_line.save()
                        booking.matched = True
                        booking.save()
                        match_buddies.append(match_line.as_dict())
                    if len(match_buddies) > 1:
                        for match_attendee in match_buddies:
                            matchlist = match_buddies[:]
                            matchlist.remove(match_attendee)
                            # HotelView.send_email(request, match_attendee['booking']['attendee'], 'email/match_buddy.html', matchlist)
            # end insert automatically matched bookings to matches table
        unmatched_bookings_data = []
        unmatched_bookings = Booking.objects.filter(room_id=room_id).exclude(id__in=bookings_matched)
        for unmatched_book in unmatched_bookings:
            unmatched_bookings_data.append(unmatched_book)
        # get matched bookings from matches table
        matched_bookings_from_matches = []
        matches = Match.objects.filter(room_id=room_id)
        single_bookings_match = []
        from itertools import chain
        check_booking = []
        for match in matches:
            match_lines = match.lines.all()
            # print(len(match_lines))
            if len(match_lines) > 1:
                booking_list_1 = []
                for line in match_lines:
                    booking_list_1.append(line.booking)
                    check_booking.append(line.booking)
                matched_bookings_from_matches.append(booking_list_1)
            else:
                for line in match_lines:
                    single_bookings_match.append(line.booking)

        for single_booking in single_bookings_match:
            if single_booking not in check_booking and single_booking not in unmatched_bookings_data:
                unmatched_bookings_data.append(Booking.objects.get(id=single_booking.id))
        # end get matched bookings from matches table
        logger.debug("-----------------'matched_bookings_from_matches'------------------------")
        for data in matched_bookings_from_matches:
            logger.debug("-----------------'matched_bookings'------------------------")
            for d in data:
                logger.debug(d.id)
        room_info = Room.objects.get(id=room_id)
        context = {
            'matched_bookings': matched_bookings_from_matches,
            'unmatched_bookings': unmatched_bookings_data,
            'room_info': room_info
        }
        return context
        # return

    def check_pair_bookings(request, booking, room_id, already_matched_booking):
        room_buddy = []
        room_buddy.append(booking.id)
        requested_buddies = booking.buddies.all()
        for buddy in requested_buddies:
            room_buddy = RoomView.get_requested_buddies(request, buddy, room_buddy, room_id, already_matched_booking)
        bookings_matched = MatchLine.objects.values('booking_id').all()
        request_me = RequestedBuddy.objects.filter(buddy_id=booking.attendee_id).exclude(Q(booking_id__in=room_buddy)| Q(booking_id__in=bookings_matched))
        for my_booking in request_me:
            # already_booked = MatchLine.objects.filter(booking_id = my_booking.booking_id)
            # if my_booking.booking_id not in room_buddy and not already_booked.exists():
            room_buddy.append(my_booking.booking_id)
        return room_buddy

    def get_requested_buddies(request, buddy, room_buddy, room_id, already_matched_booking):
        # if buddy.booking_id not in already_matched_booking:
        bookings_matched = MatchLine.objects.values('booking_id').all()
        if buddy.exists == 1:
            buddy_booking = Booking.objects.filter(room_id=room_id, broken_up=False,
                                                   attendee_id=buddy.buddy_id).exclude(id__in=bookings_matched)
            if len(buddy_booking) < 1:
                room_buddy = []
            for booking in buddy_booking:
                if booking.id not in already_matched_booking:
                    if not booking.id in room_buddy:
                        room_buddy.append(booking.id)
                        buddy_requested_buddies = booking.buddies.all()
                        for buddy in buddy_requested_buddies:
                            room_buddy = RoomView.get_requested_buddies(request, buddy, room_buddy, room_id,
                                                                        already_matched_booking)
        else:
            requested_buddy_email = buddy.email
            checked_name = requested_buddy_email.strip().split(' ')
            if len(checked_name) > 1:
                attendees = Attendee.objects.filter(firstname=checked_name[0], lastname=checked_name[1],
                                                    event_id=request.session['event_auth_user']['event_id'],
                                                    status="registered")
            else:
                attendees = Attendee.objects.filter(email=requested_buddy_email,
                                                    event_id=request.session['event_auth_user']['event_id'],
                                                    status="registered")
            if len(attendees) > 0:
                for attendee in attendees:
                    buddy_booking = Booking.objects.filter(room_id=room_id, broken_up=False,
                                                           attendee_id=attendee.id).exclude(id__in=bookings_matched)
                    for booking in buddy_booking:
                        if booking.id not in already_matched_booking:
                            if not booking.id in room_buddy:
                                room_buddy.append(booking.id)
                                buddy_requested_buddies = booking.buddies.all()
                                for buddy in buddy_requested_buddies:
                                    room_buddy = RoomView.get_requested_buddies(request, buddy, room_buddy, room_id,
                                                                                already_matched_booking)
        return room_buddy

    @staticmethod
    def get_common_dates(booking_list):
        a_list = []
        all_dates = []
        attendee_dates = {}

        for booking in booking_list:
            key = 'a' + str(booking.attendee_id)
            if key not in attendee_dates:
                attendee_dates[key] = []

        for booking in booking_list:
            booking_check_in = booking.check_in
            booking_check_out = booking.check_out
            day_count = (booking_check_out - booking_check_in).days
            for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                all_dates.append(single_date)
                if 'a' + str(booking.attendee_id) in attendee_dates:
                    attendee_dates['a' + str(booking.attendee_id)].append(single_date)
        for key in attendee_dates:
            a_list.append(attendee_dates[key])
        for i in range(0, len(a_list)):
            for j in range(1, len(a_list)):
                all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
        return all_dates

    @staticmethod
    def get_booking_common_dates(bookings):
        a_list = []
        all_dates = []
        booking_list = Booking.objects.filter(id__in=bookings)
        for booking in booking_list:
            booking_check_in = booking.check_in
            booking_check_out = booking.check_out
            day_count = (booking_check_out - booking_check_in).days + 1
            booking_date_list = []
            for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                booking_date_list.append(single_date)
                all_dates.append(single_date)
            a_list.append(booking_date_list)

        for i in range(0, len(a_list)):
            for j in range(1, len(a_list)):
                all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
        return all_dates

    def check_allotment(request, room_id, common_dates):
        check = True
        for c_dates in common_dates:
            total_allotments = RoomAllotment.objects.filter(room_id=room_id, available_date=c_dates)
            matched_attendee = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                count_match__gt=1, match__room_id=room_id)
            count_matched_pairs = matched_attendee.filter(match__start_date__lte=c_dates,
                                                          match__end_date__gte=c_dates).count()
            match_id = []
            if matched_attendee.count() > 0:
                for match in matched_attendee:
                    match_id.append(match['match_id'])
            count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
                match_id__in=match_id, booking__check_in__lte=c_dates, booking__check_out__gte=c_dates).exclude(
                match__start_date__lte=c_dates, match__end_date__gte=c_dates).count()
            # matched_booking = []
            # booking_matched = MatchLine.objects.filter(match_id__in=match_id)
            # if booking_matched.exists():
            #     for booking in booking_matched:
            #         matched_booking.append(booking.booking_id)
            # count_unmatched_attendee = Booking.objects.filter(room_id=room_id,check_in__lte=c_dates, check_out__gte=c_dates).exclude(id__in=matched_booking).count();
            total = count_matched_pairs + count_matched_singles
            if total_allotments.exists():
                total_remain = total_allotments[0].allotments - total
                if total_remain < 1:
                    check = False
        return check


class RoomDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return Room.objects.filter(id=pk)
        except Room.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        room = self.get_object(pk)
        # get_all_match = RoomView.get_matched_pair(request, room)
        paymentGroup = GroupView.get_paymentGroup(request)
        room_allotments = RoomView.find_booking(pk)
        context = {
            'room': room[0],
            'paymentGroup': paymentGroup,
            'room_alloments': room_allotments['details']
        }
        return render(request, 'hotel/edit_room.html', context)
