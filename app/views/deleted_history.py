
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from app.models import DeletedAttendee, DeletedHistory
from django_datatables_view.base_datatable_view import BaseDatatableView
import json
from app.views.gbhelper.common_helper import CommonHelper

from app.views.common_views import TimeDetailView, EventView


class DeletedAttendees(BaseDatatableView):

    def get_event_id(self):
        return self.request.session['event_auth_user']['event_id']

    def get_admin_id(self):
        return self.request.session['event_auth_user']['id']

    def get_initial_queryset(self):
        attendees = DeletedAttendee.objects.filter(event_id=DeletedAttendees.get_event_id(self))
        search = self.request.POST.get('search[value]', None).strip()
        filtered_qs = attendees.annotate(fullname=Concat('firstname', Value(' '), 'lastname')).filter(
            Q(firstname__icontains=search) | Q(lastname__icontains=search) | Q(email__icontains=search) |
            Q(phonenumber__icontains=search)|Q(fullname__istartswith=search))
        return filtered_qs

    # def filter_queryset(self, qs):
    #      no need to override this method
    #     return qs

    def prepare_results(self, qs):
        json_data = []
        for att in qs:
            row = [att.id, att.firstname, att.lastname, att.email, att.phonenumber]
            json_data.append(row)
        return json_data

    def ordering(self, qs):
        order_column = int(self.request.POST.get('order[0][column]'))
        order_key = self.request.POST.get('order[0][dir]')
        if order_column == 0:
            qs = qs.filter().order_by('id') if order_key=='asc' else qs.filter().order_by('-id')
        elif order_column == 1:
            qs = qs.filter().order_by('firstname') if order_key == 'asc' else qs.filter().order_by('-firstname')
        elif order_column == 2:
            qs = qs.filter().order_by('lastname') if order_key == 'asc' else qs.filter().order_by('-lastname')
        elif order_column == 3:
            qs = qs.filter().order_by('email') if order_key == 'asc' else qs.filter().order_by('-email')
        elif order_column == 4:
            qs = qs.filter().order_by('phonenumber') if order_key == 'asc' else qs.filter().order_by('-phonenumber')
        return qs

    def paging(self, qs):
        if self.pre_camel_case_notation:
            limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        if limit == -1:
            return qs
        offset = start + limit
        return qs[start:offset]


class DeletedView(TemplateView):

    def get(self, request):
        if EventView.check_read_permissions(request, 'deleted_attendee_permission'):
            return render(request, 'deleted-history/deleted_attendees.html')

    def attendee_history(request):
        response_data = {"success":True}

        user_id = request.POST.get('attendee_id')
        deletedhistory = DeletedHistory.objects.filter(attendee_id=user_id).order_by('-created')

        for history in deletedhistory:
            history.created = TimeDetailView.utc_to_local(request, str(history.created.strftime("%Y-%m-%d %H:%M:%S")))
        context = {
            'activity_history': deletedhistory,
            'current_admin': request.session['event_auth_user'],
            'date_format': CommonHelper.get_python_date_format(request) + ' H:i'
        }
        history_list = render_to_string('attendee/history.html', context)
        del_att = DeletedAttendee.objects.get(id=user_id)
        response_data['name'] = del_att.firstname + " " + del_att.lastname
        response_data['history'] = history_list
        return HttpResponse(json.dumps(response_data), content_type="application/json")