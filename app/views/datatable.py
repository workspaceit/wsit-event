from app.models import Attendee, Group, Questions, Answers, CurrentFilter,AttendeeTag,Tag, AttendeeGroups, \
    Orders, Payments, RegistrationGroupOwner
from app.views.gbhelper.economy_library import EconomyLibrary
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from itertools import chain
import time
from app.views.common_views import TimeDetailView
from app.views.gbhelper.common_helper import CommonHelper
from .filter import FilterView
import json
from django.db.models.functions import Concat
from django.db.models import Value


class AttendeeListView(BaseDatatableView):
    order_columns = ['0', '111111', '222222', '333333', '444444', '555555', '666666', '777777', '888888', '999999', '100001']
    questions = []
    manualColumns = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    manualVisibleCols = []

    def get_event_id(self):
        return self.request.session['event_auth_user']['event_id']

    def get_admin_id(self):
        return self.request.session['event_auth_user']['id']

    def get_initial_queryset(self):
        self.questions = []
        self.order_columns = ['0', '111111', '222222', '333333', '444444', '555555', '666666', '777777', '888888', '999999', '100001']
        question_groups = Group.objects.filter(type="question", is_show=1, event_id=self.get_event_id()).order_by('group_order')
        for group in question_groups:
            questions_g = Questions.objects.all().filter(group_id=group.id)
            for q_g in questions_g:
                self.questions.append(q_g)
        for question in self.questions:
            self.order_columns.append(question.id)
        attendees = Attendee.objects.filter(event_id=self.get_event_id(),status="registered").order_by('id')
        return attendees

    def filter_queryset(self, qs):
        start_time = time.time()
        if not self.pre_camel_case_notation:
            search = self.request.POST.get('search[value]', None).strip()
            try:
                search.index(' ')
                has_space = True
            except:
                has_space = False
                pass
            visible_columns = list(map(int, self.request.POST.get('visible', None).split(',')))
            self.manualVisibleCols = list(set(visible_columns).intersection(self.manualColumns))
            combined_visible_columns = visible_columns
            visible_columns = list(set(visible_columns) ^ set(self.manualVisibleCols))
            activate_rule = self.request.POST.get('activate_rule', None)
            first_name_visible = last_name_visible = False

            filtered_attendees = Attendee.objects.filter(event_id=self.get_event_id(),status="registered")
            rule_id = self.request.POST.get('rule_id', None)
            if len(visible_columns) != 0:
                currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee')
                if currentFilter.count()>0:
                        CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee').update(visible_columns=json.dumps(combined_visible_columns))
                else:
                        current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),visible_columns=json.dumps(combined_visible_columns))
                        current.save()

                visible_questions = [self.order_columns[x] for x in visible_columns]

                if activate_rule == 'true' and rule_id is not None and rule_id != '':

                    filtered_attendees = FilterView.get_filtered_attendees(self.request, rule_id)
                    # add to database
                    currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee')
                    if currentFilter.count()>0:
                        CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee').update(filter_id=rule_id)
                    else:
                        current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),filter_id=rule_id)
                        current.save()
                    extra_answers_filtered = Answers.objects.filter(user__in=filtered_attendees).values_list('user_id',flat=True).order_by('user_id')
                    answers_filtered = Answers.objects.filter(user__in=filtered_attendees, value__icontains=search,
                                                              question_id__in=visible_questions).values_list('user_id',flat=True).order_by('user_id')
                else:
                    currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee')

                    if currentFilter.count() > 0:
                        CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee').update(filter_id=None)
                    else:
                        current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),filter_id=None)
                        current.save()
                    extra_answers_filtered = Answers.objects.filter(user__in=filtered_attendees).select_related('user').values_list('user_id',flat=True).order_by('user_id')
                    answers_filtered = Answers.objects.filter(user__in=filtered_attendees,value__icontains=search,
                                                              question_id__in=visible_questions).select_related('user').values_list('user_id',flat=True).order_by('user_id')
            else:
                answers_filtered = Answers.objects.filter(user__in=filtered_attendees,value__icontains=search).values_list('user_id',flat=True).order_by('user_id')
            attendee_ids = set(answers_filtered)
            extra_attendee_ids = set(extra_answers_filtered)
            matched_attendees_combined = []
            if has_space:
                all_questions = Questions.objects.filter(id__in=visible_questions)
                for question in all_questions:
                    if question.actual_definition == 'firstname':
                        first_name_visible = True
                    elif question.actual_definition == 'lastname':
                        last_name_visible = True
                if first_name_visible and last_name_visible:
                    full_name_matches_attendee = filtered_attendees.annotate(
                        full_name=Concat('firstname', Value(' '), 'lastname')).filter(full_name__istartswith=search)
                    for a in full_name_matches_attendee:
                        matched_attendees_combined.append(a.id)

            attendee_ids = list(chain(attendee_ids, matched_attendees_combined))

            # section to add ( manual Columns search results )
            newResultsId = []

            if 2 in self.manualVisibleCols:
                newResults = Attendee.objects.filter(created__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)
            if 3 in self.manualVisibleCols:
                newResults = Attendee.objects.filter(updated__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)

            if 4 in self.manualVisibleCols:
                newResults = Attendee.objects.filter(secret_key__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)

            if 5 in self.manualVisibleCols:
                newResults = Attendee.objects.filter(bid__startswith=search, id__in=extra_attendee_ids)
                for newResult in newResults:
                    newResultsId.append(newResult.id)

            if 6 in self.manualVisibleCols:
                tempGroupresult = AttendeeGroups.objects.filter(group__name__icontains=search, attendee_id__in=extra_attendee_ids)
                for newResult in tempGroupresult:
                    newResultsId.append(newResult.attendee.id)

            if 7 in self.manualVisibleCols:
                tempTagresults = Tag.objects.filter(name__startswith=search,event_id=self.get_event_id())

                for tempTagresult in tempTagresults:
                    tempAttendeeTags = AttendeeTag.objects.filter(tag_id=tempTagresult.id, attendee_id__in=extra_attendee_ids)
                    for tempAttendeeTag in tempAttendeeTags:
                        newResultsId.append(tempAttendeeTag.attendee_id)

            if 8 in self.manualVisibleCols:
                tempOrderAttendee = Orders.objects.filter(order_number__startswith=search, attendee_id__in=extra_attendee_ids, cost__gt=0).values('attendee_id')
                newResultsId.extend(tem_att['attendee_id'] for tem_att in tempOrderAttendee)

            if 9 in self.manualVisibleCols:
                tempOrderAttendee = Orders.objects.filter(invoice_ref__icontains=search, attendee_id__in=extra_attendee_ids, cost__gt=0).values('attendee_id')
                newResultsId.extend(tem_att['attendee_id'] for tem_att in tempOrderAttendee)

            if 10 in self.manualVisibleCols:
                att_orders = Orders.objects.filter(attendee_id__in=extra_attendee_ids, cost__gt=0).values('order_number')
                att_payment_order_numbers = Payments.objects.filter(transaction__icontains=search, order_number__in=att_orders).values('order_number')
                tempOrderAttendee = Orders.objects.filter(order_number__in=att_payment_order_numbers).values('attendee_id')
                newResultsId.extend(tem_att['attendee_id'] for tem_att in tempOrderAttendee)

            newResultsId = list(set(newResultsId) ^ set(list(set(attendee_ids).intersection(newResultsId))))
            attendee_ids = list(chain(attendee_ids, newResultsId))

            q1 = Q()
            q1 |= Q(id__in=attendee_ids)
            qs = qs.filter(q1).order_by('id')
        return qs

    def prepare_results(self, qs):
        json_data = []
        country_list = CommonHelper.get_country_list(self)
        for q in qs:
            items = [q.id, q.id]
            #local time
            created_date=TimeDetailView.utc_to_local(self.request,str(q.created.strftime("%Y-%m-%d %H:%M:%S")))
            updated_date=TimeDetailView.utc_to_local(self.request,str(q.updated.strftime("%Y-%m-%d %H:%M:%S")))

            items.append(CommonHelper.get_formated_date(self.request,created_date))
            items.append(CommonHelper.get_formated_date(self.request,updated_date))
            items.append(q.secret_key)
            items.append(q.bid)

            groups = AttendeeGroups.objects.filter(attendee_id=q.id)
            groupList = ','.join(g.group.name for g in groups)
            items.append(groupList)

            tags = AttendeeTag.objects.filter(attendee_id=q.id)
            taglist = ','.join(t.tag.name for t in tags)
            items.append(taglist)

            if RegistrationGroupOwner.objects.filter(owner_id=q.id).exists():
                group_info = EconomyLibrary.get_group_registration_info(q.id)
                att_orders_temp = Orders.objects.filter(attendee_id__in=group_info['grp-atts'], cost__gt=0).values('order_number', 'invoice_ref')
                att_order_numbers = []
                att_orders = []
                for att_o_items in att_orders_temp:
                    if att_o_items['order_number'] not in att_order_numbers:
                        att_order_numbers.append(att_o_items['order_number'])
                        att_orders.append(att_o_items)

                temp_order_data = ', '.join(str(att_order['order_number']) + ' (order owner)' for att_order in att_orders)
                items.append(temp_order_data)
            else:
                att_orders = Orders.objects.filter(attendee_id=q.id, cost__gt=0).values('order_number', 'invoice_ref')
                if q.registration_group:
                    temp_order_data = ', '.join(str(att_order['order_number']) for att_order in att_orders)
                else:
                    temp_order_data = ', '.join(str(att_order['order_number']) + ' (order owner)' for att_order in att_orders)
                items.append(temp_order_data)

            temp_order_data = ', '.join(att_or['invoice_ref'] for att_or in list(filter(lambda a_o: a_o['invoice_ref'], att_orders)))
            items.append(temp_order_data)
            att_payments = Payments.objects.filter(order_number__in=[a_o['order_number'] for a_o in att_orders]).values('transaction')
            temp_order_data = ', '.join(att_pymnt['transaction'] for att_pymnt in list(filter(lambda a_p: a_p['transaction'], att_payments)))
            items.append(temp_order_data)

            answers_for_attendee = Answers.objects.filter(user_id=q.id).order_by('user_id')
            for question in self.questions:
                ans = 'N/A'
                for answer in answers_for_attendee:
                    if answer.question_id == question.id:
                        if answer.question.type == 'checkbox':
                            ans = answer.value.replace('<br>',', ')
                        elif answer.question.type == 'date_range':
                            values = json.loads(answer.value)
                            if len(values[0]) > 0 and len(values[1]) > 0:
                                ans = values[0]+' to '+values[1]
                        elif answer.question.type == 'time_range':
                            values = json.loads(answer.value)
                            if len(values[0]) > 0 and len(values[1]) > 0:
                                ans = values[0]+' to '+values[1]
                        elif answer.question.type == 'country':
                            if answer.value in country_list:
                                ans = country_list[answer.value]
                        else:
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
            attendee_ids = []
            event_id = self.get_event_id()
            if question_id == 111111:
                # sort by attendee id
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
                event_groups_atts = AttendeeGroups.objects.filter(attendee_id__in=qs).order_by('group__name').values('attendee_id')
                attendee_ids = [a['attendee_id'] for a in event_groups_atts]
            elif question_id == -666666:
                event_groups_atts = AttendeeGroups.objects.filter(attendee_id__in=qs).order_by('-group__name').values('attendee_id')
                attendee_ids = [a['attendee_id'] for a in event_groups_atts]
            elif question_id == 777777:
                event_tags_atts = AttendeeTag.objects.filter(attendee_id__in=qs).order_by('tag__name').values('attendee_id')
                attendee_ids = [a['attendee_id'] for a in event_tags_atts]
            elif question_id == -777777:
                event_tags_atts = AttendeeTag.objects.filter(attendee_id__in=qs).order_by('-tag__name').values('attendee_id')
                attendee_ids = [a['attendee_id'] for a in event_tags_atts]
            elif question_id == 888888:
                aaa = Orders.objects.filter(attendee__event_id=event_id, attendee_id__in=qs, cost__gt=0).order_by('order_number')
                attendee_ids = [a.attendee_id for a in aaa]
            elif question_id == -888888:
                aaa = Orders.objects.filter(attendee__event_id=event_id, attendee_id__in=qs, cost__gt=0).order_by('-order_number')
                attendee_ids = [a.attendee_id for a in aaa]
            elif question_id == 999999:
                aaa = Orders.objects.filter(attendee__event_id=event_id, attendee_id__in=qs, cost__gt=0).order_by('invoice_ref')
                attendee_ids = [a.attendee_id for a in aaa]
            elif question_id == -999999:
                aaa = Orders.objects.filter(attendee__event_id=event_id, attendee_id__in=qs, cost__gt=0).order_by('-invoice_ref')
                attendee_ids = [a.attendee_id for a in aaa]
            elif question_id == 100001:
                att_orders = Orders.objects.filter(attendee_id__in=qs, cost__gt=0).values('order_number')
                att_payment_order_numbers = Payments.objects.filter(order_number__in=att_orders).order_by('transaction').values('order_number')
                if att_payment_order_numbers.exists():
                    clauses = ' '.join(['WHEN order_number=%s THEN %s' % (o_n['order_number'], i) for i, o_n in enumerate(att_payment_order_numbers)])
                    ordering = 'CASE %s END' % clauses
                    aaa = Orders.objects.filter(order_number__in=att_payment_order_numbers).extra(select={'ordering': ordering}, order_by=('ordering',))
                    attendee_ids = [a.attendee_id for a in aaa]
            elif question_id == -100001:
                att_orders = Orders.objects.filter(attendee_id__in=qs, cost__gt=0).values('order_number')
                att_payment_order_numbers = Payments.objects.filter(order_number__in=att_orders).order_by('-transaction').values('order_number')
                if att_payment_order_numbers.exists():
                    clauses = ' '.join(['WHEN order_number=%s THEN %s' % (o_n['order_number'], i) for i, o_n in enumerate(att_payment_order_numbers)])
                    ordering = 'CASE %s END' % clauses
                    aaa = Orders.objects.filter(order_number__in=att_payment_order_numbers).extra(select={'ordering': ordering}, order_by=('ordering',))
                    attendee_ids = [a.attendee_id for a in aaa]

            else:
                # sort by question answers
                if question_id < 0:
                    question_id *= -1
                    answers_ordered = Answers.objects.filter(question_id=question_id, user__in=qs).order_by('-value')
                else:
                    answers_ordered = Answers.objects.filter(question_id=question_id, user__in=qs).order_by('value')
                for answer in answers_ordered:
                    attendee_ids.append(answer.user_id)
            clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(attendee_ids)])
            ordering = 'CASE %s END' % clauses
            attendees_ordered = Attendee.objects.filter(pk__in=attendee_ids).extra(select={'ordering': ordering}, order_by=('ordering',))
            empty_attendee = list(set([aaa.id for aaa in qs]) - set(attendee_ids))
            attendees_without_question = Attendee.objects.filter(pk__in=empty_attendee).filter(
                event_id=self.get_event_id())
            result_list = list(chain(attendees_ordered, attendees_without_question))
            return result_list
        return qs

    def paging(self, qs):
        """ Paging
        """
        if self.pre_camel_case_notation:
            limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        if limit == -1:
            return qs

        sort_column = self.request.POST.get('order[0][column]')
        sort_asc_desc = self.request.POST.get('order[0][dir]')
        if sort_column:
            sort_column = int(sort_column)
        if not sort_asc_desc:
            sort_asc_desc = 'asc'

        currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='attendee')
        if currentFilter:
            currentFilter[0].show_rows = int(limit)
            currentFilter[0].sorted_column = sort_column
            currentFilter[0].sorting_order = sort_asc_desc
            currentFilter[0].save()
        else:
            current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),show_rows=int(limit))
            current.save()
        offset = start + limit
        return qs[start:offset]
