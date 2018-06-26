import pytz

from django.utils import timezone
from app.models import Group,Setting

import datetime

class TimezoneMiddleware(object):
    def process_request(self, request, *args, **kwargs):
        # tzname = request.session.get('django_timezone')
        setting_timezone = Setting.objects.filter(name='timezone')
        if setting_timezone:
            tzname = setting_timezone[0].value
            print(tzname)
        else:
            tzname=""

        if tzname:
            timezone.activate(pytz.timezone(tzname))
            # print("Datetime Now: "+ str(datetime.datetime.now()))
            # print("Timezone Now: "+ str(timezone.now()))
            # print("timezone local Now:  "+str(timezone.localtime(timezone.now())))
        else:
            timezone.deactivate()
