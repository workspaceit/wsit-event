
from app.models import SeminarsUsers, Session, SeminarSpeakers


class General():

    def testSession(attendee_id,session_id):

        response = {}
        response['valid'] = True
        session = Session.objects.get(id=session_id)
        if session:
            response['session']=session.name
            capacity = session.max_attendees
            count = SeminarsUsers.objects.filter(session_id=session_id,status='attending').count()
            # if capacity > count: [condition changed when require to allow max_attendees=0 that means unlimited atnde alolw]
            if capacity > count or capacity == 0:
                    already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',session__allow_overlapping=0)
                    already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id)
                    Inbetween = 0
                    isSpeaker = 0
                    if session.allow_overlapping == 0:
                        for sessionlist in already_has_session:
                           # if sessionlist.session.start <= session.start <sessionlist.session.end:
                           #     Inbetween = 1
                           #     break
                           # elif sessionlist.session.start <session.end <=sessionlist.session.end:
                           #     Inbetween = 1
                           #     break
                            if sessionlist.session.start <= session.start <sessionlist.session.end:
                               Inbetween = 1
                               break
                            elif sessionlist.session.start <session.end <=sessionlist.session.end:
                               Inbetween = 1
                               break
                            if session.start <= sessionlist.session.start <session.end:
                               Inbetween = 1
                               break
                            elif session.start < sessionlist.session.end <=session.end:
                               Inbetween = 1
                               break
                        for sessionlist in already_has_session_as_speaker:
                            if sessionlist.session.start <= session.start <sessionlist.session.end:
                               Inbetween = 1
                               isSpeaker = 1
                               break
                            elif sessionlist.session.start <session.end <=sessionlist.session.end:
                               Inbetween = 1
                               isSpeaker = 1
                               break
                            if session.start <= sessionlist.session.start <session.end:
                               Inbetween = 1
                               isSpeaker = 1
                               break
                            elif session.start < sessionlist.session.end <=session.end:
                               Inbetween = 1
                               isSpeaker = 1
                               break

                    if Inbetween==1:
                        if isSpeaker==1:
                            response['reason'] = "Attendee is already speaker of a Session"
                        else:
                            response['reason'] = "Attendee has Session Clash"
                        response['valid'] = False
            else:
                response['valid'] = False
                response['reason'] = "Session limit exceed."
                if session.allow_attendees_queue:
                    response['is_queue'] = True
        else:
            response['valid'] = False
            response['reason'] = "Session not found."
        print(response)
        return response

