from app.models import Attendee, Group, Questions, Answers, CurrentFilter
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from itertools import chain
from .filter import FilterView
import json
from django.db.models.functions import Concat
from django.db.models import Value


class AttendeeListView(BaseDatatableView):
    order_columns = ['0', '111111']
    questions = []

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
        for question in self.questions:
            self.order_columns.append(question.id)

        attendees = Attendee.objects.filter(event_id=self.get_event_id(),status="registered").order_by('id')
        return attendees

    def get_filtered_attendees(self, rule_id):
        attendees = FilterView.get_filtered_attendees(self.request,rule_id)
        return attendees

    def filter_queryset(self, qs):
        if not self.pre_camel_case_notation:
            search = self.request.POST.get('search[value]', None)
            try:
                search.index(' ')
                has_space = True
            except:
                has_space = False
                pass

            visible_columns = list(map(int, self.request.POST.get('visible', None).split(',')))
            activate_rule = self.request.POST.get('activate_rule', None)
            first_name_visible = last_name_visible = False
            filtered_attendees = Attendee.objects.filter(event_id=self.get_event_id(),status="registered")
            rule_id = self.request.POST.get('rule_id', None)
            if len(visible_columns) != 0:
                currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id())
                if currentFilter.count()>0:
                        CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id()).update(visible_columns=json.dumps(visible_columns))
                else:
                        current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),visible_columns=json.dumps(visible_columns))
                        current.save()
                visible_questions = [self.order_columns[x] for x in visible_columns]
                if activate_rule == 'true' and rule_id is not None and rule_id != '':

                    filtered_attendees = self.get_filtered_attendees(rule_id)
                    # add to database
                    currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id())
                    if currentFilter.count()>0:
                        CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id()).update(filter_id=rule_id)
                    else:
                        current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),filter_id=rule_id)
                        current.save()


                    answers_filtered = Answers.objects.filter(user__in=filtered_attendees, value__istartswith=search,
                                                              question_id__in=visible_questions).order_by('user_id')
                else:
                    currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id())

                    if currentFilter.count() > 0:
                        CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id()).update(filter_id=None)
                    else:
                        current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),filter_id=None)
                        current.save()


                    search_attendees = Attendee.objects.filter(secret_key__istartswith=search,status="registered")
                    answers_filtered = Answers.objects.filter(Q(value__istartswith=search,
                                                              question_id__in=visible_questions) | Q (user_id__in=search_attendees)).order_by('user_id')
            else:
                answers_filtered = Answers.objects.filter(value__istartswith=search).order_by('user_id')
            attendee_ids = []
            for answer in answers_filtered:
                attendee_ids.append(answer.user_id)

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
            q1 = Q()
            q1 |= Q(id__in=attendee_ids)
            qs = qs.filter(q1).order_by('id')
        return qs

    def prepare_results(self, qs):
        json_data = []
        for q in qs:
            items = [q.id,q.secret_key]
            answers_for_attendee = Answers.objects.filter(user_id=q.id).order_by('user_id')
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
            if question_id == 111111:
                # sort by attendee id
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by('id')
                return answers_ordered
            elif question_id == -111111:
                answers_ordered = Attendee.objects.filter(event_id=self.get_event_id(), id__in=qs).order_by(
                    '-id')
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
        currentFilter = CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id())
        if currentFilter.count()>0:
            CurrentFilter.objects.filter(admin_id=self.get_admin_id(),event_id=self.get_event_id()).update(show_rows=int(limit))
        else:
            current = CurrentFilter(admin_id=self.get_admin_id(),event_id=self.get_event_id(),show_rows=int(limit))
            current.save()
        offset = start + limit
        return qs[start:offset]
