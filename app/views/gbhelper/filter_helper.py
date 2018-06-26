import json

from django.views import generic
from app.models import Attendee, SeminarsUsers, Answers, AttendeeGroups, AttendeeTag, DeviceToken, Booking, \
    Room, MatchLine, SeminarSpeakers, EmailReceivers, MessageReceiversHistory, AttendeeSubmitButton, \
    RegistrationGroupOwner, Orders, CreditOrders, OrderItems, Checkpoint, Scan
from app.views.room_view import RoomView
import datetime
from django.db.models import Q, F
from django.db.models.aggregates import Count, Sum


class FilterHelper(generic.TemplateView):
    def get_attendee_using_filter(event_id, filters, match_condition, matched_attendees=[]):
        all_main_q = Q()
        if match_condition == 1:
            all_main_q = Q(id=-11)
        if len(matched_attendees) == 0:
            matched_attendees = []
        if match_condition == '2':
            all_attendees_data = Attendee.objects.filter(event_id=event_id,status="registered").values('id')
            all_attendee_data = []
            for all_att in all_attendees_data:
                all_attendee_data.append(all_att['id'])
            matched_attendees = all_attendee_data
        flag = 0
        for filter1 in filters:
            if isinstance(filter1[0], dict):
                if match_condition == '2':
                    if len(matched_attendees) != 0:
                        matched_attendees = list(set(matched_attendees) & set(all_attendee_data))
                    elif flag == 0:
                        matched_attendees = all_attendee_data
                    flag =1
                    single_filter = filter1[0]
                    if single_filter['field']=='1':
                        q = Q()
                        if single_filter['condition'] == '1':
                            q &= Q(created__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '2':
                            q &= ~Q(created__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '3':
                            single_filter['values'][0] += ' 23:59:59'
                            q &= Q(created__gt=single_filter['values'][0])
                        if single_filter['condition'] == '4':
                            single_filter['values'][0] += ' 00:00:00'
                            q &= Q(created__lt=single_filter['values'][0])
                        if single_filter['condition'] == '5':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q &= Q(created__range=(earlier, now))
                        if single_filter['condition'] == '6':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q &= ~Q(created__range=(earlier, now))
                        if single_filter['condition'] == '7':
                            start_date = single_filter['values'][0] + ' 00:00:00'
                            end_date = single_filter['values'][1] + ' 23:59:59'
                            q &= Q(created__range=(start_date, end_date))

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='2':
                        q = Q()
                        if single_filter['condition'] == '1':
                            q &= Q(updated__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '2':
                            q &= ~Q(updated__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '3':
                            single_filter['values'][0] += ' 23:59:59'
                            q &= Q(updated__gt=single_filter['values'][0])
                        if single_filter['condition'] == '4':
                            single_filter['values'][0] += ' 00:00:00'
                            q &= Q(updated__lt=single_filter['values'][0])
                        if single_filter['condition'] == '5':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q &= Q(updated__range=(earlier, now))
                        if single_filter['condition'] == '6':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q &= ~Q(updated__range=(earlier, now))
                        if single_filter['condition'] == '7':
                            start_date = single_filter['values'][0] + ' 00:00:00'
                            end_date = single_filter['values'][1] + ' 23:59:59'
                            q &= Q(updated__range=(start_date, end_date))

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='3':
                        q = Q()
                        attendee_ids = AttendeeGroups.objects.filter(group_id=single_filter['values'][0]).values(
                            'attendee_id')
                        if single_filter['condition'] == '1':
                            q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            q &= ~Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            new_attende_ids=[]
                            for attendee in attendee_ids:
                                if not AttendeeGroups.objects.filter(attendee_id=attendee['attendee_id']).exclude(group_id=single_filter['values'][0]).exists():
                                   new_attende_ids.append(attendee['attendee_id'])
                            q &= Q(id__in=new_attende_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='4':
                        q = Q()
                        attendee_ids = AttendeeTag.objects.filter(tag_id=single_filter['values'][0]).values(
                            'attendee_id')
                        if single_filter['condition'] == '1':
                            q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            q &= ~Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            new_attende_ids=[]
                            for attendee in attendee_ids:
                                if not AttendeeTag.objects.filter(attendee_id=attendee['attendee_id']).exclude(tag_id=single_filter['values'][0]).exists():
                                   new_attende_ids.append(attendee['attendee_id'])
                            q &= Q(id__in=new_attende_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='6':
                        q = Q()
                        attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0]).values(
                            'attendee_id')
                        if single_filter['condition'] == '1':
                            attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                                                                         status='attending').values('attendee_id')
                            q &= Q(id__in=attending)
                        elif single_filter['condition'] == '2':
                            attending_data = SeminarsUsers.objects.filter(Q(Q(session_id=single_filter['values'][0]) & Q(Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))).values('attendee_id')
                            q &= ~Q(id__in=attending_data)
                        elif single_filter['condition'] == '3':
                            attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                                                                        status='in-queue').values('attendee_id')
                            q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '4':
                            attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                                                                        status='deciding').values('attendee_id')
                            q &= Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='7':
                        q = Q()
                        attendees_matches = []
                        if 'type' in single_filter and (single_filter['type'] == 'text' or single_filter['type'] == 'textarea'):
                            if single_filter['values'][0] == '1':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__icontains=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '2':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value__icontains=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                                # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
                                #                                            value__icontains=single_filter['values'][
                                #                                                1]).values('user_id')
                                #
                                # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
                                #     id__in=attendees_excludes)
                                # q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '3':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '4':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                                # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
                                #                                            value=single_filter['values'][1]).values('user_id')
                                # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
                                #     id__in=attendees_excludes)
                                # q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '5':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__istartswith=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '6':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__iendswith=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)

                            elif single_filter['values'][0] == '7':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)

                            elif single_filter['values'][0]=='8':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'date':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value=single_filter['values'][1])
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                #single_filter['values'][1] += ' 23:59:59'
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__gt=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                #single_filter['values'][1] += ' 00:00:00'
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__lt=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__range=(earlier, now)).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value__range=(earlier, now))
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__range=(start_date, end_date)).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '8':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '9':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'date_range':
                            if single_filter['values'][0] == '1':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                date_range = '["{0}","{1}"]'.format(start_date, end_date)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value=date_range).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                date_range = '["{0}","{1}"]'.format(start_date, end_date)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value=date_range)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                start_date_2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                                end_date_2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                                for a in attendee_list:
                                    dates = json.loads(a.value)
                                    date_from = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
                                    date_to = datetime.datetime.strptime(dates[1], "%Y-%m-%d")
                                    if start_date_2 <= date_from and end_date_2 >= date_to:
                                        attendee_ids.append(a.user_id)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                start_date_2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                                end_date_2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                                for a in attendee_list:
                                    dates = json.loads(a.value)
                                    date_from = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
                                    date_to = datetime.datetime.strptime(dates[1], "%Y-%m-%d")
                                    if not(start_date_2 <= date_from and end_date_2 >= date_to):
                                        attendee_ids.append(a.user_id)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '6':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'time':
                            if single_filter['values'][0] == '1':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value=time).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value=time)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__gt=time).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__lt=time).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                time = single_filter['values'][1].zfill(5)
                                date_time_now = datetime.datetime.now()
                                now = date_time_now.strftime('%H:%M')
                                if single_filter['values'][2] == "1":
                                    earlier_date = date_time_now - datetime.timedelta(minutes=int(single_filter['values'][1]))
                                elif single_filter['values'][2] == "2":
                                    earlier_date = date_time_now - datetime.timedelta(hours=int(single_filter['values'][1]))
                                earlier = earlier_date.strftime('%H:%M')
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__range=(earlier, now)).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                date_time_now = datetime.datetime.now()
                                now = date_time_now.strftime('%H:%M')
                                if single_filter['values'][2] == "1":
                                    earlier_date = date_time_now - datetime.timedelta(minutes=int(single_filter['values'][1]))
                                elif single_filter['values'][2] == "2":
                                    earlier_date = date_time_now - datetime.timedelta(hours=int(single_filter['values'][1]))
                                earlier = earlier_date.strftime('%H:%M')
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value__range=(earlier, now))
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value__range=(start_time, end_time)).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '8':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '9':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'time_range':
                            if single_filter['values'][0] == '1':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                time_range = '["{0}","{1}"]'.format(start_time, end_time)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value=time_range).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                time_range = '["{0}","{1}"]'.format(start_time, end_time)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value=time_range)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                for a in attendee_list:
                                    times = json.loads(a.value)
                                    time_from = datetime.datetime.strptime(times[0], '%H:%M').strftime('%H:%M')
                                    time_to = datetime.datetime.strptime(times[1], '%H:%M').strftime('%H:%M')
                                    if start_time <= time_from and end_time >= time_to:
                                        attendee_ids.append(a.user_id)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                for a in attendee_list:
                                    times = json.loads(a.value)
                                    time_from = datetime.datetime.strptime(times[0], '%H:%M').strftime('%H:%M')
                                    time_to = datetime.datetime.strptime(times[1], '%H:%M').strftime('%H:%M')
                                    if not(start_time <= time_from and end_time >= time_to):
                                        attendee_ids.append(a.user_id)
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '6':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)
                        elif 'type' in single_filter and single_filter['type'] == 'country':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '4':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)
                        else:
                            if single_filter['values'][0] == '1':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '2':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                q &= Q(id__in=attendees_matches)
                                # attendees_excludes = Answers.objects.filter(
                                #     question_id=int(single_filter['condition']),
                                #     value=single_filter['values'][1]).values('user_id')
                                # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(id__in=attendees_excludes)
                                # q &= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '3':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0]=='4':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q &= Q(id__in=attendees_matches)
                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)


                    if single_filter['field']=='8':
                        q = Q()
                        attendee_ids = DeviceToken.objects.all().values('attendee_id')
                        if single_filter['condition'] == '1':
                           q &= Q(id__in=attendee_ids)
                        else:
                           q &= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='9':
                        q = Q()
                        if single_filter['condition']=='1':
                            room_id = single_filter['values'][1]
                            # attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
                            if single_filter['values'][0]=='1':
                                attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = Booking.objects.exclude(room_id=int(room_id)).values('attendee_id')
                                q &= Q(id__in=attendees)
                                # q &= ~Q(id__in=attendees)

                        if single_filter['condition']=='2':

                            if single_filter['values'][0] == '1':
                                attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)
                            if single_filter['values'][0] == '2':
                                attendees = Booking.objects.exclude(check_in__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
                                # q &= ~Q(id__in=attendees)
                            if single_filter['values'][0] == '3':
                                # single_filter['values'][1] += ' 23:59:59'
                                attendees = Booking.objects.filter(check_in__gt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)

                            if single_filter['values'][0] == '4':
                                # single_filter['values'][1] += ' 00:00:00'
                                attendees = Booking.objects.filter(check_in__lt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)

                            if single_filter['values'][0]== '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendees)
                            if single_filter['values'][0]== '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.exclude(check_in__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
                                # q &= ~Q(id__in=attendees)

                            if single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendees = Booking.objects.filter(check_in__range=(start_date, end_date)).values('attendee_id')
                                q &= Q(id__in=attendees)

                        if single_filter['condition']=='3':

                            if single_filter['values'][0] == '1':
                                attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)
                            if single_filter['values'][0] == '2':
                                attendees = Booking.objects.exclude(check_out__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
                                # q &= ~Q(id__in=attendees)
                            if single_filter['values'][0] == '3':
                                # single_filter['values'][1] += ' 23:59:59'
                                attendees = Booking.objects.filter(check_out__gt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)

                            if single_filter['values'][0] == '4':
                                # single_filter['values'][1] += ' 00:00:00'
                                attendees = Booking.objects.filter(check_out__lt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendees)

                            if single_filter['values'][0]== '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendees)
                            if single_filter['values'][0]== '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.exclude(check_out__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
                                # q &= ~Q(id__in=attendees)

                            if single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendees = Booking.objects.filter(check_out__range=(start_date, end_date)).values('attendee_id')
                                q &= Q(id__in=attendees)

                        if single_filter['condition']=='4':
                            room_number = single_filter['values'][1]

                            if single_filter['values'][0]=='1':
                                attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = Booking.objects.exclude(room__beds=int(room_number)).values('attendee_id')
                                q &= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
                                # q &= ~Q(id__in=attendees)
                            elif single_filter['values'][0]=='3':
                                attendees = Booking.objects.filter(room__beds__gt=int(room_number)).values('attendee_id')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='4':
                                attendees = Booking.objects.filter(room__beds__lt=int(room_number)).values('attendee_id')
                                q &= Q(id__in=attendees)

                        if single_filter['condition']=='5':
                            if single_filter['values'][1] == '':
                                single_filter['values'][1] = 0
                            occupancy_value = int(single_filter['values'][1])


                            rooms = Room.objects.all()


                            if single_filter['values'][0]=='1':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))

                                    if occupancy['total_occupancy'] == occupancy_value:
                                        selected_rooms.append(room.id)
                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] != occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q &= Q(id__in=attendees)

                            elif single_filter['values'][0]=='3':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] > occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q &= Q(id__in=attendees)

                            elif single_filter['values'][0]=='4':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] < occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q &= Q(id__in=attendees)


                        if single_filter['condition']=='6':
                           value = single_filter['values'][1]
                           attendee_ids =[]
                           attendees = MatchLine.objects.raw('select m.* from match_line as m where m.match_id in (select n.match_id from match_line as n group by n.match_id having COUNT(*) > 1)')
                           for attendee in attendees:
                               attendee_ids.append(attendee.booking.attendee.id)

                           if single_filter['values'][0]=='1':
                              if value == '1':
                                  q &= Q(id__in=attendee_ids)
                              if value == '2':
                                  q &= ~Q(id__in=attendee_ids)

                           elif single_filter['values'][0]=='2':
                              if value == '1':
                                  q &= ~Q(id__in=attendee_ids)
                              if value == '2':
                                  q &= Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='10':
                        q = Q()
                        attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values('attendee_id')
                        if single_filter['condition'] == '1':
                           q &= Q(id__in=attendee_ids)
                        else:
                           q &= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='11':
                        q = Q()
                        attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],attendee_id__isnull=False).values('attendee_id')
                        if single_filter['values'][0] == '1':
                           q &= Q(id__in=attendee_ids)
                        else:
                           q &= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='12':
                        q = Q()
                        attendee_ids = MessageReceiversHistory.objects.filter(receiver__message_content_id=single_filter['condition'],receiver__attendee_id__isnull=False).values('receiver__attendee_id')
                        if single_filter['values'][0] == '1':
                           q &= Q(id__in=attendee_ids)
                        else:
                           q &= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='13':
                        q = Q()
                        if single_filter['values'][0] == '1':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
                           q &= Q(id__in=attendee_ids)

                        elif single_filter['values'][0] == '2':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
                           q &= ~Q(id__in=attendee_ids)

                        elif single_filter['values'][0] == '3':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count=int(single_filter['values'][1])).values('attendee_id')
                           q &= Q(id__in=attendee_ids)
                        elif single_filter['values'][0] == '4':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__gt=int(single_filter['values'][1])).values('attendee_id')
                           q &= Q(id__in=attendee_ids)
                        elif single_filter['values'][0] == '5':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__lt=int(single_filter['values'][1])).values('attendee_id')
                           q &= Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='14':
                        q = Q()
                        if single_filter['condition'] == '1':
                           attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
                           q &= Q(id__in=attendee_ids)

                        elif single_filter['condition'] == '2':
                           attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
                           q &= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field'] == '15':
                        q = Q()
                        if single_filter['condition'] == '1':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Attendee.objects.filter(registration_group__isnull=False, event_id=event_id,
                                                                       status="registered").values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
                                q &= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '2':
                                owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
                                attendee_ids = Attendee.objects.filter(registration_group__isnull=True, event_id=event_id,
                                                                       status="registered").values('id').exclude(id__in=owner_ids)
                                q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            if single_filter['values'][0] == '1':
                                attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values(
                                    'owner_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values(
                                    'owner_id')
                                q &= ~Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            if single_filter['values'][0] == '1':
                                value_checker = int(single_filter['values'][1])
                                if value_checker > 1:
                                    value_checker = value_checker - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
                                    cnt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
                                    'owner_id')
                                q &= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '2':
                                value_checker = int(single_filter['values'][1])
                                if value_checker > 1:
                                    value_checker = value_checker - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).exclude(
                                    cnt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
                                    'owner_id')
                                q &= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '3':
                                value_checker = int(single_filter['values'][1]) - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
                                    cnt__gt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
                                    'owner_id')
                                q &= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '4':
                                value_checker = int(single_filter['values'][1])
                                if value_checker > 1:
                                    value_checker = value_checker - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
                                    cnt__lt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
                                    'owner_id')
                                q &= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees, q, event_id)

                    if single_filter['field'] == '16':
                        q = Q()
                        if single_filter['condition'] == '1':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(status=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(status=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(created_at__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(created_at__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                single_filter['values'][1] += ' 23:59:59'
                                attendee_ids = Orders.objects.filter(created_at__gt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                single_filter['values'][1] += ' 00:00:00'
                                attendee_ids = Orders.objects.filter(created_at__lt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.filter(created_at__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.exclude(created_at__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1] + ' 00:00:00'
                                end_date = single_filter['values'][2] + ' 23:59:59'
                                attendee_ids = Orders.objects.filter(created_at__range=(start_date, end_date)).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(due_date__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(due_date__startswith=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                single_filter['values'][1] += ' 23:59:59'
                                attendee_ids = Orders.objects.filter(due_date__gt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                single_filter['values'][1] += ' 00:00:00'
                                attendee_ids = Orders.objects.filter(due_date__lt=single_filter['values'][1]).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.filter(due_date__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.exclude(due_date__range=(earlier, now)).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1] + ' 00:00:00'
                                end_date = single_filter['values'][2] + ' 23:59:59'
                                attendee_ids = Orders.objects.filter(due_date__range=(start_date, end_date)).values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '4':
                            # multiple_attendee_ids = Orders.objects.raw('SELECT o1.id,o1.attendee_id FROM orders o1 JOIN(SELECT order_number,Count(order_number) as order_number_count FROM orders GROUP BY order_number) o2 ON o1.order_number=o2.order_number where o2.order_number_count > 1')
                            # attendee_ids = []
                            # for attendee in multiple_attendee_ids:
                            #    attendee_ids.append(attendee.attendee.id)
                            multiple_groups = Orders.objects.values('order_number').annotate(count=Count('order_number')).filter(count__gt=1)
                            multiple_groups_no = []
                            for order_no in multiple_groups:
                                multiple_groups_no.append(order_no['order_number'])
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(order_number__in=multiple_groups_no).values('attendee_id')
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(order_number__in=multiple_groups_no).values('attendee_id')
                            q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '5':
                            current_time = datetime.datetime.now()
                            if single_filter['values'][0]=='1':
                                attendee_ids = Orders.objects.filter(due_date__lt=current_time,status="pending").values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                            elif single_filter['values'][0]=='2':
                                attendee_ids = Orders.objects.filter(due_date__gte=current_time,status="pending").values('attendee_id')
                                q &= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '6':
                            if single_filter['values'][0]=='1':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance=single_filter['values'][1]).exclude(status='paid')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').exclude(total_balance=single_filter['values'][1]).exclude(status='paid')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='3':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__gt=single_filter['values'][1]).exclude(status='paid')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='4':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__lt=single_filter['values'][1]).exclude(status='paid')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='5':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__range=(single_filter['values'][1],single_filter['values'][2])).exclude(status='paid')
                                q &= Q(id__in=attendees)
                        elif single_filter['condition'] == '7':
                            if single_filter['values'][0]=='1':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost=single_filter['values'][1])
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').exclude(total_cost=single_filter['values'][1])
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='3':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__gt=single_filter['values'][1])
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='4':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__lt=single_filter['values'][1])
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0]=='5':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__range=(single_filter['values'][1],single_filter['values'][2]))
                                q &= Q(id__in=attendees)
                        elif single_filter['condition'] == '8':
                            if single_filter['values'][0] == '1':
                                tmp_att = Orders.objects.filter(attendee__registration_group__isnull=True).exclude(status='cancelled').values('attendee_id')
                                attendees = RegistrationGroupOwner.objects.filter(owner_id__in=tmp_att).values('owner_id')
                                q &= Q(id__in=attendees)
                            elif single_filter['values'][0] == '2':
                                tmp_att = Orders.objects.filter(attendee__registration_group__isnull=True).exclude(status='cancelled').values('attendee_id')
                                attendees = RegistrationGroupOwner.objects.filter(owner_id__in=tmp_att).values('owner_id')
                                attendees = Orders.objects.exclude(attendee_id__in=attendees).values('attendee_id')
                                q &= Q(id__in=attendees)

                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)
                    if single_filter['field'] == '17':
                        q = Q()
                        if single_filter['values'][0] == '1':
                            attendee_ids = OrderItems.objects.filter(rebate_id=single_filter['condition']).values('order__attendee_id')
                            q &= Q(id__in=attendee_ids)
                        elif single_filter['values'][0] == '2':
                            attendee_ids = OrderItems.objects.exclude(rebate_id=single_filter['condition']).values('order__attendee_id')
                            q &= Q(id__in=attendee_ids)
                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)
                    if single_filter['field'] == '18':
                        q = Q()
                        checkpoint = Checkpoint.objects.get(id=single_filter['condition'])
                        checked_attendees = Scan.objects.filter(checkpoint_id=checkpoint.id, status=1).values('attendee_id')
                        if single_filter['values'][0] == '1':
                            if checkpoint.filter_id:
                                filter_checkpont = json.loads(checkpoint.filter.preset)
                                filtered_checkpoint_attendees = FilterHelper.get_attendee_using_filter(event_id, filter_checkpont, filter_checkpont[0][0]['matchFor'])
                                filter_checked_attendees = []
                                for att in checked_attendees:
                                    filter_checked_attendees.append(att['attendee_id'])
                                attendee_ids = list(set(filtered_checkpoint_attendees).intersection(filter_checked_attendees))
                            else:
                                attendee_ids = checked_attendees
                            q &= Q(id__in=attendee_ids)
                        else:
                            if checkpoint.session_id:
                                attendee_ids = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').exclude(attendee_id__in=checked_attendees).values('attendee_id')
                            elif checkpoint.filter_id:
                                filter_checkpont = json.loads(checkpoint.filter.preset)
                                filtered_checkpoint_attendees = FilterHelper.get_attendee_using_filter(event_id, filter_checkpont, filter_checkpont[0][0]['matchFor'])
                                filter_checked_attendees = []
                                for att in checked_attendees:
                                    filter_checked_attendees.append(att['attendee_id'])
                                attendee_ids = list(set(filtered_checkpoint_attendees) - set(filter_checked_attendees))
                            q &= Q(id__in=attendee_ids)
                        matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,q,event_id)


                elif match_condition == '1':
                    single_filter = filter1[0]
                    if single_filter['field']== '1' :
                        q = Q()
                        if single_filter['condition'] == '1':
                            q |= Q(created__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '2':
                            q |= ~Q(created__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '3':
                            single_filter['values'][0] += ' 23:59:59'
                            q |= Q(created__gt=single_filter['values'][0])
                        if single_filter['condition'] == '4':
                            single_filter['values'][0] += ' 00:00:00'
                            q |= Q(created__lt=single_filter['values'][0])
                        if single_filter['condition'] == '5':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q |= Q(created__range=(earlier, now))
                        if single_filter['condition'] == '6':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q |= ~Q(created__range=(earlier, now))
                        if single_filter['condition'] == '7':
                            start_date = single_filter['values'][0] + ' 00:00:00'
                            end_date = single_filter['values'][1] + ' 23:59:59'
                            q |= Q(created__range=(start_date, end_date))

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)


                    if single_filter['field']=='2':
                        # need to test again
                        q = Q()
                        if single_filter['condition'] == '1':
                            q |= Q(updated__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '2':
                            q |= ~Q(updated__startswith=single_filter['values'][0])
                        if single_filter['condition'] == '3':
                            single_filter['values'][0] += ' 23:59:59'
                            q |= Q(updated__gt=single_filter['values'][0])
                        if single_filter['condition'] == '4':
                            single_filter['values'][0] += ' 00:00:00'
                            q |= Q(updated__lt=single_filter['values'][0])
                        if single_filter['condition'] == '5':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q |= Q(updated__range=(earlier, now))
                        if single_filter['condition'] == '6':
                            now = datetime.datetime.now()
                            if single_filter['values'][1] == "1":
                                days_to_go = int(single_filter['values'][0]) * 1
                            elif single_filter['values'][1] == "2":
                                days_to_go = int(single_filter['values'][0]) * 7
                            elif single_filter['values'][1] == "3":
                                days_to_go = int(single_filter['values'][0]) * 30
                            earlier = now - datetime.timedelta(days_to_go)
                            q |= ~Q(updated__range=(earlier, now))
                        if single_filter['condition'] == '7':
                            start_date = single_filter['values'][0] + ' 00:00:00'
                            end_date = single_filter['values'][1] + ' 23:59:59'
                            q |= Q(updated__range=(start_date, end_date))

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='3':
                        q = Q()
                        attendee_ids = AttendeeGroups.objects.filter(group_id=single_filter['values'][0]).values(
                            'attendee_id')
                        if single_filter['condition'] == '1':
                            q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            q |= ~Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            new_attende_ids=[]
                            for attendee in attendee_ids:
                                if not AttendeeGroups.objects.filter(attendee_id=attendee['attendee_id']).exclude(group_id=single_filter['values'][0]).exists():
                                   new_attende_ids.append(attendee['attendee_id'])
                            q |= Q(id__in=new_attende_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='4':
                        q = Q()
                        attendee_ids = AttendeeTag.objects.filter(tag_id=single_filter['values'][0]).values(
                            'attendee_id')
                        if single_filter['condition'] == '1':
                            q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            q |= ~Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            new_attende_ids=[]
                            for attendee in attendee_ids:
                                if not AttendeeTag.objects.filter(attendee_id=attendee['attendee_id']).exclude(tag_id=single_filter['values'][0]).exists():
                                   new_attende_ids.append(attendee['attendee_id'])
                            q |= Q(id__in=new_attende_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='6':
                        q = Q()
                        attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0]).values(
                            'attendee_id')
                        if single_filter['condition'] == '1':
                            attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                                                                         status='attending').values('attendee_id')
                            q |= Q(id__in=attending)
                            # q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            # not_attending = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                            #                                              status='not-attending').values('attendee_id')
                            attending_data = SeminarsUsers.objects.filter(Q(Q(session_id=single_filter['values'][0]) & Q(Q(status='attending') | Q(status='in-queue') | Q(status='deciding')))).values('attendee_id')
                            # not_attending = Attendee.objects.values('id').exclude(id__in=attending_data)
                            # all_not_attending = attendee_ids | not_attending
                            q |= ~Q(id__in=attending_data)
                        elif single_filter['condition'] == '3':
                            attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                                                                        status='in-queue').values('attendee_id')
                            q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '4':
                            attendee_ids = SeminarsUsers.objects.filter(session_id=single_filter['values'][0],
                                                                        status='deciding').values('attendee_id')
                            q |= Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='7':
                        q = Q()
                        if 'type' in single_filter and (single_filter['type'] == 'text' or single_filter['type'] == 'textarea'):
                            if single_filter['values'][0] == '1':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__icontains=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '2':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value__icontains=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                                # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
                                #                                             value__icontains=single_filter['values'][
                                #                                                 1]).values('user_id')
                                #
                                # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
                                #     id__in=attendees_excludes)
                                # q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '3':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '4':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                                # attendees_excludes = Answers.objects.filter(question_id=int(single_filter['condition']),
                                #                                             value=single_filter['values'][1]).values(
                                #     'user_id')
                                # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
                                #     id__in=attendees_excludes)
                                # q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '5':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__istartswith=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '6':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']), value__iendswith=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0]=='7':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0]=='8':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)
                        elif 'type' in single_filter and single_filter['type'] == 'date':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value=single_filter['values'][1])
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                # single_filter['values'][1] += ' 23:59:59'
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__gt=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                # single_filter['values'][1] += ' 00:00:00'
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__lt=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__range=(earlier, now)).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value__range=(earlier, now))
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__range=(start_date, end_date)).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '8':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '9':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'date_range':
                            if single_filter['values'][0] == '1':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                date_range = '["{0}","{1}"]'.format(start_date, end_date)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value=date_range).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                date_range = '["{0}","{1}"]'.format(start_date, end_date)
                                attendee_ids = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id').exclude(value=date_range)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                start_date_2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                                end_date_2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                                for a in attendee_list:
                                    dates = json.loads(a.value)
                                    date_from = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
                                    date_to = datetime.datetime.strptime(dates[1], "%Y-%m-%d")
                                    if start_date_2 <= date_from and end_date_2 >= date_to:
                                        attendee_ids.append(a.user_id)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                start_date_2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                                end_date_2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                                for a in attendee_list:
                                    dates = json.loads(a.value)
                                    date_from = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
                                    date_to = datetime.datetime.strptime(dates[1], "%Y-%m-%d")
                                    if not(start_date_2 <= date_from and end_date_2 >= date_to):
                                        attendee_ids.append(a.user_id)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '6':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'time':
                            if single_filter['values'][0] == '1':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value=time).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id').exclude(value=time)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__gt=time).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                time = single_filter['values'][1].zfill(5)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__lt=time).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                date_time_now = datetime.datetime.now()
                                now = date_time_now.strftime('%H:%M')
                                if single_filter['values'][2] == "1":
                                    earlier_date = date_time_now - datetime.timedelta(minutes=int(single_filter['values'][1]))
                                elif single_filter['values'][2] == "2":
                                    earlier_date = date_time_now - datetime.timedelta(hours=int(single_filter['values'][1]))
                                earlier = earlier_date.strftime('%H:%M')
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__range=(earlier, now)).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                date_time_now = datetime.datetime.now()
                                now = date_time_now.strftime('%H:%M')
                                if single_filter['values'][2] == "1":
                                    earlier_date = date_time_now - datetime.timedelta(minutes=int(single_filter['values'][1]))
                                elif single_filter['values'][2] == "2":
                                    earlier_date = date_time_now - datetime.timedelta(hours=int(single_filter['values'][1]))
                                earlier = earlier_date.strftime('%H:%M')
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value__range=(earlier, now))
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value__range=(start_time, end_time)).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '8':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '9':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)

                        elif 'type' in single_filter and single_filter['type'] == 'time_range':
                            if single_filter['values'][0] == '1':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                time_range = '["{0}","{1}"]'.format(start_time, end_time)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                      value=time_range).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                start_time = datetime.datetime.strptime(single_filter['values'][1],'%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                time_range = '["{0}","{1}"]'.format(start_time, end_time)
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id').exclude(value=time_range)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                for a in attendee_list:
                                    times = json.loads(a.value)
                                    time_from = datetime.datetime.strptime(times[0], '%H:%M').strftime('%H:%M')
                                    time_to = datetime.datetime.strptime(times[1], '%H:%M').strftime('%H:%M')
                                    if start_time <= time_from and end_time >= time_to:
                                        attendee_ids.append(a.user_id)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                start_time = datetime.datetime.strptime(single_filter['values'][1], '%H:%M').strftime('%H:%M')
                                end_time = datetime.datetime.strptime(single_filter['values'][2], '%H:%M').strftime('%H:%M')
                                attendee_list = Answers.objects.filter(question_id=int(single_filter['condition']))
                                attendee_ids = []
                                for a in attendee_list:
                                    times = json.loads(a.value)
                                    time_from = datetime.datetime.strptime(times[0], '%H:%M').strftime('%H:%M')
                                    time_to = datetime.datetime.strptime(times[1], '%H:%M').strftime('%H:%M')
                                    if not (start_time <= time_from and end_time >= time_to):
                                        attendee_ids.append(a.user_id)
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '6':
                                attendees_matches = Answers.objects.filter(
                                    question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)
                        elif 'type' in single_filter and single_filter['type'] == 'country':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition']), value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '4':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)
                        else:
                            if single_filter['values'][0] == '1':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition']),
                                                                           value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0] == '2':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                q |= Q(id__in=attendees_matches)
                                # attendees_excludes = Answers.objects.filter(
                                #     question_id=int(single_filter['condition']),
                                #     value=single_filter['values'][1]).values('user_id')
                                # attendees_matches = Attendee.objects.filter(event_id=event_id,status="registered").exclude(
                                #     id__in=attendees_excludes)
                                # q |= Q(id__in=attendees_matches)


                                # attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).exclude(value=single_filter['values'][1]).values('user_id')
                                # q |= Q(id__in=attendees_matches)
                            elif single_filter['values'][0]=='3':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q |= ~Q(id__in=attendees_matches)
                            elif single_filter['values'][0]=='4':
                                attendees_matches = Answers.objects.filter(question_id=int(single_filter['condition'])).values('user_id')
                                q |= Q(id__in=attendees_matches)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='8':
                        q = Q()
                        attendee_ids = DeviceToken.objects.all().values('attendee_id')
                        if single_filter['condition'] == '1':
                           q |= Q(id__in=attendee_ids)
                        else:
                           q |= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='9':
                        q = Q()
                        if single_filter['condition']=='1':
                            room_id = single_filter['values'][1]
                            # attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
                            if single_filter['values'][0]=='1':
                                attendees = Booking.objects.filter(room_id=int(room_id)).values('attendee_id')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = Booking.objects.exclude(room_id=int(room_id)).values('attendee_id')
                                q |= Q(id__in=attendees)
                                # q |= ~Q(id__in=attendees)

                        if single_filter['condition']=='2':

                            if single_filter['values'][0] == '1':
                                attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)
                            if single_filter['values'][0] == '2':
                                attendees = Booking.objects.exclude(check_in__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_in__startswith=single_filter['values'][1]).values('attendee_id')
                                # q |= ~Q(id__in=attendees)
                            if single_filter['values'][0] == '3':
                                # single_filter['values'][1] += ' 23:59:59'
                                attendees = Booking.objects.filter(check_in__gt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)

                            if single_filter['values'][0] == '4':
                                # single_filter['values'][1] += ' 00:00:00'
                                attendees = Booking.objects.filter(check_in__lt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)

                            if single_filter['values'][0]== '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendees)
                            if single_filter['values'][0]== '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.exclude(check_in__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_in__range=(earlier, now)).values('attendee_id')
                                # q |= ~Q(id__in=attendees)

                            if single_filter['values'][0] == '7':
                                # start_date = single_filter['values'][1] + ' 00:00:00'
                                # end_date = single_filter['values'][2] + ' 23:59:59'
                                # change
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendees = Booking.objects.filter(check_in__range=(start_date, end_date)).values('attendee_id')
                                q |= Q(id__in=attendees)

                        if single_filter['condition']=='3':

                            if single_filter['values'][0] == '1':
                                attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)
                            if single_filter['values'][0] == '2':
                                attendees = Booking.objects.exclude(check_out__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_out__startswith=single_filter['values'][1]).values('attendee_id')
                                # q |= ~Q(id__in=attendees)
                            if single_filter['values'][0] == '3':
                                # single_filter['values'][1] += ' 23:59:59'
                                attendees = Booking.objects.filter(check_out__gt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)

                            if single_filter['values'][0] == '4':
                                # single_filter['values'][1] += ' 00:00:00'
                                attendees = Booking.objects.filter(check_out__lt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendees)

                            if single_filter['values'][0]== '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendees)
                            if single_filter['values'][0]== '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendees = Booking.objects.exclude(check_out__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(check_out__range=(earlier, now)).values('attendee_id')
                                # q |= ~Q(id__in=attendees)

                            if single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1]
                                end_date = single_filter['values'][2]
                                attendees = Booking.objects.filter(check_out__range=(start_date, end_date)).values('attendee_id')
                                q |= Q(id__in=attendees)

                        if single_filter['condition']=='4':
                            room_number = single_filter['values'][1]

                            if single_filter['values'][0]=='1':
                                attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = Booking.objects.exclude(room__beds=int(room_number)).values('attendee_id')
                                q |= Q(id__in=attendees)
                                # attendees = Booking.objects.filter(room__beds=int(room_number)).values('attendee_id')
                                # q |= ~Q(id__in=attendees)
                            elif single_filter['values'][0]=='3':
                                attendees = Booking.objects.filter(room__beds__gt=int(room_number)).values('attendee_id')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='4':
                                attendees = Booking.objects.filter(room__beds__lt=int(room_number)).values('attendee_id')
                                q |= Q(id__in=attendees)

                        if single_filter['condition']=='5':
                            if single_filter['values'][1] == '':
                                single_filter['values'][1] = 0
                            occupancy_value = int(single_filter['values'][1])

                            rooms = Room.objects.all()


                            if single_filter['values'][0]=='1':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] == occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] != occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q |= Q(id__in=attendees)

                            elif single_filter['values'][0]=='3':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] > occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q |= Q(id__in=attendees)

                            elif single_filter['values'][0]=='4':
                                selected_rooms=[]
                                for room in rooms:
                                    occupancy = RoomView.find_booking(str(room.id))
                                    if occupancy['total_occupancy'] < occupancy_value:
                                        selected_rooms.append(room.id)


                                attendees = Booking.objects.filter(room_id__in=selected_rooms).values('attendee_id')
                                q |= Q(id__in=attendees)

                        if single_filter['condition']=='6':
                           value = single_filter['values'][1]
                           attendee_ids =[]
                           attendees = MatchLine.objects.raw('select m.* from match_line as m where m.match_id in (select n.match_id from match_line as n group by n.match_id having COUNT(*) > 1)')
                           for attendee in attendees:
                               attendee_ids.append(attendee.booking.attendee.id)

                           if single_filter['values'][0]=='1':
                              if value == '1':
                                  q |= Q(id__in=attendee_ids)
                              if value == '2':
                                  q |= ~Q(id__in=attendee_ids)

                           elif single_filter['values'][0]=='2':
                              if value == '1':
                                  q |= ~Q(id__in=attendee_ids)
                              if value == '2':
                                  q |= Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='10':
                        q = Q()
                        attendee_ids = SeminarSpeakers.objects.all().extra(select={'attendee_id': 'speaker_id'}).values('attendee_id')
                        if single_filter['condition'] == '1':
                           q |= Q(id__in=attendee_ids)
                        else:
                           q |= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='11':
                        q = Q()
                        attendee_ids = EmailReceivers.objects.filter(email_content_id=single_filter['condition'],attendee_id__isnull=False).values('attendee_id')
                        if single_filter['values'][0] == '1':
                           q |= Q(id__in=attendee_ids)
                        else:
                           q |= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='12':
                        q = Q()
                        attendee_ids = MessageReceiversHistory.objects.filter(receiver__message_content_id=single_filter['condition'],receiver__attendee_id__isnull=False).values('receiver__attendee_id')
                        if single_filter['values'][0] == '1':
                           q |= Q(id__in=attendee_ids)
                        else:
                           q |= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='13':
                        q = Q()
                        if single_filter['values'][0] == '1':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
                           q |= Q(id__in=attendee_ids)

                        elif single_filter['values'][0] == '2':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition']).values('attendee_id')
                           q |= ~Q(id__in=attendee_ids)

                        elif single_filter['values'][0] == '3':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count=int(single_filter['values'][1])).values('attendee_id')
                           q |= Q(id__in=attendee_ids)
                        elif single_filter['values'][0] == '4':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__gt=int(single_filter['values'][1])).values('attendee_id')
                           q |= Q(id__in=attendee_ids)
                        elif single_filter['values'][0] == '5':
                           attendee_ids = AttendeeSubmitButton.objects.filter(button_id=single_filter['condition'],hit_count__lt=int(single_filter['values'][1])).values('attendee_id')
                           q |= Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field']=='14':
                        q = Q()
                        if single_filter['condition'] == '1':
                           attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
                           q |= Q(id__in=attendee_ids)

                        elif single_filter['condition'] == '2':
                           attendee_ids = Attendee.objects.filter(language_id=single_filter['values'][0],status="registered").values('id')
                           q |= ~Q(id__in=attendee_ids)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

                    if single_filter['field'] == '15':
                        q = Q()
                        if single_filter['condition'] == '1':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Attendee.objects.filter(registration_group__isnull=False, event_id=event_id, status="registered").values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
                                q |= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '2':
                                owner_ids = RegistrationGroupOwner.objects.filter(group__event_id=event_id).values('owner_id')
                                attendee_ids = Attendee.objects.filter(registration_group__isnull=True, event_id=event_id, status="registered").values('id').exclude(id__in=owner_ids)
                                q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            if single_filter['values'][0] == '1':
                                attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values('owner_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = RegistrationGroupOwner.objects.filter(owner__event_id=event_id).values('owner_id')
                                q |= ~Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            if single_filter['values'][0] == '1':
                                value_checker = int(single_filter['values'][1])
                                if value_checker>1:
                                    value_checker = value_checker - 1
                                groups_ids = Attendee.objects.filter(event_id=15,registration_group__isnull=False).values('registration_group_id').annotate(cnt=Count('registration_group_id')).filter(cnt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values('owner_id')
                                q |= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '2':
                                value_checker = int(single_filter['values'][1])
                                if value_checker > 1:
                                    value_checker = value_checker - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).exclude(
                                    cnt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values('owner_id')
                                q |= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '3':
                                value_checker = int(single_filter['values'][1]) - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
                                    cnt__gt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
                                    'owner_id')
                                q |= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)
                            elif single_filter['values'][0] == '4':
                                value_checker = int(single_filter['values'][1])
                                if value_checker > 1:
                                    value_checker = value_checker - 1
                                groups_ids = Attendee.objects.filter(event_id=15, registration_group__isnull=False).values(
                                    'registration_group_id').annotate(cnt=Count('registration_group_id')).filter(
                                    cnt__lt=value_checker).values('registration_group_id')
                                attendee_ids = Attendee.objects.filter(registration_group_id__in=groups_ids).values('id')
                                owner_ids = RegistrationGroupOwner.objects.filter(group_id__in=groups_ids).values(
                                    'owner_id')
                                q |= Q(id__in=attendee_ids)
                                q |= Q(id__in=owner_ids)


                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees, q, event_id)

                    if single_filter['field'] == '16':
                        q = Q()
                        if single_filter['condition'] == '1':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(status=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(status=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '2':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(created_at__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(created_at__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                single_filter['values'][1] += ' 23:59:59'
                                attendee_ids = Orders.objects.filter(created_at__gt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                single_filter['values'][1] += ' 00:00:00'
                                attendee_ids = Orders.objects.filter(created_at__lt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.filter(created_at__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.exclude(created_at__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1] + ' 00:00:00'
                                end_date = single_filter['values'][2] + ' 23:59:59'
                                attendee_ids = Orders.objects.filter(created_at__range=(start_date, end_date)).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '3':
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(due_date__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(due_date__startswith=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '3':
                                single_filter['values'][1] += ' 23:59:59'
                                attendee_ids = Orders.objects.filter(due_date__gt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '4':
                                single_filter['values'][1] += ' 00:00:00'
                                attendee_ids = Orders.objects.filter(due_date__lt=single_filter['values'][1]).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '5':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.filter(due_date__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '6':
                                now = datetime.datetime.now()
                                if single_filter['values'][2] == "1":
                                    days_to_go = int(single_filter['values'][1]) * 1
                                elif single_filter['values'][2] == "2":
                                    days_to_go = int(single_filter['values'][1]) * 7
                                elif single_filter['values'][2] == "3":
                                    days_to_go = int(single_filter['values'][1]) * 30
                                earlier = now - datetime.timedelta(days_to_go)
                                attendee_ids = Orders.objects.exclude(due_date__range=(earlier, now)).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0] == '7':
                                start_date = single_filter['values'][1] + ' 00:00:00'
                                end_date = single_filter['values'][2] + ' 23:59:59'
                                attendee_ids = Orders.objects.filter(due_date__range=(start_date, end_date)).values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '4':
                            # multiple_attendee_ids = Orders.objects.raw('SELECT o1.id,o1.attendee_id FROM orders o1 JOIN(SELECT order_number,Count(order_number) as order_number_count FROM orders GROUP BY order_number) o2 ON o1.order_number=o2.order_number where o2.order_number_count > 1')
                            # attendee_ids = []
                            # for attendee in multiple_attendee_ids:
                            #    attendee_ids.append(attendee.attendee.id)
                            multiple_groups = Orders.objects.values('order_number').annotate(count=Count('order_number')).filter(count__gt=1)
                            multiple_groups_no = []
                            for order_no in multiple_groups:
                                multiple_groups_no.append(order_no['order_number'])
                            if single_filter['values'][0] == '1':
                                attendee_ids = Orders.objects.filter(order_number__in=multiple_groups_no).values('attendee_id')
                            elif single_filter['values'][0] == '2':
                                attendee_ids = Orders.objects.exclude(order_number__in=multiple_groups_no).values('attendee_id')
                            q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '5':
                            current_time = datetime.datetime.now()
                            if single_filter['values'][0]=='1':
                                attendee_ids = Orders.objects.filter(due_date__lt=current_time,status="pending").values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                            elif single_filter['values'][0]=='2':
                                attendee_ids = Orders.objects.filter(due_date__gte=current_time,status="pending").values('attendee_id')
                                q |= Q(id__in=attendee_ids)
                        elif single_filter['condition'] == '6':
                            if single_filter['values'][0]=='1':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance=single_filter['values'][1]).exclude(status='paid')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').exclude(total_balance=single_filter['values'][1]).exclude(status='paid')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='3':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__gt=single_filter['values'][1]).exclude(status='paid')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='4':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__lt=single_filter['values'][1]).exclude(status='paid')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='5':
                                attendees = CreditOrders.objects.values('order_id').annotate(count=Count('order_id'),total_balance=Sum('cost_including_vat')).values('order__attendee_id').filter(total_balance__range=(single_filter['values'][1],single_filter['values'][2])).exclude(status='paid')
                                q |= Q(id__in=attendees)
                        elif single_filter['condition'] == '7':
                            if single_filter['values'][0]=='1':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost=single_filter['values'][1])
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='2':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').exclude(total_cost=single_filter['values'][1])
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='3':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__gt=single_filter['values'][1])
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='4':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__lt=single_filter['values'][1])
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0]=='5':
                                attendees = Orders.objects.annotate(total_cost=F('cost')+F('vat_amount')).values('attendee_id').filter(total_cost__range=(single_filter['values'][1],single_filter['values'][2]))
                                q |= Q(id__in=attendees)
                        elif single_filter['condition'] == '8':
                            if single_filter['values'][0] == '1':
                                tmp_att = Orders.objects.filter(attendee__registration_group__isnull=True).exclude(status='cancelled').values('attendee_id')
                                attendees = RegistrationGroupOwner.objects.filter(owner_id__in=tmp_att).values('owner_id')
                                q |= Q(id__in=attendees)
                            elif single_filter['values'][0] == '2':
                                tmp_att = Orders.objects.filter(attendee__registration_group__isnull=True).exclude(status='cancelled').values('attendee_id')
                                attendees = RegistrationGroupOwner.objects.filter(owner_id__in=tmp_att).values('owner_id')
                                attendees = Orders.objects.exclude(attendee_id__in=attendees).values('attendee_id')
                                q |= Q(id__in=attendees)

                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)
                    if single_filter['field'] == '17':
                        q = Q()
                        if single_filter['values'][0] == '1':
                            attendee_ids = OrderItems.objects.filter(rebate_id=single_filter['condition']).values('order__attendee_id')
                            q |= Q(id__in=attendee_ids)
                        elif single_filter['values'][0] == '2':
                            attendee_ids = OrderItems.objects.exclude(rebate_id=single_filter['condition']).values('order__attendee_id')
                            q |= Q(id__in=attendee_ids)
                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)
                    if single_filter['field'] == '18':
                        q = Q()
                        checkpoint = Checkpoint.objects.get(id=single_filter['condition'])
                        checked_attendees = Scan.objects.filter(checkpoint_id=checkpoint.id, status=1).values('attendee_id')
                        if single_filter['values'][0] == '1':
                            if checkpoint.filter_id:
                                filter_checkpont = json.loads(checkpoint.filter.preset)
                                filtered_checkpoint_attendees = FilterHelper.get_attendee_using_filter(event_id, filter_checkpont, filter_checkpont[0][0]['matchFor'])
                                filter_checked_attendees = []
                                for att in checked_attendees:
                                    filter_checked_attendees.append(att['attendee_id'])
                                attendee_ids = list(set(filtered_checkpoint_attendees).intersection(filter_checked_attendees))
                            else:
                                attendee_ids = checked_attendees
                            q |= Q(id__in=attendee_ids)
                        else:
                            if checkpoint.session_id:
                                attendee_ids = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').exclude(attendee_id__in=checked_attendees).values('attendee_id')
                            elif checkpoint.filter_id:
                                filter_checkpont = json.loads(checkpoint.filter.preset)
                                filtered_checkpoint_attendees = FilterHelper.get_attendee_using_filter(event_id, filter_checkpont, filter_checkpont[0][0]['matchFor'])
                                filter_checked_attendees = []
                                for att in checked_attendees:
                                    filter_checked_attendees.append(att['attendee_id'])
                                attendee_ids = list(set(filtered_checkpoint_attendees) - set(filter_checked_attendees))
                            q |= Q(id__in=attendee_ids)
                        matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,q,event_id)

            else:
                match_condition_inner = filter1[0][0]['matchFor']
                if match_condition == '2':
                    main_q = Q()
                    total_matched_attendees = FilterHelper.get_attendee_using_filter(event_id, filter1, match_condition_inner)
                    main_q &= Q(id__in=total_matched_attendees)
                    matched_attendees = FilterHelper.get_matched_attendees(matched_attendees,main_q,event_id)
                    # main_q &= Q(id__in=FilterHelper.get_attendee_using_filter(event_id, filter1, match_condition_inner))
                elif match_condition == '1':
                    main_q = Q(id=-11)
                    total_matched_attendees = FilterHelper.get_attendee_using_filter(event_id, filter1, match_condition_inner,matched_attendees)
                    main_q |= Q(id__in=total_matched_attendees)
                    matched_attendees = FilterHelper.get_all_matched_attendees(matched_attendees,main_q,event_id)
                    # main_q |= Q(id__in=FilterHelper.get_attendee_using_filter(event_id, filter1, match_condition_inner))
        all_main_q &= Q(event_id=event_id)
        all_main_q &= Q(id__in=matched_attendees, status='registered')
        total_attendees = Attendee.objects.filter(all_main_q).values('id')

        all_attendess = []
        for att in total_attendees:
            all_attendess.append(att['id'])
        return all_attendess
    
    def get_matched_attendees(matched_attendees,q,event_id):
        attendees = Attendee.objects.filter(q).filter(event_id=event_id).values('id')
        attendees_array = []
        for attendee in attendees:
            attendees_array.append(attendee['id'])
        matched_attendees = list(set(matched_attendees) & set(attendees_array))
        return matched_attendees

    def get_all_matched_attendees(matched_attendees,q,event_id):
        attendees = Attendee.objects.filter(q).filter(event_id=event_id).values('id')
        attendees_array = []
        for attendee in attendees:
            attendees_array.append(attendee['id'])
        matched_attendees = list(set(matched_attendees) | set(attendees_array))
        return matched_attendees