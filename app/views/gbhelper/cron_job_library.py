from datetime import datetime, timedelta
from app.models import Session, SeminarsUsers, Attendee, Setting

def daily_job():
    """This cron-job performs every night 12.01 am"""

    # Session: After session registration deadline, turn in-queue to not-attending
    session_inQueue_to_notAttending()

    # delete pending attendees
    delete_pending_attendee()
    return

def session_inQueue_to_notAttending():
    try:
        today = datetime.today()
        sessions = Session.objects.filter(group__event__end__gte=today, end__lt=today).values('id')
        SeminarsUsers.objects.filter(session_id__in=sessions, status='in-queue').update(status='not-attending')
    except Exception as ex:
        print(ex)
    return

def delete_pending_attendee():
    try:
        from_dtime_to_delete = datetime.today() - timedelta(minutes=60)
        attendee_satus = 'pending'
        if attendee_satus == 'pending':
            Attendee.objects.filter(status=attendee_satus, created__lte=from_dtime_to_delete).delete()
    except Exception as ex:
        print(ex)
    return