import json
import os
import sys
from django.db.models import Count
from django.http import HttpResponse
from django.views import generic
from datetime import datetime, timedelta
from app.models import AttendeeGroups, Session, \
    RuleSet, DashboardPlugin, SeminarsUsers
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.filter import FilterView
from django.db import connection
from django.template.loader import render_to_string
import calendar
from collections import OrderedDict


class DashboardView(generic.DetailView):
    def pagehit_statistic(request):
        response_data = {}
        response_data['label'] = []
        response_data['label'].append("All Hit")
        response_data['label'].append("Unique Hit")
        try:
            hit_by_date = []
            unique_hit_by_date = []

            date_format = "%Y-%m-%d"
            start_time = datetime.strptime(request.POST.get('start_time'), date_format)
            end_time = datetime.strptime(request.POST.get('end_time'), date_format)

            DashboardView.save_dashboard_setting(request, 'pagehit_statistic',
                                                 {'start_time': request.POST.get('start_time'),
                                                  'end_time': request.POST.get('end_time')})
            [time_format, time_format_sql, time_for_sync, labels, time] = DashboardView.label_decide(start_time,
                                                                                                     end_time)
            hit_labels = labels.copy()
            unique_hit_labels = labels.copy()

            cursor = connection.cursor()
            hit_count_sql = render_to_string('dashboard/dashboard_query.html',
                                             {
                                                 'event_id': request.session['event_auth_user']['event_id'],
                                                 'page_id': request.POST.get("page"),
                                                 'time_format': time_format,
                                                 'time_format_sql': time_format_sql,
                                                 'start_time': start_time,
                                                 'end_time': end_time,
                                                 'select_sql': "hitcountsql",
                                             })
            cursor.execute(hit_count_sql)
            hit_counts = cursor.fetchall()

            unique_hit_count_sql = render_to_string('dashboard/dashboard_query.html',
                                                    {
                                                        'event_id': request.session['event_auth_user']['event_id'],
                                                        'page_id': request.POST.get("page"),
                                                        'time_format': time_format,
                                                        'time_format_sql': time_format_sql,
                                                        'start_time': start_time,
                                                        'end_time': end_time,
                                                        'select_sql': "uniquehitcountsql",
                                                    })
            cursor.execute(unique_hit_count_sql)
            unique_hit_counts = cursor.fetchall()

            if len(hit_counts) <= 1:
                hit_by_date.append(0)

            for i, hit_count in enumerate(hit_counts):
                hit_labels[hit_count[0].strftime(time_for_sync)] = int(hit_count[1])
            for field in hit_labels:
                hit_by_date.append(hit_labels[field])

            if len(hit_counts) <= 1:
                hit_by_date.append(0)

            if len(unique_hit_counts) <= 1:
                unique_hit_by_date.append(0)

            for unique_hit_count in unique_hit_counts:
                unique_hit_labels[unique_hit_count[0].strftime(time_for_sync)] = int(unique_hit_count[1])
            for field in unique_hit_labels:
                unique_hit_by_date.append(unique_hit_labels[field])

            if len(unique_hit_counts) <= 1:
                unique_hit_by_date.append(0)
            response_data["hit_by_date"] = hit_by_date
            response_data["unique_hit_by_date"] = unique_hit_by_date
            response_data["time"] = time
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def reg_statistic(request):
        response_data = {}
        response_data['label'] = []
        response_data['label'].append("Registration")

        try:

            reg_by_date = []
            date_format = "%Y-%m-%d"
            start_time = datetime.strptime(request.POST.get('start_time'), date_format)
            end_time = datetime.strptime(request.POST.get('end_time'), date_format)
            DashboardView.save_dashboard_setting(request, 'reg_statistic',
                                                 {'start_time': request.POST.get('start_time'),
                                                  'end_time': request.POST.get('end_time')})
            [time_format, time_format_sql, time_for_sync, labels, time] = DashboardView.label_decide(start_time,
                                                                                                     end_time)
            cursor = connection.cursor()
            reg_count_sql = render_to_string('dashboard/dashboard_query.html',
                                             {
                                                 'event_id': request.session['event_auth_user']['event_id'],
                                                 'time_format': time_format,
                                                 'time_format_sql': time_format_sql,
                                                 'start_time': start_time,
                                                 'end_time': end_time,
                                                 'select_sql': "regcountsql",
                                             })
            cursor.execute(reg_count_sql)
            reg_counts = cursor.fetchall()
            if len(reg_counts) <= 1:
                reg_by_date.append(0)
            for i, reg_count in enumerate(reg_counts):
                labels[reg_count[0].strftime(time_for_sync)] = int(reg_count[1])
            for field in labels:
                reg_by_date.append(labels[field])
            if len(reg_counts) <= 1:
                reg_by_date.append(0)
            response_data["reg_by_date"] = reg_by_date
            response_data["time"] = time
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def attendeegroup_statistic(request):
        response_data = {}
        response_data['label'] = []
        response_data['label'].append("Attendee Group")
        try:
            groups = []
            DashboardView.save_dashboard_setting(request, 'attendeegroup_statistic', request.POST.get('groups'))
            if request.POST.get('groups') != "null":
                for group in json.loads(request.POST.get('groups')):
                    groups.append(group)
                attendee_counts = AttendeeGroups.objects
                attendee_counts = attendee_counts.filter(group_id__in=groups)
                attendee_counts = attendee_counts.values('group__name').annotate(count=Count('id'))
                groups = []
                attendee_by_groups = []
                for attendee_count in attendee_counts:
                    groups.append(attendee_count['group__name'])
                    attendee_by_groups.append(attendee_count['count'])
                response_data["groups"] = groups
                response_data["attendee_by_groups"] = attendee_by_groups
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def session_statistic(request, session_grp_id):
        response_data = {}
        try:
            DashboardView.save_dashboard_setting(request, 'session_statistic', session_grp_id)
            if int(session_grp_id) != 0:
                sessionsData = Session.objects.filter(group_id=session_grp_id).only('id', 'name').all()
                sessions = []
                for session in sessionsData:
                    session_arr = {}
                    session_arr['session_name'] = session.name
                    session_arr['total_attendee'] = SeminarsUsers.objects.filter(session_id=session.id,
                                                                                 status='attending').count()
                    sessions.append(session_arr)
                response_data = sessions
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def filter_statistic(request, filter_grp_id):
        response_data = {}
        try:
            DashboardView.save_dashboard_setting(request, 'filter_statistic', filter_grp_id)
            if int(filter_grp_id) != 0:
                filtersData = RuleSet.objects.filter(group_id=filter_grp_id).only('id', 'name').all()
                filters = []
                for filter in filtersData:
                    filter_arr = {}
                    filter_arr['filter_name'] = filter.name
                    filter_arr['total_attendee'] = FilterView.get_filtered_attendees_count(request, filter.id)
                    filters.append(filter_arr)
                response_data = filters
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def message_statistic(request):
        response_data = {}
        response_data['label'] = []

        try:
            email_by_date = []
            sms_by_date = []
            notification_by_date = []
            date_format = "%Y-%m-%d"
            start_time = datetime.strptime(request.POST.get('start_time'), date_format)
            end_time = datetime.strptime(request.POST.get('end_time'), date_format)
            DashboardView.save_dashboard_setting(request, 'message_statistic',
                                                 {'start_time': request.POST.get('start_time'),
                                                  'end_time': request.POST.get('end_time')})
            [time_format, time_format_sql, time_for_sync, labels, time] = DashboardView.label_decide(start_time,
                                                                                                     end_time)
            email_labels = labels.copy()
            sms_labels = labels.copy()
            notification_labels = labels.copy()
            cursor = connection.cursor()
            email_count_sql = render_to_string('dashboard/dashboard_query.html',
                                               {
                                                   'event_id': request.session['event_auth_user']['event_id'],
                                                   'time_format': time_format,
                                                   'time_format_sql': time_format_sql,
                                                   'start_time': start_time,
                                                   'end_time': end_time,
                                                   'select_sql': "emailcountsql",
                                               })
            cursor.execute(email_count_sql)
            email_counts = cursor.fetchall()
            sms_count_sql = render_to_string('dashboard/dashboard_query.html',
                                             {
                                                 'event_id': request.session['event_auth_user']['event_id'],
                                                 'time_format': time_format,
                                                 'time_format_sql': time_format_sql,
                                                 'start_time': start_time,
                                                 'end_time': end_time,
                                                 'select_sql': "smscountsql",
                                             })
            cursor.execute(sms_count_sql)
            sms_counts = cursor.fetchall()
            notification_count_sql = render_to_string('dashboard/dashboard_query.html',
                                                      {
                                                          'event_id': request.session['event_auth_user']['event_id'],
                                                          'time_format': time_format,
                                                          'time_format_sql': time_format_sql,
                                                          'start_time': start_time,
                                                          'end_time': end_time,
                                                          'select_sql': "notificationcountsql",
                                                      })
            cursor.execute(notification_count_sql)
            notification_counts = cursor.fetchall()

            if len(email_counts) <= 1:
                email_by_date.append(0)
            if len(sms_counts) <= 1:
                sms_by_date.append(0)
            if len(notification_counts) <= 1:
                notification_by_date.append(0)

            for i, email_count in enumerate(email_counts):
                email_labels[email_count[0].strftime(time_for_sync)] = int(email_count[1])
            for i, sms_count in enumerate(sms_counts):
                sms_labels[sms_count[0].strftime(time_for_sync)] = int(sms_count[1])
            for i, notification_count in enumerate(notification_counts):
                notification_labels[notification_count[0].strftime(time_for_sync)] = int(notification_count[1])

            for field in email_labels:
                email_by_date.append(email_labels[field])
            for field in sms_labels:
                sms_by_date.append(sms_labels[field])
            for field in notification_labels:
                notification_by_date.append(notification_labels[field])

            if len(email_counts) <= 1:
                email_by_date.append(0)
            if len(sms_counts) <= 1:
                sms_by_date.append(0)
            if len(notification_counts) <= 1:
                notification_by_date.append(0)

            response_data['label'].append("Send Email")
            response_data['label'].append("Sent SMS")
            response_data['label'].append("Sent notifications")

            response_data["email_by_date"] = email_by_date
            response_data["sms_by_date"] = sms_by_date
            response_data["notification_by_date"] = notification_by_date
            response_data["time"] = time
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def sort_plugin(request):
        response_data = {}
        try:
            DashboardView.save_dashboard_setting(request, 'sort_data', request.POST.get('sort'))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            response_data['error'] = exc_type + fname + exc_tb.tb_lineno
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_dashboard_setting(request, name, data):
        try:
            dashboard_plugin = DashboardPlugin.objects.filter(event_id=request.session['event_auth_user']['event_id'],
                                                              modified_by_id=request.session['event_auth_user'][
                                                                  'id'])
            setting_data = {}
            if dashboard_plugin.exists():
                setting_data = json.loads(dashboard_plugin[0].setting_data)
            setting_data[name] = data
            if data == None or data == "null":
                del setting_data[name]

            if dashboard_plugin.exists():
                DashboardPlugin.objects.filter(event_id=request.session['event_auth_user']['event_id'],
                                               modified_by_id=request.session['event_auth_user'][
                                                   'id']).update(setting_data=json.dumps(setting_data))
            else:
                new_dashboard_plugin = DashboardPlugin(event_id=request.session['event_auth_user']['event_id'],
                                                       modified_by_id=request.session['event_auth_user']['id'],
                                                       setting_data=json.dumps(setting_data))
                new_dashboard_plugin.save()
        except Exception as e:
            ErrorR.efail(e)

    def get_label_array(type):
        context = OrderedDict()
        if type == "W":
            context['Mon'] = 0
            context['Tue'] = 0
            context['Wed'] = 0
            context['Thu'] = 0
            context['Fri'] = 0
            context['Sat'] = 0
            context['Sun'] = 0
        elif type == 'M':
            context['01'] = 0
            context['02'] = 0
            context['03'] = 0
            context['04'] = 0
            context['05'] = 0
            context['06'] = 0
            context['07'] = 0
            context['08'] = 0
            context['09'] = 0
            context['10'] = 0
            context['11'] = 0
            context['12'] = 0
            context['13'] = 0
            context['14'] = 0
            context['15'] = 0
            context['16'] = 0
            context['17'] = 0
            context['18'] = 0
            context['19'] = 0
            context['20'] = 0
            context['21'] = 0
            context['22'] = 0
            context['23'] = 0
            context['24'] = 0
            context['25'] = 0
            context['26'] = 0
            context['27'] = 0
            context['28'] = 0
            context['29'] = 0
            context['30'] = 0

        elif type == 'Y':
            context['Jan'] = 0
            context['Feb'] = 0
            context['Mar'] = 0
            context['Apr'] = 0
            context['May'] = 0
            context['Jun'] = 0
            context['Jul'] = 0
            context['Aug'] = 0
            context['Sep'] = 0
            context['Oct'] = 0
            context['Nov'] = 0
            context['Dec'] = 0
        return context

    def month_converter(month):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return months[month - 1]

    def add_months(sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day)

    def label_decide(start_time, end_time):
        time_format = ""
        time_format_sql = ""
        time_for_sync = ""
        time = []
        delta_time = end_time - start_time
        labels = OrderedDict()
        cur_time = start_time
        if 1 >= delta_time.days:
            time_format = "week"
            time_format_sql = "week"
            time_for_sync = "%a"
            # while cur_time <= end_time:
            labels[cur_time.strftime(time_for_sync)] = 0
            time.append("")
            time.append(cur_time.strftime(time_for_sync))
            time.append("")
            cur_time = cur_time + timedelta(days=1)

        elif 1 < delta_time.days < 7:
            time_format = "day"
            time_format_sql = "date"
            time_for_sync = "%d"
            while cur_time <= end_time:
                labels[cur_time.strftime(time_for_sync)] = 0
                time.append(cur_time.strftime(time_for_sync))
                cur_time = cur_time + timedelta(days=1)
        elif 7 >= delta_time.days < 8:
            time_format = "week"
            time_format_sql = "week"
            time_for_sync = "%a"
            while cur_time <= end_time:
                labels[cur_time.strftime(time_for_sync)] = 0
                time.append(cur_time.strftime(time_for_sync))
                cur_time = cur_time + timedelta(days=1)
        elif 7 < delta_time.days < 31:
            time_format = "month"
            time_format_sql = "date"
            time_for_sync = "%d"
            while cur_time <= end_time:
                labels[cur_time.strftime(time_for_sync)] = 0
                time.append(cur_time.strftime(time_for_sync))
                cur_time = cur_time + timedelta(days=1)
        elif 31 < delta_time.days:
            time_format = "year"
            time_format_sql = "month"
            time_for_sync = "%b"
            while cur_time <= end_time:
                labels[cur_time.strftime(time_for_sync)] = 0
                time.append(cur_time.strftime(time_for_sync))
                cur_time = DashboardView.add_months(cur_time, 1)

        return [time_format, time_format_sql, time_for_sync, labels, time]
