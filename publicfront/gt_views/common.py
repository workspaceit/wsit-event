from django.shortcuts import render, redirect
from django.views import generic
from app.models import Users, Attendee, SessionTags, Session, Group, SeminarsUsers, Answers, SeminarSpeakers, \
    SessionRating, Notification, Setting, PageContent ,Booking ,MatchLine
import datetime
from django.db.models import Q
import time
from django.http import HttpResponse
import json
from datetime import timedelta
from pytz import timezone
from django.conf import settings
from django.http import Http404


class CommonMenu(generic.DeleteView):

    def start(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                sessions_finished = CommonMenu.get_finished_sessions(request)
                sessions_next_up = CommonMenu.get_nextup_sessions(request)
                notifications = CommonMenu.session_notifications(request)
                new_noty = 0
                if notifications.count() > 0:
                    new_noty = notifications[notifications.count() - 1].id
                new_sessions_finished = []
                for session in sessions_finished:
                    new_sessions_finished.append(session.session.id)
                new_sessions_next_up = []
                for next_session in sessions_next_up:
                    new_sessions_next_up.append(next_session['id'])
                context = {
                    'sessions_finished': sessions_finished,
                    'sessions_next_up': sessions_next_up,
                    'time': datetime.datetime.now(),
                    'notifications': notifications
                }
                request.session['event_user']['last_noty'] = new_noty
                request.session['event_user']['new_sessions_finished'] = new_sessions_finished
                request.session['event_user']['new_sessions_next_up'] = new_sessions_next_up
                request.session.modified = True
                return render(request, 'gt/common/start.html', context)
            else:
                return render(request, 'gt/common/start_before.html')
        else:
            return render(request, 'gt/common/start_before.html')

    def start_test(request):
        return render(request, 'gt/common/start_test.html')

    def mina_kurser(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            today = datetime.datetime.today()
            sesion_groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Kurser',
                                                 event_id=request.session['event_user']['event_id']).order_by(
                'group_order')
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
            return render(request, 'gt/common/mina_kurser.html',data)
        else:
            return redirect('gt-welcome')

    def mina_kurser_post(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            today = datetime.datetime.today()
            sesion_groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Kurser',
                                                 event_id=request.session['event_user']['event_id']).order_by(
                'group_order')
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
            return render(request, 'gt/common/mina_kurser_post.html',data)
        else:
            return redirect('gt-welcome')

    def mina_training_aktiviteter(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            today = datetime.datetime.today()
            sesion_groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Träning & Aktiviteter',
                                                 event_id=request.session['event_user']['event_id']).order_by(
                'group_order')
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
            return render(request, 'gt/common/mina_training_aktiviteter.html',data)
        else:
            return redirect('gt-welcome')

    def mina_semiarieval(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            today = datetime.datetime.today()
            sesion_groups = Group.objects.filter(type='session', is_show=1, is_searchable=1,
                                                 event_id=request.session['event_user']['event_id']).order_by(
                'group_order').exclude(Q(name='Kurser')|Q(name='Aktiviteter')|Q(name='Middagar')|Q(name='Träning & Aktiviteter'))
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
            return render(request, 'gt/common/mina_semiarieval.html',data)
        else:
            return redirect('gt-welcome')

    def aktiviteter(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            today = datetime.datetime.today()
            sesion_groups = Group.objects.filter(type='session', is_show=1, is_searchable=1, name='Aktiviteter',
                                                 event_id=request.session['event_user']['event_id']).order_by(
                'group_order')
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
            return render(request, 'gt/common/aktiviteter.html',data)
        else:
            return redirect('gt-welcome')

    def summering(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee = request.session['event_user']['id']

            # accomodation
            bookings = Booking.objects.filter(attendee_id=attendee).order_by('check_in','check_out')
            booking_info = []
            for booking in bookings:
                booking_data ={}
                booking_data['check_in']=booking.check_in
                booking_data['check_out']=booking.check_out
                booking_data['room_description']=booking.room.description
                booking_data['hotel_name']= booking.room.hotel.name
                match = MatchLine.objects.filter(booking_id=booking.id)
                if match.exists():
                    match_id = match[0].match_id
                    matches = MatchLine.objects.filter(match_id=match_id).exclude(booking_id=booking.id)
                    roombuddy=[]
                    for match_buddy in matches:
                        buddy={}
                        buddy['firstname']= match_buddy.booking.attendee.firstname
                        buddy['lastname']= match_buddy.booking.attendee.lastname
                        buddy['email']= match_buddy.booking.attendee.email
                        roombuddy.append(buddy)
                    booking_data['roombuddy']=roombuddy

                booking_info.append(booking_data)

            #middagar
            dinners = SeminarsUsers.objects.filter(attendee_id=attendee,session__group__name='Middagar',status='attending')

            #middagar
            courses = SeminarsUsers.objects.filter(attendee_id=attendee,session__group__name='Kurser',status='attending').order_by('session__start')

            #activity
            activities = SeminarsUsers.objects.filter(attendee_id=attendee,session__group__name='Aktiviteter',status='attending').order_by('session__start')

            #Training activity
            training_activities = SeminarsUsers.objects.filter(attendee_id=attendee,session__group__name='Träning & Aktiviteter',status='attending').order_by('session__start')

            # seminars

            seminars = SeminarsUsers.objects.filter(attendee_id=attendee,status='attending').exclude(Q(session__group__name='Kurser')|Q(session__group__name='Aktiviteter')|Q(session__group__name='Middagar')|Q(session__group__name='Träning & Aktiviteter')).order_by('session__start')

           #matavvikelser
            matavvikelser = Answers.objects.filter(question_id=140,user_id=attendee)
            answer = None
            if matavvikelser.exists():
                answer=matavvikelser[0].value

            #grouping

            # Lokal lördag kl. 09:00:
            answer1 = Answers.objects.filter(question_id=237,user_id=attendee)
            quesion_answer1 = None
            if answer1.exists():
                quesion_answer1=answer1[0].value

             # Lokal lördag kl. 10:40:
            answer2 = Answers.objects.filter(question_id=238,user_id=attendee)
            quesion_answer2 = None
            if answer2.exists():
                quesion_answer2=answer2[0].value


            # Bordsnummer
            answer3 = Answers.objects.filter(question_id=236,user_id=attendee)
            quesion_answer3 = None
            if answer3.exists():
                quesion_answer3=answer3[0].value

            sessions_finished = CommonMenu.get_finished_sessions(request)
            sessions_next_up = CommonMenu.get_nextup_sessions(request)
            notifications = CommonMenu.session_notifications(request)
            new_noty = 0
            if notifications.count() > 0:
                new_noty = notifications[notifications.count() - 1].id
            new_sessions_finished = []
            for session in sessions_finished:
                new_sessions_finished.append(session.session.id)
            new_sessions_next_up = []
            for next_session in sessions_next_up:
                new_sessions_next_up.append(next_session['id'])

            data={
                'booking_info': booking_info,
                'dinners': dinners,
                'courses': courses,
                'activities': activities,
                'seminers': seminars,
                'answer': answer,
                'training_activities': training_activities,
                'quesion_answer1': quesion_answer1,
                'quesion_answer2': quesion_answer2,
                'quesion_answer3': quesion_answer3,
                'sessions_finished': sessions_finished,
                'sessions_next_up': sessions_next_up,
                'time': datetime.datetime.now(),
                'notifications': notifications
            }
            request.session['event_user']['last_noty'] = new_noty
            request.session['event_user']['new_sessions_finished'] = new_sessions_finished
            request.session['event_user']['new_sessions_next_up'] = new_sessions_next_up
            request.session.modified = True

            return render(request, 'gt/common/summering.html',data)
        else:
            return redirect('gt-welcome')

    def mina_seminarier(request):
        return CommonMenu.checkAccess(request, 'gt/common/mina_seminarier.html')

    def information(request):
        return CommonMenu.checkAccess(request, 'gt/common/information.html')

    def get_together(request):
        return CommonMenu.checkAccess(request, 'gt/common/get_together.html')

    def hitta_hit(request):
        return CommonMenu.checkAccess(request, 'gt/common/hitta_hit.html')

    def ladda_ner(request):
        return CommonMenu.checkAccess(request, 'gt/common/ladda_ner.html')

    def gt_app(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                page_list = PageContent.objects.filter(url='ladda-ner-som-app', event_id=request.session['event_id'])
                if page_list.exists():
                    page = page_list[0]
                    if page.is_show:
                        if page.login_required:
                            if 'is_user_login' not in request.session:
                                return redirect('gt-welcome')
                            elif 'is_user_login' in request.session and request.session['is_user_login'] == False:
                                return redirect('gt-welcome')
                        pageContent = page.content
                        # pageContent = StaticPage.replace_questions(request, pageContent)
                        if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                            pageContent = pageContent.replace('{secret_key}', str(request.session['event_user']['secret_key']))
                        if page.template_id == 1:
                            content = pageContent.replace('[[static_alt]]', settings.STATIC_URL_ALT)
                            context = {
                                "content": content,
                                "static_page": page
                            }
                            return render(request, 'gt/static_pages/page.html', context)
                    else:
                        raise Http404
                else:
                    return redirect('gt-welcome')
            else:
                return redirect('gt-welcome')
        else:
            return redirect('gt-welcome')

    def gt_ff(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                page_list = PageContent.objects.filter(url='framgangsfaktorer', event_id=request.session['event_id'])
                if page_list.exists():
                    page = page_list[0]
                    if page.is_show:
                        if page.login_required:
                            if 'is_user_login' not in request.session:
                                return redirect('gt-welcome')
                            elif 'is_user_login' in request.session and request.session['is_user_login'] == False:
                                return redirect('gt-welcome')
                        pageContent = page.content
                        # pageContent = StaticPage.replace_questions(request, pageContent)
                        if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                            pageContent = pageContent.replace('{secret_key}', str(request.session['event_user']['secret_key']))
                        if page.template_id == 1:
                            content = pageContent.replace('[[static_alt]]', settings.STATIC_URL_ALT)
                            context = {
                                "content": content,
                                "static_page": page
                            }
                            return render(request, 'gt/static_pages/page.html', context)
                    else:
                        raise Http404
                else:
                    return redirect('gt-welcome')
            else:
                return redirect('gt-welcome')
        else:
            return redirect('gt-welcome')

    def gt_vfk(request):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                page_list = PageContent.objects.filter(url='varde-for-kunden', event_id=request.session['event_id'])
                if page_list.exists():
                    page = page_list[0]
                    if page.is_show:
                        if page.login_required:
                            if 'is_user_login' not in request.session:
                                return redirect('gt-welcome')
                            elif 'is_user_login' in request.session and request.session['is_user_login'] == False:
                                return redirect('gt-welcome')
                        pageContent = page.content
                        # pageContent = StaticPage.replace_questions(request, pageContent)
                        if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                            pageContent = pageContent.replace('{secret_key}', str(request.session['event_user']['secret_key']))
                        if page.template_id == 1:
                            content = pageContent.replace('[[static_alt]]', settings.STATIC_URL_ALT)
                            context = {
                                "content": content,
                                "static_page": page
                            }
                            return render(request, 'gt/static_pages/page.html', context)
                    else:
                        raise Http404
                else:
                    return redirect('gt-welcome')
            else:
                return redirect('gt-welcome')
        else:
            return redirect('gt-welcome')



    def checkAccess(request, path):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                return render(request, path)
            else:
                return redirect('gt-welcome')
        else:
            return redirect('gt-welcome')

    def get_finished_sessions(request, *args, **kwargs):
        user_id = request.session['event_user']['id']
        rated_sessions = SessionRating.objects.values('session_id').filter(attendee_id=user_id)
        # today = datetime.datetime.today() + datetime.timedelta(minutes=60)
        # today = timezone.now()
        time_now = CommonMenu.getTimezoneNow(request)
        f = '%Y-%m-%d %H:%M:%S'
        today = datetime.datetime.strptime(str(time_now).split(".")[0], f)

        current_time = today + datetime.timedelta(minutes=11)
        # sessions = SeminarsUsers.objects.filter(attendee_id=user_id, status='attending',
        #                                         session__end__lt=current_time, session__show_on_evaluation=1).exclude(
        #     session_id__in=rated_sessions)

        sql = "SELECT `seminars_has_users`.`id`, `seminars_has_users`.`attendee_id`, `seminars_has_users`.`session_id`, `seminars_has_users`.`status`, `seminars_has_users`.`created`, `seminars_has_users`.`queue_order` FROM `seminars_has_users` INNER JOIN `sessions` ON ( `seminars_has_users`.`session_id` = `sessions`.`id` ) WHERE (`sessions`.`end` < '" + str(
                current_time) + "' AND `seminars_has_users`.`attendee_id` =" + str(
                user_id) + " AND `sessions`.`show_on_evaluation` = True AND `seminars_has_users`.`status` = 'attending' AND NOT ((`seminars_has_users`.`session_id`) IN (SELECT U0.`session_id` FROM `session_ratings` U0 WHERE U0.`attendee_id` = " + str(
                user_id) + ")))"
        sessions = SeminarsUsers.objects.raw(
                sql
        )
        return list(sessions)

    def get_nextup_sessions(request, *args, **kwargs):
        user_id = request.session['event_user']['id']
        # now = datetime.datetime.now() + datetime.timedelta(minutes=60)
        # now = timezone.now()
        time_now = CommonMenu.getTimezoneNow(request);
        f = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.strptime(str(time_now).split(".")[0], f)
        # now = datetime.datetime.now()
        time_after_1hr = now + datetime.timedelta(minutes=60)
        time_before_15min = now - datetime.timedelta(minutes=15)
        time_after_1hr = datetime.datetime.strptime(str(time_after_1hr).split(".")[0], f)
        time_before_15min = datetime.datetime.strptime(str(time_before_15min).split(".")[0], f)
        sql = 'select DISTINCT sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                user_id) + ' and sessions.group_id = groups.id and sessions.show_on_next_up = True and groups.is_searchable = 1 and (sessions.start <= "' + str(
                time_after_1hr) + '" and sessions.start >="' + str(time_before_15min) + '")';
        sessions = Session.objects.raw(
                sql
        )
        response_data = []
        if len(list(sessions)) > 0:
            for session in sessions:
                id = session.id
                name = session.name
                group = session.group_id
                location = session.location.name
                location_id = session.location.id
                start = session.start
                end = session.end
                tags = SessionTags.objects.filter(session_id=session.id)
                taglist = []
                for tag in tags:
                    taglist.append(tag.tag.name)

                speakers = SeminarSpeakers.objects.filter(session_id=id)
                speakersData = []
                if speakers.count() > 0:
                    for speaker in speakers:
                        badge_firstname = Answers.objects.filter(question__actual_definition='firstname', user_id=speaker.speaker.id)
                        if badge_firstname.exists():
                            firstname = badge_firstname[0].value
                        else:
                            firstname = speaker.speaker.firstname

                        badge_lastname = Answers.objects.filter(question__actual_definition='lastname', user_id=speaker.speaker.id)
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
                session_start = datetime.datetime.strptime(str(session.start).split("+")[0], f)
                print(session_start)
                difference = (session_start - now).total_seconds()
                if difference > 0:
                    difference = difference / 60
                    difference = difference + 1
                else:
                    difference = 0

                session_obj = {
                    'id': id,
                    'title': name,
                    'resourceId': group,
                    'start': start,
                    'end': end,
                    'location': location,
                    'location_id': location_id,
                    'speakers': speakersData,
                    'taglist': taglist,
                    'difference': int(difference)

                }
                response_data.append(session_obj)
                # print(response_data)
        return response_data

    def session_notifications(request, *args, **kwargs):
        user_id = request.session['event_user']['id']
        notification = Notification.objects.filter(to_attendee_id=user_id, status=0)
        total_seconds = CommonMenu.get_timout(request.session['event_user']['event_id'])
        for nt in notification:

            first_name = Answers.objects.filter(question__actual_definition='firstname', user_id=nt.sender_attendee_id)
            last_name = Answers.objects.filter(question__actual_definition='lastname', user_id=nt.sender_attendee_id)
            if first_name.exists():
                nt.sender_attendee.firstname = first_name[0].value
            if last_name.exists():
                nt.sender_attendee.lastname = last_name[0].value

            nt.expire_at = nt.created_at + datetime.timedelta(seconds=total_seconds);
            nt.save();
        return notification

    def getTimezoneNow(request, *args, **kwargs):
        setting_timezone = Setting.objects.filter(name='timezone',event_id=request.session['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            now = datetime.datetime.now(timezone_active)
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.strptime(now,"%Y-%m-%d %H:%M:%S")
            # print(now.strftime('%Y-%m-%d_%H-%M-%S'))
            return now

    def get_timout(event_id):
        setting = Setting.objects.filter(name='notification_timeout',event_id=event_id)
        timeout = setting[0].value
        new_timeout = time.strptime(timeout, "%H:%M")
        total_seconds = timedelta(hours=new_timeout.tm_hour, minutes=new_timeout.tm_min, seconds=new_timeout.tm_sec).total_seconds()
        return total_seconds

    def set_session_ratings(request, *args, **kwargs):
        session_ratings = json.loads(request.POST.get('sessions_rating'))
        response_data = {}
        for session in session_ratings:
            rating_data = {
                'session_id': session['session_id'],
                'attendee_id': request.session['event_user']['id'],
                'rating': session['rating']
            }
            rating = SessionRating(**rating_data)
            rating.save()
        if str(request.session['event_id']) == str(10):
            response_data['success'] = "Din utvärdering är mottagen"
        else:
            response_data['success'] = "You successfully rated your sessions"
        return HttpResponse(json.dumps(response_data), content_type="application/json")
