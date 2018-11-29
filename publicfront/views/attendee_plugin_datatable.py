from itertools import chain
from datetime import datetime
from django.db.models import Q, Count, Max, Sum, F
from django_datatables_view.base_datatable_view import BaseDatatableView
from app.models import ExportRule, Questions, Answers, AttendeeGroups, AttendeeTag, Orders, Payments, Attendee, Tag, \
    Session, SeminarsUsers, Booking, MatchLine, RequestedBuddy, OrderItems, CreditUsages, Group
from app.views.gbhelper.common_helper import CommonHelper
from publicfront.views.common import utc_to_local, get_formated_date_string, get_formated_date
from publicfront.views.helper import HelperData
from .attendee_plugin import AttendeePluginList
import json


class AttendeePluginDatatable(BaseDatatableView):
    order_columns = []
    questions = []
    table_headers = []
    session_list = []
    hotel_columns = []
    economy_columns = ""
    max_attendee_orders = 1
    max_booking_number = 1
    max_actual_room_buddy = 1
    country_list = []
    show_counting_column = False
    start = 0
    limit = 10

    def get_initial_queryset(self):
        self.questions = []
        self.table_headers = []
        self.order_columns = []
        self.session_list = []
        self.hotel_columns = []
        self.max_booking_number = 1
        self.max_actual_room_buddy = 1
        self.show_counting_column = False
        self.country_list = CommonHelper.get_country_list(self)
        self.start = 0
        self.limit = 10
        attendee_export_id = self.request.POST.get('attendee_export_id')
        export_rule = ExportRule.objects.filter(id=attendee_export_id)
        preset_data = json.loads(export_rule[0].preset)
        filter_id = preset_data['rule_id']

        show_counting_column = self.request.POST.get('show_counting_column')
        self.show_counting_column = eval(show_counting_column) if show_counting_column else False

        if self.show_counting_column:
            self.order_columns.append('1_count')

        if 'uid' in preset_data and preset_data['uid']:
            self.table_headers.append('uid')
            self.order_columns.append('111111_gen')
        if 'rdate' in preset_data and preset_data['rdate']:
            self.table_headers.append('rdate')
            self.order_columns.append('222222_gen')
        if 'udate' in preset_data and preset_data['udate']:
            self.table_headers.append('udate')
            self.order_columns.append('333333_gen')
        if 'secret' in preset_data and preset_data['secret']:
            self.table_headers.append('secret')
            self.order_columns.append('444444_gen')
        if 'bid' in preset_data and preset_data['bid']:
            self.table_headers.append('bid')
            self.order_columns.append('555555_gen')
        if 'attGroup' in preset_data and preset_data['attGroup']:
            self.table_headers.append('att-grp')
            self.order_columns.append('666666_gen')
        if 'attTag' in preset_data and preset_data['attTag']:
            self.table_headers.append('att-tag')
            self.order_columns.append('777777_gen')

        question_ids = preset_data['questions'].split(',')
        if '' in question_ids:
            question_ids.remove('')
        question_ids = [int(c_i) for c_i in question_ids]
        attendees = AttendeePluginList.get_all_attendee(self.request, filter_id).order_by('id')
        self.questions = Questions.objects.filter(id__in=question_ids)
        for question in self.questions:
            self.order_columns.append(str(question.id) + '_qid')

        if 'sessions' in preset_data and preset_data['sessions'] != '':
            sessions = preset_data['sessions'].split(',')
            for session in sessions:
                if session != '':
                    self.order_columns.append(str(session) + '_session')
                    self.session_list.append(Session.objects.filter(id=session).first())

        if 'hotel_columns' in preset_data:
            hotels = preset_data['hotel_columns'].split(',')
            if hotels not in [None, '']:
                max_b_number_obj = Booking.objects.filter(attendee_id__in=attendees).values('attendee_id').annotate(
                    total=Count('attendee_id')).aggregate(max_booking_number=Max('total'))
                if max_b_number_obj['max_booking_number']:
                    self.max_booking_number = max_b_number_obj['max_booking_number']
                if 'rba-col' in hotels or 'rba-checkin-col' in hotels or 'rba-checkout-col' in hotels:
                    match_ids = MatchLine.objects.filter(booking__attendee_id__in=attendees).values('match_id')
                    max_a_room_bud = MatchLine.objects.filter(match_id__in=match_ids).values(
                        'match_id').annotate(total=Count('match_id')).aggregate(max_total=Max('total'))
                    if max_a_room_bud['max_total']:
                        self.max_actual_room_buddy = max_a_room_bud['max_total'] - 1

                for max_booking_i in range(0, self.max_booking_number):
                    if 'booking-id-col' in hotels:
                        self.hotel_columns.append('booking-id-col')
                    if 'match-id-col' in hotels:
                        self.hotel_columns.append('match-id-col')
                    if 'hotel-name-col' in hotels:
                        self.hotel_columns.append('hotel-name-col')
                    if 'description-col' in hotels:
                        self.hotel_columns.append('description-col')
                    if 'room-id-col' in hotels:
                        self.hotel_columns.append('room-id-col')
                    if 'check-in-col' in hotels:
                        self.hotel_columns.append('check-in-col')
                    if 'check-out-col' in hotels:
                        self.hotel_columns.append('check-out-col')
                    if 'beds-col' in hotels:
                        self.hotel_columns.append('beds-col')
                    if 'location-col' in hotels:
                        self.hotel_columns.append('location-col')
                    if 'rbr-col' in hotels:
                        self.hotel_columns.append('rbr-col')
                    for i in range(0, self.max_actual_room_buddy):
                        if 'rba-col' in hotels:
                            self.hotel_columns.append('rba-col')
                        if 'rba-checkin-col' in hotels:
                            self.hotel_columns.append('rba-checkin-col')
                        if 'rba-checkout-col' in hotels:
                            self.hotel_columns.append('rba-checkout-col')

        if 'economy_columns' in preset_data:
            self.economy_columns = preset_data.get('economy_columns')
            max_order_counter_obj = Orders.objects.filter(attendee_id__in=attendees, cost__gt=0).values('attendee_id').annotate(
                total=Count('attendee_id')).aggregate(max_order_counter=Max('total'))
            if max_order_counter_obj["max_order_counter"]:
                self.max_attendee_orders = max_order_counter_obj["max_order_counter"]
        return attendees

    def filter_queryset(self, qs):
        if not self.pre_camel_case_notation:
            search = self.request.POST.get('search[value]', None).strip()
            if not search:
                return qs
            try:
                search.index(' ')
                has_space = True
            except:
                has_space = False

            extra_answers_filtered = Answers.objects.filter(user__in=qs).values_list('user_id', flat=True).order_by('user_id')
            extra_attendee_ids = set(extra_answers_filtered)
            answers_filtered = Answers.objects.filter(user__in=qs, value__icontains=search,
                                                      question__in=self.questions).values_list('user_id', flat=True).order_by('user_id')
            attendee_ids = set(answers_filtered)
            newResultsId = []

            if 'rdate' in self.table_headers:
                newResults = Attendee.objects.filter(created__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)
            if 'udate' in self.table_headers:
                newResults = Attendee.objects.filter(updated__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)

            if 'secret' in self.table_headers:
                newResults = Attendee.objects.filter(secret_key__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)

            if 'bid' in self.table_headers:
                newResults = Attendee.objects.filter(bid__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)

            if 'att-grp' in self.table_headers:
                tempGroupresult = AttendeeGroups.objects.filter(group__name__icontains=search,attendee_id__in=extra_attendee_ids)
                for newResult in tempGroupresult:
                    newResultsId.append(newResult.attendee.id)

            if 'att-tag' in self.table_headers:
                tempTagresults = Tag.objects.filter(name__startswith=search, event_id=self.request.session['event_id'])

                for tempTagresult in tempTagresults:
                    tempAttendeeTags = AttendeeTag.objects.filter(tag_id=tempTagresult.id,
                                                                  attendee_id__in=extra_attendee_ids)
                    for tempAttendeeTag in tempAttendeeTags:
                        newResultsId.append(tempAttendeeTag.attendee_id)

            newResultsId = list(set(newResultsId) ^ set(list(set(attendee_ids).intersection(newResultsId))))
            attendee_ids = list(chain(attendee_ids, newResultsId))
            q1 = Q()
            q1 |= Q(id__in=attendee_ids)
            qs = qs.filter(q1).order_by('id')
        return qs

    def prepare_results(self, qs):
        json_data = []
        counter = self.start + 1
        event_id = self.request.session['event_id']
        event_vat_count = 0
        if self.economy_columns:
            if "vat-xx-percent-sum" in self.economy_columns:
                vat_objects = Group.objects.filter(event_id=event_id, type='payment').values('name')
                for vat in vat_objects:
                    if vat["name"].isdigit():
                        event_vat_count += 1
        for q in qs:
            items = []
            if self.show_counting_column:
                items.append(counter)
                counter += 1
            if 'uid' in self.table_headers:
                items.append(q.id)
            if 'rdate' in self.table_headers:
                created_date = utc_to_local(self.request, str(q.created.strftime("%Y-%m-%d %H:%M:%S")))
                items.append(get_formated_date(self.request, created_date))
            if 'udate' in self.table_headers:
                updated_date = utc_to_local(self.request, str(q.updated.strftime("%Y-%m-%d %H:%M:%S")))
                items.append(get_formated_date(self.request, updated_date))
            if 'secret' in self.table_headers:
                items.append(q.secret_key)
            if 'bid' in self.table_headers:
                items.append(q.bid)
            if 'att-grp' in self.table_headers:
                groups = AttendeeGroups.objects.filter(attendee_id=q.id)
                groupList = ','.join(g.group.name for g in groups)
                items.append(groupList)
            if 'att-tag' in self.table_headers:
                tags = AttendeeTag.objects.filter(attendee_id=q.id)
                taglist = ','.join(t.tag.name for t in tags)
                items.append(taglist)

            answers = Answers.objects.filter(user_id=q.id).order_by('user_id')
            for question in self.questions:
                ans = ''
                for answer in answers:
                    if answer.question_id == question.id:
                        if answer.question.type == 'checkbox':
                            ans = answer.value.replace('<br>', ', ')
                        elif answer.question.type == 'date_range':
                            values = json.loads(answer.value)
                            if len(values[0]) > 0 and len(values[1]) > 0:
                                ans = values[0]+' to '+values[1]
                        elif answer.question.type == 'time_range':
                            values = json.loads(answer.value)
                            if len(values[0]) > 0 and len(values[1]) > 0:
                                ans = values[0]+' to '+values[1]
                        elif answer.question.type == 'country':
                            if answer.value in self.country_list:
                                ans = self.country_list[answer.value]
                        else:
                            ans = answer.value
                        break
                items.append(ans)

            for session in self.session_list:
                ans = ''
                session_object = SeminarsUsers.objects.filter(attendee_id=q.id, session_id=session.id).first()
                if session_object:
                    if session_object.status in ['attending', 'Attending']:
                        ans = 'Attending'
                items.append(ans)

            if self.hotel_columns not in [None, '']:
                max_booking_number = self.max_booking_number
                att_booking_counter = 0
                att_bookings = Booking.objects.filter(attendee_id=q.id)
                for att_booking in att_bookings:
                    att_booking_counter += 1
                    items.extend(self.get_hotel_booking_data(q, att_booking))
                if max_booking_number > att_booking_counter:
                    max_booking_number -= att_booking_counter
                    for i in range(0, max_booking_number):
                        items.extend(self.get_hotel_booking_data(q, None))
            if self.economy_columns:
                attendee_orders = Orders.objects.filter(attendee_id=q.id, cost__gt=0)
                for attendee_order in attendee_orders:
                    cost_excl_vat = 0
                    cost_incl_vat = 0
                    transaction_date = ""
                    payment_method = ""
                    credit_usage_value = 0
                    credit_usage_obj = CreditUsages.objects.filter(order_number=attendee_order.order_number).aggregate(Sum('cost'))
                    if credit_usage_obj['cost__sum']:
                        credit_usage_value = credit_usage_obj['cost__sum']

                    if 'order-number' in self.economy_columns:
                        if q.registration_group:
                            items.append(attendee_order.order_number)
                        else:
                            items.append("{}(order owner)".format(attendee_order.order_number))
                    if 'order-status' in self.economy_columns:
                        items.append(attendee_order.status)
                    if 'invoice-id' in self.economy_columns:
                        items.append(attendee_order.invoice_ref if attendee_order.invoice_ref else "")
                    if 'invoice-date' in self.economy_columns:
                        invoice_date = ""
                        if attendee_order.invoice_date:
                            invoice_date = attendee_order.invoice_date.strftime("%Y-%m-%d")
                        items.append(invoice_date)
                    if 'due-date' in self.economy_columns:
                        due_date = ""
                        if attendee_order.due_date:
                            due_date = attendee_order.due_date.strftime("%Y-%m-%d")
                        items.append(due_date)
                    if 'transaction-id' in self.economy_columns:
                        transaction_id = ""
                        if attendee_order.status == "paid":
                            payment_obj = Payments.objects.filter(order_number=attendee_order.order_number).values(
                                'transaction', 'created_at', 'method')
                            if payment_obj:
                                transaction_id = payment_obj[0]['transaction']
                                transaction_date = payment_obj[0]['created_at'].strftime("%Y-%m-%d")
                                payment_method = payment_obj[0]['method']
                        items.append(transaction_id)
                    if 'transaction-date' in self.economy_columns:
                        if not transaction_date:
                            payment_obj = Payments.objects.filter(order_number=attendee_order.order_number).values(
                                'created_at', 'method')
                            if payment_obj:
                                transaction_date = payment_obj[0]['created_at'].strftime("%Y-%m-%d")
                                payment_method = payment_obj[0]['method']
                        items.append(transaction_date)
                    if 'paid-by-card-invoice' in self.economy_columns:
                        if not payment_method:
                            payment_obj = Payments.objects.filter(order_number=attendee_order.order_number).values('method')
                            if payment_obj:
                                payment_method = payment_obj[0]['method']
                        items.append(payment_method)
                    if 'vat-xx-percent-sum' in self.economy_columns:
                        order_vats = OrderItems.objects.values('vat_rate').filter(order__order_number=attendee_order.order_number).exclude(
                            item_type__in=['rebate', 'adjustment']).annotate(value=Sum((F('cost') * F('vat_rate')) / 100)).order_by('vat_rate')
                        for vat in order_vats:
                            items.append(vat['value'])
                        for i in range(0, event_vat_count - order_vats.count()):
                            items.append("")
                    if 'vat-total-sum' in self.economy_columns:
                        vat_total_sum_obj = Orders.objects.filter(order_number=attendee_order.order_number, cost__gt=0).annotate(
                            total=Sum(F('cost') + F('vat_amount'))).aggregate(Sum('vat_amount'), Sum('cost'), Sum('total'))
                        cost_excl_vat = vat_total_sum_obj['cost__sum']
                        cost_incl_vat = vat_total_sum_obj['total__sum']
                        vat_total_sum = vat_total_sum_obj['vat_amount__sum'] if vat_total_sum_obj['vat_amount__sum'] else ""
                        items.append(vat_total_sum)

                    if 'rebate-sum' in self.economy_columns:
                        order_rebate = Orders.objects.filter(order_number=attendee_order.order_number, cost__gt=0).aggregate(Sum('rebate_amount'))
                        items.append(order_rebate["rebate_amount__sum"] if order_rebate["rebate_amount__sum"] else "")
                    if 'credit-usage' in self.economy_columns:
                        items.append(credit_usage_value if credit_usage_value else "")
                    if 'total-order-sum-excl-vat' in self.economy_columns:
                        if not cost_excl_vat:
                            cost_excl_vat_obj = Orders.objects.filter(order_number=attendee_order.order_number, cost__gt=0).annotate(
                                total=Sum(F('cost') + F('vat_amount'))).aggregate(Sum('cost'), Sum('total'))
                            cost_incl_vat = cost_excl_vat_obj['total__sum']
                            cost_excl_vat = cost_excl_vat_obj['cost__sum'] if cost_excl_vat_obj['cost__sum'] else ""
                        items.append(cost_excl_vat - credit_usage_value)
                    if 'total-order-sum-incl-vat' in self.economy_columns:
                        if not cost_incl_vat:
                            cost_incl_vat = Orders.objects.filter(order_number=attendee_order.order_number, cost__gt=0).annotate(
                                total=Sum(F('cost') + F('vat_amount'))).aggregate(Sum('total'))
                            cost_incl_vat = cost_incl_vat['total__sum'] if cost_incl_vat['total__sum'] else ""
                        items.append(cost_incl_vat - credit_usage_value)
                    if 'order-group-id' in self.economy_columns:
                        items.append(q.registration_group.name if q.registration_group else "")

                for i in range(self.max_attendee_orders - attendee_orders.count()):
                    if 'order-number' in self.economy_columns:
                        items.append('')
                    if 'order-status' in self.economy_columns:
                        items.append('')
                    if 'invoice-id' in self.economy_columns:
                        items.append('')
                    if 'invoice-date' in self.economy_columns:
                        items.append('')
                    if 'due-date' in self.economy_columns:
                        items.append('')
                    if 'transaction-id' in self.economy_columns:
                        items.append('')
                    if 'transaction-date' in self.economy_columns:
                        items.append('')
                    if 'paid-by-card-invoice' in self.economy_columns:
                        items.append('')
                    if 'vat-xx-percent-sum' in self.economy_columns:
                        for j in range(0, event_vat_count):
                            items.append('')
                    if 'vat-total-sum' in self.economy_columns:
                        items.append('')
                    if 'rebate-sum' in self.economy_columns:
                        items.append('')
                    if 'credit-usage' in self.economy_columns:
                        items.append('')
                    if 'total-order-sum-excl-vat' in self.economy_columns:
                        items.append('')
                    if 'total-order-sum-incl-vat' in self.economy_columns:
                        items.append('')
                    if 'order-group-id' in self.economy_columns:
                        items.append('')

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
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0
            sdir = '-' if sort_dir == 'desc' else ''
            if sort_col >= len(order_columns):
                return qs
            sortcol = order_columns[sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc))
            else:
                order.append('{0}{1}'.format(sdir, sortcol))
            if order:
                order_type = order[0].split('_')[1]
                question_id = int(order[0].split('_')[0])
                attendee_ids = []
                event_id = self.request.session['event_id']

                if order_type == 'gen':
                    if question_id == 111111:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('id')
                        return answers_ordered
                    elif question_id == -111111:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('-id')
                        return answers_ordered
                    if question_id == 222222:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('created')
                        return answers_ordered
                    elif question_id == -222222:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('-created')
                        return answers_ordered
                    elif question_id == 333333:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('updated')
                        return answers_ordered
                    elif question_id == -333333:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('-updated')
                        return answers_ordered
                    elif question_id == 444444:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('secret_key')
                        return answers_ordered
                    elif question_id == -444444:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('-secret_key')
                        return answers_ordered
                    elif question_id == 555555:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('bid')
                        return answers_ordered
                    elif question_id == -555555:
                        answers_ordered = Attendee.objects.filter(event_id=event_id, id__in=qs).order_by('-bid')
                        return answers_ordered
                    elif question_id == 666666:
                        event_groups_atts = AttendeeGroups.objects.filter(attendee_id__in=qs).order_by(
                            'group__name').values('attendee_id')
                        attendee_ids = [a['attendee_id'] for a in event_groups_atts]
                    elif question_id == -666666:
                        event_groups_atts = AttendeeGroups.objects.filter(attendee_id__in=qs).order_by(
                            '-group__name').values('attendee_id')
                        attendee_ids = [a['attendee_id'] for a in event_groups_atts]
                    elif question_id == 777777:
                        event_tags_atts = AttendeeTag.objects.filter(attendee_id__in=qs).order_by('tag__name').values(
                            'attendee_id')
                        attendee_ids = [a['attendee_id'] for a in event_tags_atts]
                    elif question_id == -777777:
                        event_tags_atts = AttendeeTag.objects.filter(attendee_id__in=qs).order_by('-tag__name').values(
                            'attendee_id')
                        attendee_ids = [a['attendee_id'] for a in event_tags_atts]

                elif order_type == 'session':
                    if question_id < 0:
                        question_id *= -1
                        session_atts = SeminarsUsers.objects.filter(attendee_id__in=qs, session_id=question_id).order_by('-status').values('attendee_id')
                        attendee_ids = [a['attendee_id'] for a in session_atts]
                    else:
                        session_atts = SeminarsUsers.objects.filter(attendee_id__in=qs, session_id=question_id).order_by('status').values('attendee_id')
                        attendee_ids = [a['attendee_id'] for a in session_atts]
                else:
                    if question_id < 0:
                        question_id *= -1
                        answers_ordered = Answers.objects.filter(question_id=question_id, user__in=qs).order_by('-value').values('user_id')
                    else:
                        answers_ordered = Answers.objects.filter(question_id=question_id, user__in=qs).order_by('value').values('user_id')
                    attendee_ids = [a['user_id'] for a in answers_ordered]
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(attendee_ids)])
                ordering = 'CASE %s END' % clauses
                attendees_ordered = Attendee.objects.filter(pk__in=attendee_ids).extra(select={'ordering': ordering},order_by=('ordering',))
                empty_attendee = list(set([aaa.id for aaa in qs]) - set(attendee_ids))
                attendees_without_question = Attendee.objects.filter(pk__in=empty_attendee).filter(event_id=event_id)
                result_list = list(chain(attendees_ordered, attendees_without_question))
                return result_list
        return qs

    def paging(self, qs):
        if self.pre_camel_case_notation:
            limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            start = int(self._querydict.get('start', 0))
        if limit == -1:
            return qs
        offset = start + limit

        self.start = start
        self.limit = limit

        return qs[start:offset]

    def get_hotel_booking_data(self, q, att_booking):
        hotel_data = []
        if 'booking-id-col' in self.hotel_columns:
            hotel_data.append(att_booking.id if att_booking else "")
        if 'match-id-col' in self.hotel_columns:
            match_id_str = ''
            if att_booking:
                match_lines = MatchLine.objects.filter(booking_id=att_booking.id)
                for match_line in match_lines:
                    match_id_str += str(match_line.match_id) + ', '
                if len(match_id_str) > 0:
                    match_id_str = match_id_str[:-2]
            hotel_data.append(match_id_str)
        if 'hotel-name-col' in self.hotel_columns:
            hotel_data.append(att_booking.room.hotel.name if att_booking else '')
        if 'description-col' in self.hotel_columns:
            hotel_data.append(att_booking.room.description if att_booking else '')
        if 'room-id-col' in self.hotel_columns:
            hotel_data.append(att_booking.room_id if att_booking else '')
        if 'check-in-col' in self.hotel_columns:
            check_in = ''
            if att_booking:
                check_in = HelperData.utc_to_local(self.request,
                                                   str(datetime.strftime(att_booking.check_in, "%Y-%m-%d %H:%M:%S")))
                check_in = HelperData.get_formated_date_string(check_in, self.request.session['language_id'])
                hotel_data.append(check_in)
            else:
                hotel_data.append('')
        if 'check-out-col' in self.hotel_columns:
            check_out = ''
            if att_booking:
                check_out = HelperData.utc_to_local(self.request,
                                                    str(datetime.strftime(att_booking.check_out, "%Y-%m-%d %H:%M:%S")))
                check_out = HelperData.get_formated_date_string(check_out, self.request.session['language_id'])
                hotel_data.append(check_out)
            else:
                hotel_data.append('')
        if 'beds-col' in self.hotel_columns:
            hotel_data.append(att_booking.room.beds if att_booking else '')
        if 'location-col' in self.hotel_columns:
            hotel_data.append(att_booking.room.hotel.location.name if att_booking else '')
        if 'rbr-col' in self.hotel_columns:
            rbr_text = ''
            if att_booking:
                rbr_objs = RequestedBuddy.objects.filter(booking_id=att_booking.id)
                for rbr_obj in rbr_objs:
                    rbr_text += rbr_obj.email if rbr_obj.email else rbr_obj.buddy.get_full_name() + ', '
                if len(rbr_text) > 0:
                    rbr_text = rbr_text[:-2]
            hotel_data.append(rbr_text)

        if att_booking:
            max_actual_room_buddy = self.max_actual_room_buddy
            if 'rba-col' in self.hotel_columns or 'rba-checkin-col' in self.hotel_columns or 'rba-checkout-col' in self.hotel_columns:
                match_ids = MatchLine.objects.filter(booking_id=att_booking.id).values('match_id')
                other_bookings = MatchLine.objects.filter(match_id__in=match_ids).exclude(booking_id=att_booking.id)
                actual_bud_counter = 0
                for other_booking in other_bookings:
                    actual_bud_counter += 1
                    if 'rba-col' in self.hotel_columns:
                        hotel_data.append(other_booking.booking.attendee.get_full_name())
                    if 'rba-checkin-col' in self.hotel_columns:
                        check_in = utc_to_local(self.request, str(
                            datetime.strftime(other_booking.booking.check_in, "%Y-%m-%d %H:%M:%S")))
                        check_in = get_formated_date_string(check_in, self.request.session['language_id'])
                        hotel_data.append(check_in)
                    if 'rba-checkout-col' in self.hotel_columns:
                        check_out = utc_to_local(self.request, str(
                            datetime.strftime(other_booking.booking.check_out, "%Y-%m-%d %H:%M:%S")))
                        check_out = get_formated_date_string(check_out, self.request.session['language_id'])
                        hotel_data.append(check_out)
                if self.max_actual_room_buddy > actual_bud_counter:
                    max_actual_room_buddy -= actual_bud_counter
                    for i in range(0, max_actual_room_buddy):
                        if 'rba-col' in self.hotel_columns:
                            hotel_data.append('')
                        if 'rba-checkin-col' in self.hotel_columns:
                            hotel_data.append('')
                        if 'rba-checkout-col' in self.hotel_columns:
                            hotel_data.append('')
        else:
            for i in range(0, self.max_actual_room_buddy):
                if 'rba-col' in self.hotel_columns:
                    hotel_data.append('')
                if 'rba-checkin-col' in self.hotel_columns:
                    hotel_data.append('')
                if 'rba-checkout-col' in self.hotel_columns:
                    hotel_data.append('')
        return hotel_data
