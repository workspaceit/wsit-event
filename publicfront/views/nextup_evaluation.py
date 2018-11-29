import sys
from django.http import HttpResponse
from app.models import Attendee, Session, SeminarsUsers, Notification, Setting, Elements, ElementPresetLang, ElementDefaultLang
from datetime import datetime, timedelta
from pytz import timezone
from app.snsHelper import SNSHelper
import threading
import os
import time
import logging


class NextupEvaluation():
    def socket_nextup(request, secret_key, total_conncetion, **kwargs):
        logger = logging.getLogger(__name__)
        logger.debug('Total Connection ----'+str(len(total_conncetion)))
        start_time = time.time()
        try:
            attendee = Attendee.objects.get(secret_key=secret_key)
            element_id = 17
            logger.debug('Attendee ----'+str(attendee.id))
            setting_keys = ['appear_next_up_setting','disappear_next_up_setting','timezone']
            setting_data = NextupEvaluation.get_settings_data(attendee.event_id, setting_keys)
            db_time = setting_data["appear_next_up_setting"]
            db_time_after = NextupEvaluation.hms_to_minutes(db_time)
            db_time = setting_data["disappear_next_up_setting"]
            db_time_before = NextupEvaluation.hms_to_minutes(db_time)
            event_query = setting_data["timezone"]
            time_zone_name = event_query
            timezone_active = timezone(time_zone_name)
            time_now = datetime.now(timezone_active)
            f = '%Y-%m-%d %H:%M:%S'
            now = datetime.strptime(str(time_now).split(".")[0], f)
            time_after = now + timedelta(minutes=db_time_after)
            time_after = datetime.strptime(str(time_after).split(".")[0], f)
            time_before = now - timedelta(minutes=db_time_before)
            time_before = datetime.strptime(str(time_before).split(".")[0], f)
            sql = 'select DISTINCT sessions.*,seminars_has_users.id as seminars_has_user_id, seminars_has_users.status from seminars_has_users, sessions where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                attendee.id) + ' AND (sessions.start <= "' + str(
                time_after) + '" AND sessions.start >="' + str(
                time_before) + '" ' \
                               ' AND seminars_has_users.status_socket_nextup=False' \
                               ' AND `sessions`.`show_on_next_up` = True)'
            sessions = Session.objects.raw(
                sql
            )
            sessions = list(sessions)
            socket_data = []
            if len(sessions) > 0:
                s_time = time.time()
                lang_keys = ['nextup_notify_socket_session_will_start','nextup_notify_socket_session_started']
                language = NextupEvaluation.catch_lang_key_multiple(attendee.language_id, element_id, lang_keys)
                logger.debug('---lang time----'+str(time.time()-s_time)+'')
                for session in sessions:
                    session_start = datetime.strptime(str(session.start).split("+")[0], f)
                    session_start = datetime.strptime(str(session_start).split(".")[0], f)
                    now = datetime.strptime(str(now), f)
                    start = datetime.strptime(str(session_start), f)
                    if now < start:
                        difference = (start - now).total_seconds()
                        if difference > 0:
                            difference = difference / 60
                        else:
                            difference = 0
                        import decimal
                        msg = language['langkey']['nextup_notify_socket_session_will_start'].replace(
                            '{session_name}', str(session.name))
                        message = msg.replace('{remain_time}', str(round(difference)))
                        socket_data.append(message)
                        if os.environ['ENVIRONMENT_TYPE'] == 'master':
                            SendPushNotification(request, attendee, message)
                    else:
                        message = language['langkey']['nextup_notify_socket_session_started'].replace(
                            '{session_name}', str(session.name))
                        socket_data.append(message)
                        if os.environ['ENVIRONMENT_TYPE'] == 'master':
                            SendPushNotification(request, attendee, message)
                    SeminarsUsers.objects.filter(id=session.seminars_has_user_id).update(status_socket_nextup=True)
            # if len(sessions):
                return socket_data
            logger.debug('---socket Nextup time----'+str(time.time()-start_time)+'')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            logger.debug('---socket Nextup Error----'+str(time.time()-start_time)+'')
            logger.debug(str(e))
        return {}

    def socket_evaluation(request, secret_key, **kwargs):
        try:
            logger = logging.getLogger(__name__)
            start_time = time.time()
            attendee = Attendee.objects.get(secret_key=secret_key)
            element_id = 15
            setting_keys = ['appear_evaluation_setting','timezone']
            setting_data = NextupEvaluation.get_settings_data(attendee.event_id, setting_keys)
            db_time = setting_data["appear_evaluation_setting"]
            db_time_after = NextupEvaluation.hms_to_minutes(db_time)
            event_query = setting_data["timezone"]
            time_zone_name = event_query
            timezone_active = timezone(time_zone_name)
            time_now = datetime.now(timezone_active)
            f = '%Y-%m-%d %H:%M:%S'
            now = datetime.strptime(str(time_now).split(".")[0], f)
            time_after = now + timedelta(minutes=db_time_after)
            time_after = datetime.strptime(str(time_after).split(".")[0], f)
            sql = "SELECT sessions.*," \
                  "`seminars_has_users`.`id`," \
                  "`seminars_has_users`.`id` as seminars_has_user_id, " \
                  "`seminars_has_users`.`attendee_id`, " \
                  "`seminars_has_users`.`session_id`, " \
                  "`seminars_has_users`.`status`, " \
                  "`seminars_has_users`.`created`, " \
                  "`seminars_has_users`.`queue_order`" \
                  " FROM `seminars_has_users`" \
                  " INNER JOIN `sessions`" \
                  " ON ( `seminars_has_users`.`session_id` = `sessions`.`id` )" \
                  " WHERE (`sessions`.`end` < '" + str(time_after) + "' " \
                               " AND (`seminars_has_users`.`attendee_id` =" + str(attendee.id) + " " \
                                                                                                   " AND `sessions`.`show_on_evaluation` = True " \
                                                                                                   " AND `seminars_has_users`.`status` = 'attending' " \
                                                                                                   " AND NOT ((`seminars_has_users`.`session_id`) " \
                                                                                                   " IN (SELECT U0.`session_id` FROM `session_ratings` U0 WHERE U0.`attendee_id` = " + str(
                attendee.id) + ")))" \
                                  " AND seminars_has_users.status_socket_evaluation=False)"
            sessions = Session.objects.raw(
                sql
            )
            sessions = list(sessions)
            for session in sessions:
                SeminarsUsers.objects.filter(id=session.seminars_has_user_id).update(
                    status_socket_evaluation=True)
            socket_data = []
            logger.debug('---socket Evaluation time----'+str(time.time()-start_time)+'')
            if len(sessions):
                lang_keys = ['evaluation_notify_socket']
                language = NextupEvaluation.catch_lang_key_multiple(attendee.language_id, element_id, lang_keys)
                message = language['langkey']['evaluation_notify_socket']
                socket_data.append(message)
                if os.environ['ENVIRONMENT_TYPE'] == 'master':
                    SendPushNotification(request, attendee, message)
                return socket_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        return {}

    def socket_message(request, secret_key, **kwargs):
        try:
            logger = logging.getLogger(__name__)
            start_time = time.time()
            socket_data = []
            attendee = Attendee.objects.get(secret_key=secret_key)
            element_id=16
            notifications = Notification.objects.filter(to_attendee=attendee.id, status_socket_message=False)
            logger.debug('---socket Message time----'+str(time.time()-start_time)+'')
            if notifications.exists():
                lang_keys = ['messages_notify_socket_session']
                language = NextupEvaluation.catch_lang_key_multiple(attendee.language_id, element_id, lang_keys)
                socket_data.append(language['langkey']['messages_notify_socket_session'])
                for notification in notifications:
                    Notification.objects.filter(id=notification.id).update(status_socket_message=True)
                return socket_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        return {}

    def get_lang_key(language_id, element_id):
        try:
            response_data = {}
            elementObj = Elements.objects.filter(id=element_id)
            if elementObj.exists():
                lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                             element_default_lang__element_id=elementObj[0].id).select_related('element_default_lang')
                if lang_data.exists():
                    lang_key = {}
                    for lang in lang_data:
                        lang_key[lang.element_default_lang.lang_key] = lang.value

                    response_data['langkey'] = lang_key
                else:
                    default_lang_data = ElementDefaultLang.objects.filter(element_id=elementObj[0].id)
                    lang_key = {}
                    for lang in default_lang_data:
                        lang_key[lang.lang_key] = lang.default_value
                    response_data['langkey'] = lang_key
        except Exception as e:
            response_data = {
                'error': True,
                'message': 'Something went wrong. Please try again.'
            }
            import traceback
            traceback.print_exc()
        return response_data

    def catch_lang_key_multiple(language_id, element_id, lang_keys):
        response = {}
        try:
            lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                         element_default_lang__element_id=element_id,
                                                         element_default_lang__lang_key__in=lang_keys).select_related('element_default_lang')
            lang_key = {}
            for lang in lang_data:
                lang_key[lang.element_default_lang.lang_key] = lang.value
            response['langkey'] = lang_key
        except Exception as e:
            response_data = {
                'error': True,
                'message': 'Something went wrong. Please try again.'
            }
            import traceback
            traceback.print_exc()
            return response_data
        return response

    def get_settings_data(event_id, setting_keys):
        all_settings = Setting.objects.filter(name__in=setting_keys, event=event_id)
        settings = {}
        for setting in all_settings:
            settings[setting.name] = setting.value
        return settings

    def hms_to_minutes(t):
        h, m = [int(i) for i in t.split(':')]
        return 60 * h + m

    def nextup(request, pk, **kwargs):
        seminar_users = SeminarsUsers.objects.values('attendee_id').filter(status='attending', session_id=pk)
        attendee_list = Attendee.objects.filter(id__in=seminar_users)
        return HttpResponse("nextup working fine")

    def evaluation(request, pk, **kwargs):
        seminar_users = SeminarsUsers.objects.values('attendee_id').filter(status='attending', session_id=pk)
        attendee_list = Attendee.objects.filter(id__in=seminar_users)
        return HttpResponse("evaluation working fine")

    def messages(request, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            notifications = Notification.objects.filter(to_attendee_id=attendee_id, status=0)
            new_noty = 0
            if notifications.count() > 0:
                new_noty = notifications[notifications.count() - 1].id
            last_noty = request.session['event_user']['last_noty']
            if new_noty > last_noty:
                print("You have a new message")
            request.session['event_user']['last_noty'] = new_noty
            request.session.modified = True
            return HttpResponse("message working fine")
        else:
            return HttpResponse("No new message found")


class SendPushNotification(threading.Thread):
    """docstring for PushNotification"""

    def __init__(self, request, attendee, msg):
        self.request = request
        self.attendee = attendee
        self.msg = msg
        threading.Thread.__init__(self)

    def run(self):
        session = SNSHelper()
        my_msg = self.msg
        if self.attendee.push_notification_status:
            for device in self.attendee.devicetoken_set.all():
                endpoint = device.arn_enpoint
                endpointAttr = session.getEndpointAttr(endpoint)
                logger = logging.getLogger(__name__)
                logger.debug('-----------Push notification-----------------------')
                logger.debug(endpoint)
                if 'attributes' in endpointAttr:
                    if endpointAttr['attributes']['Enabled']:
                        if device.os_type == '1' or device.os_type == 1:
                            session.androidMessageJSON(endpoint, my_msg, self.subject)
                        elif device.os_type == '2' or device.os_type == 2:
                            if 'ENVIRONMENT_TYPE' in os.environ:
                                if os.environ['ENVIRONMENT_TYPE'] == 'master':
                                    session.iosMessageJSON(endpoint, my_msg)
                                else:
                                    session.iosDevMessageJSON(endpoint, my_msg)
                    else:
                        device.is_enable = False
                        device.save()
