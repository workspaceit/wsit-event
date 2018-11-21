from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
import json
from app.forms import session_form
from app.models import Session, Locations, Notification, SeminarSpeakers, Attendee, Group, GeneralTag, SessionTags, \
    GeneralTag, SeminarsUsers, Answers, SessionRating, Setting, VisibleColumns, Events, Checkpoint, RuleSet, \
    ActivityHistory, Questions, CurrentFilter, AttendeeTag, \
    AttendeeGroups, Travel, RoomAllotment, Room, Option, MessageContents, EmailContents, Scan, CustomClasses, \
    SessionClasses
from django.http import Http404

from app.views.gbhelper.editor_helper import EditorHelper
from app.views.room_view import RoomView
from app.views.gbhelper.error_report_helper import ErrorR
from .filter import FilterView
# import datetime
from .common_views import GroupView, EventView, CommonContext
from django.db.models import Max, Avg, Count
from publicfront.views.profile import SessionDetail, AttendeeProfile
from django.db.models import Q
import os
from .mail import MailHelper
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.views.gbhelper.language_helper import LanguageH

scheduler = BackgroundScheduler()
scheduler.add_jobstore('redis')
scheduler.start()
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

from django.db import transaction

from .export_lambda import ExcelView

from .general_view import General


class SessionView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'session_permission'):
            context = {}
            try:
                session_groups = GroupView.get_sessionGroup(request)
                filter_groups = GroupView.get_filterGroup(request)
                for group in filter_groups:
                    group.filters = RuleSet.objects.filter(group_id=group.id).exclude(name='quick-filter')

                travel_groups = GroupView.get_travelGroup(request)
                for group in travel_groups:
                    group.travels = Travel.objects.all().filter(group_id=group.id)

                for group in session_groups:
                    group.sessions = Session.objects.all().filter(group_id=group.id).order_by('session_order')
                    group.sessions = SessionView.get_session_reoprt(group.sessions)
                locationGroup = GroupView.get_locationGroup(request)
                for group in locationGroup:
                    group.locations = Locations.objects.all().filter(group_id=group.id)

                event_id = request.session['event_auth_user']['event_id']
                admin_id = request.session['event_auth_user']['id']
                visible_columns = VisibleColumns.objects.filter(event_id=event_id, admin_id=admin_id, type='session')
                columns = [0, 1, 12, 13]
                if visible_columns.exists():
                    if visible_columns[0].visible_columns:
                        columns = json.loads(visible_columns[0].visible_columns)
                        if 12 not in columns:
                            columns.append(12)
                        if 13 not in columns:
                            columns.append(13)
                else:
                    visibleColumns = VisibleColumns(event_id=event_id, admin_id=admin_id, visible_columns=columns,
                                                    type='session')
                    visibleColumns.save()
                event = Events.objects.filter(id=event_id)
                if event.exists():
                    event = event[0]

                hotel_group = GroupView.get_hotelGroup(request)
                for group in hotel_group:
                    group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
                    for room in group.rooms:
                        # room.vat = Group.objects.get(id=room.vat_id)
                        room_allotments = RoomView.find_booking(str(room.id))
                        date_allotments = []
                        for allotments in room_allotments['details']:
                            if allotments['occupancy'] < 100:
                                date_allotments.append(str(allotments['available_date']))
                        if len(date_allotments) > 0:
                            new_date = datetime.strptime(date_allotments[-1], "%Y-%m-%d") + timedelta(days=1)
                            new_allotments = str(new_date).split(' ')[0]
                            date_allotments.append(new_allotments)
                        room.allotment = json.dumps(date_allotments)

                questionGroup = GroupView.get_questionGroup(request)
                for group in questionGroup:
                    group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')

                quick_filter = RuleSet.objects.filter(name='quick-filter',
                                                      created_by_id=request.session['event_auth_user']['id'],
                                                      group__event_id=event_id)
                quick_filter_id = ''
                if quick_filter.exists():
                    quick_filter_id = quick_filter[0].id

                vat_objects = Group.objects.filter(type='payment', event_id=event_id)
                vats = [vat.name for vat in vat_objects]

                context = {
                    'hotel_groups': hotel_group,
                    'filter_groups': filter_groups,
                    'locationGroup': locationGroup,
                    'travel_groups': travel_groups,
                    'visible_columns': columns,
                    'questionGroup': questionGroup,
                    'columns': columns,
                    'quick_filter_id': quick_filter_id,
                    'event': event,
                    'now': datetime.now(),
                    'vats': vats
                }
                # print(context)
                filter_context = CommonContext.get_filter_context(request)
                context.update(filter_context)
                context['session_groups'] = session_groups
                editor_common_context = EditorHelper.get_editor_context(request, max_height=200)
                context.update(editor_common_context)
                context.update(LanguageH.get_current_and_all_presets(request))
            except Exception as e:
                ErrorR.efail(e)
            return render(request, 'seminar/seminar.html', context)

    def post(self, request):
        response = {}
        if EventView.check_permissions(request, 'session_permission'):
            try:
                event_id = request.session['event_auth_user']['event_id']
                user_id = request.session['event_auth_user']['id']
                form_data = {
                    "description": request.POST.get('description'),
                    "group_id": request.POST.get('group'),
                    "start": request.POST.get('start'),
                    "end": request.POST.get('end'),
                    "reg_between_start": request.POST.get('reg_between_start'),
                    "reg_between_end": request.POST.get('reg_between_end'),
                    "max_attendees": request.POST.get('max_attendees'),
                    "allow_attendees_queue": request.POST.get('allow_attendees_queue') == 'true',
                    "location_id": request.POST.get('location'),
                    "speakers": request.POST.get('speakers'),
                    "cost": request.POST.get('cost') if request.POST.get('cost') else 0,
                    "vat": request.POST.get('vat') if request.POST.get('vat') else None,
                }
                tags = request.POST.get('tags')
                custom_classes = request.POST.get('custom_classes')
                receive_answer = request.POST.get('receive_answer')
                form_data['receive_answer'] = False
                if receive_answer == '1':
                    form_data['receive_answer'] = True

                allow_attendees_queue = request.POST.get('allow_attendees_queue')
                form_data['allow_attendees_queue'] = False
                if allow_attendees_queue == '1':
                    form_data['allow_attendees_queue'] = True

                has_time = request.POST.get('hasTime')
                form_data['has_time'] = True
                if has_time == '0':
                    form_data['has_time'] = False

                not_show_evaluation = request.POST.get('not_show_evaluation')
                form_data['show_on_evaluation'] = True
                if not_show_evaluation == 'true':
                    form_data['show_on_evaluation'] = False

                not_show_next_up = request.POST.get('not_show_next_up')
                form_data['show_on_next_up'] = True
                if not_show_next_up == 'true':
                    form_data['show_on_next_up'] = False

                allow_overlapping = request.POST.get('allow_overlapping')
                form_data['allow_overlapping'] = False
                if allow_overlapping == 'true':
                    form_data['allow_overlapping'] = True

                allow_all_day = request.POST.get('allow_all_day')
                form_data['all_day'] = False
                if allow_all_day == 'true':
                    form_data['all_day'] = True
                if request.POST.get('max_attendees') == '':
                    form_data['max_attendees'] = 0
                current_language_id = LanguageH.get_current_language_id(event_id)
                default_language_id = current_language_id
                name_lang = request.POST.get('name_lang')
                description_lang = request.POST.get('description_lang')
                if 'id' in request.POST:
                    response = {}
                    session_id = request.POST.get('id')
                    session_old = Session.objects.get(id=session_id)
                    current_language_id = request.POST.get('current_language_id')
                    if current_language_id == default_language_id:
                        form_data["name"] = request.POST.get('name')
                    form_data = LanguageH.update_lang(current_language_id, form_data, "name_lang", name_lang,
                                                      session_old.name_lang)
                    form_data = LanguageH.update_lang(current_language_id, form_data, "description_lang",
                                                      description_lang, session_old.description_lang)
                    old_capacity = session_old.max_attendees
                    form = session_form.SessionForm(request.POST, instance=session_old)
                    if form.is_valid():
                        if request.POST.get('max_attendees') != '':
                            if old_capacity < int(request.POST.get('max_attendees')):
                                new_capacity = int(request.POST.get('max_attendees'))
                                increased_capacity = new_capacity - old_capacity
                                attendees_in_queue = SeminarsUsers.objects.filter(session_id=session_id,
                                                                                  status="in-queue")[
                                                     :increased_capacity]
                                for attendee_in_queue in attendees_in_queue:
                                    SessionDetail.notify_queue_user(request.session['event_auth_user']['event_id'],
                                                                    session_id, attendee_in_queue.attendee_id)
                        Session.objects.filter(id=session_id).update(**form_data)
                        SeminarSpeakers.objects.filter(session_id=session_id).delete()
                        speakers = request.POST['speakers'].split(',')
                        response['speakerError'] = []
                        if speakers[0] != '':
                            for speaker_id in speakers:
                                if SessionView.checkSessionClashing(speaker_id, session_old):
                                    shs = SeminarSpeakers(session_id=session_id, speaker_id=speaker_id)
                                    shs.save()
                                else:
                                    spk = Attendee.objects.filter(id=speaker_id)
                                    response['speakerError'].append([
                                        {'msg': "Speaker " + spk[0].firstname + " " + spk[
                                            0].lastname + " has time clash.",
                                         'spk': spk[0].as_dict(), 'session_id': session_id}])
                                    # speaker_form_data = {
                                    # "speaker_id" : speaker_id,
                                    #     "session_id" : session_id
                                    # }
                                    # speaker = SeminarSpeakers(**speaker_form_data)
                                    # speaker.save();
                        SessionTags.objects.filter(session_id=session_id).delete()
                        session_tags = tags.split(',')
                        for tag in session_tags:
                            tag_id = tag
                            if tag.strip() != "" and tag != None:
                                if not tag.isdigit():
                                    general_tag = GeneralTag(name=tag, category='session', event_id=event_id)
                                    general_tag.save()
                                    tag_id = general_tag.id
                                session_tag_form_data = {
                                    "session_id": session_id,
                                    "tag_id": tag_id
                                }
                                session_tag = SessionTags(**session_tag_form_data)
                                session_tag.save()
                        SessionClasses.objects.filter(session_id=session_id).delete()
                        session_custom_classes = custom_classes.split(',')
                        for custom_class in session_custom_classes:
                            custom_class_id = custom_class
                            if custom_class.strip() != "" and custom_class != None:
                                if not custom_class.isdigit():
                                    general_class = CustomClasses(classname=custom_class, created_by_id=user_id,
                                                                  event_id=event_id)
                                    general_class.save()
                                    custom_class_id = general_class.id
                                session_class_form_data = {
                                    "session_id": session_id,
                                    "classname_id": custom_class_id
                                }
                                session_class = SessionClasses(**session_class_form_data)
                                session_class.save()
                        session = Session.objects.get(id=session_id)
                        updated_session = SessionView.get_updated_session(session)
                        response['success'] = True
                        response['message'] = "Session Updated"
                        response['session'] = updated_session
                    else:
                        response['success'] = False
                        response['message'] = form.errors
                    return HttpResponse(json.dumps(response), content_type="application/json")
                else:
                    form_data["name"] = request.POST.get('name')
                    session_order = SessionView.get_sessions_order(request.POST.get('group'))
                    form_data["session_order"] = session_order
                    form_data = LanguageH.insert_lang(current_language_id, form_data, "name_lang", name_lang)
                    form_data = LanguageH.insert_lang(current_language_id, form_data, "description_lang",
                                                      description_lang)
                    response = {}
                    form = session_form.SessionForm(request.POST or None)
                    if form.is_valid():
                        session = Session(**form_data)
                        session.save()

                        # default session checkpoint add
                        # user_id=request.session['event_auth_user']['id']
                        # event_id=request.session['event_auth_user']['event_id']
                        checkpoint_data = {
                            'name': session.name,
                            'allow_re_entry': 0,
                            'is_hide': 0,
                            'session_id': session.id,
                            'created_by_id': user_id,
                            'event_id': event_id,
                        }
                        checkpoint = Checkpoint(**checkpoint_data)
                        checkpoint.save()

                        speakers = session.speakers.split(',')
                        # for speaker_id in speakers:
                        # speaker_form_data = {
                        #         "speaker_id" : speaker_id,
                        #         "session_id" : session.id
                        #     }
                        #     speaker = SeminarSpeakers(**speaker_form_data)
                        #     speaker.save();

                        # session.start=datetime.datetime.strptime(session.start,'%Y-%m-%d %H:%M:%S')
                        # session.end=datetime.datetime.strptime(session.end,'%Y-%m-%d %H:%M:%S')
                        ssn = Session.objects.get(pk=session.id)
                        response['speakerError'] = []
                        if speakers[0] != '':
                            for speaker_id in speakers:
                                if SessionView.checkSessionClashing(speaker_id, ssn):
                                    shs = SeminarSpeakers(session_id=session.id, speaker_id=speaker_id)
                                    shs.save()
                                else:
                                    spk = Attendee.objects.filter(id=speaker_id)
                                    response['speakerError'].append([
                                        {'msg': "Speaker " + spk[0].firstname + " " + spk[
                                            0].lastname + " has time clash.",
                                         'spk': spk[0].as_dict(), 'session_id': session.id}])

                        session_tags = tags.split(',')
                        for tag in session_tags:
                            if tag.strip() != "" and tag != None:
                                tag_id = tag
                                if not tag.isdigit():
                                    general_tag = GeneralTag(name=tag, category='session', event_id=event_id)
                                    general_tag.save()
                                    tag_id = general_tag.id
                                session_tag_form_data = {
                                    "session_id": session.id,
                                    "tag_id": tag_id
                                }
                                session_tag = SessionTags(**session_tag_form_data)
                                session_tag.save()
                        session_tags = tags.split(',')
                        for tag in session_tags:
                            if tag.strip() != "" and tag != None:
                                tag_id = tag
                                if not tag.isdigit():
                                    general_tag = GeneralTag(name=tag, category='session', event_id=event_id)
                                    general_tag.save()
                                    tag_id = general_tag.id
                                session_tag_form_data = {
                                    "session_id": session.id,
                                    "tag_id": tag_id
                                }
                                session_tag = SessionTags(**session_tag_form_data)
                                session_tag.save()
                        session_custom_classes = custom_classes.split(',')
                        for custom_class in session_custom_classes:
                            if custom_class.strip() != "" and custom_class != None:
                                custom_class_id = custom_class
                                if not custom_class.isdigit():
                                    general_class = CustomClasses(classname=custom_class, created_by_id=user_id,
                                                                  event_id=event_id)
                                    general_class.save()
                                    custom_class_id = general_class.id
                                session_class_form_data = {
                                    "session_id": session.id,
                                    "classname_id": custom_class_id
                                }
                                session_class = SessionClasses(**session_class_form_data)
                                session_class.save()
                        updated_session = SessionView.get_updated_session(session)
                        response['success'] = True
                        response['message'] = "Session Created"
                        response['session'] = updated_session
                    else:
                        response['success'] = False
                        response['message'] = form.errors
                    return HttpResponse(json.dumps(response), content_type="application/json")
            except Exception as e:
                ErrorR.efail(e)
                response['success'] = False
                response['message'] = "Someting went wrong"
                return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            response = {}
            response['error'] = 'You do not have Permission to do this'
            return HttpResponse(json.dumps(response), content_type="application/json")

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'session_permission'):
            id = request.POST.get('id')
            session = Session.objects.get(id=id)
            session.delete()
            response_data['success'] = 'Session Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def remove_queue(request):
        response_data = {}
        try:
            if EventView.check_permissions(request, 'session_permission'):
                seminar_user_id = request.POST.get('seminar_user_id')
                session_id = request.POST.get('session_id')
                if seminar_user_id == 'all':
                    all_seminar_users = SeminarsUsers.objects.filter(session_id=session_id, status="in-queue")
                    for user in all_seminar_users:
                        activity_history = ActivityHistory(attendee_id=user.attendee.id,
                                                           admin_id=request.session['event_auth_user']['id'],
                                                           activity_type='update', category='session',
                                                           session_id=user.session_id, old_value='In Queue',
                                                           new_value='Not Attending',
                                                           event_id=request.session['event_auth_user']['event_id'])
                        activity_history.save()
                    session = SeminarsUsers.objects.filter(session_id=session_id, status="in-queue").delete()
                    notifications = Notification.objects.filter(new_session_id=session_id, type="session",
                                                                status=0).update(
                        status=1)
                else:
                    seminar_user = SeminarsUsers.objects.get(id=seminar_user_id)
                    notifications = Notification.objects.filter(to_attendee_id=seminar_user.attendee_id,
                                                                new_session_id=session_id, type="session",
                                                                status=0).update(
                        status=1)
                    activity_history = ActivityHistory(attendee_id=seminar_user.attendee.id,
                                                       admin_id=request.session['event_auth_user']['id'],
                                                       activity_type='update', category='session',
                                                       session_id=seminar_user.session_id, old_value='In Queue',
                                                       new_value='Not Attending',
                                                       event_id=request.session['event_auth_user']['event_id'])
                    activity_history.save()
                    SeminarsUsers.objects.filter(id=seminar_user_id).delete()
                total_queue = SeminarsUsers.objects.filter(session_id=session_id, status="in-queue").count()
                response_data['total_queue'] = total_queue
                response_data['success'] = 'Queue Removed Successfully'
            else:
                response_data['error'] = 'You do not have Permission to do this'
        except Exception as e:
            response_data['error'] = 'Something went wrong'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_tags(request):
        response_data = {}
        val = request.POST.get('q')
        event_id = request.session['event_auth_user']['event_id']
        tags = GeneralTag.objects.values('name', 'id').filter(name__icontains=val, category='session',
                                                              event_id=event_id)
        my_data = []
        for tag in tags:
            arr_data = {
                'id': tag['id'],
                'text': tag['name']
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_custom_class(request):
        response_data = {}
        val = request.POST.get('q')
        event_id = request.session['event_auth_user']['event_id']
        custom_classes = CustomClasses.objects.values('classname', 'id').filter(classname__icontains=val,
                                                                                event_id=event_id)
        my_data = []
        for custom_class in custom_classes:
            arr_data = {
                'id': custom_class['id'],
                'text': custom_class['classname']
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def session_attending(request):
        session_id = request.POST.get('session_id')
        session = Session.objects.get(id=session_id)
        attendee_attending = SeminarsUsers.objects.filter(session_id=session_id, status='attending').order_by(
            'queue_order')
        visible_questions = SessionView.get_visible_questions(request)

        visible_columns_info = SessionView.get_visible_column_info(visible_questions)

        SessionView.get_all_attendee_visible_info(attendee_attending, visible_questions)

        context = {
            "attendee_attending": attendee_attending,
            "session": session,
            "visible_columns_info": visible_columns_info
        }

        return render(request, 'seminar/edit_seminar_attending.html', context)

    def get_visible_questions(request):
        questions = []
        order_columns = ['0', '111111', '222222', '333333', '444444', '555555', '666666']
        # order_columns = []
        question_groups = Group.objects.filter(type="question", is_show=1,
                                               event_id=request.session['event_auth_user']['event_id']).order_by(
            'group_order')
        for group in question_groups:
            questions_g = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
            for q_g in questions_g:
                questions.append(q_g)
        for question in questions:
            order_columns.append(question.id)

        visible = CurrentFilter.objects.filter(event_id=request.session['event_auth_user']['event_id'],
                                               admin_id=request.session['event_auth_user']['id'], table_type='attendee')
        if visible.exists():
            visible_columns = visible[0].visible_columns.replace('[', '(').replace(']', ')')
            visible_columns = list(eval(visible_columns))
            visible_columns = visible_columns[2:]

        visible_questions = [order_columns[x] for x in visible_columns]
        return visible_questions

    def get_visible_column_info(visible_questions):
        visible_columns_info = []

        for question in visible_questions:
            if question == '222222':
                visible_columns_info.append('Registration Date')
            elif question == '333333':
                visible_columns_info.append('Updated Date')
            elif question == '444444':
                visible_columns_info.append('UID(External)')
            elif question == '555555':
                visible_columns_info.append('Group')
            elif question == '666666':
                visible_columns_info.append('Tag')
            else:
                question_info = Questions.objects.get(id=question)
                title = question_info.title
                visible_columns_info.append(title)
        return visible_columns_info

    def get_all_attendee_visible_info(attendee_attending, visible_questions):

        for attendee in attendee_attending:
            question_answers = []
            for question in visible_questions:
                if question == '222222':
                    question_answers.append({
                        "title": 'Registration Date',
                        "answer": attendee.attendee.created,
                    })
                elif question == '333333':
                    question_answers.append({
                        "title": 'Updated Date',
                        "answer": attendee.attendee.updated,
                    })
                elif question == '444444':
                    question_answers.append({
                        "title": 'UID(External)',
                        "answer": attendee.attendee.secret_key,
                    })
                elif question == '555555':
                    attendeeGroup = AttendeeGroups.objects.filter(attendee_id=attendee.attendee_id)
                    groups = ""
                    for group in attendeeGroup:
                        groups += group.group.name + ", "
                    groups = groups[:-2]
                    question_answers.append({
                        "title": 'Group',
                        "answer": groups,
                    })
                elif question == '666666':
                    attendeeTag = AttendeeTag.objects.filter(attendee_id=attendee.attendee_id)
                    tags = ""
                    for tag in attendeeTag:
                        tags += tag.tag.name + ", "
                    tags = tags[:-2]
                    question_answers.append({
                        "title": 'Tag',
                        "answer": tags,
                    })
                else:
                    question_info = Questions.objects.get(id=question)
                    title = question_info.title
                    answer_value = Answers.objects.filter(question_id=question, user_id=attendee.attendee_id)
                    if answer_value.exists():
                        answer = answer_value[0].value
                        # print(answer[0].question.title+":"+answer[0].value)
                    else:
                        answer = "N/A"
                        # print(question_info.title+":"+"N/A")
                    question_answers.append({
                        "title": title,
                        "answer": answer,
                    })
            # print(question_answers)
            attendee.question_answers = question_answers

    def session_queue(request):
        session_id = request.POST.get('session_id')
        session = Session.objects.get(id=session_id)
        event_id = request.session['event_auth_user']['event_id']

        all_sessions = Session.objects.filter(group__event_id=event_id)

        attendee_queue = SeminarsUsers.objects.filter(session_id=session_id, status='in-queue').order_by('queue_order')

        visible_questions = SessionView.get_visible_questions(request)
        visible_columns_info = SessionView.get_visible_column_info(visible_questions)

        SessionView.get_all_attendee_visible_info(attendee_queue, visible_questions)

        # for user in attendee_queue:
        #     first_name = Answers.objects.filter(question_id=68, user_id=user.attendee_id)
        #     last_name = Answers.objects.filter(question_id=69, user_id=user.attendee_id)
        #     if first_name.exists():
        #         user.attendee.firstname = first_name[0].value
        #     if last_name.exists():
        #         user.attendee.lastname = last_name[0].value
        session_groups = GroupView.get_sessionGroup(request)
        for group in session_groups:
            group.sessions = Session.objects.all().filter(group_id=group.id).order_by('session_order')
            group.sessions = SessionView.get_session_reoprt(group.sessions)
        context = {
            "session_groups": session_groups,
            "attendee_queue": attendee_queue,
            "session": session,
            "visible_columns_info": visible_columns_info,
            "all_sessions": SessionView.get_session_reoprt(all_sessions)
        }
        return render(request, 'seminar/edit_seminar_queue.html', context)

    def session_checkpoint(request):
        session_id = request.POST.get('session_id')
        session = Session.objects.get(id=session_id)
        attendee_attending = Scan.objects.filter(checkpoint__session_id=session_id, status=1).order_by('-scan_time')
        visible_questions = SessionView.get_visible_questions(request)

        visible_columns_info = SessionView.get_visible_column_info(visible_questions)

        SessionView.get_all_attendee_visible_info(attendee_attending, visible_questions)

        context = {
            "attendee_attending": attendee_attending,
            "session": session,
            "visible_columns_info": visible_columns_info
        }

        return render(request, 'seminar/edit_seminar_checklist.html', context)

    def session_move_queue(request):
        session_id = request.POST.get('session_id')
        semninar_user_list = json.loads(request.POST.get('semninar_user_list'))
        errors = []
        msg = ""
        response_msg = ""
        update_count = 0
        session = Session.objects.filter(id=session_id).first()
        is_not_conflict = True
        for seminar_user_id in semninar_user_list:
            # test_session = General.testSession(seminar_user_id,session.id)
            seminar_user = SeminarsUsers.objects.filter(id=seminar_user_id).first()
            already_session_check = SeminarsUsers.objects.filter(session_id=session_id,
                                                                 attendee_id=seminar_user.attendee.id).exclude(
                status='not-attending').count()
            if already_session_check > 0:
                errors.append("Attendee " + seminar_user.attendee.firstname + " " + " already in session")
                continue
            session_attendees = SeminarsUsers.objects.filter(session_id=session_id, status='attending')
            if session_attendees.count() < session.max_attendees or session.max_attendees == 0:
                if session.allow_overlapping == 0:
                    is_not_conflict = SessionView.checkSessionClashing(seminar_user.attendee_id, session)
                if is_not_conflict == True:
                    SeminarsUsers.objects.filter(attendee_id=seminar_user.attendee.id, session_id=session_id).delete()
                    in_queue_activity_history = ActivityHistory(attendee_id=seminar_user.attendee_id,
                                                                admin_id=request.session['event_auth_user']['id'],
                                                                activity_type='update', category='session',
                                                                session_id=seminar_user.session_id,
                                                                old_value='In Queue', new_value='Not Attending',
                                                                event_id=request.session['event_auth_user']['event_id'])
                    in_queue_activity_history.save()
                    seminar_user.session_id = session_id
                    seminar_user.status = "attending"
                    seminar_user.save()
                    update_count += 1
                    # session1 = session.name
                    session1 = "{session_id:"+str(session.id)+"}"

                    # response_msg += "Session <strong>"+session1+"</strong> has been added to "+seminar_user.attendee.firstname+" "+seminar_user.attendee.lastname+" agenda."

                    if str(request.session['event_auth_user']['event_id']) == str(10):
                        msg = "Aktiviteten <strong>" + session1 + "</strong> har lagts till i din agenda."
                    else:
                        msg = "The session <strong>" + session1 + "</strong> has been added to your agenda."

                    notify = Notification(type="session_attend", message=msg, status=0,
                                          to_attendee_id=seminar_user.attendee.id)
                    notify.save()
                    activity_history = ActivityHistory(attendee_id=seminar_user.attendee.id,
                                                       admin_id=request.session['event_auth_user']['id'],
                                                       activity_type='update', category='session',
                                                       session_id=session_id, old_value='Not Answered',
                                                       new_value='Attending',
                                                       event_id=request.session['event_auth_user']['event_id'])
                    activity_history.save()

                    base_url = 'http://127.0.0.1:8000/'

                    context = {
                        'new_session': session,
                        'queue_attendee': seminar_user,
                        'base_url': base_url,
                    }
                    subject = "Bekräftelse - Kunskapsveckan och GetTogether"
                    sender_mail = "mahedi@workspaceit.com"
                    if seminar_user.attendee.event_id == 11:
                        subject = "NOTIFICATION - KINGFOMARKET"
                        sender_mail = "mahedi@workspaceit.com"
                    to = seminar_user.attendee.email
                    # MailHelper.mail_send('email/no_conflict_session.html',context,subject,to,sender_mail)
                else:
                    allAttSessions = SeminarsUsers.objects.filter(attendee_id=seminar_user.attendee_id,
                                                                  status='attending', session__allow_overlapping=0)

                    for sessionlist in allAttSessions:
                        if (sessionlist.session.start <= session.start < sessionlist.session.end) or (
                                sessionlist.session.start < session.end <= sessionlist.session.end) or (
                                session.start <= sessionlist.session.start < session.end) or (
                                session.start < sessionlist.session.end <= session.end):
                            clash_session = sessionlist.session_id

                    allSpeakerSessions = SeminarSpeakers.objects.filter(speaker_id=seminar_user.attendee_id)
                    for sessionlist in allSpeakerSessions:
                        if (sessionlist.session.start <= session.start < sessionlist.session.end) or (
                                sessionlist.session.start < session.end <= sessionlist.session.end) or (
                                session.start <= sessionlist.session.start < session.end) or (
                                session.start < sessionlist.session.end <= session.end):
                            clash_session = sessionlist.session_id

                    event_id = request.session['event_auth_user']['event_id']
                    clash = Session.objects.get(id=clash_session)
                    clash_session_id = clash.id
                    new_opened_session_id = session.id
                    # ur11 = reverse('public-session-detail', args=[session.id])
                    # ur12 = reverse('public-session-detail', args=[clash.id])
                    # session1 = "<a href='"+ur11+"'>"+ session.name+"</a>"
                    # session2 = "<a href='"+ur12+"'>"+ clash.name+"</a>"
                    # session1 = session.name
                    # session2 = clash.name

                    session1 = "{session_id:" + str(session.id) + "}"
                    session2 = "{session_id:" + str(clash.id) + "}"
                    if str(request.session['event_auth_user']['event_id']) == str(10):
                        msg = "En plats till <strong>" + session1 + "</strong> är ledig. vill du hellre delta på denna aktivitet än ditt tidigare val <strong>" + session2 + "</strong>?"
                    else:
                        msg = "A seat has opened up for <strong>" + session1 + "</strong> Would you rather go to this session than your previously booked session <strong>" + session2 + "</strong>?"
                    notification = Notification(type="session", message=msg, status=0,
                                                to_attendee_id=seminar_user.attendee_id,
                                                clash_session_id=clash_session_id, new_session_id=new_opened_session_id)
                    notification.save()
                    # scheduler.add_jobstore('redis', jobs_key=str(notification.id)+".jobs", run_times_key=str(notification.id)+".run_times")
                    total_seconds = AttendeeProfile.get_timout(event_id)
                    alarm_time = datetime.now() + timedelta(seconds=total_seconds)
                    # alarm_time = timezone.now() + timedelta(seconds=total_seconds)
                    scheduler.add_job(SessionDetail.activeSchedule, 'date', run_date=alarm_time,
                                      args=[event_id, notification.id], id=str(notification.id))
                    SeminarsUsers.objects.filter(attendee_id=seminar_user.attendee_id, session_id=session.id).delete()
                    active_deciding = SeminarsUsers(attendee_id=seminar_user.attendee_id, session_id=session.id,
                                                    status='deciding')
                    active_deciding.save()
                    # session_data = DjangoSession.objects.all().first()
                    #
                    # session_info = session_data.get_decoded()
                    #
                    # event_id = session_info['event_user']['event_id']
                    activity = ActivityHistory(activity_type="update", category="session",
                                               attendee_id=seminar_user.attendee_id, session_id=session.id,
                                               old_value="In Queue", new_value="Deciding", event_id=event_id)
                    activity.save()
                    setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
                    notification_timeout = '01:00'
                    if setting.exists:
                        notification_timeout = setting[0].value
                    base_url = 'http://127.0.0.1:8000/'
                    context = {
                        'new_session': session,
                        'clash_session': clash,
                        'queue_attendee': active_deciding,
                        'notification_timeout': notification_timeout,
                        'base_url': base_url,
                    }
                    subject = "Bekräftelse - Kunskapsveckan och GetTogether"
                    sender_mail = "mahedi@workspaceit.com"
                    if active_deciding.attendee.event_id == 11:
                        subject = "NOTIFICATION - KINGFOMARKET"
                        sender_mail = "mahedi@workspaceit.com"
                    to = active_deciding.attendee.email
                    # MailHelper.mail_send('email/conflict_session.html',context,subject,to,sender_mail)

                    errors.append(
                        "Conflict for attendee " + seminar_user.attendee.firstname + " " + seminar_user.attendee.lastname)
            else:
                if update_count < 1:
                    errors.append("Session full")
                else:
                    msg = "Session full after " + str(update_count) + " attendees. "
                break
        response_data = {}
        if errors:
            response_data['errors'] = errors
        else:
            # response_data['success'] = msg
            response_data['success'] = "Successfully moved queue."
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def session_deciding(request):
        session_id = request.POST.get('session_id')
        session = Session.objects.get(id=session_id)
        attendee_deciding = SeminarsUsers.objects.filter(session_id=session_id, status='deciding').order_by(
            'queue_order')

        visible_questions = SessionView.get_visible_questions(request)
        visible_columns_info = SessionView.get_visible_column_info(visible_questions)

        SessionView.get_all_attendee_visible_info(attendee_deciding, visible_questions)

        for user in attendee_deciding:
            session_timeout = Setting.objects.filter(name='notification_timeout',
                                                     event_id=request.session['event_auth_user']['event_id'])
            timeout = '0:05'
            if session_timeout.exists:
                timeout = session_timeout[0].value
            times = timeout.split(':')
            minutes = int(times[0]) * 60 + int(times[1])
            end_time = user.created + timedelta(minutes=minutes)
            difference = end_time - datetime.now()
            s = difference.total_seconds()
            # hours
            hours = s // 3600
            # remaining seconds
            s = s - (hours * 3600)
            # minutes
            minutes = s // 60
            # remaining seconds
            seconds = s - (minutes * 60)
            user.hours = int(hours)
            user.minutes = int(minutes)
        context = {
            "attendee_deciding": attendee_deciding,
            "visible_columns_info": visible_columns_info,
            "session": session
        }
        return render(request, 'seminar/edit_seminar_deciding.html', context)

    def queue_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'session_permission'):
            queue_order = json.loads(request.POST.get('queue_order'))
            session_id = request.POST.get('session_id')
            for queue in queue_order:
                SeminarsUsers.objects.filter(id=queue['seminar_id']).update(queue_order=queue['order'])
            response_data['success'] = 'Session Queue Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def importSession(request):
        ErrorR.ex_time_init()
        response_data = []
        SessionView.handle_uploaded_file(request.FILES.get('upload_file'))
        user_id = request.session['event_auth_user']['id']
        event_id = request.session['event_auth_user']['event_id']
        current_language_id = LanguageH.get_current_language_id(event_id)

        from openpyxl import load_workbook

        wb = load_workbook(filename='sessionList/sample_import.xlsx', read_only=True)
        ws = wb['Sheet']  # ws is now an IterableWorksheet

        allHeaders = []

        import re, string;
        pattern = re.compile('[\W_]+')
        header = {}
        pick_header = False
        row_data = {}
        for ridx, row in enumerate(ws.rows):
            error_flag = False
            session = []
            error_message = []
            if not pick_header:
                for index, col in enumerate(row):
                    header[index] = pattern.sub('', col.value).lower()
                pick_header = True
                print(header)
                continue

            name = ''
            try:
                row_data[ridx] = {}
                # ROW assignment
                for index, col in enumerate(row):
                    row_data[ridx][header[index]] = col.value

                print(row_data[ridx])
                name = row_data[ridx]['sessionname']  # TODO

                seminar_group = row_data[ridx]['seminargroup']  # TODO

                start_date = str(row_data[ridx]['startdate'])  # TODO
                start_time = start_date + " " + str(row_data[ridx]['starttime'])  # TODO
                end_date = str(row_data[ridx]['enddate'])  # TODO
                end_time = end_date + " " + str(row_data[ridx]['endtime'])  # TODO
                registration_open = str(row_data[ridx]['registrationopeningday'])  # TODO
                registration_end = str(row_data[ridx]['registrationendingday'])  # TODO

                location_col = row_data[ridx]['location']  # TODO
                speaker_col = row_data[ridx]['speaker']  # TODO

                cost = row_data[ridx]['cost']
                vat = row_data[ridx]['vat']
                # name
                session_name_existance = Session.objects.filter(name=name, group__event_id=event_id)
                if name is None:
                    error_flag = True
                    error_message.append("Name can't be empty")
                elif session_name_existance:
                    error_flag = True
                    error_message.append("Session name exists")

                # description
                description = ""
                if 'description' in row_data[ridx]:
                    if len(description.strip()) > 0:
                        description = row_data[ridx]['description']
                    # if description is None:
                    #     error_flag = True
                    #     error_message.append("Description can't be empty")
                    # elif len(description.strip()) == 0:
                    #     error_flag = True
                    #     error_message.append("Description can't be empty")

                # seminar group
                if seminar_group is None:
                    error_flag = True
                    error_message.append("Seminar group can't be empty")
                elif len(seminar_group.strip()) == 0:
                    error_flag = True
                    error_message.append("Seminar group can't be empty")

                # all day
                # without column
                all_day = 0
                if 'allday' in row_data[ridx]:
                    allday = row_data[ridx]['allday']
                    if allday is None:
                        all_day = 0
                    elif str(allday).strip().lower() == 'yes':
                        all_day = 1
                    else:
                        all_day = 0

                # start time
                if all_day == 0 and start_time is None:
                    error_flag = True
                    error_message.append("Seminar group can't be empty")

                # end time
                if all_day == 0 and end_time is None:
                    error_flag = True
                    error_message.append("Seminar group can't be empty")

                if SessionView.validate_dateTime(start_time) == 0:
                    error_flag = True
                    error_message.append("Date-time validation for Start Date-time. Given =" + str(start_time))

                if SessionView.validate_dateTime(end_time) == 0:
                    error_flag = True
                    error_message.append("Date-time validation for End Date-time. Given =" + str(end_time))

                if SessionView.validate_date(registration_open) == 0:
                    error_flag = True
                    error_message.append(
                        "Date-time validation for Registration opening time. Given =" + str(registration_open))

                if SessionView.validate_date(registration_end) == 0:
                    error_flag = True
                    error_message.append(
                        "Date-time validation for Registration Ending time. Given =" + str(registration_end))

                max_att = 0
                if 'max' in row_data[ridx]:
                    max_att = row_data[ridx]['max']
                    if max_att is None:
                        max_att = 0
                    else:
                        if not isinstance(max_att, int):
                            error_flag = True
                            error_message.append("Max attendee wrongly set")

                # without column
                att_q = 0
                if 'allowattendeestoqueue' in row_data[ridx]:
                    allowattendeestoqueue_col = row_data[ridx]['allowattendeestoqueue']
                    if str(allowattendeestoqueue_col).lower == 'yes':
                        att_q = 1
                    else:
                        att_q = 0

                location = Locations.objects.filter(name=location_col, group__event_id=event_id)
                if (location.exists()):
                    loc_id = location[0].id
                else:
                    error_flag = True
                    error_message.append("Location not found")

                speakers = []
                speakers_str = ""
                speakersArr = []
                if isinstance(speaker_col, str):
                    speakersArr = [x.strip() for x in speaker_col.split(',')]
                elif isinstance(speaker_col, int):
                    speakersArr = [speaker_col]
                # else:
                #     # error_flag = True
                #     error_message.append("Speaker is not in correct format")

                for spk in speakersArr:
                    atts = Attendee.objects.filter(email=spk.strip(), event_id=event_id)
                    if atts.exists():
                        for att in atts:
                            speakers.extend(att)
                            speakers_str += str(att.id) + ","
                    else:
                        # error_flag = True
                        error_message.append(" Speaker " + str(spk) + " not found")
                if len(speakers_str) > 0:
                    speakers_str = speakers_str[:-1]

                # without column
                tags = []
                if 'tags' in row_data[ridx]:
                    tags_col = row_data[ridx]['tags']
                    if isinstance(tags_col, str):
                        tags = [x.strip() for x in tags_col.split(',')]
                    elif isinstance(tags_col, int):
                        tags = [tags_col]

                # without column
                evaluation = True
                if 'showonevaluation' in row_data[ridx]:
                    showonevaluation = row_data[ridx]['showonevaluation']
                    if str(showonevaluation).strip().lower() == "yes":
                        evaluation = True
                    else:
                        evaluation = False

                # Attendee Can Choose Not to Participate
                # without column
                recieve_answer = False
                if 'attendeecanchoosenottoparticipate' in row_data[ridx]:
                    attendeecanchoosenottoparticipate = row_data[ridx]['attendeecanchoosenottoparticipate']
                    if str(attendeecanchoosenottoparticipate).strip().lower() == "yes":
                        recieve_answer = True

                # without column
                allow_overlapping = False
                if 'allowoverlappingsessions' in row_data[ridx]:
                    allowoverlappingsessions = row_data[ridx]['allowoverlappingsessions']
                    if str(allowoverlappingsessions).strip().lower() == "yes":
                        allow_overlapping = True

                # without column
                custom_classes = []
                if 'customclasses' in row_data[ridx]:
                    customclasses = row_data[ridx]['customclasses']
                    if isinstance(customclasses, str):
                        custom_classes = [x.strip() for x in customclasses.split(',')]
                    elif isinstance(customclasses, int):
                        custom_classes = [customclasses]

                if cost is None:
                    cost = 0
                else:
                    if not (isinstance(cost, int) or isinstance(cost, float)):
                        error_flag = True
                        error_message.append("Cost wrongly set")

                if vat is None:
                    if cost != 0:
                        error_flag = True
                        error_message.append("VAT is not set when Cost is present")
                else:
                    if Group.objects.filter(type="payment",event_id=event_id,name=str(vat).strip()).exists():
                        error_flag = True
                        error_message.append("VAT not exists")
                    elif not (isinstance(vat, int) or isinstance(vat, float)):
                        error_flag = True
                        error_message.append("VAT wrongly set")
                default_answer='attending'
                if 'defaultstatus' in row_data[ridx]:
                    if row_data[ridx]['defaultstatus'] in ['attending','in-queue','not-attending','deciding']:
                        default_answer =row_data[ridx]['defaultstatus']

                default_answer_status='leave'
                if 'defaultresetaction' in row_data[ridx]:
                    if row_data[ridx]['defaultresetaction'] in ['set','leave','empty']:
                        default_answer_status =row_data[ridx]['defaultresetaction']

                if error_flag == True:
                    response_data.append({'sessionName': name, 'error': error_message})
                    continue

                with transaction.atomic():

                    givenGroup = Group.objects.filter(name__icontains=seminar_group.strip(), event_id=event_id)
                    if givenGroup.exists():
                        group_id = givenGroup[0].id
                    else:
                        max_group_order = Group.objects.filter(type='session', event_id=event_id).aggregate(
                            Max('group_order'))
                        # print(max_group_order['group_order__max'])
                        group_lang = seminar_group.replace('"', "&quot;").replace("'", "&apos;")
                        seminar_group_lang = str({current_language_id: group_lang}).replace("'", '"')
                        givenGroup = Group(name=seminar_group, name_lang=seminar_group_lang, type='session',
                                           group_order=(max_group_order['group_order__max'] + 1),
                                           event_id=event_id, is_show=1)
                        # print(givenGroup)
                        givenGroup.save()
                        group_id = givenGroup.id

                    fdt = '%Y-%m-%d %H:%M:%S'
                    fd = '%Y-%m-%d %H:%M:%S'
                    session_n_lang = name.replace('"', "&quot;").replace("'", "&apos;")
                    session_d_lang = description.replace('"', "&quot;").replace("'", "&apos;")
                    seminar_name_lang = str({current_language_id: session_n_lang}).replace("'", '"')
                    seminar_description_lang = str({current_language_id: session_d_lang}).replace("'", '"')
                    form_data = {
                        "name": name,
                        "description": description,
                        "name_lang": seminar_name_lang,
                        "description_lang": seminar_description_lang,
                        "group_id": group_id,
                        "all_day": all_day,
                        "start": datetime.strptime(start_time.split(".")[0], fdt),
                        "end": datetime.strptime(end_time.split(".")[0], fdt),
                        "reg_between_start": datetime.strptime(registration_open, fd),
                        "reg_between_end": datetime.strptime(registration_end, fd),
                        "max_attendees": max_att,
                        "allow_attendees_queue": att_q,
                        "location_id": loc_id,
                        "has_time": 1,
                        "session_order": SessionView.get_sessions_order(group_id),
                        "show_on_evaluation": evaluation,
                        "allow_overlapping": allow_overlapping,
                        "receive_answer": recieve_answer,
                        "speakers": speakers_str,
                        "cost": cost,
                        "vat": vat,
                        "default_answer": default_answer,
                        "default_answer_status": default_answer_status
                    }

                    ErrorR.c_bipurple(form_data)

                    session = Session(**form_data)

                    session.save()

                    checkpoint_data = {
                        'name': session.name,
                        'allow_re_entry': 0,
                        'is_hide': 0,
                        'session_id': session.id,
                        'created_by_id': user_id,
                        'event_id': event_id,
                    }
                    checkpoint = Checkpoint(**checkpoint_data)
                    checkpoint.save()

                    speakersErr = []
                    all_speakers = []
                    for spk in speakers:
                        shs = SeminarSpeakers.objects.filter(session_id=session.id, speaker_id=spk.id)
                        if not shs.exists():
                            if SessionView.checkSessionClashing(spk.id, session):
                                all_speakers.append(SeminarSpeakers(session_id=session.id, speaker_id=spk.id))
                            else:
                                speakersErr.append("Speaker " + spk.firstname + " " + spk.lastname + " has time clash.")

                    all_tags = []
                    for tag in tags:
                        currentTag = GeneralTag.objects.filter(name=tag, event_id=event_id)
                        if currentTag.exists():
                            sessionTag = SessionTags.objects.filter(session_id=session.id, tag_id=currentTag[0].id)
                            if not sessionTag.exists():
                                all_tags.append(SessionTags(session_id=session.id, tag_id=currentTag[0].id))
                        else:
                            newTag = GeneralTag(name=tag, event_id=event_id)
                            newTag.save()
                            all_tags.append(SessionTags(session_id=session.id, tag_id=newTag.id))

                    all_classes = []
                    for class_name in custom_classes:
                        currentClasses = CustomClasses.objects.filter(classname=class_name, event_id=event_id)
                        if currentClasses.exists():
                            sessionClass = SessionClasses.objects.filter(session_id=session.id,
                                                                         classname_id=currentClasses[0].id)
                            if not sessionClass.exists():
                                all_classes.append(
                                    SessionClasses(session_id=session.id, classname_id=currentClasses[0].id))
                                # shc.save()
                        else:
                            newClass = CustomClasses(classname=class_name, created_by_id=user_id, event_id=event_id)
                            newClass.save()
                            all_classes.append(SessionClasses(session_id=session.id, classname_id=newClass.id))
                            # shc.save()
                    SeminarSpeakers.objects.bulk_create(all_speakers)
                    SessionTags.objects.bulk_create(all_tags)
                    SessionClasses.objects.bulk_create(all_classes)
                    response_data.append(
                        {'sessionName': name, 'success': "Successfully added session", 'error': error_message})

            except Exception as e:
                ErrorR.efail(e)
                response_data.append({'sessionName': name, 'error': ["Exception happens for " + name + str(e)]})

        context = {
            'results': response_data
        }
        ErrorR.ex_time()
        return render(request, 'dashboard/session_import_result.html', context)

        # return HttpResponse(json.dumps(response_data), content_type="application/json")

    def checkSessionClashing(attendee_id, session):
        allAttSessions = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                      session__allow_overlapping=0)

        for sessionlist in allAttSessions:
            if (sessionlist.session.start <= session.start < sessionlist.session.end) or (
                    sessionlist.session.start < session.end <= sessionlist.session.end) or (
                    session.start <= sessionlist.session.start < session.end) or (
                    session.start < sessionlist.session.end <= session.end):
                return False

        allSpeakerSessions = SeminarSpeakers.objects.filter(speaker_id=attendee_id)
        for sessionlist in allSpeakerSessions:
            if (sessionlist.session.start <= session.start < sessionlist.session.end) or (
                    sessionlist.session.start < session.end <= sessionlist.session.end) or (
                    session.start <= sessionlist.session.start < session.end) or (
                    session.start < sessionlist.session.end <= session.end):
                return False

        return True

    def addSpeakerFourcefullyToSession(request):
        if request.is_ajax():
            try:
                attendee_id = request.POST.get('attendee_id')
                session_id = request.POST.get('session_id')
                session = Session.objects.get(id=session_id)
                allAttSessions = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending')

                for sessionlist in allAttSessions:
                    if (sessionlist.session.start <= session.start < sessionlist.session.end) or (
                            sessionlist.session.start < session.end <= sessionlist.session.end):
                        print(sessionlist)
                        sessionlist.status = 'not-attending'
                        sessionlist.save()

                allSpeakerSessions = SeminarSpeakers.objects.filter(speaker_id=attendee_id)
                for sessionlist in allSpeakerSessions:
                    if (sessionlist.session.start <= session.start < sessionlist.session.end) or (
                            sessionlist.session.start < session.end <= sessionlist.session.end):
                        sessionlist.delete()

                shs = SeminarSpeakers(session_id=session_id, speaker_id=attendee_id)
                shs.save()
                return HttpResponse(json.dumps({'success': 'Success!!!'}))

            except Exception as e:
                return HttpResponse(json.dumps({'error': 'Something ERROR!!!' + str(e)}))

        else:
            return HttpResponse(json.dumps({'error': 'Method Not allowed!!'}))

    def handle_uploaded_file(f):
        import os

        if not os.path.exists("sessionList/"):
            os.makedirs("sessionList/")
        filepath = 'sessionList/'
        filename = "sample_import.xlsx"
        with open(filepath + filename, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def validate_date(value):
        try:
            f = '%Y-%m-%d %H:%M:%S'
            datetime.strptime(value, f)
            return 1
        except Exception as e:
            print(str(e))
            return 0

    def validate_dateTime(value):
        try:
            f = '%Y-%m-%d %H:%M:%S'
            datetime.strptime(value.split(".")[0], f)
            return 1
        except Exception as e:
            print(str(e))
            return 0

    def session_search(request):
        search_key = request.POST.get('search_key')
        all_sessions_groups = []

        if search_key:
            sessions_group = Group.objects.filter(
                Q(type="session", is_show=1, event_id=request.session['event_auth_user']['event_id']) & (
                    Q(session__name__icontains=search_key))).order_by('group_order').distinct()
        else:
            sessions_group = Group.objects.filter(
                Q(type="session", is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by(
                'group_order').distinct()

        for group in sessions_group:
            group.session = Session.objects.filter(Q(group_id=group.id) & (Q(name__icontains=search_key))).order_by(
                'session_order')
            group.session = SessionView.get_session_reoprt(group.session)
            group_dict = dict(
                id=group.id,
                name=group.name,
                session=group.session
            )
            all_sessions_groups.append(group_dict)

        data = {
            'session_groups': all_sessions_groups
        }
        return render(request, 'seminar/seminar_result.html', data)

    def session_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        if EventView.check_permissions(request, 'session_permission'):
            session_id = request.POST.get('session_id')
            session = Session.objects.get(id=session_id)

            duplicate_existance = Session.objects.filter(name=session.name + '[Copy]', group__event_id=event_id)
            if duplicate_existance.exists():
                response_data['error'] = 'This session is already make a duplicate.'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            session.pk = None
            session.name += '[Copy]'
            session.save()

            user_id = request.session['event_auth_user']['id']
            event_id = request.session['event_auth_user']['event_id']
            checkpoint_data = {
                'name': session.name,
                'allow_re_entry': 0,
                'is_hide': 0,
                'session_id': session.id,
                'created_by_id': user_id,
                'event_id': event_id,
            }
            checkpoint = Checkpoint(**checkpoint_data)
            checkpoint.save()

            updated_session = SessionView.get_updated_session(session)
            response_data['success'] = "Create duplicate session Successfully"
            response_data['session'] = updated_session
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def get_updated_session(session):
        updated_session = session.as_dict()
        updated_session['in_queue'] = SeminarsUsers.objects.filter(session_id=session.id, status='in-queue').count()
        updated_session['attending'] = SeminarsUsers.objects.filter(session_id=session.id, status='attending').count()
        updated_session['not_attending'] = SeminarsUsers.objects.filter(session_id=session.id,
                                                                        status='not-attending').count()
        updated_session['pending'] = SeminarsUsers.objects.filter(session_id=session.id, status='deciding').count()
        if int(updated_session['max_attendees']) != 0:
            percentage = (int(updated_session['attending']) / int(updated_session['max_attendees'])) * 100
            percentage = round(percentage, 1)
            updated_session['percentage'] = str(percentage) + "%"
        else:
            updated_session['percentage'] = str(0.0) + "%"
        evaluations = SessionRating.objects.filter(session_id=session.id)
        rating = 0
        for evaluation in evaluations:
            rating += evaluation.rating
        if rating != 0:
            updated_session['no_of_attendees_evaluating'] = evaluations.count()
            average_rating = rating / updated_session['no_of_attendees_evaluating']
            updated_session['average_rating'] = round(average_rating, 2)
        return updated_session

    def session_conflick(request):
        session_id = request.POST.get('session_id')
        session = Session.objects.get(id=session_id)
        session_users = SeminarsUsers.objects.filter(session_id=session_id).exclude(status='not-attending')
        number_of_attending_user_has_clash = 0
        number_of_queue_user_has_clash = 0
        for attende in session_users:
            attende_id = attende.attendee_id
            if attende.status == "attending":
                sessions_of_queue_attende = SeminarsUsers.objects.filter(attendee_id=attende_id, status='attending',
                                                                         session__allow_overlapping=0)
                Inbetween = 0

                for sessionlist in sessions_of_queue_attende:
                    if sessionlist.session.start <= session.start < sessionlist.session.end:
                        Inbetween = 1
                        break
                    elif sessionlist.session.start < session.end <= sessionlist.session.end:
                        Inbetween = 1
                        break
                if Inbetween == 1:
                    number_of_attending_user_has_clash += 1
            elif attende.status == "in-queue":
                sessions_of_queue_attende = SeminarsUsers.objects.filter(attendee_id=attende_id, status='attending',
                                                                         session__allow_overlapping=0)
                Inbetween = 0

                for sessionlist in sessions_of_queue_attende:
                    if sessionlist.session.start <= session.start < sessionlist.session.end:
                        Inbetween = 1
                        break
                    elif sessionlist.session.start < session.end <= sessionlist.session.end:
                        Inbetween = 1
                        break
                if Inbetween == 1:
                    number_of_queue_user_has_clash += 1

        response_data = {
            'success': True,
            'number_of_attending_user_has_clash': number_of_attending_user_has_clash,
            'number_of_queue_user_has_clash': number_of_queue_user_has_clash

        }

        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def session_remove_conflict(request):
        session_id = request.POST.get('session_id')
        session = Session.objects.get(id=session_id)
        session_users = SeminarsUsers.objects.filter(session_id=session_id).exclude(status='not-attending')
        number_of_attending_user_has_clash = 0
        number_of_queue_user_has_clash = 0
        for attende in session_users:
            attende_id = attende.attendee_id
            if attende.status == "attending":
                sessions_of_queue_attende = SeminarsUsers.objects.filter(attendee_id=attende_id, status='attending',
                                                                         session__allow_overlapping=0)
                Inbetween = 0

                for sessionlist in sessions_of_queue_attende:
                    if sessionlist.session.start <= session.start < sessionlist.session.end:
                        Inbetween = 1
                        break
                    elif sessionlist.session.start < session.end <= sessionlist.session.end:
                        Inbetween = 1
                        break
                if Inbetween == 1:
                    number_of_attending_user_has_clash += 1
                    SeminarsUsers.objects.filter(attendee_id=attende_id, session_id=session_id).delete()
                    seminar_attendee = SeminarsUsers(attendee_id=attende_id, session_id=session_id,
                                                     status='not-attending')
                    seminar_attendee.save()
            elif attende.status == "in-queue":
                sessions_of_queue_attende = SeminarsUsers.objects.filter(attendee_id=attende_id, status='attending',
                                                                         session__allow_overlapping=0)
                Inbetween = 0

                for sessionlist in sessions_of_queue_attende:
                    if sessionlist.session.start <= session.start < sessionlist.session.end:
                        Inbetween = 1
                        break
                    elif sessionlist.session.start < session.end <= sessionlist.session.end:
                        Inbetween = 1
                        break
                if Inbetween == 1:
                    number_of_queue_user_has_clash += 1
                    SeminarsUsers.objects.filter(attendee_id=attende_id, session_id=session_id).delete()
                    seminar_attendee = SeminarsUsers(attendee_id=attende_id, session_id=session_id,
                                                     status='not-attending')
                    seminar_attendee.save()

        queue_user_getting_chance = SeminarsUsers.objects.filter(session_id=session_id, status="in-queue").order_by(
            'queue_order')[:number_of_attending_user_has_clash]
        for user in queue_user_getting_chance:
            SeminarsUsers.objects.filter(id=user.id).update(status="attending")

        response_data = {
            'success': True,

        }

        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def set_sessions_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'session_permission'):
            sessions_order = json.loads(request.POST.get('sessions_order'))
            for session in sessions_order:
                Session.objects.filter(id=session['session_id']).update(session_order=session['order'])
            response_data['success'] = 'Sessions Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_sessions_order(group_id):
        session = Session.objects.values('session_order').filter(group_id=group_id).aggregate(Max('session_order'))
        if session['session_order__max']:
            session_order = session['session_order__max'] + 1
        else:
            session_order = 1
        return session_order

    def generate_session_report_excel(request):
        event_id = request.session['event_auth_user']['event_id']
        # sessions = Session.objects.filter(group__event_id=event_id)
        sessions = Session.objects.filter(group__event_id=event_id).order_by('group__group_order', 'session_order')
        sessions_info = SessionView.get_session_reoprt(sessions)
        headers = ["Session Id", "Group", "Name", "Attending", "Max", "Percentage", "In Queue", "Pending",
                   "Not Attending", "Average Rating", "Rating Recieved",
                   'Description', 'All Day', 'Start Date-time', 'End Date-time', 'Registration Opening Day',
                   'Registration Ending Day',
                   'Max Attendees', 'Allow Attendees to Queue', 'Location', 'Speaker', 'Tags', 'Show on Evaluation',
                   'Attendee Can Choose Not to Participate',
                   'Allow Overlapping Sessions', 'Custom Classes', 'Cost', 'Vat', 'Default Status',
                   'Default Reset Action']

        session_rows = [headers]
        for session in sessions_info:
            each_row = []
            each_row.extend([session.id, session.group_name, session.name, session.attending, session.max_attendees,
                             session.percentage, session.in_queue, session.pending, session.not_attending,
                             session.average_rating, session.no_of_attendees_evaluating])
            each_row.extend([session.description, 'Yes' if session.all_day else 'No', session.start, session.end,
                             session.reg_between_start, session.reg_between_end])
            each_row.extend([session.max_attendees, 'Yes' if session.allow_attendees_queue else 'No',
                             session.location.name, SessionView.get_session_speakers(session.id),
                             SessionView.get_session_tags(session.id)])
            each_row.extend(['Yes' if session.show_on_evaluation else 'No',
                             'Yes' if session.receive_answer else 'No',
                             'Yes' if session.allow_overlapping else 'No'])
            each_row.extend(
                [SessionView.get_session_classes(session.id), session.cost, session.vat if session.vat else ''])
            each_row.extend([session.default_answer, session.default_answer_status])
            session_rows.append(each_row)

        return ExcelView.write_excel(session_rows, "Session report.xlsx")

    def get_session_speakers(sid):
        speakers = ""
        session_speakers = SeminarSpeakers.objects.filter(session_id=sid)
        for speaker in session_speakers:
            speakers += speaker.speaker.email + ", "
        if len(speakers) > 0:
            speakers = speakers[:-2]
        return speakers

    def get_session_tags(sid):
        tags = ""
        session_tag = SessionTags.objects.filter(session_id=sid)
        for tag in session_tag:
            tags += tag.tag.name + ", "
        if len(tags) > 0:
            tags = tags[:-2]
        return tags

    def get_session_classes(sid):
        classes = ""
        session_classes = SessionClasses.objects.filter(session_id=sid)
        for class_name in session_classes:
            classes += class_name.classname.classname + ", "
        if len(classes) > 0:
            classes = classes[:-2]
        return classes

    def set_visible_columns(request):
        event_id = request.session['event_auth_user']['event_id']
        admin_id = request.session['event_auth_user']['id']
        visible_columns = request.POST.get('visible_columns')
        visible = VisibleColumns.objects.filter(event_id=event_id, admin_id=admin_id)
        if visible.exists():
            VisibleColumns.objects.filter(event_id=event_id, admin_id=admin_id, type='session').update(
                visible_columns=visible_columns)
        else:
            new = VisibleColumns(event_id=event_id, admin_id=admin_id, visible_columns=visible_columns, type='session')
            new.save()
        response_data = {}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_session_reoprt(sessions):
        for session in sessions:
            session.group_name = session.group.name
            session.in_queue = SeminarsUsers.objects.filter(session_id=session.id, status='in-queue').count()
            session.attending = SeminarsUsers.objects.filter(session_id=session.id, status='attending').count()
            session.not_attending = SeminarsUsers.objects.filter(session_id=session.id, status='not-attending').count()
            session.pending = SeminarsUsers.objects.filter(session_id=session.id, status='deciding').count()
            session.available_seat = session.max_attendees - session.attending
            if session.max_attendees != 0:
                percentage = (session.attending / session.max_attendees) * 100
                percentage = round(percentage, 1)
                session.percentage = str(percentage) + "%"
                session.available_seat = session.max_attendees - session.attending
            else:
                session.percentage = str(0.0) + "%"
                session.available_seat = 99999999
            evaluations = SessionRating.objects.filter(session_id=session.id)
            rating = 0
            session.average_rating = "N/A"
            session.no_of_attendees_evaluating = "N/A"
            for evaluation in evaluations:
                rating += evaluation.rating
            if rating != 0:
                session.no_of_attendees_evaluating = evaluations.count()
                average_rating = rating / session.no_of_attendees_evaluating
                session.average_rating = round(average_rating, 2)
        return sessions


class SessionDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        session = self.get_object(pk)

        # attendees = Attendee.objects.filter(seminarspeakers__session_id=session.id)
        attendees = Attendee.objects.values('firstname', 'lastname', 'id').all()
        attendees = attendees.filter(seminarspeakers__session_id=session.id)
        my_data = []
        for attendee in attendees:
            arr_data = {}
            arr_data['id'] = attendee['id']
            arr_data['text'] = attendee['firstname'] + ' ' + attendee['lastname']
            my_data.append(arr_data)

        session.speakers = my_data
        session_tags = SessionTags.objects.filter(session_id=pk)
        tags = []
        for tag in session_tags:
            tag_data = {}
            tag_data['id'] = tag.tag.id
            tag_data['text'] = tag.tag.name
            tags.append(tag_data)
        session_custom_class = SessionClasses.objects.filter(session_id=pk)
        custom_classes = []
        for custom_class in session_custom_class:
            custom_class_data = {}
            custom_class_data['id'] = custom_class.classname.id
            custom_class_data['text'] = custom_class.classname.classname
            custom_classes.append(custom_class_data)
        event_id = request.session['event_auth_user']['event_id']
        current_language_id = LanguageH.get_current_language_id(event_id)
        response = {
            'success': True,
            'session': session.as_dict(),
            'tags': tags,
            'custom_classes': custom_classes,
            'current_language_id': current_language_id
        }
        return HttpResponse(json.dumps(response), content_type='application/json')

    def session_filter_status(request):
        filter_id = request.POST.get('filter')
        action = request.POST.get('action')
        session_for_filter = request.POST.get('session')
        attendees = FilterView.get_filtered_attendees(request, filter_id)
        response_data = {}
        response_data['total_attendees'] = attendees.count()

        already_attender = SeminarsUsers.objects.filter(attendee__in=attendees, session_id=session_for_filter,
                                                        status='attending').count()
        response_data['already_attending'] = already_attender
        total_attender = SeminarsUsers.objects.filter(session_id=session_for_filter, status='attending').count()
        response_data['total_attender'] = total_attender

        already_queue_user = SeminarsUsers.objects.filter(attendee__in=attendees, session_id=session_for_filter,
                                                          status='in-queue').count()
        response_data['already_queue_user'] = already_queue_user
        number_of_attending_user_has_clash = 0
        session = Session.objects.get(id=session_for_filter)

        for attende in attendees:
            sessions_of_attende = SeminarsUsers.objects.filter(attendee_id=attende.id, status='attending',
                                                               session__allow_overlapping=0).exclude(
                session_id=session_for_filter)
            Inbetween = 0

            for sessionlist in sessions_of_attende:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = 1
                    break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = 1
                    break
            if Inbetween == 1:
                number_of_attending_user_has_clash += 1

        response_data['number_of_attending_user_has_clash'] = number_of_attending_user_has_clash
        response_data['session_capacity'] = session.max_attendees
        seat_available = session.max_attendees - total_attender
        free_attendees = response_data['total_attendees'] - already_attender - number_of_attending_user_has_clash
        response_data['attendee_to_be_qued'] = 0
        if free_attendees > seat_available:
            response_data['attendee_to_be_qued'] = free_attendees - seat_available

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def session_filter_attending(request):
        filter_id = request.POST.get('filter')
        action = request.POST.get('action')
        session_for_filter = request.POST.get('session')
        session = Session.objects.get(id=session_for_filter)
        attendees = FilterView.get_filtered_attendees(request, filter_id)
        response_data = {}

        event_id = request.session['event_auth_user']['event_id']
        for attendee in attendees:
            already_attender = SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=session_for_filter,
                                                            status='attending')
            if not already_attender.exists():
                capacity = session.max_attendees
                attendee_id = attendee.id
                count = SeminarsUsers.objects.filter(session_id=session_for_filter).exclude(
                    status='not-attending').count()

                if capacity != 0:
                    if capacity > count:
                        already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                                           session__allow_overlapping=0)
                        already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id)
                        Inbetween = 0
                        if session.allow_overlapping == 0:
                            for sessionlist in already_has_session:
                                if sessionlist.session.start <= session.start < sessionlist.session.end:
                                    Inbetween = 1
                                    break
                                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                                    Inbetween = 1
                                    break
                                if session.start <= sessionlist.session.start < session.end:
                                    Inbetween = 1
                                    break
                                elif session.start < sessionlist.session.end <= session.end:
                                    Inbetween = 1
                                    break

                            for sessionlist in already_has_session_as_speaker:
                                if sessionlist.session.start <= session.start < sessionlist.session.end:
                                    Inbetween = 1
                                    break
                                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                                    Inbetween = 1
                                    break
                                if session.start <= sessionlist.session.start < session.end:
                                    Inbetween = 1
                                    break
                                elif session.start < sessionlist.session.end <= session.end:
                                    Inbetween = 1
                                    break


                        else:
                            Inbetween = 0

                        if Inbetween == 0:
                            old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                                       session_id=session_for_filter)
                            if old_history.exists():
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id, session_id=session_for_filter,
                                                           old_value="Not Attending", new_value="Attending",
                                                           event_id=event_id)
                                activity.save()
                            else:
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id, session_id=session_for_filter,
                                                           old_value="Not Answered", new_value="Attending",
                                                           event_id=event_id)
                                activity.save()

                            SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                         session_id=session_for_filter).delete()

                            seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_for_filter)
                            seminar_attendee.save()

                    else:
                        if not session.receive_answer and session.allow_attendees_queue:
                            old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                                       session_id=session_for_filter)
                            if old_history.exists():
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id, session_id=session_for_filter,
                                                           old_value="Not Attending", new_value="In Queue",
                                                           event_id=event_id)
                                activity.save()
                            else:
                                activity = ActivityHistory(activity_type="update", category="session",
                                                           attendee_id=attendee_id, session_id=session_for_filter,
                                                           old_value="Not Answered", new_value="In Queue",
                                                           event_id=event_id)
                                activity.save()

                            SeminarsUsers.objects.filter(attendee_id=attendee_id,
                                                         session_id=session_for_filter).delete()
                            # if not already_has_session:
                            form_data = {
                                "attendee_id": attendee_id,
                                "session_id": session_for_filter,
                                "status": "in-queue"
                            }
                            all_queue = SeminarsUsers.objects.filter(session_id=session_for_filter,
                                                                     status='in-queue').order_by('queue_order')
                            if all_queue.exists():
                                form_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                            seminar_attendee = SeminarsUsers(**form_data)
                            seminar_attendee.save()




                else:
                    old_history = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_for_filter)
                    if old_history.exists():
                        activity = ActivityHistory(activity_type="update", category="session", attendee_id=attendee_id,
                                                   session_id=session_for_filter, old_value="Not Attending",
                                                   new_value="Attending", event_id=event_id)
                        activity.save()
                    else:
                        activity = ActivityHistory(activity_type="update", category="session", attendee_id=attendee_id,
                                                   session_id=session_for_filter, old_value="Not Answered",
                                                   new_value="Attending", event_id=event_id)
                        activity.save()

                    SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_for_filter).delete()
                    seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_for_filter)
                    seminar_attendee.save()
        response_data['msg'] = "Action completed successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def session_filter_not_attending(request):
        filter_id = request.POST.get('filter')
        action = request.POST.get('action')
        session_for_filter = request.POST.get('session')
        attendees = FilterView.get_filtered_attendees(request, filter_id)
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']

        for attendee in attendees:
            already_attender = SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=session_for_filter)
            if already_attender.exists():
                type = already_attender[0].status
                attendee_id = attendee.id
                session_id = session_for_filter
                if type == 'in-queue':
                    SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                    seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id,
                                                     status='not-attending')
                    seminar_attendee.save()
                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=attendee_id,
                                               session_id=session_id, old_value="In Queue", new_value="Not Attending",
                                               event_id=event_id)
                    activity.save()


                elif type == "attending":
                    SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).delete()
                    # if has_seminar.exists():
                    #     seminar_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session_id).update(status='not-attending')
                    # else:
                    seminar_attendee = SeminarsUsers(attendee_id=attendee_id, session_id=session_id,
                                                     status='not-attending')
                    seminar_attendee.save()

                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=attendee_id,
                                               session_id=session_id, old_value="Attending", new_value="Not Attending",
                                               event_id=event_id)
                    activity.save()
                    SessionDetail.notify_queue_user(event_id, session_id)

        response_data['msg'] = "Action completed successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def create_temp_session_filter(request):
        response_data = {}
        try:
            session_id = request.POST.get('session_id')
            session_type = request.POST.get('session_type')
            event_id = request.session['event_auth_user']['event_id']
            admin_id = request.session['event_auth_user']['id']
            temp_groups = Group.objects.filter(name='temporary-filter', event_id=event_id)
            if temp_groups.exists():
                group_id = temp_groups[0].id
                condition = '1'
                if session_type == 'checkpoint':
                    checkpoint = Checkpoint.objects.filter(session_id=session_id, is_hide=0).first()
                    condition = str(checkpoint.id)
                    preset = '[[{"field":"18","condition":"' + condition + '","values":["1"],"matchFor":"1"}]]'
                else:
                    if session_type == 'attending':
                        condition = '1'
                    elif session_type == 'in-queue':
                        condition = '3'
                    elif session_type == 'pending':
                        condition = '4'
                    preset = '[[{"field":"6","condition":"' + condition + '","values":["' + str(
                        session_id) + '"],"matchFor":"1"}]]'
                existing_temp_filter = RuleSet.objects.filter(name='quick-filter', created_by_id=admin_id,
                                                              group__event_id=event_id)
                if existing_temp_filter.exists():
                    filter_id = existing_temp_filter[0].id
                    RuleSet.objects.filter(id=filter_id).update(preset=preset)
                else:
                    filter_order = FilterView.get_filters_order(group_id)
                    rule_order = filter_order
                    temp_filter = RuleSet(name='quick-filter', group_id=group_id, preset=preset, rule_order=rule_order,
                                          created_by_id=admin_id)
                    temp_filter.save()
                    filter_id = temp_filter.id
                currentFilter = CurrentFilter.objects.filter(admin_id=admin_id, event_id=event_id,
                                                             table_type='attendee')
                if currentFilter.exists():
                    CurrentFilter.objects.filter(admin_id=admin_id, event_id=event_id, table_type='attendee').update(
                        filter_id=filter_id)
                else:
                    current = CurrentFilter(admin_id=admin_id, event_id=event_id, filter_id=filter_id)
                    current.save()
                response_data['success'] = True
            else:
                response_data['success'] = False
                response_data['message'] = "Temporary filter group not found"
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")
