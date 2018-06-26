from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Users, Attendee, Tag, Session, Group, Room, SeminarsUsers, Questions, Booking, Answers, \
    RequestedBuddy, RoomAllotment, AttendeeTag, UsedRule
import json
from datetime import datetime, timedelta
from django.http import Http404
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from .question_view import QuestionView
from .common_views import AnswerView, GroupView
from django.db.models import Q
from django.db import transaction
import string
import random
from django.contrib.auth.hashers import make_password
from publicfront.views.attendee import AttendeeRegistration
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.conf import settings
import os
from itertools import chain


class AttendeeView(TemplateView):
    def get(self, request):
        search_key = ""
        if 'search_key' in request.GET:
            search_key = request.GET.get('search_key')
            attendees = Attendee.objects.annotate(fullname=Concat('firstname',V(' ') ,'lastname')).filter(Q(firstname__icontains=search_key) | Q(lastname__icontains=search_key) | Q(email__icontains=search_key) | Q(fullname__icontains=search_key))
            session_groups = GroupView.get_sessionGroup(request)
            for group in session_groups:
                group.sessions = Session.objects.all().filter(group_id=group.id)
            attendee_groups = GroupView.get_attendeeGroup(request)
            questionGroup = GroupView.get_questionGroup(request)
            hotel_group = GroupView.get_hotelGroup(request)
            filter_group = GroupView.get_filterGroup(request)
            for group in hotel_group:
                group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
                # for room in group.rooms:
                #     room.vat = Group.objects.get(id=room.vat_id)
            tags = Tag.objects.all()
            last_used_rules = UsedRule.objects.filter(user_id=request.session['event_auth_user']['id'])
            context = {
                'session_groups': session_groups,
                'attendee_groups': attendee_groups,
                'hotel_groups': hotel_group,
                'last_used_rules': last_used_rules,
                'tags': tags,
                'questionGroup': questionGroup,
                'filter_group': filter_group,
                'attendees': attendees

            }
            return render(request,'attendee/attendee_result.html',context)
        else:
            print("here")
            session_groups = GroupView.get_sessionGroup(request)
            for group in session_groups:
                group.sessions = Session.objects.all().filter(group_id=group.id)
            attendee_groups = GroupView.get_attendeeGroup(request)
            questionGroup = GroupView.get_questionGroup(request)
            hotel_group = GroupView.get_hotelGroup(request)
            filter_group = GroupView.get_filterGroup(request)
            for group in hotel_group:
                group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
                # for room in group.rooms:
                #     room.vat = Group.objects.get(id=room.vat_id)
            tags = Tag.objects.all()
            last_used_rules = UsedRule.objects.filter(user_id=request.session['event_auth_user']['id'])

            questionGroup = Group.objects.filter(type="question",is_show=1).order_by('group_order')
            for group in questionGroup:
                group.questions = Questions.objects.all().filter(group_id=group.id)

            context = {
                'session_groups': session_groups,
                'attendee_groups': attendee_groups,
                'hotel_groups': hotel_group,
                'last_used_rules': last_used_rules,
                'tags': tags,
                'questionGroup': questionGroup,
                'filter_group': filter_group,
                'search_key': search_key,
                'question_groups': questionGroup,
            }
            return render(request, 'attendee/attendee2.html', context)
        # template_name = 'attendee/attendee.html'

    @transaction.atomic
    def post(self, request):
        response_data = {}
        form_data = {
            "firstname": request.POST.get('fname'),
            "lastname": request.POST.get('lname'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
            "group_id": request.POST.get('role')
        }

        answers = json.loads(request.POST.get('answers'))
        attendee_session = json.loads(request.POST.get('attendee_session'))
        # attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
        attendee_tags = json.loads(request.POST.get('attendee_tags'))

        if 'id' in request.POST:
            user_id = request.POST.get('id')
            if not (Attendee.objects.filter(email=form_data['email']).exclude(id=user_id).exists()):
                form_data["updated"] = datetime.now()
                Attendee.objects.filter(id=user_id).update(**form_data)
                tag_exist = []
                for tag in attendee_tags:
                    if tag.isdigit():
                        tag_exist.append(tag)
                        if not (AttendeeTag.objects.filter(attendee_id=user_id, tag_id=tag).exists()):
                            attendee_tag = AttendeeTag(attendee_id=user_id, tag_id=tag)
                            attendee_tag.save()
                    else:
                        new_tag = Tag(name=tag)
                        new_tag.save()
                        attendee_tag = AttendeeTag(attendee_id=user_id, tag_id=new_tag.id)
                        attendee_tag.save()
                        tag_exist.append(new_tag.id)
                deleted_tag = AttendeeTag.objects.filter(attendee_id=user_id).exclude(tag_id__in=tag_exist)
                for tag in deleted_tag:
                    tag.delete()

                for answer in answers:
                    save_answers = AnswerView.saveAnswers(user_id, answer)
                    # if "email already Exist" in save_answers:
                    #     response_data['error'] = 'email already Exist'
                    #     return HttpResponse(json.dumps(response_data), content_type="application/json")
                for session in attendee_session:
                    attendeeSessions = SeminarsUsers(attendee_id=user_id, session_id=session['id'])
                    attendeeSessions.save()

                # adding hotel rooms and requested buddies for attendee
                attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
                for attendee_booking in attendee_bookings:
                    if attendee_booking['exists'] == 1:
                        room_available = AttendeeView.check_available_room(attendee_booking)
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
                                                                 name=buddy)
                                requested_buddy.save()
                    else:
                        room_available = AttendeeView.check_available_room(attendee_booking)
                        if not room_available:
                            response_data['error'] = 'Those Rooms are not available'
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                        booking = Booking(attendee_id=user_id, room_id=attendee_booking['room_id'],
                                          check_in=attendee_booking['check_in'],
                                          check_out=attendee_booking['check_out'])
                        booking.save()
                        buddies = attendee_booking['room_buddies']
                        for buddy in buddies:
                            if buddy.isdigit():
                                requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                                requested_buddy.save()
                            else:
                                requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False, name=buddy)
                                requested_buddy.save()

                response_data['success'] = 'Attendee Update Successfully'
                send_mail = request.POST.get('send_mail')
                print(send_mail)
                if send_mail == 'true':
                    updated_attendee = Attendee.objects.get(id=user_id)
                    # if os.environ['ENVIRONMENT_TYPE'] == 'master':
                    #     AttendeeRegistration.send_email(request, updated_attendee)
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['error'] = 'email already Exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
            if not (Attendee.objects.filter(email=form_data['email']).exists()):
                form_data["type"] = "user"
                form_data["password"] = make_password(form_data["password"])
                flag = True
                while (flag):
                    secret_key = ''.join(
                        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
                        range(10))
                    checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
                    if checkUniquity < 1:
                        flag = False
                form_data["secret_key"] = secret_key
                attendee = Attendee(**form_data)
                attendee.save()

                for tag in attendee_tags:
                    if tag.isdigit():
                        attendee_tag = AttendeeTag(attendee_id=attendee.id, tag_id=tag)
                        attendee_tag.save()
                    else:
                        new_tag = Tag(name=tag)
                        new_tag.save()
                        attendee_tag = AttendeeTag(attendee_id=attendee.id, tag_id=new_tag.id)
                        attendee_tag.save()
                for answer in answers:
                    save_answers = AnswerView.saveAnswers(attendee.id, answer)
                    # if "email already Exist" in save_answers:
                    #     response_data['error'] = 'email already Exist'
                    #     return HttpResponse(json.dumps(response_data), content_type="application/json")
                # adding sessions for attendee
                for session in attendee_session:
                    attendeeSessions = SeminarsUsers(attendee_id=attendee.id, session_id=session['id'])
                    attendeeSessions.save()

                # adding hotel rooms and requested buddies for attendee
                for attendee_booking in attendee_bookings:
                    room_available = AttendeeView.check_available_room(attendee_booking)
                    if not room_available:
                        response_data['error'] = 'Those Rooms are not available'
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                    booking = Booking(attendee_id=attendee.id, room_id=attendee_booking['room_id'],
                                      check_in=attendee_booking['check_in'], check_out=attendee_booking['check_out'])
                    booking.save()
                    buddies = attendee_booking['room_buddies']
                    for buddy in buddies:
                        if buddy.isdigit():
                            requested_buddy = RequestedBuddy(booking_id=booking.id, buddy_id=buddy)
                            requested_buddy.save()
                        else:
                            requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False, name=buddy)
                            requested_buddy.save()

                response_data['success'] = 'Attendee Create Successfully'
                # AttendeeRegistration.send_email(request, attendee)
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['error'] = 'email already Exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete(request):
        response_data = {}
        id = request.POST.get('id')
        attendee = Attendee.objects.get(id=id)
        attendee.delete()
        response_data['success'] = 'Attendee Deleted Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_speakers(request):
        response_data = {}
        val = request.POST.get('q')
        attendeeis = Attendee.objects.values('firstname', 'lastname', 'id').filter(
            Q(firstname__icontains=val) | Q(lastname__icontains=val))
        # #attendeeis = Attendee.objects.filter(Q(firstname__icontains=val) | Q( lastname__icontains=val))
        attendees = attendeeis.all()
        my_data = []
        for attendee in attendees:
            arr_data = {}
            arr_data['id'] = attendee['id']
            arr_data['text'] = attendee['firstname'] + ' ' + attendee['lastname']
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_session(request):
        response_data = {}
        id = request.POST.get('id')
        attendee_session = SeminarsUsers.objects.get(id=id)
        attendee_session.delete()
        response_data['success'] = 'Attendees Session Deleted Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_booking(request):
        response_data = {}
        id = request.POST.get('id')
        attendee_booking = Booking.objects.get(id=id)
        attendee_booking.delete()
        response_data['success'] = 'Attendees Booking Deleted Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_attendees(request):
        response_data = {}
        val = request.POST.get('q')
        print(val)
        attendees = Attendee.objects.values('firstname', 'lastname', 'id').filter(
            Q(firstname__icontains=val) | Q(lastname__icontains=val))
        my_data = []
        for attendee in attendees:
            arr_data = {
                'id': attendee['id'],
                'text': attendee['firstname'] + ' ' + attendee['lastname']
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
            # attList.append(attendee['id'])

        print(attList)
        attList = attList[2:]
        print(attList)
        question_groups = []
        questionGroup = Group.objects.filter(type="question", is_show=1).order_by('group_order')
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
        # similar_booking = Booking.objects.raw('select * from bookings where attendee_id in ('+attList+') group by check_in,check_out,room_id having count(*) > 1')
        # booking_list = []
        # booked_id_list = []
        # print(similar_booking[0])
        # for booked in similar_booking:
        #     booked_dict = dict(
        #     id=similar_booking[0].id
        # )
        #     booked_id_list.append(booked_dict)
        # # for booked in similar_booking:
        # as_dict = dict(
        #     id=similar_booking[0].id,
        #     attendee=similar_booking[0].attendee.as_dict(),
        #     room=similar_booking[0].room.as_dict(),
        #     check_in=str(similar_booking[0].check_in),
        #     check_out=str(similar_booking[0].check_out)
        # )
        # requested_buddies = RequestedBuddy.objects.filter(booking_id=similar_booking[0].id)
        # bookings_buddies = {}
        # bookings_buddies['booking'] = as_dict
        # buddy_list = []
        # for requested_buddy in requested_buddies:
        #     if requested_buddy.buddy_id:
        #         buddy_list.append(requested_buddy.as_dict())
        #     else:
        #         buddy_list.append(requested_buddy.as_dict_alt())
        #
        # bookings_buddies['buddies'] = buddy_list
        # booking_list.append(bookings_buddies)
        # # booking_list.append(as_dict)
        # data = {'attendees': attendee_list, 'question_groups' : question_groups, 'booking_list': booking_list, 'booked_id_list': booked_id_list }
        data = {'attendees': attendee_list, 'question_groups': question_groups}
        return HttpResponse(json.dumps(data), content_type="application/json")

    def update_multiple_attendee(request):
        response_data = {}
        attendees = json.loads(request.POST.get('attendees'))
        answers = json.loads(request.POST.get('answers'))
        attendee_session = json.loads(request.POST.get('attendee_session'))
        for attendee in attendees:
            attendee_id = attendee['id']
            for answer in answers:
                AnswerView.saveAnswers(attendee_id, answer)

            for session in attendee_session:
                attendeeSessions = SeminarsUsers(attendee_id=attendee_id, session_id=session['id'])
                attendeeSessions.save()

                # adding hotel rooms and requested buddies for attendee
                attendee_bookings = json.loads(request.POST.get('attendee_bookings'))
                for attendee_booking in attendee_bookings:
                    if attendee_booking['exists'] == 1:
                        room_available = AttendeeView.check_available_room(attendee_booking)
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
                                                                 name=buddy)
                                requested_buddy.save()
                    else:
                        room_available = AttendeeView.check_available_room(attendee_booking)
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
                                requested_buddy = RequestedBuddy(booking_id=booking.id, exists=False, name=buddy)
                                requested_buddy.save()

        response_data['success'] = 'Multiple Attendee Question Update Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def check_available_room(booking):
        start_date = datetime.strptime(booking['check_in'], '%Y-%m-%d')
        end_date = datetime.strptime(booking['check_out'], '%Y-%m-%d')
        day_count = (end_date - start_date).days + 1
        room = Room.objects.get(id=booking['room_id'])
        available = True
        for single_date in (start_date + timedelta(n) for n in range(day_count)):
            current_date = datetime.strftime(single_date, '%Y-%m-%d')
            allotments = RoomAllotment.objects.filter(available_date=current_date, room_id=booking['room_id'])
            if allotments.count():
                get_bookings = Booking.objects.filter(room_id=booking['room_id'], check_in__lte=current_date,
                                                      check_out__gte=current_date).count()
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
        # request.POST.get('secret_key')
        checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
        if checkUniquity < 1:
            return HttpResponse("false")
        else:
            return HttpResponse("true")


class AttendeeListView(BaseDatatableView):

    attendees = Attendee.objects.all()
    order_columns = ['-1']
    questions = []
    question_groups = Group.objects.filter(type="question",is_show=1).order_by('group_order')
    for group in question_groups:
        questions_g = Questions.objects.all().filter(group_id=group.id)
        for q_g in questions_g:
            questions.append(q_g)
    for question in questions:
        order_columns.append(question.id)

    def filter_queryset(self, qs):
        if not self.pre_camel_case_notation:
            search = self.request.GET.get('search[value]', None)
            #col_data = self.extract_datatables_column_data()
            visible_columns = list(map(int, self.request.GET.get('visible', None).split(',')))
            if len(visible_columns) != 0:
                visible_questions = [self.order_columns[x] for x in visible_columns]
                answers_filtered = Answers.objects.filter(value__startswith=search, question_id__in=visible_questions)
            else:
                answers_filtered = Answers.objects.filter(value__startswith=search)
            attendee_ids = []
            for answer in answers_filtered:
                attendee_ids.append(answer.user_id)
            q = Q()
            q |= Q(id__in=attendee_ids)
            qs = qs.filter(q)
        return qs

    def get_initial_queryset(self):
        return self.attendees

    def prepare_results(self, qs):
        json_data = []
        for q in qs:
            items = [q.id]
            answers_for_attendee = Answers.objects.filter(user_id=q.id)
            for question in self.questions:
                ans = 'N/A'
                for answer in answers_for_attendee:
                    if answer.question_id == question.id:
                        ans = answer.value
                        break
                items.append(ans)
            json_data.append(items)
        return json_data

    def ordering(self, qs):
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)
        order = []
        order_columns = self.get_order_columns()
        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0
            sdir = '-' if sort_dir == 'desc' else ''
            sortcol = order_columns[sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc))
            else:
                order.append('{0}{1}'.format(sdir, sortcol))
        if order:
            question_id = int(order[0])
            if question_id < 0:
                question_id *= -1
                answers_ordered = Answers.objects.filter(question_id=question_id, user__in=qs).order_by('-value')
            else:
                answers_ordered = Answers.objects.filter(question_id=question_id, user__in=qs).order_by('value')
            attendee_ids = []
            for answer in answers_ordered:
                attendee_ids.append(answer.user_id)
            clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(attendee_ids)])
            ordering = 'CASE %s END' % clauses
            attendees_ordered = Attendee.objects.filter(pk__in=attendee_ids).extra(select={'ordering': ordering}, order_by=('ordering',))
            attendees_without_question = Attendee.objects.exclude(pk__in=attendee_ids)
            f = attendees_ordered | attendees_without_question
            return attendees_ordered
        return qs


class AttendeeDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            # return Users.objects.filter(id=pk).values()
            return Attendee.objects.filter(id=pk)
        except Users.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        allAnswers = user[0].answers_set.all()
        answer_list = []
        for answer in allAnswers:
            answer_list.append(answer.as_dict())
        if not (Answers.objects.filter(question_id=68, user_id=user[0].id).exists()):
            firstname = Answers.objects.get(question_id=63, user_id=user[0].id)
            question = Questions.objects.get(id=68)
            get_dict = dict(
                id=firstname.id,
                user=user[0].as_dict(),
                question=question.as_dict(),
                value=firstname.value

            )
            answer_list.append(get_dict)
        if not (Answers.objects.filter(question_id=69, user_id=user[0].id)):
            lastname = Answers.objects.get(question_id=64, user_id=user[0].id)
            question = Questions.objects.get(id=69)
            get_dict = dict(
                id=lastname.id,
                user=user[0].as_dict(),
                question=question.as_dict(),
                value=lastname.value

            )
            answer_list.append(get_dict)
        attendee = user[0].as_dict()
        question_groups = []
        questionGroup = Group.objects.filter(type="question", is_show=1).order_by('group_order')
        for group in questionGroup:
            group.questions = Questions.objects.all().filter(group_id=group.id)
            question_list = []
            data = QuestionView.get_Questions(request, group.questions)
            question_list.append(data)
            q_obj = {
                'group': group.as_dict(),
                'questions': question_list
            }
            question_groups.append(q_obj)
        attendee_sessions = SeminarsUsers.objects.filter(attendee_id=pk)
        all_attendee_groups = GroupView.get_attendeeGroup(request)
        attendee_groups = []
        for group in all_attendee_groups:
            attendee_groups.append(group.as_dict())
        session_list = []
        for session in attendee_sessions:
            session_list.append(session.as_dict())

        # get the bookings and requested buddy list
        bookings = Booking.objects.filter(attendee_id=user)
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
            booking_list.append(bookings_buddies)

        tag_list = []
        attendee_tags = AttendeeTag.objects.filter(attendee_id=pk)
        for tag in attendee_tags:
            tag_list.append(tag.as_dict())

        data = {
            'user': attendee,
            'question_groups': question_groups,
            'answers': answer_list,
            'attendee_sessions': session_list,
            'attendee_groups': attendee_groups,
            'bookings_buddies': booking_list,
            'attendee_tags': tag_list
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
