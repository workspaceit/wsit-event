from django.db.models.functions import Concat

from app.models import Attendee, Group, Questions, Answers, CurrentFilter, AttendeeTag, Checkpoint, Scan, \
    SeminarsUsers, AttendeeGroups
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q, Value
from .filter import FilterView
from app.views.gbhelper.error_report_helper import ErrorR, DateTimeHelper
from app.views.common_views import TimeDetailView
from itertools import chain
import json
class AttendeeListView(BaseDatatableView):
    order_columns = []
    questions = []
    manualColumns = [2, 3, 4, 5, 6, 7]
    manualVisibleCols = []

    def get_event_id(self):
        return self.request.session['event_auth_user']['event_id']

    def get_admin_id(self):
        return self.request.session['event_auth_user']['id']

    def get_initial_queryset(self):
        self.questions = []
        self.order_columns = ['0', '111111']
        question_groups = Group.objects.filter(type="question", is_show=1, event_id=self.get_event_id()).order_by(
            'group_order')
        for group in question_groups:
            questions_g = Questions.objects.all().filter(group_id=group.id)
            for q_g in questions_g:
                self.questions.append(q_g)

        checkpoint = Checkpoint.objects.filter(id=self.request.POST.get('checkpoint_id')).first()

        if checkpoint.questions:
            ch_questions = checkpoint.questions.split(',')
        else:
            ch_questions = []

        if checkpoint.defaults:
            gen_questions = checkpoint.defaults.split(',')
        else:
            gen_questions = []

        for g_qus in gen_questions:
            if g_qus == 'uid':
                self.order_columns.append(444444)
            if g_qus == 'bid':
                self.order_columns.append(777777)
            elif g_qus == 'created':
                self.order_columns.append(222222)
            elif g_qus == 'update':
                self.order_columns.append(333333)
            elif g_qus == 'group':
                self.order_columns.append(555555)
            elif g_qus == 'tag':
                self.order_columns.append(666666)

        for question in ch_questions:
            self.order_columns.append(question)

        attendees = Attendee.objects.filter(event_id=self.get_event_id(), status="registered").order_by('id')
        return attendees

    def filter_queryset(self, qs):
        checkpoint = Checkpoint.objects.filter(id=self.request.POST.get('checkpoint_id')).first()
        attendee_ids = []

        if checkpoint.session:
            seminar_users = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending')
            for seminar_user in seminar_users:
                attendee_ids.append(seminar_user.attendee_id)
        else:
            attendees = FilterView.get_filtered_attendees(self.request, checkpoint.filter_id)
            for att in attendees:
                attendee_ids.append(att.id)

        q1 = Q()
        q1 |= Q(id__in=attendee_ids)
        qs = qs.filter(q1).order_by('id')

        search = self.request.POST.get('search[value]', '').strip()
        if len(search) > 0:
            total_attendees = qs.filter(id__icontains=search).values('id')
            general_questions = checkpoint.defaults.split(',') if checkpoint.defaults and checkpoint.defaults.strip() != '' else []
            if 'uid' in general_questions:
                searched_ids = qs.filter(secret_key__icontains=search).values('id')
                total_attendees |= searched_ids
            # if 'bid' in general_questions:
            searched_ids = qs.filter(bid__icontains=search).values('id')
            total_attendees |= searched_ids
            if 'created' in general_questions:
                searched_ids = qs.filter(created__icontains=search).values('id')
                total_attendees |= searched_ids
            if 'update' in general_questions:
                searched_ids = qs.filter(updated__icontains=search).values('id')
                total_attendees |= searched_ids
            if 'group' in general_questions:
                group_attendees = AttendeeGroups.objects.filter(attendee_id__in=qs, group__name__icontains=search).values('attendee_id')
                searched_ids = qs.filter(id__in=group_attendees).values('id')
                total_attendees |= searched_ids
            if 'group' in general_questions:
                tag_attendees = AttendeeTag.objects.filter(attendee_id__in=qs, tag__name__icontains=search).values('attendee_id')
                searched_ids = qs.filter(id__in=tag_attendees).values('id')
                total_attendees |= searched_ids

            questions = checkpoint.questions.split(',') if checkpoint.questions and checkpoint.questions.strip() != '' else []
            if questions:
                try:
                    search.index(' ')
                    has_space = True
                except:
                    has_space = False
                    pass
                if has_space:
                    first_name_visible = False
                    last_name_visible = False
                    attendees = []
                    all_questions = Questions.objects.filter(id__in=questions)
                    for question in all_questions:
                        if question.actual_definition == 'firstname':
                            first_name_visible = True
                        elif question.actual_definition == 'lastname':
                            last_name_visible = True
                    if first_name_visible and last_name_visible:
                        full_name_matches_attendee = qs.annotate(
                            full_name=Concat('firstname', Value(' '), 'lastname')).filter(full_name__istartswith=search)
                        for a in full_name_matches_attendee:
                            attendees.append(a.id)
                        total_attendees |= qs.filter(id__in=attendees).values('id')

                matched_answer_attendees = Answers.objects.filter(user__in=qs, question_id__in=questions, value__icontains=search).values_list('user_id')
                searched_ids = qs.filter(id__in=matched_answer_attendees).values('id')
                total_attendees |= searched_ids

            q1 = Q()
            q1 |= Q(id__in=total_attendees)
            qs = qs.filter(q1).order_by('id')
        return qs

    def prepare_results(self, qs):
        search = self.request.POST.get('search[value]', None).strip()
        checkpoint_id = self.request.POST.get('checkpoint_id')
        json_data = []

        for q in qs:
            # here flag is used for searching when searching keyword is available then checked and flag=True that will allow item to append to json_data
            checkpoint = Checkpoint.objects.filter(id=checkpoint_id).first()
            if checkpoint.questions:
                questions = checkpoint.questions.split(',') if len(checkpoint.questions.strip())>1 else []
            else:
                questions = []
            scan = Scan.objects.filter(attendee_id=q.id, checkpoint_id=checkpoint_id).first()
            scandetails= {}
            if scan:
                temp_datetime = TimeDetailView.utc_to_local(self.request, str(scan.scan_time))
                scandetails['scan_time'] = DateTimeHelper.get_formated_date_string(temp_datetime, scan.attendee.language_id)
                scandetails['scan_status'] = scan.status
            else:
                scandetails['scan_status'] = 0
            items = [scandetails, q.id]

            if checkpoint.defaults:
                general_questions = checkpoint.defaults.split(',')
            else:
                general_questions = []

            for g_qus in general_questions:
                g_qus_att = Attendee.objects.filter(id=q.id).first()
                if g_qus == 'uid':
                    items.append(g_qus_att.secret_key)
                elif g_qus == 'bid':
                    items.append(g_qus_att.bid)
                elif g_qus == 'created':
                    temp_datetime = TimeDetailView.utc_to_local(self.request, str(g_qus_att.created))
                    items.append(DateTimeHelper.get_formated_date_string(temp_datetime, g_qus_att.language_id))
                elif g_qus == 'update':
                    items.append(g_qus_att.updated)
                elif g_qus == 'group':
                    groupResults = AttendeeGroups.objects.filter(attendee__id=g_qus_att.id)
                    groupList = ""
                    for group in groupResults:
                        groupList += group.group.name + ", "
                    if len(groupList)>0:
                        groupList = groupList[:-2]
                    items.append(groupList)
                elif g_qus == 'tag':
                    tags = AttendeeTag.objects.filter(attendee_id=q.id)
                    taglist = ""
                    for tag in tags:
                        taglist += tag.tag.name + ", "
                    if len(taglist) > 0:
                        taglist = taglist[:-2]
                    items.append(taglist)

            for qus in questions:
                ans = Answers.objects.filter(question__id=qus, user__id=q.id).first()
                if ans:
                    if ans.question.type == 'date_range':
                        values = json.loads(ans.value)
                        val = values[0] + ' to ' + values[1]
                        items.append(val)
                    elif ans.question.type == 'time_range':
                        values = json.loads(ans.value)
                        val = values[0] + ' to ' + values[1]
                        items.append(val)
                    else:
                        items.append(ans.value)
                else:
                    items.append("N/A")
            items.append(q.id)
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
        # order_columns = self.get_order_columns()
        order_columns = self.order_columns
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
            if order[0] == '-0':
                # -0 turn into 0 when convert to int
                question_id = order[0]
            else:
                question_id = int(order[0])

            if question_id in [0, '-0']:
                checkpoint_id = self.request.POST.get('checkpoint_id')
                answers_ordered = []
                if checkpoint_id:
                    checked_atts = Scan.objects.filter(checkpoint_id=checkpoint_id, status=1).values('attendee_id')
                    unchecked_atts = qs.exclude(id__in=checked_atts)
                    checked_atts = qs.exclude(id__in=unchecked_atts)
                    answers_ordered = list(chain(checked_atts, unchecked_atts)) if question_id == 0 else list(chain(unchecked_atts, checked_atts))
                return answers_ordered
            elif question_id == 111111:
                # sort by attendee id
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by('id')
                return answers_ordered
            elif question_id == -111111:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-id')
                return answers_ordered
            elif question_id == 222222:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by('created')
                return answers_ordered
            elif question_id == -222222:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-created')
                return answers_ordered
            elif question_id == 333333:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    'updated')
                return answers_ordered
            elif question_id == -333333:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-updated')
                return answers_ordered
            elif question_id == 444444:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    'secret_key')
                return answers_ordered
            elif question_id == -444444:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-secret_key')
                return answers_ordered
            elif question_id == 555555:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    'id')
                return answers_ordered
            elif question_id == -555555:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-id')
                return answers_ordered
            elif question_id == 666666:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    'id')
                return answers_ordered
            elif question_id == -666666:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-id')
                return answers_ordered
            elif question_id == 777777:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by('bid')
                return answers_ordered
            elif question_id == -777777:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by('-bid')
                return answers_ordered

            else:
                # sort by question answers
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
            attendees_ordered = Attendee.objects.filter(pk__in=attendee_ids).extra(select={'ordering': ordering},
                                                                                   order_by=('ordering',))
            attendees_without_question = Attendee.objects.exclude(pk__in=attendee_ids).filter(
                event_id=self.get_event_id())
            f = attendees_ordered | attendees_without_question
            result_list = list(chain(attendees_ordered, attendees_without_question))
            # return result_list
            return attendees_ordered
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

        currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id(), table_type='checkpoint')
        if currentFilter:
            currentFilter[0].show_rows = int(limit)
            currentFilter[0].sorted_column = sort_column
            currentFilter[0].sorting_order = sort_asc_desc
            currentFilter[0].save()

        offset = start + limit
        return qs[start:offset]
