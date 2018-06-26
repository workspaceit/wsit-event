from django.http import Http404
from django.views import generic
from app.models import Setting, Presets, Events, PresetEvent, Attendee
from datetime import datetime, timedelta
from pytz import timezone
import time, re

from publicfront.views.error_report import ErrorR


class HelperData(generic.DetailView):

    def getTimezoneNow(request, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            now = datetime.now(timezone_active)
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            return now

    def get_timout(event_id):
        setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
        timeout = setting[0].value
        new_timeout = time.strptime(timeout, "%H:%M")
        total_seconds = timedelta(hours=new_timeout.tm_hour, minutes=new_timeout.tm_min,
                                  seconds=new_timeout.tm_sec).total_seconds()
        return total_seconds

    def utc_to_local(request, date_input):
        setting_timezone = Setting.objects.filter(name='timezone',event_id=request.session['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value
        import datetime
        from pytz import timezone
        date_input = (date_input.split('.'))[0]
        date_input = (date_input.split('+'))[0]
        unaware_est = datetime.datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
        utctz = timezone("UTC")
        aware_est = utctz.localize(unaware_est)
        convertedtz = timezone(tzname)
        convertedtime = aware_est.astimezone(convertedtz)
        return convertedtime

    def convert_datetime_to_date_and_time(date_input):
        datetime_field = {}
        date_input = (date_input.split('.'))[0]
        date_input = (date_input.split('+'))[0]
        date_data = datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
        datetime_field['date_field'] = date_data.date()
        datetime_field['time_field'] = date_data.time()
        return datetime_field

    def isfloat(x):
        try:
            a = float(x)
        except ValueError:
            return False
        else:
            return True

    def isint(x):
        try:
            a = float(x)
            b = int(a)
        except ValueError:
            return False
        else:
            return a == b

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

    def checkEventSession(request, event_url):
        response = {}
        request.session['event_url'] = event_url
        event_data = Events.objects.filter(url=event_url)
        if event_data.exists():
            current_event_id = event_data[0].id
        else:
            raise Http404
        if 'event_id' in request.session:
            if request.session['event_id'] != current_event_id:
                if 'is_user_login' in request.session:
                    del request.session['is_user_login']
                if 'event_user' in request.session:
                    del request.session['event_user']
                if 'language_id' in request.session:
                    del request.session['language_id']
                    presetsEvent = PresetEvent.objects.filter(event_id=current_event_id).first()
                    request.session['language_id'] = presetsEvent.preset_id
                response['event_response'] = "You have already logged in in another Event"
        request.session['event_id'] = current_event_id
        request.session.modified = True
        return response

    def tem_login_make(request, attendee_id):
        try:
            attendee = Attendee.objects.get(id=attendee_id)
            tem_session = {}
            if "event_user" in request.session:
                tem_session["event_user"] = request.session['event_user']
            tem_session["event_id"] = request.session['event_id']
            if "is_user_login" in request.session:
                tem_session["is_user_login"] = request.session['is_user_login']
            auth_user = {
                "id": attendee.id,
                "name": '',
                "email": "",
                "type": attendee.type,
                "attending": "",
                "avatar": "",
                "secret_key": "",
                "event_id": request.session['event_id']
            }
            if attendee.firstname and attendee.firstname:
                auth_user["name"] = attendee.firstname + " " + attendee.lastname
            if attendee.email:
                auth_user["email"] = attendee.email
            if attendee.status:
                auth_user["attending"] = attendee.status
            if attendee.avatar:
                auth_user["avatar"] = attendee.avatar
            if attendee.secret_key:
                auth_user["secret_key"] = attendee.secret_key
            request.session['event_user'] = auth_user
            request.session['event_id'] = auth_user['event_id']
            request.session['is_user_login'] = True
            request.session.modified = True
            return tem_session
        except Exception as e:
            del request.session["event_user"]
            del request.session["is_user_login"]
            del request.session["event_id"]
            del request.session["is_user_login"]
            ErrorR.efail(e)

    def tem_login_clean(request, tem_session):
        try:
            if "event_user" in tem_session:
                request.session['event_user'] = tem_session["event_user"]
            else:
                del request.session['event_user']
            request.session['event_id'] = tem_session["event_id"]
            if "is_user_login" in tem_session:
                request.session['is_user_login'] = tem_session["is_user_login"]
            else:
                del request.session['is_user_login']
            request.session.modified = True
        except Exception as e:
            del request.session["event_user"]
            del request.session["is_user_login"]
            del request.session["event_id"]
            del request.session["is_user_login"]
            ErrorR.efail(e)

    def get_allow_same_email_multiple_registration(event_id):
        setting_allow_same_email = Setting.objects.filter(name='allow_same_email_multiple_registration', event_id=event_id)
        result = True if setting_allow_same_email and setting_allow_same_email[0].value == 'true' else False
        return result
