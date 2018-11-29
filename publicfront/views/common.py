import re

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from app.models import SessionTags, Session, Group, SeminarsUsers, Answers, SeminarSpeakers, \
    SessionRating, Setting, Events, Presets
import json
from publicfront.views.lang_key import LanguageKey
from .page2 import DynamicPage
import datetime
from django.db.models import Q
from django.utils.timezone import localtime
from pytz import timezone
from slugify import slugify
import os
from icalendar import Calendar, Event
import io
from bs4 import BeautifulSoup
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.helper import HelperData


class AttendeeSession(generic.DeleteView):
    def welcome(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            return DynamicPage.get_static_page(request, 'logged-in', True, *args, **kwargs)
        else:
            return DynamicPage.get_static_page(request, 'start', True, *args, **kwargs)

    def webcal(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                attendee_id = request.session['event_user']['id']
                query_string = 'SELECT ssn.*, shu.status FROM sessions ssn left join seminars_has_users shu on ssn.id = shu.session_id left join seminars_has_speakers shs on ssn.id=shs.session_id left join groups grp on ssn.group_id = grp.id where (( shu.attendee_id=' + str(
                    attendee_id) + ' and shu.status="attending") or shs.speaker_id=' + str(
                    attendee_id) + ') and grp.is_searchable = 1 group by ssn.id order by grp.group_order'
                sessions = Session.objects.raw(query_string)
                event_id = request.session['event_id']
                event = Events.objects.get(id=event_id)

                setting_timezone = Setting.objects.filter(name='timezone', event_id=event_id)
                timezone = "UTC"
                if setting_timezone:
                    timezone = setting_timezone[0].value

                cal = Calendar()
                # from datetime import datetime
                cal.add('prodid', event.name)
                cal.add('name', event.name)
                cal.add('X-WR-CALNAME', event.name)
                cal.add('version', '2.0')
                import pytz

                for session in sessions:
                    event = Event()
                    event.add('summary', session.name)
                    if session.all_day:
                        event.add('dtstart', session.start.date())
                        event.add('dtend', session.end.date() + datetime.timedelta(days=1))
                    else:
                        event.add('dtstart', session.start.replace(tzinfo=pytz.timezone(timezone)))
                        event.add('dtend', session.end.replace(tzinfo=pytz.timezone(timezone)))
                    event.add('location', session.location.name)

                    soup = BeautifulSoup(session.description, "html.parser")

                    text_parts = soup.findAll(text=True)
                    text = ''.join(text_parts)
                    event.add('DESCRIPTION', text)
                    cal.add_component(event)

                out = io.BytesIO()
                out.write(cal.to_ical())

                response = HttpResponse(content_type='text/Calendar')
                response['Content-Disposition'] = 'inline; filename=hi.ics'
                response.write(out.getvalue())
                return response
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def checkAccess(request, path, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                return render(request, path)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def sessionSchedule(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            today = datetime.datetime.today()
            sesion_groups = Group.objects.filter(type='session', is_show=1, is_searchable=1,
                                                 event_id=request.session['event_user']['event_id']).order_by(
                'group_order')

            for group in sesion_groups:
                group.slug_name = slugify(group.name)
            sessions = Session.objects.all().select_related("group").filter(group__is_show=1,
                                                                            group__is_searchable=1, group__event_id=
                                                                            request.session['event_user'][
                                                                                'event_id']).filter(
                Q(start__gte=today))
            if sessions.exists():
                start_date = str(sessions[0].start.strftime('%Y-%m-%d'))
            else:
                start_date = "2015-11-20"

            data = {
                'start_date': start_date,
                'session_groups': sesion_groups
            }
            return render(request, 'public/session/session_schdule_new.html', data)
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def getSessionGroup(request, *args, **kwargs):
        groups = Group.objects.filter(type='session', is_show=1, is_searchable=1,
                                      event_id=request.session['event_user']['event_id']).order_by('group_order')
        response_data = []
        if groups.exists():
            for group in groups:
                id = group.id
                name = group.name
                group_obj = {
                    'id': id,
                    'title': name,
                    'eventColor': 'red'
                }
                response_data.append(group_obj)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def getSessionEvent(request, *args, **kwargs):
        tab = request.GET.get('tab')
        attendee_id = request.session['event_user']['id']
        sessions = Session.objects.all().select_related("group").filter(group__is_show=1, group__is_searchable=1,
                                                                        group__event_id=request.session['event_user'][
                                                                            'event_id'])

        if tab == "all-session":
            sessions = Session.objects.all().select_related("group").filter(group__is_show=1, group__is_searchable=1,
                                                                            group__event_id=
                                                                            request.session['event_user']['event_id'])
            # for s in sessions:
            #     print(s.id)
        elif tab == "my-session":
            sessions = Session.objects.raw(
                'select DISTINCT sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                    attendee_id) + ' and sessions.group_id = groups.id  and groups.is_searchable = 1 order by groups.group_order')

        response_data = []
        if len(list(sessions)) > 0:
            for session in sessions:
                id = session.id
                name = session.name
                group = session.group_id
                location = session.location.name
                location_id = session.location.id
                start = str(localtime(session.start))
                end = str(localtime(session.end))
                # color = '#FA4092'
                color = '#FFFFFF'
                borderColor = ""
                status = "no"
                tags = SessionTags.objects.filter(session_id=session.id)
                taglist = []
                for tag in tags:
                    taglist.append(tag.tag.name)

                speakers = SeminarSpeakers.objects.filter(session_id=id)
                speakersData = []
                if speakers.count() > 0:
                    for speaker in speakers:
                        badge_firstname = Answers.objects.filter(question_id=68, user_id=speaker.speaker.id)
                        if badge_firstname.exists():
                            firstname = badge_firstname[0].value
                        else:
                            firstname = speaker.speaker.firstname

                        badge_lastname = Answers.objects.filter(question_id=69, user_id=speaker.speaker.id)
                        if badge_lastname.exists():
                            lastname = badge_lastname[0].value
                        else:
                            lastname = speaker.speaker.lastname
                        speaker_obj = {
                            'id': speaker.speaker.id,
                            'firstname': firstname,
                            'lastname': lastname
                        }
                        speakersData.append(speaker_obj)

                session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
                if session_attendee.count() > 0:
                    if session_attendee[0].status == 'attending':
                        color = '#00B67D'
                        status = "yes"
                        # borderColor="#00B67D"
                    elif session_attendee[0].status == 'in-queue':
                        color = '#FFC000'
                        status = "in-queue"

                session_obj = {
                    'id': id,
                    'title': name,
                    'resourceId': group,
                    'start': start,
                    'end': end,
                    # 'color': color,
                    'allDay': False,
                    'status': status,
                    'location': location,
                    'speakers': speakersData,
                    'taglist': taglist,
                    'eventBorderColor': borderColor,
                    'location_id': location_id

                }
                response_data.append(session_obj)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # new plugin

    def getSessionGroup2(request, *args, **kwargs):
        group = request.GET.get('group')
        if group == "mina_kurser":
            groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Kurser',
                                          event_id=request.session['event_user']['event_id']).order_by('group_order')
        elif group == 'mina_semiarieval':
            groups = Group.objects.filter(type='session', is_show=1, is_searchable=1,
                                          event_id=request.session['event_user']['event_id']).order_by(
                'group_order').exclude(Q(name='Kurser') | Q(name='Aktiviteter') | Q(name='Träning & Aktiviteter'))
        elif group == "aktiviteter":
            groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Aktiviteter',
                                          event_id=request.session['event_user']['event_id']).order_by('group_order')
        elif group == "training_activity":
            groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Träning & Aktiviteter',
                                          event_id=request.session['event_user']['event_id']).order_by('group_order')
        else:
            groups = Group.objects.filter(type='session', is_show=1, is_searchable=1,
                                          event_id=request.session['event_user']['event_id']).order_by(
                'group_order').exclude(name='All King')
        response_data = []
        if groups.exists():
            for group in groups:
                id = group.id
                name = group.name
                color = group.color
                group_obj = {
                    'value': id,
                    'text': name,
                    'color': None
                }
                response_data.append(group_obj)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def getSessionEvent2(request, *args, **kwargs):
        tab = request.GET.get('tab')
        group = request.GET.get('group')
        attendee_id = request.session['event_user']['id']
        sessions = Session.objects.all().select_related("group").filter(group__is_show=1, group__is_searchable=1,
                                                                        group__event_id=request.session['event_user'][
                                                                            'event_id'])

        if tab == "all-session":
            if group:
                sessions = Session.objects.all().select_related("group").filter(group__is_show=1,
                                                                                group__is_searchable=1,
                                                                                group__event_id=
                                                                                request.session['event_user'][
                                                                                    'event_id'], group__name='Kurser')
            else:
                sessions = Session.objects.all().select_related("group").filter(group__is_show=1,
                                                                                group__is_searchable=1,
                                                                                group__event_id=
                                                                                request.session['event_user'][
                                                                                    'event_id'])
        elif tab == "my-session":
            if group:
                sessions = Session.objects.raw(
                    'SELECT ssn.*, shu.status FROM sessions ssn left join seminars_has_users shu on ssn.id = shu.session_id left join seminars_has_speakers shs on ssn.id=shs.session_id left join groups grp on ssn.group_id = grp.id where (( shu.attendee_id=' + str(
                        attendee_id) + ' and shu.status="attending") or shs.speaker_id=' + str(
                        attendee_id) + ') and grp.is_searchable = 1 and grp.name="Kurser" group by ssn.id order by grp.group_order')
            else:
                # sessions = Session.objects.raw(
                #         'select DISTINCT sessions.*, seminars_has_users.status from seminars_has_users,sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                #                 attendee_id) + ' and sessions.group_id = groups.id  and groups.is_searchable = 1 group by sessions.id order by groups.group_order')
                query_string = 'SELECT ssn.*, shu.status FROM sessions ssn left join seminars_has_users shu on ssn.id = shu.session_id left join seminars_has_speakers shs on ssn.id=shs.session_id left join groups grp on ssn.group_id = grp.id where (( shu.attendee_id=' + str(
                    attendee_id) + ' and shu.status="attending") or shs.speaker_id=' + str(
                    attendee_id) + ') and grp.is_searchable = 1 group by ssn.id order by grp.group_order'
                sessions = Session.objects.raw(query_string)
        response_data = []
        if len(list(sessions)) > 0:
            for session in sessions:
                id = session.id
                name = session.name
                group = session.group_id
                location = session.location.name
                location_id = session.location.id

                capacity = session.max_attendees
                count = SeminarsUsers.objects.filter(session_id=id).exclude(status='not-attending').count()
                full = False
                if capacity != 0:
                    if capacity <= count:
                        full = True

                start = str(session.start)
                end = str(session.end)
                allday = session.all_day
                if allday:
                    start = session.start.strftime("%Y-%m-%d")
                    end = session.end.strftime("%Y-%m-%d")

                background = Group.objects.get(id=group)
                color = background.color
                status = "not-attending"
                tags = SessionTags.objects.filter(session_id=session.id)
                taglist = []
                for tag in tags:
                    taglist.append(tag.tag.name)

                speakers = SeminarSpeakers.objects.filter(session_id=id)
                speakersData = []
                if speakers.count() > 0:
                    for speaker in speakers:
                        badge_firstname = Answers.objects.filter(question__actual_definition='firstname',
                                                                 user_id=speaker.speaker.id)
                        if badge_firstname.exists():
                            firstname = badge_firstname[0].value
                        else:
                            firstname = speaker.speaker.firstname

                        badge_lastname = Answers.objects.filter(question__actual_definition='lastname',
                                                                user_id=speaker.speaker.id)
                        if badge_lastname.exists():
                            lastname = badge_lastname[0].value
                        else:
                            lastname = speaker.speaker.lastname

                        speaker_obj = {
                            'id': speaker.speaker.id,
                            'firstname': firstname,
                            'lastname': lastname
                        }
                        speakersData.append(speaker_obj)

                session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
                session_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id, session_id=session.id)
                if session_attendee.count() > 0:
                    if session_attendee[0].status == 'attending':
                        status = "attending"
                    elif session_attendee[0].status == 'in-queue':
                        status = "in-queue"
                    elif session_attendee[0].status == 'deciding':
                        status = "deciding"
                    elif session_attendee[0].status == 'not-attending':
                        session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                                                                           status="attending",
                                                                           session__allow_overlapping=0) & (
                                                                             Q(session__start__lte=session.start,
                                                                               session__end__gt=session.start) | Q(
                                                                                 session__start__lt=session.end,
                                                                                 session__end__gte=session.end)))

                        if session_attending.count() > 0:
                            status = 'clash'
                        else:
                            status = 'not-attending'
                else:

                    session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                                                                       status="attending",
                                                                       session__allow_overlapping=0) & (
                                                                         Q(session__start__lte=session.start,
                                                                           session__end__gt=session.start) | Q(
                                                                             session__start__lt=session.end,
                                                                             session__end__gte=session.end)))

                    if session_attending.count() > 0:
                        status = 'clash'
                    else:
                        status = 'not-answered'
                if session_speaker.count() > 0:
                    status = "attending"

                session_obj = {
                    'id': id,
                    'Title': name,
                    'groupId': group,
                    'groupName': background.name,
                    'Start': start,
                    'End': end,
                    'color': color,
                    'IsAllDay': allday,
                    'full': full,
                    'status': status,
                    'location': location,
                    'speakers': speakersData,
                    'taglist': taglist,
                    'location_id': location_id

                }
                response_data.append(session_obj)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def set_session_ratings(request, *args, **kwargs):
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                session_ratings = json.loads(request.POST.get('sessions_rating'))
                response_data = {}
                import time
                start_time = time.time()
                sessions_dict = {}
                new_ratings = []
                user_id = request.session['event_user']['id']

                new_ratings = []
                for session in session_ratings:
                    rating_data = {
                        'session_id': session['session_id'],
                        'attendee_id': request.session['event_user']['id'],
                        'rating': session['rating']
                    }
                    rating_info = SessionRating.objects.filter(session_id=session['session_id'],
                                                               attendee_id=request.session['event_user']['id']).first()
                    if rating_info:
                        SessionRating.objects.filter(id=rating_info.id).update(**rating_data)
                    else:
                        rating = SessionRating(**rating_data)
                        new_ratings.append(rating)
                SessionRating.objects.bulk_create(new_ratings)
                empty_txt_language = LanguageKey.catch_lang_key(request, 'evaluations', 'evaluation_txt_empty')
                notification_language = LanguageKey.catch_lang_key(request, 'evaluations',
                                                                   'evaluation_notify_session_success')
                response_data['success'] = True
                response_data['message'] = notification_language
                response_data['empty_txt_language'] = empty_txt_language
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse(json.dumps({}), content_type="application/json")
        except Exception as e:
            ErrorR.efail(e)
            return HttpResponse(json.dumps({}), content_type="application/json")

    def getTimezoneNow(request, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            now = datetime.datetime.now(timezone_active)
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            return now

    def getAllowedEmail(request, *args, **kwargs):
        if 'event_url' in kwargs:
            event_url = kwargs['event_url']
            event_response = HelperData.checkEventSession(request, event_url)
            if 'event_response' in event_response:
                ErrorR.ilog(event_response['event_response'])
        group = Group.objects.filter(type="email", is_show=1, event_id=request.session['event_id']).order_by(
            'group_order')
        list = []
        for grp in group:
            list.append(grp.as_dict())

        return HttpResponse(json.dumps(list), content_type="application/json")

    def get_timezone(request, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_user']['event_id'])
        timezone = "Asia/Dhaka"
        if setting_timezone:
            timezone = setting_timezone[0].value
        else:
            timezone = ""

        response_data = {
            'timezone': timezone
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def reset_password(request, *args, **kwargs):
        return DynamicPage.get_static_page(request, 'reset-password-page', True, *args, **kwargs)

    def request_login(request, *args, **kwargs):
        return DynamicPage.get_static_page(request, 'request-login-page', True, *args, **kwargs)


def utc_to_local(request, date_input):
    setting_timezone = Setting.objects.filter(name='timezone',
                                              event_id=request.session['event_id'])
    if setting_timezone:
        tzname = setting_timezone[0].value

    import datetime
    from pytz import timezone
    date_input = (date_input.split('.'))[0]
    unaware_est = datetime.datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
    utctz = timezone("UTC")
    aware_est = utctz.localize(unaware_est)
    convertedtz = timezone(tzname)
    convertedtime = aware_est.astimezone(convertedtz)
    return convertedtime

def get_formated_date(request,date_obj):
    event_id = request.session['event_id']
    date_format_obj = Setting.objects.filter(event_id=event_id,name='default_date_format')
    format = '%Y-%m-%d'
    if date_format_obj.exists():
        format_json_obj = json.loads(date_format_obj[0].value)
        if 'python' in format_json_obj:
            format = format_json_obj['python']
            compiled_re = re.compile('[a-zA-Z]')
            matched_keys = compiled_re.findall(format)
            for key in matched_keys:
                format = format.replace(key, '%' + key)

    format = format+' %H:%M'
    date_string = date_obj.strftime(format)
    return date_string

def get_formated_date_string(date_value, lang_id):
    try:
        if type(date_value) is str:
            date_value = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
        date_format = Presets.objects.get(id=lang_id).date_format
        compiled_re = re.compile('[a-zA-Z]')
        matched_keys = compiled_re.findall(date_format)
        for key in matched_keys:
            date_format = date_format.replace(key, '%' + key)

        date_string = date_value.strftime(date_format)
    except Exception as excep:
        print(excep)
        date_string = ''

    return date_string