from django.shortcuts import render, redirect
from django.views import generic
from app.models import Answers, SessionTags, SeminarsUsers, Session, SeminarSpeakers


class SessionFilter(generic.DetailView):
    def search_sessions(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            sort = request.GET.get('sort')
            tab = request.GET.get('tab')
            search_key = request.GET.get('search_key')
            search_key = "%%%s%%" % search_key
            user_id = request.session['event_user']['id']
            event_id = request.session["event_user"]["event_id"]
            if sort == 'sort-by-category':
                if tab == 'all-session':
                    sessions = Session.objects.raw(
                        'select DISTINCT sessions.* from sessions left join session_has_tags ON ( session_has_tags.session_id = sessions.id ) left join general_tags ON ( session_has_tags.tag_id = general_tags.id and general_tags.category =  "session" ) left join groups on (sessions.group_id = groups.id) left join seminars_has_speakers on (seminars_has_speakers.session_id = sessions.id) left join attendees on (seminars_has_speakers.speaker_id = attendees.id) left join answers a1 on (seminars_has_speakers.speaker_id=a1.user_id and a1.question_id = 68) left join answers a2 on (seminars_has_speakers.speaker_id=a2.user_id and a2.question_id = 69) where groups.is_searchable = 1 and groups.event_id = event_id and (sessions.name like %s or attendees.firstname like %s or attendees.lastname like %s or groups.name like %s or general_tags.name like %s or a1.value like %s or a2.value like %s) order by groups.group_order',
                        [search_key, search_key, search_key, search_key, search_key, search_key, search_key])
                else:

                    sessions = Session.objects.raw(
                        'select DISTINCT sessions.* from sessions left join session_has_tags ON ( session_has_tags.session_id = sessions.id ) left join general_tags ON ( session_has_tags.tag_id = general_tags.id and general_tags.category =  "session" ) left join seminars_has_speakers on (seminars_has_speakers.session_id = sessions.id) left join attendees on (seminars_has_speakers.speaker_id = attendees.id) left join groups on (sessions.group_id = groups.id) left join seminars_has_users on (seminars_has_users.session_id = sessions.id) left join answers a1 on (seminars_has_speakers.speaker_id=a1.user_id and a1.question_id = 68) left join answers a2 on (seminars_has_speakers.speaker_id=a2.user_id and a2.question_id = 69) where seminars_has_users.attendee_id=' + str(
                            user_id) + ' and seminars_has_users.status = "attending" and groups.is_searchable = 1 and (sessions.name like %s or attendees.firstname like %s or attendees.lastname like %s or groups.name like %s  or general_tags.name like %s or a1.value like %s or a2.value like %s) order by groups.group_order',
                        [search_key, search_key, search_key, search_key, search_key, search_key, search_key])
            elif sort == 'sort-by-category-name':
                if tab == 'all-session':
                    sessions = Session.objects.raw(
                        'select DISTINCT sessions.* from sessions left join session_has_tags ON ( session_has_tags.session_id = sessions.id ) left join general_tags ON ( session_has_tags.tag_id = general_tags.id and general_tags.category =  "session" ) left join groups on (sessions.group_id = groups.id) left join seminars_has_speakers on (seminars_has_speakers.session_id = sessions.id) left join attendees on (seminars_has_speakers.speaker_id = attendees.id) left join answers a1 on (seminars_has_speakers.speaker_id=a1.user_id and a1.question_id = 68) left join answers a2 on (seminars_has_speakers.speaker_id=a2.user_id and a2.question_id = 69) where groups.is_searchable = 1 and groups.event_id = event_id and (sessions.name like %s or attendees.firstname like %s or attendees.lastname like %s or groups.name like %s or general_tags.name like %s or a1.value like %s or a2.value like %s) order by groups.name',
                        [search_key, search_key, search_key, search_key, search_key, search_key, search_key])
                else:
                    sessions = Session.objects.raw(
                        'select DISTINCT sessions.* from sessions left join session_has_tags ON ( session_has_tags.session_id = sessions.id ) left join general_tags ON ( session_has_tags.tag_id = general_tags.id and general_tags.category =  "session" ) left join seminars_has_speakers on (seminars_has_speakers.session_id = sessions.id) left join attendees on (seminars_has_speakers.speaker_id = attendees.id) left join groups on (sessions.group_id = groups.id) left join seminars_has_users on (seminars_has_users.session_id = sessions.id) left join answers a1 on (seminars_has_speakers.speaker_id=a1.user_id and a1.question_id = 68) left join answers a2 on (seminars_has_speakers.speaker_id=a2.user_id and a2.question_id = 69) where seminars_has_users.attendee_id=' + str(
                            user_id) + ' and seminars_has_users.status = "attending" and groups.is_searchable = 1 and (sessions.name like %s or attendees.firstname like %s or attendees.lastname like %s or groups.name like %s  or general_tags.name like %s or a1.value like %s or a2.value like %s) order by groups.name',
                        [search_key, search_key, search_key, search_key, search_key, search_key, search_key])
            else:
                if tab == 'all-session':
                    sessions = Session.objects.raw(
                        'select DISTINCT sessions.* from sessions left join session_has_tags ON ( session_has_tags.session_id = sessions.id ) left join general_tags ON ( session_has_tags.tag_id = general_tags.id and general_tags.category =  "session" ) left join groups on (sessions.group_id = groups.id) left join seminars_has_speakers on (seminars_has_speakers.session_id = sessions.id) left join attendees on (seminars_has_speakers.speaker_id = attendees.id) left join answers a1 on (seminars_has_speakers.speaker_id=a1.user_id and a1.question_id = 68) left join answers a2 on (seminars_has_speakers.speaker_id=a2.user_id and a2.question_id = 69) where groups.is_searchable = 1 and groups.event_id = event_id and (sessions.name like %s or attendees.firstname like %s or attendees.lastname like %s or groups.name like %s or general_tags.name like %s or a1.value like %s or a2.value like %s) order by sessions.start',
                        [search_key, search_key, search_key, search_key, search_key, search_key, search_key])
                else:
                    sessions = Session.objects.raw(
                        'select DISTINCT sessions.* from sessions left join session_has_tags ON ( session_has_tags.session_id = sessions.id ) left join general_tags ON ( session_has_tags.tag_id = general_tags.id and general_tags.category =  "session" ) left join seminars_has_speakers on (seminars_has_speakers.session_id = sessions.id) left join attendees on (seminars_has_speakers.speaker_id = attendees.id) left join groups on (sessions.group_id = groups.id) left join seminars_has_users on (seminars_has_users.session_id = sessions.id) left join answers a1 on (seminars_has_speakers.speaker_id=a1.user_id and a1.question_id = 68) left join answers a2 on (seminars_has_speakers.speaker_id=a2.user_id and a2.question_id = 69) where seminars_has_users.attendee_id=' + str(
                            user_id) + ' and seminars_has_users.status = "attending" and groups.is_searchable = 1 and (sessions.name like %s or attendees.firstname like %s or attendees.lastname like %s or groups.name like %s  or general_tags.name like %s or a1.value like %s or a2.value like %s) order by sessions.start',
                        [search_key, search_key, search_key, search_key, search_key, search_key, search_key])
            all_sessions_groups = []

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
                seminarUsers = SeminarsUsers.objects.filter(session_id=session.id,
                                                            attendee_id=request.session['event_user']['id'])
                if seminarUsers.exists():
                    session.status = seminarUsers[0].status
                tags = SessionTags.objects.filter(session_id=session.id)
                session.tags = tags
                all_sessions_groups.append(session)
            html = 'public/session/session_sort_time.html'
            data = {
                'sessionsGroups': all_sessions_groups
            }
            return render(request, html, data)
        else:
            return redirect('welcome', event_url=request.session['event_url'])
