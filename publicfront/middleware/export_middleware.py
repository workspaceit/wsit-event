
from app.models import ExportState, Attendee
from datetime import datetime, timedelta
from django.contrib.sessions.models import Session

class ExportMiddleware(object):
    def process_request(self, request):
        path = request.path.split('/')[1]

        if path == 'admin':
            now = datetime.now()
            time_before_5min = now - timedelta(minutes=6)
            if 'event_auth_user' in request.session:
                export_state= ExportState.objects.filter(admin_id=request.session['event_auth_user']['id'],event_id=request.session['event_auth_user']['event_id'], status=0, created__gt=time_before_5min )
                if export_state:
                    request.export_state="on"

                try:
                    from_dtime_to_delete = datetime.today() - timedelta(minutes=60)
                    attendee_satus = 'pending'
                    if attendee_satus == 'pending':
                        Attendee.objects.filter(status=attendee_satus, created__lte=from_dtime_to_delete).delete()
                except Exception as ex:
                    print(ex)

                try:
                    date = datetime.now() - timedelta(hours=1)
                    Session.objects.filter(expire_date__lt=date).delete()
                except Exception as ex:
                    print(ex)

