from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from app.models import Attendee, Locations , Answers, SessionTags , Booking, MatchLine, SeminarsUsers, Session, \
    Group, Notification, Setting, SeminarSpeakers,ActivityHistory




class SessionDetail(generic.DetailView):

    def get(self, request, pk):

        if 'is_user_login' in request.session and request.session['is_user_login']:
            session = Session.objects.get(id=pk)
            user_id = request.session['event_user']['id']
            speakers = SeminarSpeakers.objects.filter(session_id=session.id)
            spkFlag=False
            if speakers.count() > 0:
                for speaker in speakers:
                    if speaker.speaker_id==user_id:
                        spkFlag=True
                    badge_firstname = Answers.objects.filter(question_id=68, user_id=speaker.speaker.id)
                    if badge_firstname.exists():
                        speaker.speaker.firstname = badge_firstname[0].value
                    badge_lastname = Answers.objects.filter(question_id=69, user_id=speaker.speaker.id)
                    if badge_lastname.exists():
                        speaker.speaker.lastname = badge_lastname[0].value
            session.speakers = speakers
            attendee_id = request.session['event_user']['id']
            attendee = Attendee.objects.filter(id=attendee_id)
            status = 'Not Answered'
            session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
            count = SeminarsUsers.objects.filter(attendee_id=attendee_id, session=session).count()
            if count > 0:
                if session_attendee[0].status == 'attending':
                    status = 'Attending'
                elif session_attendee[0].status == 'in-queue':
                    status = 'In Queue'
                elif session_attendee[0].status == 'not-attending':
                    status = 'Not Attending'
                elif session_attendee[0].status == 'deciding':
                    status = 'Deciding'

            tags = SessionTags.objects.filter(session_id=session.id)
            session_full = True
            session_attendee_count = SeminarsUsers.objects.filter(session_id=session.id).exclude(status='not-attending').count()
            if session.max_attendees > session_attendee_count:
                session_full = False
            context = {
                'session': session,
                'attendee': attendee,
                'status': status,
                'tag_list':tags,
                'isSpeaker':spkFlag,
                'session_full': session_full
            }
            return render(request, 'gt/session/session_detail.html', context)
        else:
            return redirect('welcome')
    def session_detail_post(request, pk):

        if 'is_user_login' in request.session and request.session['is_user_login']:
            session = Session.objects.get(id=pk)
            user_id = request.session['event_user']['id']
            speakers = SeminarSpeakers.objects.filter(session_id=session.id)
            spkFlag=False
            if speakers.count() > 0:
                for speaker in speakers:
                    if speaker.speaker_id==user_id:
                        spkFlag=True
                    badge_firstname = Answers.objects.filter(question_id=68, user_id=speaker.speaker.id)
                    if badge_firstname.exists():
                        speaker.speaker.firstname = badge_firstname[0].value
                    badge_lastname = Answers.objects.filter(question_id=69, user_id=speaker.speaker.id)
                    if badge_lastname.exists():
                        speaker.speaker.lastname = badge_lastname[0].value
            session.speakers = speakers
            attendee_id = request.session['event_user']['id']
            attendee = Attendee.objects.filter(id=attendee_id)
            status = 'Not Answered'
            session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
            count = SeminarsUsers.objects.filter(attendee_id=attendee_id, session=session).count()
            if count > 0:
                if session_attendee[0].status == 'attending':
                    status = 'Attending'
                elif session_attendee[0].status == 'in-queue':
                    status = 'In Queue'
                elif session_attendee[0].status == 'not-attending':
                    status = 'Not Attending'
                elif session_attendee[0].status == 'deciding':
                    status = 'Deciding'

            tags = SessionTags.objects.filter(session_id=session.id)
            session_full = True
            session_attendee_count = SeminarsUsers.objects.filter(session_id=session.id).exclude(status='not-attending').count()
            if session.max_attendees > session_attendee_count:
                session_full = False
            context = {
                'session': session,
                'attendee': attendee,
                'status': status,
                'tag_list':tags,
                'isSpeaker':spkFlag,
                'session_full': session_full
            }
            return render(request, 'gt/session/session_detail_post.html', context)
        else:
            return redirect('welcome')