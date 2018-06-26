import re
import django
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views import generic
from app.models import Attendee, Locations, Answers, SessionTags, Booking, MatchLine, SeminarsUsers, Session, \
    Group, Notification, Setting, SeminarSpeakers, ActivityHistory, Questions, Elements, EmailTemplates, StyleSheet
import json
import base64
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Q
import os
import io
import time
import boto
import base64
from boto.s3.key import Key

from publicfront.views.helper import HelperData
from publicfront.views.lang_key import LanguageKey
from publicfront.views.notify_view import NotifyView
from django.template.loader import render_to_string
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image, ExifTags

from publicfront.views.send_email import UserEmail
from publicfront.views.error_report import ErrorR

scheduler = BackgroundScheduler()
# scheduler.add_jobstore('redis')
scheduler.start()
# from publicfront.views.page import StaticPage
from django.contrib.staticfiles.templatetags.staticfiles import static
from publicfront.views.session_seat_availability import SessionSeatAvailability
from app.views.gbhelper.economy_library import EconomyLibrary


class AttendeeProfile(generic.DetailView):

    def getnotifications(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                user_id = request.session['event_user']['id']
                searchkey = request.POST.get('key')
                type = request.POST.get('sort_type')
                if type == None:
                    notification = Notification.objects.filter(to_attendee_id=user_id, status=0)
                else:
                    if type == "all":
                        if searchkey:
                            notification = Notification.objects.filter(to_attendee_id=user_id, status=0,
                                                                       message__contains=searchkey)
                        else:
                            notification = Notification.objects.filter(to_attendee_id=user_id, status=0)
                    else:
                        if type == 'session':
                            notification = Notification.objects.filter(
                                Q(to_attendee_id=user_id, status=0, message__contains=searchkey) & Q(
                                    Q(type='session') | Q(type='session_attend')))
                        else:
                            notification = Notification.objects.filter(to_attendee_id=user_id, status=0,
                                                                       message__contains=searchkey, type=type)

                total_seconds = AttendeeProfile.get_timout(request.session['event_user']['event_id'])
                for nt in notification:
                    if nt.sender_attendee_id != None:
                        first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                            user_id=nt.sender_attendee_id)
                        last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                           user_id=nt.sender_attendee_id)
                        if first_name.exists():
                            nt.sender_attendee.firstname = first_name[0].value
                        if last_name.exists():
                            nt.sender_attendee.lastname = last_name[0].value
                    nt.expire_at = nt.created_at + timedelta(seconds=total_seconds)
                    # nt.save()
                new_noty = 0
                if notification.count() > 0:
                    new_noty = notification[notification.count() - 1].id
                element = Elements.objects.filter(slug="messages")
                if element.exists():
                    language = LanguageKey.get_lang_key(request, element[0].id)
                    language['langkey']['pre_message_countdown'] = \
                        language['langkey']['messages_txt_countdown'].split('{countdown}')[0]
                    language['langkey']['post_message_countdown'] = \
                        language['langkey']['messages_txt_countdown'].split('{countdown}')[1]
                context = {
                    "notifications": notification,
                    "language": language
                }
                get_data = render_to_string('public/profile/my_notifications_result.html', context)
                mydata = {
                    'notifications': get_data,
                    'new_noty': new_noty
                }
                request.session['event_user']['last_noty'] = new_noty
                request.session.modified = True
                return HttpResponse(json.dumps(mydata), content_type="application/json")

    def deletenotification(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            id = request.POST.get('id')
            notification = Notification.objects.get(id=id)
            notification.status = 1
            notification.save()
            empty_txt_language = LanguageKey.catch_lang_key(request, 'messages', 'messages_txt_empty')
            notification_language = LanguageKey.catch_lang_key(request, 'messages', 'messages_notify_archived_success')
            response_data = {}
            response_data['status'] = 'success'
            response_data['empty_txt_language'] = empty_txt_language
            response_data['message'] = notification_language
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({}), content_type="application/json")

    def myLocations(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                location_groups = Group.objects.filter(type="location", is_show=1, is_searchable=1,
                                                       event_id=request.session['event_user']['event_id']).order_by(
                    'group_order')
                data = {
                    'location_groups': location_groups
                }
                return render(request, 'public/profile/locations.html', data)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def handle_uploaded_file(image_data, request, *args, **kwargs):
        f = image_data['image']
        if os.environ['ENVIRONMENT_TYPE'] != 'master' and os.environ['ENVIRONMENT_TYPE'] != 'staging' and os.environ[
            'ENVIRONMENT_TYPE'] != 'develop':
            print("ok")

        else:
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            user_id = request.session['event_user']['id']
            # filepath = settings.BASE_DIR + "/publicfront/static/public/images/attendee/"
            filename = 'public/images/attendee/attendee_' + str(user_id) + '.jpg'
            image = Image.open(io.BytesIO(base64.b64decode(f)))

            image1 = image.rotate(image_data['rotation'])
            im = image1.crop((int(image_data['data']['x']), int(image_data['data']['y']),
                              int(image_data['data']['x']) + int(image_data['data']['width']),
                              int(image_data['data']['y']) + int(image_data['data']['height'])))

            output_image = io.BytesIO()
            im.save(output_image, image.format)
            # image.show()
            # with open(filepath + filename, 'wb') as f:
            #     f.write(imgdata)
            key_name = filename
            k = Key(bucket)
            k.key = key_name
            if not k.exists():
                key = bucket.new_key(key_name)
                # key.set_contents_from_string(out_im.getvalue())
                key.set_contents_from_string(output_image.getvalue())
                key.set_metadata('Content-Type', 'image/' + image.format)
                key.set_acl('public-read')
                key.make_public()
            else:
                k.set_contents_from_string(output_image.getvalue())
                k.set_metadata('Content-Type', 'image/' + image.format)
                k.set_acl('public-read')
                k.make_public()
            Attendee.objects.filter(id=user_id).update(avatar=filename)

            activity_history = ActivityHistory(attendee_id=user_id, activity_type='update', category='profile',
                                               event_id=request.session['event_user']['event_id'])
            activity_history.save()

            request.session['event_user']['avatar'] = filename

    # Need to add response message language for Message plugin
    def sessionNotification(request, *args, **kwargs):
        response_data = {}
        try:
            id = request.POST.get('id')
            action = request.POST.get('action')
            event_id = request.session['event_user']['event_id']
            if action == "yes":
                notification = Notification.objects.get(id=id)
                if notification.status == 0:
                    notification.status = 1
                    notification.save()
                    # if notification:
                    attende_id = notification.to_attendee_id
                    session_id = notification.new_session_id
                    clash_id = notification.clash_session_id
                    session_user = SeminarsUsers.objects.filter(session_id=session_id, attendee_id=attende_id)
                    session_user = session_user[0]
                    session_user.status = "attending"
                    session_user.save()
                    activity1 = ActivityHistory(activity_type="update", category="session", attendee_id=attende_id,
                                                session_id=clash_id, old_value="Attending", new_value="Not Attending",
                                                event_id=event_id)
                    activity1.save()
                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=attende_id,
                                               session_id=session_id, old_value="Deciding", new_value="Attending",
                                               event_id=event_id)
                    activity.save()
                    SeminarsUsers.objects.filter(attendee_id=attende_id, session_id=clash_id).update(
                        status='not-attending')

                    ## Economy Start
                    order_detail = EconomyLibrary.get_order_id(attende_id, 'session', clash_id)
                    if order_detail:
                        result = EconomyLibrary.remove_item_from_order(event_id, attende_id, order_detail['order_id'],
                                                                       clash_id)
                        response_data['download_flag'] = result['download_applicable']
                        response_data['order_number'] = order_detail['order_number']

                    EconomyLibrary.place_order(event_id, attende_id, 'session', session_id)
                    ## Economy End
                    if scheduler.get_job(str(notification.id)):
                        scheduler.remove_job(str(notification.id))
                    response_data['message'] = "you have selected new session"
                else:
                    response_data['message'] = "You have already attending in this session"

            if action == "no":
                notification = Notification.objects.get(id=id)
                if notification.status == 0:
                    notification.status = 1
                    notification.save()
                    if scheduler.get_job(str(notification.id)):
                        scheduler.remove_job(str(notification.id))
                    if notification:
                        attende_id = notification.to_attendee_id
                        session_id = notification.new_session_id
                        SeminarsUsers.objects.filter(attendee_id=attende_id, session_id=session_id).update(
                            status='not-attending')
                        activity = ActivityHistory(activity_type="update", category="session", attendee_id=attende_id,
                                                   session_id=session_id, old_value="Deciding", new_value="Not Attending",
                                                   event_id=event_id)
                        activity.save()
                        SessionDetail.notify_queue_user(request, session_id)
                    response_data['message'] = "you have declined new session"
                else:
                    response_data['message'] = "you have already declined new session"
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
            response_data['message'] = "Something went wrong, Please try again."
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_timout(event_id):
        setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
        timeout = setting[0].value
        new_timeout = time.strptime(timeout, "%H:%M")
        total_seconds = timedelta(hours=new_timeout.tm_hour, minutes=new_timeout.tm_min,
                                  seconds=new_timeout.tm_sec).total_seconds()
        return total_seconds


class SessionDetail(generic.DetailView):

    def get_object(self, pk, event_id):
        try:
            return Session.objects.filter(pk=pk, group__event_id=event_id)[0]
        except Session.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        try:
            scheduler.print_jobs('redis')
            if 'is_user_login' in request.session and request.session['is_user_login']:
                event_id = request.session["event_id"]
                session = self.get_object(pk, event_id)
                attendee_id = request.session['event_user']['id']
                speakers = SeminarSpeakers.objects.filter(session_id=session.id)
                spkFlag = False
                if speakers.count() > 0:
                    for speaker in speakers:
                        if speaker.speaker_id == attendee_id:
                            spkFlag = True
                session.speakers = speakers
                attendee = Attendee.objects.filter(id=attendee_id)
                status_text = 'Not Attending'
                status = 'not-answered'
                session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
                # count = SeminarsUsers.objects.filter(attendee_id=attendee_id, session=session).count()
                if session_attendee.count() > 0:
                    status = session_attendee[0].status
                    if session_attendee[0].status == 'attending':
                        status_text = 'Attending'
                    elif session_attendee[0].status == 'in-queue':
                        status_text = 'In Queue'
                    elif session_attendee[0].status == 'not-attending':
                        status_text = 'Not Attending'
                    elif session_attendee[0].status == 'deciding':
                        status_text = 'Deciding'
                        status = 'in-queue'
                session.is_speaker = False
                if spkFlag:
                    status = 'attending'
                    status_text = 'Attending'
                    session.is_speaker = True

                tags = SessionTags.objects.filter(session_id=session.id)
                session.tags = tags
                session_full = True
                session_attendee_count = SeminarsUsers.objects.filter(session_id=session.id).exclude(
                    status='not-attending').count()
                if session.max_attendees > session_attendee_count:
                    session_full = False
                session.full = session_full
                time_now = datetime.now().date()
                setting_timezone = Setting.objects.filter(name='timezone', event_id=event_id)
                if setting_timezone:
                    tzname = setting_timezone[0].value
                    timezone_active = timezone(tzname)
                    time_now = datetime.now(timezone_active)
                    time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
                    time_now = datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S")
                    time_now = time_now.date()
                session_expire = False
                reg_between_end = session.reg_between_end
                if reg_between_end < time_now:
                    session_expire = True
                session.session_expire = session_expire
                session.session_conflict = SessionDetail.check_session_clash(request, attendee_id, session, previous_id=None)
                context = {
                    'session': session,
                    'attendee': attendee,
                    'status': status,
                    'status_text': status_text,
                    'isSpeaker': spkFlag,
                    'language': LanguageKey.catch_lang_key_obj(request, "session-radio-button"),
                    'request': request
                }
                content = render_to_string('public/element/session_details.html', context)
                template = EmailTemplates.objects.filter(name="default-web-template", event_id=event_id)
                if template.exists():
                    # get css version
                    css_version_obj = StyleSheet.objects.get(event_id=request.session['event_id'])
                    css_version = css_version_obj.version
                    page_content = template[0].content.replace('{content}', content)
                    page_content = page_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                    page_content = page_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                    page_content = page_content.replace('[[css]]',
                                                        "[[static]]public/[[event_url]]/compiled_css/style.css?v=" + str(
                                                            css_version))
                    page_content = page_content.replace('[[static]]', settings.STATIC_URL_ALT)
                    page_content = page_content.replace('public/js/jquery.min.js', static('public/js/jquery.min.js'))
                    page_content = page_content.replace('[[event_url]]', template[0].event.url)
                    page_content = page_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
                    menu_find = re.findall(r'{(menu)}', page_content)
                    if len(menu_find) > 0:
                        # menu = StaticPage.get_menu(request)
                        menu = render_to_string('public/content/menu.html', {'request': request})
                        page_content = page_content.replace('{menu}', menu)
                    context2 = {
                        'event_id': event_id,
                        'csrf_token': django.middleware.csrf.get_token(request),
                        'page_content': page_content
                    }
                    return render(request, 'public/static_pages/cms_page.html', context2)
                else:
                    return redirect('welcome', event_url=request.session['event_url'])
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(traceback.print_exc())
            import os, sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def post(self, request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            sort = request.POST.get('sort')
            tab = request.POST.get('tab')
            all_sessions_groups = []
            user_id = request.session['event_user']['id']
            if sort == 'sort-by-category':
                sort = 'group_order'
                if tab == 'all-session':
                    session_groups = Group.objects.filter(type="session", is_show=1, is_searchable=1,
                                                          event_id=request.session['event_user']['event_id']).order_by(
                        sort)
                    for group in session_groups:
                        group.session = Session.objects.filter(group_id=group.id)
                        SessionDetail.get_filtered_session(group.session, user_id)
                        group_dict = dict(
                            id=group.id,
                            name=group.name,
                            session=group.session
                        )
                        all_sessions_groups.append(group_dict)
                    html = 'public/session/session_list.html'
                else:
                    user_id = request.session['event_user']['id']
                    sessions = Session.objects.raw(
                        'select sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                            user_id) + ' and sessions.group_id = groups.id  and groups.is_searchable = 1 order by groups.group_order')
                    if len(list(sessions)) > 0:
                        for session in sessions:
                            print(session)
                            SessionDetail.get_session(session, user_id)
                            all_sessions_groups.append(session)
                    html = 'public/session/session_sort_time.html'
            elif sort == 'sort-by-category-name':
                sort = 'name'
                if tab == 'all-session':
                    session_groups = Group.objects.filter(type="session", is_show=1, is_searchable=1,
                                                          event_id=request.session['event_user']['event_id']).order_by(
                        sort)
                    for group in session_groups:
                        group.session = Session.objects.filter(group_id=group.id)
                        SessionDetail.get_filtered_session(group.session, user_id)
                        group_dict = dict(
                            id=group.id,
                            name=group.name,
                            session=group.session
                        )
                        all_sessions_groups.append(group_dict)
                    html = 'public/session/session_list.html'
                else:
                    user_id = request.session['event_user']['id']
                    sessions = Session.objects.raw(
                        'select sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                            user_id) + ' and sessions.group_id = groups.id  and groups.is_searchable = 1 order by groups.name')
                    for session in sessions:
                        SessionDetail.get_session(session, user_id)
                        all_sessions_groups.append(session)
                    html = 'public/session/session_sort_time.html'
            else:
                sort = 'start'
                if tab == 'all-session':
                    sessions = Session.objects.filter(
                        group__event_id=request.session['event_user']['event_id']).order_by(sort)
                    for session in sessions:
                        SessionDetail.get_session(session, user_id)
                        if session.group.is_searchable == 1:
                            all_sessions_groups.append(session)
                    html = 'public/session/session_sort_time.html'
                else:
                    user_id = request.session['event_user']['id']
                    sessions = Session.objects.raw(
                        'select sessions.*, seminars_has_users.status from seminars_has_users,sessions where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                            user_id) + ' order by sessions.start')
                    for session in sessions:
                        SessionDetail.get_session(session, user_id)
                        if session.group.is_searchable == 1:
                            all_sessions_groups.append(session)
                    html = 'public/session/session_sort_time.html'
            data = {
                'sessionsGroups': all_sessions_groups
            }
            return render(request, html, data)
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def check_session_clash(request, attendee_id, session, previous_id, remove_conflict=False):
        if previous_id != None:
            already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                               session__allow_overlapping=0).exclude(
                session_id__in=[session.id, previous_id])
            already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id,
                                                                            session__allow_overlapping=0).exclude(
                session_id__in=[session.id, previous_id])
        else:
            already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                               session__allow_overlapping=0).exclude(
                session_id=session.id)
            already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id,
                                                                            session__allow_overlapping=0).exclude(
                session_id=session.id)
        Inbetween = False
        if session.allow_overlapping == 0:
            for sessionlist in already_has_session:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start <= sessionlist.session.start < session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start < sessionlist.session.end <= session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                if remove_conflict and Inbetween:
                    remove_conflict_session = SessionDetail.remove_conflict_session(request, sessionlist, attendee_id)
                    if remove_conflict_session:
                        Inbetween = False

            for sessionlist in already_has_session_as_speaker:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start <= sessionlist.session.start < session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start < sessionlist.session.end <= session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                # if remove_conflict and Inbetween:
                #     remove_conflict_session = SessionDetail.remove_conflict_session(request, sessionlist, attendee_id)
                #     if remove_conflict_session:
                #         Inbetween = False

        # else :
        #     for sessionlist in already_has_session:
        #         if sessionlist.session.allow_overlapping == 0:
        #             if sessionlist.session.start <= session.start <sessionlist.session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #             elif sessionlist.session.start <session.end <=sessionlist.session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #             if session.start <= sessionlist.session.start <session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #             elif session.start < sessionlist.session.end <=session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #
        #     for sessionlist in already_has_session_as_speaker:
        #         if sessionlist.session.allow_overlapping == 0:
        #             if sessionlist.session.start <= session.start <sessionlist.session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #             elif sessionlist.session.start <session.end <=sessionlist.session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #             if session.start <= sessionlist.session.start <session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        #             elif session.start < sessionlist.session.end <=session.end:
        #                Inbetween = True
        #                # response_data['clash_session'] = sessionlist.session.as_dict()
        #                break
        return Inbetween

    def check_session_clash_act_radio(request, attendee_id, session, previous_id=[]):
        remove_conflict = False
        if 'conflict_session_setting' in request.POST:
            if request.POST.get('conflict_session_setting') == '1':
                remove_conflict = True
        if len(previous_id) != 0:
            already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                               session__allow_overlapping=0).exclude(
                session_id__in=previous_id + [session.id])
            already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id,
                                                                            session__allow_overlapping=0).exclude(
                session_id__in=previous_id + [session.id])
        else:
            already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                               session__allow_overlapping=0).exclude(
                session_id=session.id)
            already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id,
                                                                            session__allow_overlapping=0).exclude(
                session_id=session.id)
        Inbetween = False
        if session.allow_overlapping == 0:
            for sessionlist in already_has_session:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start <= sessionlist.session.start < session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start < sessionlist.session.end <= session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                if remove_conflict and Inbetween:
                    remove_conflict_session = SessionDetail.remove_conflict_session(request, sessionlist, attendee_id)
                    if remove_conflict_session:
                        Inbetween = False


            for sessionlist in already_has_session_as_speaker:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start <= sessionlist.session.start < session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                elif session.start < sessionlist.session.end <= session.end:
                    Inbetween = True
                    # response_data['clash_session'] = sessionlist.session.as_dict()
                    # break
                # if remove_conflict and Inbetween:
                #     remove_conflict_session = SessionDetail.remove_conflict_session(request, sessionlist, attendee_id)
                #     if remove_conflict_session:
                #         Inbetween = False
        return Inbetween

    def get_filtered_session(sessions, user_id):
        for session in sessions:
            speakers = SeminarSpeakers.objects.filter(session_id=session.id)
            if speakers.count() > 0:
                for speaker in speakers:
                    badge_firstname = Answers.objects.filter(question_id=68, user_id=speaker.speaker.id)
                    if badge_firstname.exists():
                        speaker.speaker.firstname = badge_firstname[0].value
                    badge_lastname = Answers.objects.filter(question_id=69, user_id=speaker.speaker.id)
                    if badge_lastname.exists():
                        speaker.speaker.lastname = badge_lastname[0].value
            session.speakers = speakers
            seminarUsers = SeminarsUsers.objects.filter(session_id=session.id, attendee_id=user_id)
            if seminarUsers.exists():
                session.status = seminarUsers[0].status
            tags = SessionTags.objects.filter(session_id=session.id)
            session.tags = tags
        return sessions

    def get_session(session, user_id):
        speakers = SeminarSpeakers.objects.filter(session_id=session.id)
        if speakers.count() > 0:
            for speaker in speakers:
                badge_firstname = Answers.objects.filter(question_id=68, user_id=speaker.speaker.id)
                if badge_firstname.exists():
                    speaker.speaker.firstname = badge_firstname[0].value
                badge_lastname = Answers.objects.filter(question_id=69, user_id=speaker.speaker.id)
                if badge_lastname.exists():
                    speaker.speaker.lastname = badge_lastname[0].value
        session.speakers = speakers
        seminarUsers = SeminarsUsers.objects.filter(session_id=session.id, attendee_id=user_id)
        if seminarUsers.exists():
            session.status = seminarUsers[0].status
        tags = SessionTags.objects.filter(session_id=session.id)
        session.tags = tags
        return session

    def attend_or_cancel(request, *args, **kwargs):
        response_data = {}
        if 'is_user_login' in request.session and request.session['is_user_login']:
            session_id = request.POST.get('session_id')
            status_type = request.POST.get('type')
            seats_option = request.POST.get('session_option')
            session = Session.objects.get(id=session_id)
            capacity = session.max_attendees
            attendee_id = request.session['event_user']['id']
            event_id = request.session['event_user']['event_id']
            # count = SeminarsUsers.objects.filter(Q(session_id=session_id)&(Q(status='attending') | Q( status='in-queue'))).count()
            count = SeminarsUsers.objects.filter(session_id=session_id).exclude(status='not-attending').count()
            # count_queue = SeminarsUsers.objects.filter(session_id=session_id, status='in-queue').count()
            all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
            if status_type == 'attend':
                response_data = SessionDetail.status_type_attend(request, session_id)

            elif status_type == 'not-attending-queue':
                SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id, status='not-attending')
                seminar_attendee.save()
                activity = ActivityHistory(activity_type="update", category="session", attendee_id=attendee_id,
                                           session_id=session_id, old_value="In Queue", new_value="Not Attending",
                                           event_id=request.session['event_user']['event_id'])
                activity.save()
                response_data['success'] = True
                response_data['status'] = 'full-queue-open'
                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                         "sessiondetails_txt_status_not_attending")
                response_data['status_queue_open_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                    "sessiondetails_txt_status_queue_open")
                response_data['message'] = NotifyView.get_notification_text(request, "notify_unregistered_session")
            else:
                # SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                # if has_seminar.exists():
                #     seminar_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).update(status='not-attending')
                # else:
                seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id, status='not-attending')
                seminar_attendee.save()

                activity = ActivityHistory(activity_type="update", category="session", attendee_id=attendee_id,
                                           session_id=session_id, old_value="Attending", new_value="Not Attending",
                                           event_id=request.session['event_user']['event_id'])
                activity.save()
                SessionDetail.notify_queue_user(request, session_id)
                response_data['success'] = True
                response_data['status'] = 'not-attending'
                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                         "sessiondetails_txt_status_not_attending")
                response_data['message'] = NotifyView.get_notification_text(request, "notify_unregistered_session")

            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, session, seats_option,
                                                                                        event_id, all_langs)
            response_data['seats_availability'] = session_seats_availability.availability
        else:
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def status_type_attend(request, session_id, previous_id=None, remove_conflict=False):
        response_data = {}
        response_data['result'] = False
        response_data['success'] = False
        response_data['exists'] = False
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            event_id = request.session['event_id']
            session = Session.objects.get(id=session_id, group__event_id=event_id)
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            if not session_expire:
                session_exist = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).exclude(
                    status='not-attending')
                if session_exist.exists():
                    seminar_user = session_exist[0]
                    if seminar_user.status == 'attending':
                        print('if')
                        response_data['result'] = True
                        response_data['message'] = NotifyView.get_notification_text(request,
                                                                                    "notify_session_already_attend")
                        response_data['status'] = 'attending'
                        response_data['already_attending'] = True
                        response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                 "sessiondetails_txt_status_attending")
                    elif seminar_user.status == 'in-queue':
                        print('else')
                        response_data['result'] = True
                        response_data['message'] = NotifyView.get_notification_text(request,
                                                                                    "notify_session_already_queue")
                        response_data['status'] = 'in-queue'
                        response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                 "sessiondetails_txt_status_in_queue")
                    response_data['success'] = True
                    response_data['exists'] = True
                else:
                    capacity = session.max_attendees
                    count = SeminarsUsers.objects.filter(session_id=session_id).exclude(status='not-attending').count()
                    if capacity != 0:
                        if capacity > count:
                            session_conflict = SessionDetail.check_session_clash(request, attendee_id, session, previous_id, remove_conflict)

                            if session_conflict:
                                response_data['success'] = True
                                response_data['result'] = False
                                response_data['status'] = 'time-conflict'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_time_conflict")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_clash_session")
                            else:
                                old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                                           session_id=session_id)
                                if old_history.exists():
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Attending",
                                                               new_value="Attending",
                                                               event_id=event_id)
                                    activity.save()
                                else:
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Answered",
                                                               new_value="Attending",
                                                               event_id=event_id)
                                    activity.save()

                                SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                                # if exists_session.exists():
                                #     SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).update(status='attending')
                                # else:

                                seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id)
                                seminar_attendee.save()
                                response_data['success'] = True
                                response_data['result'] = True
                                response_data['status'] = 'attending'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_attending")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_registered_session")
                            response_data['session_full'] = False
                        else:
                            if not session.receive_answer and session.allow_attendees_queue:
                                print("here")
                                old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                                           session_id=session_id)
                                if old_history.exists():
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Attending",
                                                               new_value="In Queue",
                                                               event_id=event_id)
                                    activity.save()
                                else:
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Answered",
                                                               new_value="In Queue",
                                                               event_id=event_id)
                                    activity.save()

                                SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                                # if not already_has_session:
                                form_data = {
                                    "attendee_id": attendee_id,
                                    "session_id": session_id,
                                    "status": "in-queue"
                                }
                                all_queue = SeminarsUsers.objects.filter(session_id=session_id,
                                                                         status='in-queue').order_by(
                                    'queue_order')
                                if all_queue.exists():
                                    form_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                                seminar_attendee = SeminarsUsers(**form_data)
                                seminar_attendee.save()
                                # else:
                                #     seminar_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).update(status='in-queue')
                                response_data['success'] = True
                                response_data['result'] = True
                                response_data['status'] = 'in-queue'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_in_queue")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_queue_session")
                            else:
                                # response_data['status'] = 'Capacity Full'
                                response_data['success'] = True
                                response_data['result'] = False
                                response_data['status'] = 'full'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_full")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_session_full")

                            response_data['session_full'] = True
                    else:
                        session_conflict = SessionDetail.check_session_clash(request, attendee_id, session, previous_id, remove_conflict)
                        if session_conflict:
                            response_data['success'] = True
                            response_data['result'] = False
                            response_data['status'] = 'time-conflict'
                            response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                     "sessiondetails_txt_status_time_conflict")
                            response_data['message'] = NotifyView.get_notification_text(request, "notify_clash_session")
                        else:
                            old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id)
                            if old_history.exists():
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id,
                                                           session_id=session_id, old_value="Not Attending",
                                                           new_value="Attending",
                                                           event_id=event_id)
                                activity.save()
                            else:
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id,
                                                           session_id=session_id, old_value="Not Answered",
                                                           new_value="Attending",
                                                           event_id=event_id)
                                activity.save()

                            SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                            seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id)
                            seminar_attendee.save()
                            response_data['success'] = True
                            response_data['result'] = True
                            response_data['status'] = 'attending'
                            response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                     "sessiondetails_txt_status_attending")
                            response_data['message'] = NotifyView.get_notification_text(request,
                                                                                        "notify_registered_session")
            else:
                response_data['rsvp_ended'] = True
        else:
            response_data['logged_in'] = False
        return response_data

    def status_type_attend_act_radio(request, session_id, previous_id=[]):
        response_data = {}
        response_data['result'] = False
        response_data['success'] = False
        response_data['exists'] = False
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            event_id = request.session['event_id']
            session = Session.objects.get(id=session_id, group__event_id=event_id)
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            if not session_expire:
                session_exist = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).exclude(
                    status='not-attending')
                if session_exist.exists():
                    seminar_user = session_exist[0]
                    if seminar_user.status == 'attending':
                        print('if')
                        response_data['result'] = True
                        response_data['message'] = NotifyView.get_notification_text(request,
                                                                                    "notify_session_already_attend")
                        response_data['status'] = 'attending'
                        response_data['already_attending'] = True
                        response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                 "sessiondetails_txt_status_attending")
                    elif seminar_user.status == 'in-queue':
                        print('else')
                        response_data['result'] = True
                        response_data['message'] = NotifyView.get_notification_text(request,
                                                                                    "notify_session_already_queue")
                        response_data['status'] = 'in-queue'
                        response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                 "sessiondetails_txt_status_in_queue")
                    response_data['success'] = True
                    response_data['exists'] = True
                else:
                    capacity = session.max_attendees
                    count = SeminarsUsers.objects.filter(session_id=session_id).exclude(status='not-attending').count()
                    if capacity != 0:
                        if capacity > count:
                            session_conflict = SessionDetail.check_session_clash_act_radio(request, attendee_id, session,
                                                                                           previous_id)

                            if session_conflict:
                                response_data['success'] = True
                                response_data['result'] = False
                                response_data['status'] = 'time-conflict'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_time_conflict")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_clash_session")
                            else:
                                old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                                           session_id=session_id)
                                if old_history.exists():
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Attending",
                                                               new_value="Attending",
                                                               event_id=event_id)
                                    activity.save()
                                else:
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Answered",
                                                               new_value="Attending",
                                                               event_id=event_id)
                                    activity.save()

                                SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                                # if exists_session.exists():
                                #     SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).update(status='attending')
                                # else:

                                seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id)
                                seminar_attendee.save()
                                response_data['success'] = True
                                response_data['result'] = True
                                response_data['status'] = 'attending'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_attending")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_registered_session")
                            response_data['session_full'] = False
                        else:
                            if not session.receive_answer and session.allow_attendees_queue:
                                print("here")
                                old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                                           session_id=session_id)
                                if old_history.exists():
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Attending",
                                                               new_value="In Queue",
                                                               event_id=event_id)
                                    activity.save()
                                else:
                                    activity = ActivityHistory(activity_type="update", category="session",
                                                               attendee_id=attendee_id,
                                                               session_id=session_id, old_value="Not Answered",
                                                               new_value="In Queue",
                                                               event_id=event_id)
                                    activity.save()

                                SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                                # if not already_has_session:
                                form_data = {
                                    "attendee_id": attendee_id,
                                    "session_id": session_id,
                                    "status": "in-queue"
                                }
                                all_queue = SeminarsUsers.objects.filter(session_id=session_id,
                                                                         status='in-queue').order_by(
                                    'queue_order')
                                if all_queue.exists():
                                    form_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                                seminar_attendee = SeminarsUsers(**form_data)
                                seminar_attendee.save()
                                # else:
                                #     seminar_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).update(status='in-queue')
                                response_data['success'] = True
                                response_data['result'] = True
                                response_data['status'] = 'in-queue'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_in_queue")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_queue_session")
                            else:
                                # response_data['status'] = 'Capacity Full'
                                response_data['success'] = True
                                response_data['result'] = False
                                response_data['status'] = 'full'
                                response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                         "sessiondetails_txt_status_full")
                                response_data['message'] = NotifyView.get_notification_text(request,
                                                                                            "notify_session_full")

                            response_data['session_full'] = True
                    else:
                        session_conflict = SessionDetail.check_session_clash_act_radio(request, attendee_id, session,
                                                                                       previous_id)
                        if session_conflict:
                            response_data['success'] = True
                            response_data['result'] = False
                            response_data['status'] = 'time-conflict'
                            response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                     "sessiondetails_txt_status_time_conflict")
                            response_data['message'] = NotifyView.get_notification_text(request, "notify_clash_session")
                        else:
                            old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id)
                            if old_history.exists():
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id,
                                                           session_id=session_id, old_value="Not Attending",
                                                           new_value="Attending",
                                                           event_id=event_id)
                                activity.save()
                            else:
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id,
                                                           session_id=session_id, old_value="Not Answered",
                                                           new_value="Attending",
                                                           event_id=event_id)
                                activity.save()

                            SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                            seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id)
                            seminar_attendee.save()
                            response_data['success'] = True
                            response_data['result'] = True
                            response_data['status'] = 'attending'
                            response_data['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                                     "sessiondetails_txt_status_attending")
                            response_data['message'] = NotifyView.get_notification_text(request,
                                                                                        "notify_registered_session")
            else:
                response_data['rsvp_ended'] = True
        else:
            response_data['logged_in'] = False
        return response_data

    def remove_conflict_session(request, sessionUser, user_id):
        response = False
        try:
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = sessionUser.session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            if not session_expire:
                event_id = sessionUser.session.group.event_id
                status = "Attending"
                if sessionUser.status == 'in-queue':
                    status = "In Queue"
                elif sessionUser.status == 'deciding':
                    status = "Deciding"
                SeminarsUsers.objects.filter(id=sessionUser.id).update(status='not-attending')
                activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                           session_id=sessionUser.session_id, old_value=status, new_value="Not Attending",
                                           event_id=event_id)
                activity.save()
                ## Economy Start
                order_detail = EconomyLibrary.get_order_id(user_id, 'session', sessionUser.session_id)
                if order_detail:
                    result = EconomyLibrary.remove_item_from_order(event_id, user_id, order_detail['order_id'],
                                                                   sessionUser.session_id)
                    ## Economy End
                SessionDetail.notify_queue_user(request, sessionUser.session_id)
                response = True
            else:
                response = False
        except Exception as e:
            ErrorR.efail(e)
            response = False
        return response

    def status_type_queue(request, session_id, user_id, event_id):
        response = {}
        response['result'] = False
        response['success'] = False
        my_session = SeminarsUsers.objects.filter(attendee_id=user_id, session_id=session_id).select_related('session')
        if my_session.exists():
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = my_session[0].session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            if not session_expire:
                SeminarsUsers.objects.filter(attendee_id=user_id, session_id=session_id).delete()
                seminar_attendee = SeminarsUsers(attendee_id=user_id, session_id=session_id, status='not-attending')
                seminar_attendee.save()
                activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                           session_id=session_id, old_value="In Queue", new_value="Not Attending",
                                           event_id=event_id)
                activity.save()

                response['success'] = True
                response['result'] = False
                response['status'] = 'full-queue-open'
                status_msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                    ["sessiondetails_txt_status_not_attending","sessiondetails_txt_status_queue_open"])
                response['status_msg'] = status_msg['langkey']['sessiondetails_txt_status_not_attending']
                response['status_queue_open_msg'] = status_msg['langkey']['sessiondetails_txt_status_queue_open']
                response['message'] = NotifyView.get_notification_text(request, "notify_unregistered_session")
            else:
                response['rsvp_ended'] = True
        return response

    def activeSchedule(request, id):
        event_id = request.session['event_id']
        print("Scheduled : Event = " + str(event_id) + " ID = " + str(id))
        notification = Notification.objects.get(id=id)
        if notification:
            if notification.status == 0:
                notification.status = 1
                notification.save()
                if notification:
                    attende_id = notification.to_attendee_id
                    session_id = notification.new_session_id
                    SeminarsUsers.objects.filter(attendee_id=attende_id, session_id=session_id).update(
                        status='not-attending')
                    SessionDetail.notify_queue_user(request, session_id)

    def notify_queue_user(request, session_id, attendee_id=None, *args, **kwargs):
        try:
            event_id = request.session['event_id']
            session = Session.objects.get(id=session_id)
            already_in_queue = SeminarsUsers.objects.filter(session_id=session_id, status='in-queue').order_by(
                'queue_order')
            attendee_id_in_queue = 0
            if attendee_id is None:
                for queue_attende in already_in_queue:
                    already_notified = Notification.objects.filter(to_attendee_id=queue_attende.attendee_id, status=0,
                                                                   new_session_id=session.id)
                    if already_notified.exists():
                        continue
                    else:
                        attendee_id_in_queue = queue_attende.attendee_id
                        break
            else:
                already_in_queue = SeminarsUsers.objects.filter(session_id=session_id, status='in-queue',
                                                                attendee_id=attendee_id)
                attendee_id_in_queue = attendee_id
            if attendee_id_in_queue != 0:
                # attendee_id_in_queue = already_in_queue[0].attendee_id
                sessions_of_queue_attende = SeminarsUsers.objects.filter(attendee_id=attendee_id_in_queue,
                                                                         status='attending',
                                                                         session__allow_overlapping=0)
                Inbetween = 0
                clash_session = 0
                if session.allow_overlapping == 0:
                    for sessionlist in sessions_of_queue_attende:
                        if sessionlist.session.start <= session.start < sessionlist.session.end:
                            Inbetween = 1
                            clash_session = sessionlist.session_id
                            break
                        elif sessionlist.session.start < session.end <= sessionlist.session.end:
                            Inbetween = 1
                            clash_session = sessionlist.session_id
                            break
                        if session.start <= sessionlist.session.start < session.end:
                            Inbetween = 1
                            clash_session = sessionlist.session_id
                            break
                        elif session.start < sessionlist.session.end <= session.end:
                            Inbetween = 1
                            clash_session = sessionlist.session_id
                            break
                else:
                    Inbetween = 0

                if Inbetween == 1:
                    clash = Session.objects.get(id=clash_session)
                    clash_session_id = clash.id
                    new_opened_session_id = session.id
                    # ur11 = reverse('public-session-detail', args=[session.id])
                    # ur12 = reverse('public-session-detail', args=[clash.id])
                    # session1 = "<a href='"+ur11+"'>"+ session.name+"</a>"
                    # session2 = "<a href='"+ur12+"'>"+ clash.name+"</a>"
                    # session1 = session.name
                    # session2 = clash.name
                    clash_name = clash.name
                    session1 = "{session_id:" + str(session.id) + "}"
                    session2 = "{session_id:" + str(clash.id) + "}"
                    # if str(event_id) == str(10):
                    #     msg = "En plats till <strong>"+session1+"</strong> är ledig. vill du hellre delta på denna aktivitet än ditt tidigare val <strong>"+session2+"</strong>?"
                    # else:
                    # msg = "A seat has opened up for <strong>"+session1+"</strong> Would you rather go to this session than your previously booked session <strong>"+session2+"</strong>?"
                    element = Elements.objects.filter(slug="messages")
                    language = LanguageKey.get_lang_key(request, element[0].id)
                    msg = language['langkey']['messages_notify_session_clash'].replace('{session1}', session1)
                    msg = msg.replace('{session2}', session2)
                    notification = Notification(type="session", message=msg, status=0,
                                                to_attendee_id=attendee_id_in_queue, clash_session_id=clash_session_id,
                                                new_session_id=new_opened_session_id)
                    notification.save()
                    # scheduler.add_jobstore('redis', jobs_key=str(notification.id)+".jobs", run_times_key=str(notification.id)+".run_times")
                    total_seconds = AttendeeProfile.get_timout(event_id)
                    alarm_time = datetime.now() + timedelta(seconds=total_seconds)
                    # alarm_time = timezone.now() + timedelta(seconds=total_seconds)

                    SeminarsUsers.objects.filter(attendee_id=attendee_id_in_queue, session_id=session.id).delete()
                    active_deciding = SeminarsUsers(attendee_id=attendee_id_in_queue, session_id=session.id,
                                                    status='deciding')
                    active_deciding.save()
                    # session_data = DjangoSession.objects.all().first()
                    #
                    # session_info = session_data.get_decoded()
                    #
                    # event_id = session_info['event_user']['event_id']
                    activity = ActivityHistory(activity_type="update", category="session",
                                               attendee_id=attendee_id_in_queue, session_id=session.id,
                                               old_value="In Queue", new_value="Deciding", event_id=event_id)
                    activity.save()
                    setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
                    notification_timeout = '01:00'
                    if setting.exists():
                        notification_timeout = setting[0].value
                    email_settings = Setting.objects.filter(name='session_conflict_confirmation', event_id=event_id)
                    if email_settings.exists():
                        email_id = email_settings[0].value
                        # email_queue = UserEmail.email_connection(request)
                        UserEmail.send_session_email_to_user(request, email_id, active_deciding.attendee, clash_name)
                    scheduler.add_job(SessionDetail.activeSchedule, 'date', run_date=alarm_time,
                                      args=[request, notification.id], id=str(notification.id))
                    # subject = "Bekräftelse - Kunskapsveckan och GetTogether"
                    # sender_mail = "registration@eventdobby.com"
                    # template_source ='gt/email_template/conflict_session.html'
                    # if active_deciding.attendee.event_id == 11:
                    #     subject = "NOTIFICATION - KINGFOMARKET"
                    #     sender_mail = "kingfomarket@eventdobby.com"
                    #     base_url = base_url+'/kingfomarket'
                    #     template_source = 'public/email_template/conflict_session.html'
                    # else:
                    #     base_url = base_url+'/gt'
                    # context = {
                    #     'new_session': session,
                    #     'clash_session': clash,
                    #     'queue_attendee': active_deciding,
                    #     'notification_timeout': notification_timeout,
                    #     'base_url': base_url,
                    # }
                    # to = active_deciding.attendee.email
                    # MailHelper.mail_send(template_source,context,subject,to,sender_mail)

                else:
                    queue_id = already_in_queue[0].id
                    s_id = already_in_queue[0].session_id
                    a_id = already_in_queue[0].attendee_id
                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=a_id,
                                               session_id=s_id, old_value="In Queue", new_value="Attending",
                                               event_id=event_id)
                    activity.save()

                    SeminarsUsers.objects.filter(id=queue_id).delete()
                    seminar_user = SeminarsUsers(session_id=s_id, attendee_id=a_id)
                    seminar_user.save()
                    # new_queue = SeminarsUsers.objects.filter(id=queue_id)
                    # ur11 = reverse('public-session-detail', args=[session.id])
                    # session1 = "<a href='"+ur11+"'>"+ session.name+"</a>"
                    # session1 = session.name
                    session1 = "{session_id:" + str(session.id) + "}"
                    session_name = session.name
                    # if str(event_id) == str(10):
                    #     msg = "Aktiviteten <strong>"+session1+"</strong> har lagts till i din agenda."
                    # else:
                    element = Elements.objects.filter(slug="messages")
                    language = LanguageKey.get_lang_key(request, element[0].id)
                    msg = language['langkey']['messages_notify_session_attend'].replace('{session}',
                                                                                        session1)
                    ErrorR.okgreen(msg)
                    notify = Notification(type="session_attend", message=msg, status=0,
                                          to_attendee_id=attendee_id_in_queue)
                    notify.save()

                    ## Economy Start
                    EconomyLibrary.place_order(event_id, a_id, 'session', s_id)
                    ## Economy End

                    email_settings = Setting.objects.filter(name='session_no_conflict_confirmation', event_id=event_id)
                    if email_settings.exists():
                        email_id = email_settings[0].value
                        # email_queue = UserEmail.email_connection(request)
                        UserEmail.send_session_email_to_user(request, email_id, seminar_user.attendee, session_name)

        except Exception as e:
            ErrorR.efail(e)
        return "success"
