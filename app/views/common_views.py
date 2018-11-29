from django.template.loader import render_to_string
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.login_view import Login

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

from django.shortcuts import redirect
import boto.ses
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Tag, Group, Questions, Attendee, Answers, ActivityHistory, Events, EventAdmin, \
    Users, CurrentEvent, PageContent, Session, Travel, Room, RoomAllotment, \
    EmailContents, StyleSheet, Setting, DashboardPlugin, ElementsAnswers, PageContentClasses, AttendeeGroups, RuleSet, \
    MessageContents, Option, PluginSubmitButton, PhotoGroup, PresetEvent, Presets, ElementPresetLang, Notification, \
    MessageReceivers, EmailReceivers, Rebates, EmailTemplates, Checkpoint, SeminarSpeakers, MessageHistory, Cookie
import json
from django.conf import settings
import boto.ses
import logging
from django.http import Http404
from django.db.models import Q
from datetime import datetime, timedelta
from boto.s3.key import Key
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Sum, Count
import time
from app.views.gbhelper.language_helper import LanguageH


class IndexView(generic.DetailView):
    def get(self, request):
        context = {}
        try:
            logger = logging.getLogger(__name__)
            if 'is_login' not in request.session or not request.session['is_login']:
                return redirect('login')
            else:
                request.session['event_auth_user']['is_attendee'] = False
                find_users_in_attendee = Attendee.objects.filter(
                    event_id=request.session['event_auth_user']['event_id'],
                    email=request.session['event_auth_user']['email'])
                if find_users_in_attendee.exists():
                    request.session['event_auth_user']['is_attendee'] = True
                page = PageContent.objects.filter(event_id=request.session['event_auth_user']['event_id'])

                attendees = Group.objects.filter(type="attendee",
                                                 event_id=request.session['event_auth_user']['event_id'])
                attendee_counts = AttendeeGroups.objects
                attendee_counts = attendee_counts.filter(group_id__in=attendees)
                attendee_counts = attendee_counts.values('group__name').annotate(count=Count('id'))

                filters = Group.objects.filter(type="filter", event_id=request.session['event_auth_user']['event_id'])

                sessions = Group.objects.filter(type="session", event_id=request.session['event_auth_user']['event_id'])

                pagehit_columns = None
                reg_columns = None
                message_columns = None
                attendee_columns = None
                filter_columns = None
                session_columns = None

                plugins = ""
                plugins_obj = ["1", "2", "3", "4", "5", "6"]
                dashboard_plugin = DashboardPlugin.objects.filter(
                    event_id=request.session['event_auth_user']['event_id'],
                    modified_by_id=request.session['event_auth_user']['id'])
                if dashboard_plugin.exists():
                    # print(dashboard_plugin[0].sort)
                    setting_data = json.loads(dashboard_plugin[0].setting_data)
                    if 'sort_data' in setting_data:
                        plugins_obj = json.loads(setting_data['sort_data'])
                    if 'pagehit_statistic' in setting_data:
                        pagehit_columns = setting_data['pagehit_statistic']
                        pagehit_columns['start_time'] = datetime.strptime(pagehit_columns['start_time'], "%Y-%m-%d")
                        pagehit_columns['end_time'] = datetime.strptime(pagehit_columns['end_time'], "%Y-%m-%d")
                    if 'reg_statistic' in setting_data:
                        reg_columns = setting_data['reg_statistic']
                        reg_columns['start_time'] = datetime.strptime(reg_columns['start_time'], "%Y-%m-%d")
                        reg_columns['end_time'] = datetime.strptime(reg_columns['end_time'], "%Y-%m-%d")
                    if 'attendeegroup_statistic' in setting_data:
                        attendee_columns = json.loads(setting_data['attendeegroup_statistic'])
                    if 'session_statistic' in setting_data:
                        session_columns = setting_data['session_statistic']
                    if 'filter_statistic' in setting_data:
                        filter_columns = setting_data['filter_statistic']
                    if 'message_statistic' in setting_data:
                        message_columns = setting_data['message_statistic']
                        message_columns['start_time'] = datetime.strptime(message_columns['start_time'], "%Y-%m-%d")
                        message_columns['end_time'] = datetime.strptime(message_columns['end_time'], "%Y-%m-%d")
                if attendee_columns != None:
                    temp_attendee_columns = attendee_columns
                    attendee_columns = []
                    for ta in range(0, len(temp_attendee_columns)):
                        attendee_columns.append(int(temp_attendee_columns[ta]))
                if session_columns == '' or session_columns == None:
                    session_columns = 0
                if filter_columns == '' or filter_columns == None:
                    filter_columns = 0
                context = {
                    'pages': page,
                    'attendees': attendee_counts,
                    'filters': filters,
                    'sessions': sessions,
                    'attendee_columns': attendee_columns,
                    'filter_columns': int(filter_columns),
                    'session_columns': int(session_columns),
                    'pagehit_columns': pagehit_columns,
                    'reg_columns': reg_columns,
                    'message_columns': message_columns,
                    'start_date': datetime.now() + timedelta(-30),
                    'end_date': datetime.now(),
                }
                context["email_count"] = EmailReceivers.objects.filter(
                    email_content__template__event_id=request.session['event_auth_user']['event_id']) \
                    .count()
                context["sms_count"] = MessageReceivers.objects.filter(
                    message_content__event_id=request.session['event_auth_user']['event_id']) \
                    .count()
                context["notification_count"] = Notification.objects.filter(
                    to_attendee__event_id=request.session['event_auth_user']['event_id']) \
                    .count()
                for x in range(0, 6):
                    context["give"] = plugins_obj[x]
                    plugins += render_to_string('dashboard/dashboard_plugins.html', context)

                context["plugins"] = plugins
        except Exception as e:
            ErrorR.efail(e)
        return render(request, 'dashboard/index.html', context)


class AnswerView(generic.DetailView):
    def get(self, request):
        return render(request, '')

    def saveAnswers(request, userId, answer):
        response = {}
        if answer['value'] != '[Multiple Values]':
            existAnswer = Answers.objects.filter(user_id=userId).filter(question_id=answer['id'])
            if existAnswer.exists():
                old_value = existAnswer[0].value
                if answer['value'] == '' or answer['value'] == 'Empty':
                    response['deleted_questions'] = existAnswer[0].id
                else:
                    existAnswer.update(value=answer['value'])
                if old_value != answer['value']:
                    activity_history = ActivityHistory(attendee_id=userId,
                                                       admin_id=request.session['event_auth_user']['id'],
                                                       activity_type='update', category='question',
                                                       question_id=answer['id'], old_value=old_value,
                                                       new_value=answer['value'],
                                                       event_id=request.session['event_auth_user']['event_id'])
                    response['questions_activity'] = activity_history
            else:
                if answer['value'] != '' and answer['value'] != 'Empty':
                    attendeeAnswer = Answers(value=answer['value'], question_id=answer['id'], user_id=userId)
                    response['new_questions_answer'] = attendeeAnswer
                    old_value = 'Empty'
                    activity_history = ActivityHistory(attendee_id=userId,
                                                       admin_id=request.session['event_auth_user']['id'],
                                                       activity_type='update', category='question',
                                                       question_id=answer['id'], old_value=old_value,
                                                       new_value=answer['value'],
                                                       event_id=request.session['event_auth_user']['event_id'])
                    response['questions_activity'] = activity_history
        return response


class GroupView(generic.DetailView):

    def get_hotelGroup(request):
        group = Group.objects.filter(type="hotel", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_paymentGroup(request):
        group = Group.objects.filter(type="payment", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_sessionGroup(request):
        group = Group.objects.filter(type="session", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_travelGroup(request):
        group = Group.objects.filter(type="travel", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_attendeeGroup(request):
        group = Group.objects.filter(type="attendee", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_locationGroup(request):
        group = Group.objects.filter(type="location", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_questionGroup(request):
        group = Group.objects.filter(type="question", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_filterGroup(request):
        group = Group.objects.filter(type="filter", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_exportfilterGroup(request):
        group = Group.objects.filter(type="export_filter", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_menuGroup(request):
        group = Group.objects.filter(type="menu", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_allowedEmail(request):
        group = Group.objects.filter(type="email", is_show=1,
                                     event_id=request.session['event_auth_user']['event_id']).order_by('group_order')
        return group

    def get_photoGroup(request):
        group = PhotoGroup.objects.filter(page__event_id=request.session['event_auth_user']['event_id'])
        return group


class CommonContext(generic.DetailView):
    def get_all_common_context(request):
        session_groups = GroupView.get_sessionGroup(request)
        for group in session_groups:
            group.sessions = Session.objects.all().filter(group_id=group.id)
        travel_groups = GroupView.get_travelGroup(request)
        for group in travel_groups:
            group.travels = Travel.objects.all().filter(group_id=group.id)
        attendee_groups = GroupView.get_attendeeGroup(request)
        questionGroup = GroupView.get_questionGroup(request)
        hotel_group = GroupView.get_hotelGroup(request)
        for group in hotel_group:
            group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id)
            for room in group.rooms:
                room_allotments = RoomAllotment.objects.filter(room_id=room.id).order_by('available_date')
                date_allotments = []
                for allotments in room_allotments:
                    date_allotments.append(str(allotments.available_date))
                if len(date_allotments) > 0:
                    new_date = datetime.strptime(date_allotments[-1], "%Y-%m-%d") + timedelta(days=1)
                    new_allotments = str(new_date).split(' ')[0]
                    date_allotments.append(new_allotments)
                room.allotment = json.dumps(date_allotments)

        for group in questionGroup:
            group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')

        context = {
            'session_groups': session_groups,
            'travel_groups': travel_groups,
            'attendee_groups': attendee_groups,
            'hotel_groups': hotel_group,
            'questionGroup': questionGroup,
        }

        return context

    def get_filter_context(request):
        event_id = request.session['event_auth_user']['event_id']
        session_groups = GroupView.get_sessionGroup(request)
        for group in session_groups:
            group.sessions = Session.objects.filter(group_id=group.id)
        tags = Tag.objects.filter(event_id=event_id)
        attendee_groups = GroupView.get_attendeeGroup(request)
        filterGroup = GroupView.get_filterGroup(request)
        for group in filterGroup:
            group.filters = RuleSet.objects.filter(group_id=group.id).order_by('rule_order').exclude(
                name='quick-filter')
        question_groups = GroupView.get_questionGroup(request)
        for question_group in question_groups:
            question_group.questions = Questions.objects.filter(group_id=question_group.id)
            for question in question_group.questions:
                if question.type != 'text' and question.type != 'textarea':
                    question.options = Option.objects.filter(question_id=question.id)

        hotelGroup = GroupView.get_hotelGroup(request)
        for group in hotelGroup:
            group.slugName = group.name.replace(" ", "_")
            group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=group.id).order_by(
                'room_order')
        pages = PageContent.objects.filter(event_id=event_id)
        for page in pages:
            page.buttons = PluginSubmitButton.objects.filter(page_id=page.id)

        emails = EmailContents.objects.filter(template__event_id=event_id, is_show=1)
        messages = MessageContents.objects.filter(event_id=event_id, is_show=1)
        rebates = Rebates.objects.filter(event_id=event_id)
        languages = Presets.objects.filter(Q(event_id=event_id) | Q(event_id=None))
        filter_checkpoints = Checkpoint.objects.filter(event_id=event_id, is_hide=0)

        context = {
            'filterGroup': filterGroup,
            'session_groups': session_groups,
            'tags': tags,
            'attendee_groups': attendee_groups,
            'question_groups': question_groups,
            'hotelGroups': hotelGroup,
            'emails': emails,
            "messages": messages,
            "pages": pages,
            "rebates": rebates,
            "filter_checkpoints": filter_checkpoints,
            "languages": languages
        }
        return context


class TagView(generic.DetailView):
    def get_tags(request):
        response_data = {}
        val = request.POST.get('q')
        event_id = request.session['event_auth_user']['event_id']
        tags = Tag.objects.values('name', 'id').filter(name__startswith=val, event_id=event_id)
        my_data = []
        for tag in tags:
            arr_data = {
                'id': tag['id'],
                'text': tag['name']
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class EventView(generic.DetailView):
    def get(self, request):
        if request.session['event_auth_user']['type'] == 'super_admin':
            # events = Events.objects.filter(is_show=1)
            events = Events.objects.all()
            context = {
                'events': events
            }
            return render(request, 'event/event.html', context)
        else:
            return render(request, 'dashboard/index.html')

    @staticmethod
    def get_managers(request):
        response_data = {}
        val = request.POST.get('q')
        managers = Users.objects.annotate(full_name=Concat('firstname', Value(' '), 'lastname')).filter(
            full_name__istartswith=val).exclude(type='super_admin')
        data = []
        for manager in managers:
            arr_data = {
                'id': manager.id,
                'text': manager.firstname + ' ' + manager.lastname
            }
            data.append(arr_data)
        response_data['results'] = data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def post(self, request):
        ErrorR.ex_time_init()
        current_admin_id = int(request.session['event_auth_user']['id'])
        admins = json.loads(request.POST.get('admin'))
        form_data = {
            "name": request.POST.get('name'),
            "description": request.POST.get('description'),
            "start": request.POST.get('start'),
            "end": request.POST.get('end'),
            "url": request.POST.get('url').replace(" ", "-"),
            "address": request.POST.get('address'),
            "last_updated_by_id": current_admin_id
        }
        if len(admins) > 0:
            form_data['admin_id'] = admins[0]
        response_data = {}
        ErrorR.ex_time()
        if 'id' in request.POST:
            event_id = request.POST.get('id')
            if not (
                    Events.objects.filter(Q(name=form_data['name']) | Q(url=form_data['url'])).exclude(
                        id=event_id).exists()):
                form_data["updated"] = datetime.now()
                Events.objects.filter(id=event_id).update(**form_data)
                event = Events.objects.get(id=event_id)
                admin_exist = []
                for admin_id in admins:
                    admin_exist.append(admin_id)
                    if not (EventAdmin.objects.filter(admin_id=admin_id, event_id=event.id).exists()):
                        event_form_data = {
                            "event_id": event.id,
                            "admin_id": admin_id
                        }
                        event_permission = EventAdmin(**event_form_data)
                        event_permission.save()
                deleted_event_admin = EventAdmin.objects.filter(event_id=event.id).exclude(admin_id__in=admin_exist)
                for event_admin in deleted_event_admin:
                    event_admin.delete()
                response_data['event'] = event.as_dict()
                response_data['success'] = 'Event Update Successfully'
            else:
                response_data['error'] = 'Event already exist'
        else:
            if not (Events.objects.filter(Q(name=form_data['name']) | Q(url=form_data['url'])).exists()):
                form_data['created_by_id'] = current_admin_id

                event_admin_assigns = []
                event_questions = []
                event_attendee_groups = []
                event_settings = []

                default_project = Events.objects.filter(url='default-project')
                if default_project.exists():
                    start_time = time.time()
                    event = Events(**form_data)
                    event.save()
                    for admin_id in admins:
                        event_form_data = {
                            "event_id": event.id,
                            "admin_id": admin_id
                        }
                        event_permission = EventAdmin(**event_form_data)
                        event_admin_assigns.append(event_permission)
                    EventAdmin.objects.bulk_create(event_admin_assigns)

                    # Create Default Language

                    languages = EventView.copy_language(request, event.id, current_admin_id)

                    # Get Default Language Id
                    current_language_id = LanguageH.get_current_language_id(event.id)
                    # Create Default Groups

                    group_data = {
                        "name": "Default",
                        "name_lang": str({current_language_id: "Default"}).replace("'", '"'),
                        "type": "question",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    group = Group(**group_data)
                    group.save()
                    # Create Default Questions Groups
                    question_group_data = {
                        "name": "Questions",
                        "name_lang": str({current_language_id: "Questions"}).replace("'", '"'),
                        "type": "question",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    question_group = Group(**question_group_data)
                    event_attendee_groups.append(question_group)
                    # Create Default Filter Groups
                    filter_data = {
                        "name": "temporary-filter",
                        "name_lang": str({current_language_id: "temporary-filter"}).replace("'", '"'),
                        "type": "filter",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    filter_group = Group(**filter_data)
                    event_attendee_groups.append(filter_group)
                    filters_data = {
                        "name": "Filters",
                        "name_lang": str({current_language_id: "Filters"}).replace("'", '"'),
                        "type": "filter",
                        "event_id": event.id,
                        "group_order": 2
                    }
                    filters_group = Group(**filters_data)
                    event_attendee_groups.append(filters_group)

                    default_event = default_project[0]

                    # Create Default Questions

                    default_questions = Questions.objects.filter(group__name='Default', group__type='question',
                                                                 group__event_id=default_event.id)
                    for question in default_questions:
                        question_form = {
                            "title": question.title,
                            "title_lang": str({current_language_id: question.title}).replace("'", '"'),
                            "type": question.type,
                            "description": question.description,
                            "description_lang": str({current_language_id: question.description}).replace("'", '"'),
                            "group_id": group.id,
                            "required": question.required,
                            "question_order": question.question_order,
                            "actual_definition": question.actual_definition
                        }
                        questions = Questions(**question_form)
                        event_questions.append(questions)
                    Questions.objects.bulk_create(event_questions)

                    # Create Default Attendee Groups

                    default_attendee_groups = Group.objects.filter(type='attendee', event_id=default_event.id)
                    for attendee_group in default_attendee_groups:
                        attendee_group_form = {
                            "name": attendee_group.name,
                            "name_lang": str({current_language_id: attendee_group.name}).replace("'", '"'),
                            "type": attendee_group.type,
                            "event_id": event.id,
                            "group_order": attendee_group.group_order
                        }
                        attendee_groups = Group(**attendee_group_form)
                        event_attendee_groups.append(attendee_groups)

                    # Create Default Payment Groups
                    payment_6_data = {
                        "name": "6",
                        "name_lang": str({current_language_id: "6"}).replace("'", '"'),
                        "type": "payment",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    payment_group_6 = Group(**payment_6_data)
                    event_attendee_groups.append(payment_group_6)
                    payment_12_data = {
                        "name": "12",
                        "name_lang": str({current_language_id: "12"}).replace("'", '"'),
                        "type": "payment",
                        "event_id": event.id,
                        "group_order": 2
                    }
                    payment_group_12 = Group(**payment_12_data)
                    event_attendee_groups.append(payment_group_12)
                    payment_25_data = {
                        "name": "25",
                        "name_lang": str({current_language_id: "25"}).replace("'", '"'),
                        "type": "payment",
                        "event_id": event.id,
                        "group_order": 3
                    }
                    payment_group_25 = Group(**payment_25_data)
                    event_attendee_groups.append(payment_group_25)

                    # Create Default Session Groups
                    session_data = {
                        "name": "Sessions",
                        "name_lang": str({current_language_id: "Sessions"}).replace("'", '"'),
                        "type": "session",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    session_group = Group(**session_data)
                    event_attendee_groups.append(session_group)

                    # Create Default Hotel Groups
                    hotel_data = {
                        "name": "Hotels",
                        "name_lang": str({current_language_id: "Hotels"}).replace("'", '"'),
                        "type": "hotel",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    hotel_group = Group(**hotel_data)
                    event_attendee_groups.append(hotel_group)

                    # Create Default Export Groups
                    export_data = {
                        "name": "Exports",
                        "name_lang": str({current_language_id: "Exports"}).replace("'", '"'),
                        "type": "export_filter",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    export_group = Group(**export_data)
                    event_attendee_groups.append(export_group)

                    # Create Default Locations Groups
                    location_data = {
                        "name": "Locations",
                        "name_lang": str({current_language_id: "Locations"}).replace("'", '"'),
                        "type": "location",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    location_group = Group(**location_data)
                    event_attendee_groups.append(location_group)

                    Group.objects.bulk_create(event_attendee_groups)

                    default_login_email_id = 0
                    reset_password_email_id = 0
                    # Create Default Email Template

                    default_email_templates = EmailTemplates.objects.filter(name='default-email-template',
                                                                            event_id=default_event.id)
                    if default_email_templates.exists():
                        email_template_form = {
                            "name": default_email_templates[0].name,
                            "category": default_email_templates[0].category,
                            "content": default_email_templates[0].content,
                            "created_by_id": current_admin_id,
                            "last_updated_by_id": current_admin_id,
                            "event_id": event.id
                        }
                        email_template = EmailTemplates(**email_template_form)
                        email_template.save()

                        # Create Default Email Confirmation

                        default_confirmation = EmailContents.objects.filter(name='default-email-confirmation',
                                                                            template__event_id=default_event.id)
                        default_email = EventView.create_default_confirmation(default_confirmation, email_template,
                                                                              current_admin_id, current_language_id)
                        if default_email['email_id'] != '':
                            attendee_add_confirmation = Setting(name="attendee_add_confirmation",
                                                                value=default_email['email_id'], event_id=event.id)
                            event_settings.append(attendee_add_confirmation)
                            attendee_edit_confirmation = Setting(name="attendee_edit_confirmation",
                                                                 value=default_email['email_id'], event_id=event.id)
                            event_settings.append(attendee_edit_confirmation)

                        # Create Request Login Email Confirmation

                        request_login_confirmation = EmailContents.objects.filter(name='request-login-confirmation',
                                                                                  template__event_id=default_event.id)
                        login_email = EventView.create_default_confirmation(request_login_confirmation, email_template,
                                                                            current_admin_id, current_language_id)
                        if login_email['email_id'] != '':
                            default_login_email_id = login_email['email_id']

                        # Create Reset Password Email Confirmation

                        reset_password_confirmation = EmailContents.objects.filter(name='reset-password-confirmation',
                                                                                   template__event_id=default_event.id)
                        reset_password_email = EventView.create_default_confirmation(reset_password_confirmation,
                                                                                     email_template, current_admin_id, current_language_id)
                        if reset_password_email['email_id'] != '':
                            reset_password_email_id = reset_password_email['email_id']

                        # Create Session is not Conflict Confirmations

                        session_confirmation_no_conflict = EmailContents.objects.filter(name='session-no-conflict-email-confirmation',
                                                                            template__event_id=default_event.id)
                        session_email_no_conflict = EventView.create_default_confirmation(session_confirmation_no_conflict, email_template,
                                                                              current_admin_id, current_language_id)
                        if session_email_no_conflict['email_id'] != '':
                            session_no_conflict_confirmation = Setting(name="session_no_conflict_confirmation",
                                                                value=session_email_no_conflict['email_id'], event_id=event.id)
                            event_settings.append(session_no_conflict_confirmation)

                        # Create Session is not Conflict Confirmations

                        session_confirmation_conflict = EmailContents.objects.filter(name='session-conflict-email-confirmation',
                                                                            template__event_id=default_event.id)
                        session_email_conflict = EventView.create_default_confirmation(session_confirmation_conflict, email_template,
                                                                              current_admin_id, current_language_id)
                        if session_email_conflict['email_id'] != '':
                            session_conflict_confirmation = Setting(name="session_conflict_confirmation",
                                                                value=session_email_conflict['email_id'], event_id=event.id)
                            event_settings.append(session_conflict_confirmation)

                    # Create Default Web Templates

                    default_web_templates = EmailTemplates.objects.filter(name='default-web-template',
                                                                          event_id=default_event.id)
                    if default_web_templates.exists():
                        web_template_form = {
                            "name": default_web_templates[0].name,
                            "category": default_web_templates[0].category,
                            "content": default_web_templates[0].content,
                            "created_by_id": current_admin_id,
                            "last_updated_by_id": current_admin_id,
                            "event_id": event.id
                        }
                        web_template = EmailTemplates(**web_template_form)
                        web_template.save()

                        exclude_plugin_settings = ['location_location_groups', 'session_radio_session_groups',
                                                   'session_checkbox_session_groups', 'submit_button_redirect_page',
                                                   'submit_button_email_send']
                        # Create Default Start Page

                        default_start_page = PageContent.objects.filter(url='start', event_id=default_event.id)
                        EventView.create_default_page(default_start_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Default Logged In Page

                        default_logged_page = PageContent.objects.filter(url='logged-in', event_id=default_event.id)
                        EventView.create_default_page(default_logged_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Default Login Page

                        default_login_page = PageContent.objects.filter(url='default-login-page',
                                                                        event_id=default_event.id)
                        EventView.create_default_page(default_login_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Request Login Page

                        default_request_login_page = PageContent.objects.filter(url='request-login-page',
                                                                                event_id=default_event.id)
                        EventView.create_default_page(default_request_login_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Reset Password Page

                        reset_password_page = PageContent.objects.filter(url='reset-password-page',
                                                                         event_id=default_event.id)
                        EventView.create_default_page(reset_password_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create New Password Page

                        new_password_page = PageContent.objects.filter(url='new-password-page',
                                                                       event_id=default_event.id)
                        EventView.create_default_page(new_password_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Message Archive Page

                        archive_message_page = PageContent.objects.filter(url='messages', event_id=default_event.id)
                        EventView.create_default_page(archive_message_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Logout Page

                        logout_page = PageContent.objects.filter(url='logout', event_id=default_event.id)
                        EventView.create_default_page(logout_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Payment Success Page

                        payment_success_page = PageContent.objects.filter(url='payment-success', event_id=default_event.id)
                        EventView.create_default_page(payment_success_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create Payment Cancel Page

                        payment_cancel_page = PageContent.objects.filter(url='payment-cancel',
                                                                          event_id=default_event.id)
                        EventView.create_default_page(payment_cancel_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create 404 Not Found Page

                        not_found_page = PageContent.objects.filter(url='404-not-found',
                                                                         event_id=default_event.id)
                        EventView.create_default_page(not_found_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create 403 Forbidden Registered page

                        forbidden_registered_page = PageContent.objects.filter(url='403-forbidden-registered',
                                                                    event_id=default_event.id)
                        EventView.create_default_page(forbidden_registered_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                        # Create 403 Forbidden Unregistered page

                        forbidden_unregistered_page = PageContent.objects.filter(url='403-forbidden-unregistered',
                                                                               event_id=default_event.id)
                        EventView.create_default_page(forbidden_unregistered_page, current_admin_id, web_template, event,
                                                      default_login_email_id, reset_password_email_id,
                                                      exclude_plugin_settings)

                    ErrorR.ex_time_init()
                    # Create Default Invoice Templates
                    default_invoice_template_lists = []
                    default_invoice_template = EmailTemplates.objects.filter(name='default-invoice-template',
                                                                             event_id=default_event.id)
                    if default_invoice_template.exists():
                        default_invoice_template_form = {
                            "name": default_invoice_template[0].name,
                            "category": default_invoice_template[0].category,
                            "content": default_invoice_template[0].content,
                            "created_by_id": current_admin_id,
                            "last_updated_by_id": current_admin_id,
                            "event_id": event.id
                        }
                        invoice_template = EmailTemplates(**default_invoice_template_form)
                        default_invoice_template_lists.append(invoice_template)
                        # invoice_template.save()

                    # Create Default Credit Invoice Templates

                    default_credit_invoice_template = EmailTemplates.objects.filter(
                        name='default-credit-invoice-template',
                        event_id=default_event.id)
                    if default_credit_invoice_template.exists():
                        default_credit_invoice_template_form = {
                            "name": default_credit_invoice_template[0].name,
                            "category": default_credit_invoice_template[0].category,
                            "content": default_credit_invoice_template[0].content,
                            "created_by_id": current_admin_id,
                            "last_updated_by_id": current_admin_id,
                            "event_id": event.id
                        }
                        credit_invoice_template = EmailTemplates(**default_credit_invoice_template_form)
                        default_invoice_template_lists.append(credit_invoice_template)
                        # credit_invoice_template.save()

                    # Create Default Receipt Templates

                    default_receipt_template = EmailTemplates.objects.filter(name='default-receipt-template',
                                                                             event_id=default_event.id)
                    if default_receipt_template.exists():
                        default_receipt_template_form = {
                            "name": default_receipt_template[0].name,
                            "category": default_receipt_template[0].category,
                            "content": default_receipt_template[0].content,
                            "created_by_id": current_admin_id,
                            "last_updated_by_id": current_admin_id,
                            "event_id": event.id
                        }
                        receipt_template = EmailTemplates(**default_receipt_template_form)
                        default_invoice_template_lists.append(receipt_template)
                    EmailTemplates.objects.bulk_create(default_invoice_template_lists)
                    # receipt_template.save()
                    ErrorR.ex_time()
                    # Create Default Style.css

                    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
                    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                    extension = 'css'
                    key_name = 'public/' + event.url + '/compiled_css/' + 'style' + '.' + extension
                    k = Key(bucket)
                    k.key = key_name
                    style = StyleSheet.objects.filter(event_id=default_event.id)
                    compiled_css = ""
                    if style.exists():
                        scss = StyleSheet(style=style[0].style, event_id=event.id, created_by_id=current_admin_id)
                        scss.save()
                        compiled_css = scss.style
                    if not k.exists():
                        key = bucket.new_key(key_name)
                        key.content_type = 'text/css'
                        key.set_contents_from_string(compiled_css, policy='public-read')
                        files_k = bucket.new_key('public/' + event.url + '/files/')
                        files_k.set_contents_from_string("", policy='public-read')
                        offline_package_k = bucket.new_key('public/' + event.url + '/files/offline_package')
                        offline_package_k.set_contents_from_string("", policy='public-read')
                    else:
                        k.content_type = 'text/css'
                        k.set_contents_from_string(compiled_css, policy='public-read')

                    # Create Default Notification Timeout

                    default_notification_timeout = Setting.objects.filter(name='notification_timeout',
                                                                          event_id=default_event.id)
                    if default_notification_timeout.exists():
                        notification_timeout = Setting(name=default_notification_timeout[0].name,
                                                       value=default_notification_timeout[0].value, event_id=event.id)
                        event_settings.append(notification_timeout)

                    # Create Default Timezone

                    default_timezone = Setting.objects.filter(name='timezone', event_id=default_event.id)
                    if default_timezone.exists():
                        timezone = Setting(name=default_timezone[0].name, value=default_timezone[0].value,
                                           event_id=event.id)
                        event_settings.append(timezone)

                    # Create Default Week Start with

                    default_week_start_day = Setting.objects.filter(name='week_start_day', event_id=default_event.id)
                    if default_week_start_day.exists():
                        week_start_day = Setting(name=default_week_start_day[0].name,
                                                 value=default_week_start_day[0].value,
                                                 event_id=event.id)
                        event_settings.append(week_start_day)

                    # Create Default Third Party Plugin language

                    default_plugin_language = Setting.objects.filter(name='plugin_language', event_id=default_event.id)
                    if default_plugin_language.exists():
                        plugin_language = Setting(name=default_plugin_language[0].name,
                                                  value=default_plugin_language[0].value,
                                                  event_id=event.id)
                        event_settings.append(plugin_language)

                    # Create Default Third Party Plugin language

                    default_uid_length = Setting.objects.filter(name='uid_length', event_id=default_event.id)
                    if default_uid_length.exists():
                        uid_length = Setting(name=default_uid_length[0].name,
                                             value=default_uid_length[0].value,
                                             event_id=event.id)
                        event_settings.append(uid_length)

                    # Create Default Session Cookie Expire

                    default_cookie_expire = Setting.objects.filter(name='cookie_expire', event_id=default_event.id)
                    if default_cookie_expire.exists():
                        cookie_expire = Setting(name=default_cookie_expire[0].name,
                                                value=default_cookie_expire[0].value,
                                                event_id=event.id)
                        event_settings.append(cookie_expire)

                    # Create Default Economy Due Date

                    default_economy_due_date = Setting.objects.filter(name='due_date', event_id=default_event.id)
                    if default_economy_due_date.exists():
                        due_date = Setting(name=default_economy_due_date[0].name,
                                                value=default_economy_due_date[0].value,
                                                event_id=event.id)
                        event_settings.append(due_date)

                    # Create Default Next Up Setting

                    default_next_up_appear = Setting.objects.filter(name='appear_next_up_setting',
                                                                    event_id=default_event.id)
                    if default_next_up_appear.exists():
                        next_up_appear = Setting(name=default_next_up_appear[0].name,
                                                 value=default_next_up_appear[0].value,
                                                 event_id=event.id)
                        event_settings.append(next_up_appear)
                    default_next_up_disappear = Setting.objects.filter(name='disappear_next_up_setting',
                                                                       event_id=default_event.id)
                    if default_next_up_disappear.exists():
                        next_up_disappear = Setting(name=default_next_up_disappear[0].name,
                                                    value=default_next_up_disappear[0].value,
                                                    event_id=event.id)
                        event_settings.append(next_up_disappear)

                    # Create Default Evaluation Setting

                    default_evaluation_appear = Setting.objects.filter(name='appear_evaluation_setting',
                                                                       event_id=default_event.id)
                    if default_evaluation_appear.exists():
                        evaluation_appear = Setting(name=default_evaluation_appear[0].name,
                                                    value=default_evaluation_appear[0].value,
                                                    event_id=event.id)
                        event_settings.append(evaluation_appear)

                    # Create Default Session Details Setting

                    default_session_details_settings = Setting.objects.filter(name='session_global_settings',
                                                                              event_id=default_event.id)
                    if default_session_details_settings.exists():
                        session_details_settings = Setting(name=default_session_details_settings[0].name,
                                                           value=default_session_details_settings[0].value,
                                                           event_id=event.id)
                        event_settings.append(session_details_settings)

                    # Create Default Location Details Setting

                    default_location_details_settings = Setting.objects.filter(name='location_global_settings',
                                                                               event_id=default_event.id)
                    if default_location_details_settings.exists():
                        location_details_settings = Setting(name=default_location_details_settings[0].name,
                                                            value=default_location_details_settings[0].value,
                                                            event_id=event.id)
                        event_settings.append(location_details_settings)

                    # Create Default Location Details Setting

                    default_economy_order_table_settings = Setting.objects.filter(name='economy_order_table_global_settings',
                                                                               event_id=default_event.id)
                    if default_economy_order_table_settings.exists():
                        economy_order_table_settings = Setting(name=default_economy_order_table_settings[0].name,
                                                            value=default_economy_order_table_settings[0].value,
                                                            event_id=event.id)
                        event_settings.append(economy_order_table_settings)

                    order_number_settings = Setting(name='start_order_number', value='{}-0000001'.format(event.id), event_id=event.id)
                    event_settings.append(order_number_settings)

                    Setting.objects.bulk_create(event_settings)

                    # Create Default Sender Email

                    default_sender_email = "mahedi@workspaceit.com"
                    sender_email = Setting(name="sender_email", value=default_sender_email, event_id=event.id)
                    sender_email.save()

                    response_data['event'] = event.as_dict()
                    response_data['success'] = 'Event Create Successfully'
                else:
                    event = Events(**form_data)
                    event.save()
                    for admin_id in admins:
                        event_form_data = {
                            "event_id": event.id,
                            "admin_id": admin_id
                        }
                        event_permission = EventAdmin(**event_form_data)
                        event_permission.save()
                    group_data = {
                        "name": "Default",
                        "type": "question",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    group = Group(**group_data)
                    group.save()
                    filter_data = {
                        "name": "temporary-filter",
                        "type": "filter",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    filter_group = Group(**filter_data)
                    filter_group.save()
                    first_name = Questions(title="First Name", type="text", description="", group_id=group.id,
                                           required=1, question_order=1, actual_definition='firstname')
                    first_name.save()
                    last_name = Questions(title="Last Name", type="text", description="", group_id=group.id, required=1,
                                          question_order=2, actual_definition='lastname')
                    last_name.save()
                    email = Questions(title="Email", type="text", description="", group_id=group.id, required=1,
                                      question_order=3, actual_definition='email')
                    email.save()
                    phone = Questions(title="Mobile phone", type="text", description="", group_id=group.id, required=1,
                                      question_order=4, actual_definition='phone')
                    phone.save()

                    # Create Attendee group

                    attending_group_form = {
                        "name": "Attending",
                        "type": "attendee",
                        "event_id": event.id,
                        "group_order": 1
                    }
                    attending_groups = Group(**attending_group_form)
                    attending_groups.save()

                    not_attending_group_form = {
                        "name": "Not Attending",
                        "type": "attendee",
                        "event_id": event.id,
                        "group_order": 2
                    }
                    not_attending_groups = Group(**not_attending_group_form)
                    not_attending_groups.save()

                    # Default Email template

                    email_template_form = {
                        "name": "default-email-template",
                        "category": "email_templates",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "event_id": event.id
                    }
                    email_template = EmailTemplates(**email_template_form)
                    email_template.save()

                    # Default Email Confirmation

                    confirmation_form = {
                        "subject": "Registration",
                        "name": "default-email-confirmation",
                        "content": "",
                        "template_id": email_template.id,
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                    }
                    email_confirmation = EmailContents(**confirmation_form)
                    email_confirmation.save()

                    attendee_add_confirmation = Setting(name="attendee_add_confirmation", value=email_confirmation.id,
                                                        event_id=event.id)
                    attendee_add_confirmation.save()
                    attendee_edit_confirmation = Setting(name="attendee_edit_confirmation", value=email_confirmation.id,
                                                         event_id=event.id)
                    attendee_edit_confirmation.save()

                    no_conflict_confirmation_form = {
                        "subject": "Session Attend",
                        "name": "session-no-conflict-email-confirmation",
                        "content": "",
                        "template_id": email_template.id,
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                    }
                    session_without_conflict_email_confirmation = EmailContents(**no_conflict_confirmation_form)
                    session_without_conflict_email_confirmation.save()

                    conflict_confirmation_form = {
                        "subject": "Session Conflict",
                        "name": "session-conflict-email-confirmation",
                        "content": "",
                        "template_id": email_template.id,
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                    }
                    session_conflict_email_confirmation = EmailContents(**conflict_confirmation_form)
                    session_conflict_email_confirmation.save()

                    session_no_conflict_confirmation = Setting(name="session_no_conflict_confirmation", value=session_without_conflict_email_confirmation.id,
                                                        event_id=event.id)
                    session_no_conflict_confirmation.save()
                    session_conflict_confirmation = Setting(name="session_conflict_confirmation", value=session_conflict_email_confirmation.id,
                                                         event_id=event.id)
                    session_conflict_confirmation.save()

                    # Request Login Confirmation

                    request_login_confirmation_form = {
                        "subject": "Login Info",
                        "name": "request-login-confirmation",
                        "content": "",
                        "template_id": email_template.id,
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                    }
                    request_login_email_confirmation = EmailContents(**request_login_confirmation_form)
                    request_login_email_confirmation.save()

                    # Reste Password Confirmation

                    reset_password_confirmation_form = {
                        "subject": "Reset Password",
                        "name": "reset-password-confirmation",
                        "content": "",
                        "template_id": email_template.id,
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                    }
                    reset_password_email_confirmation = EmailContents(**reset_password_confirmation_form)
                    reset_password_email_confirmation.save()

                    # Default Web Template

                    web_template_form = {
                        "name": "default-web-template",
                        "category": "web_pages",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "event_id": event.id
                    }
                    web_template = EmailTemplates(**web_template_form)
                    web_template.save()

                    # Default Start Page

                    start_page_form = {
                        "url": "start",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    start_page = PageContent(**start_page_form)
                    start_page.save()

                    # Default Logged In Page

                    logged_in_page_form = {
                        "url": "logged-in",
                        "login_required": 1,
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    logged_in_page = PageContent(**logged_in_page_form)
                    logged_in_page.save()

                    # Default login page

                    default_login_page_form = {
                        "url": "default-login-page",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    default_login_page = PageContent(**default_login_page_form)
                    default_login_page.save()

                    # Request Login Page

                    request_login_page_form = {
                        "url": "request-login-page",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    request_login_page = PageContent(**request_login_page_form)
                    request_login_page.save()

                    # Reset Password Page

                    reset_password_page_form = {
                        "url": "reset-password-page",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    reset_password_page = PageContent(**reset_password_page_form)
                    reset_password_page.save()

                    # New password Page

                    new_password_page_form = {
                        "url": "new-password-page",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    new_password_page = PageContent(**new_password_page_form)
                    new_password_page.save()

                    # Messages Archive Page

                    archive_message_page_form = {
                        "url": "messages",
                        "login_required": 1,
                        "content": '{section:temporary,box:2}{row:,box:3}{col:span-12,box:4}{element:archive-messages,box:1}{end_div}{end_div}{end_div}',
                        "element_filter": '[{"box_id":"box-1","element_id":"35"}]',
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    archive_message_page = PageContent(**archive_message_page_form)
                    archive_message_page.save()

                    # Logout Page

                    archive_message_page_form = {
                        "url": "logout",
                        "login_required": 1,
                        "content": ' {section:temporary,box:2}{row:,box:3}{col:span-12,box:4}{element:logout,box:1}{end_div}{end_div}{end_div}',
                        "element_filter": '[{"box_id":"box-1","element_id":"38"}]',
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "template_id": web_template.id,
                        "event_id": event.id
                    }
                    archive_message_page = PageContent(**archive_message_page_form)
                    archive_message_page.save()

                    default_invoice_template_lists = []
                    # Default Invoice Template

                    default_invoice_form = {
                        "name": "default-invoice-template",
                        "category": "invoices",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "event_id": event.id
                    }
                    default_invoice = EmailTemplates(**default_invoice_form)
                    default_invoice_template_lists.append(default_invoice)
                    # default_invoice.save()

                    # Default Credit Invoice Template

                    default_credit_invoice_form = {
                        "name": "default-credit-invoice-template",
                        "category": "invoices",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "event_id": event.id
                    }
                    default_credit_invoice = EmailTemplates(**default_credit_invoice_form)
                    default_invoice_template_lists.append(default_credit_invoice)
                    # default_credit_invoice.save()

                    # Default Receipt Template

                    default_receipt_form = {
                        "name": "default-receipt-template",
                        "category": "invoices",
                        "content": "",
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "event_id": event.id
                    }
                    default_receipt = EmailTemplates(**default_receipt_form)
                    default_invoice_template_lists.append(default_receipt)
                    # default_receipt.save()
                    EmailTemplates.objects.bulk_create(default_invoice_template_lists)

                    # Default Notification Timeout

                    notification_timeout = Setting(name="notification_timeout", value="8:00", event_id=event.id)
                    notification_timeout.save()

                    # Default Time zone

                    default_timezone = Setting(name="timezone", value="Europe/Stockholm", event_id=event.id)
                    default_timezone.save()

                    # Default Week Start with

                    default_week_start_day = Setting(name="week_start_day", value="mon", event_id=event.id)
                    default_week_start_day.save()

                    # Default Third party Plugin Language

                    default_plugin_language = Setting(name="plugin_language", value="en", event_id=event.id)
                    default_plugin_language.save()

                    # Default UID length

                    default_uid_length = Setting(name="uid_length", value="16", event_id=event.id)
                    default_uid_length.save()

                    # Default Session Cookie Expire

                    default_cookie_expire = Setting(name="cookie_expire", value="864000", event_id=event.id)
                    default_cookie_expire.save()

                    # Nest Up Setting

                    appear_next_up_setting = Setting(name="appear_next_up_setting", value="1:00", event_id=event.id)
                    appear_next_up_setting.save()

                    disappear_next_up_setting = Setting(name="disappear_next_up_setting", value="0:15",
                                                        event_id=event.id)
                    disappear_next_up_setting.save()

                    # Evaluation Setting

                    appear_evaluation_setting = Setting(name="appear_evaluation_setting", value="0:10",
                                                        event_id=event.id)
                    appear_evaluation_setting.save()

                    # Default Sender Email

                    default_sender_email = "mahedi@workspaceit.com"
                    sender_email = Setting(name="sender_email", value=default_sender_email, event_id=event.id)
                    sender_email.save()

                    # Create Default Language

                    default_language = Presets.objects.filter(id=6)
                    if default_language.exists():
                        default_event_language = PresetEvent(event_id=event.id, preset_id=default_language[0].id)
                        default_event_language.save()

                    # copy public folder on S3 for newly created event
                    '''
                    session = BotoSession(
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name='eu-west-1'
                    )
                    client = session.client('s3')
                    response = client.list_objects(
                        Bucket='wsit-event-dev',
                        Prefix='public/'
                    )
                    for name in response['Contents']:
                        client.copy_object(
                            ACL='public-read',
                            Bucket='wsit-event-dev',
                            CopySource='wsit-event-dev' + '/' + name['Key'],
                            Key='events/' + event.url + '/' + name['Key']
                        )
                    '''
                    # end copy public folder on S3 for newly created event
                    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
                    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                    extension = 'css'
                    key_name = 'public/' + event.url + '/compiled_css/' + 'style' + '.' + extension
                    k = Key(bucket)
                    k.key = key_name

                    if not k.exists():
                        key = bucket.new_key(key_name)
                        key.content_type = 'text/css'
                        key.set_contents_from_string("", policy='public-read')
                        files_k = bucket.new_key('public/' + event.url + '/files/')
                        files_k.set_contents_from_string("", policy='public-read')
                        offline_package_k = bucket.new_key('public/' + event.url + '/files/offline_package')
                        offline_package_k.set_contents_from_string("", policy='public-read')
                    else:
                        k.content_type = 'text/css'
                        k.set_contents_from_string("", policy='public-read')
                    response_data['event'] = event.as_dict()
                    response_data['success'] = 'Event Create Successfully'
            else:
                response_data['error'] = 'Event already exist'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def create_default_page(default_page, current_admin_id, web_template, event, default_login_email_id,
                            reset_password_email_id, exclude_plugin_settings):
        response = {}
        if default_page.exists():
            start_page_form = {
                "url": default_page[0].url,
                "login_required": default_page[0].login_required,
                "disallow_logged_in": default_page[0].disallow_logged_in,
                "content": default_page[0].content,
                "element_filter": default_page[0].element_filter,
                "created_by_id": current_admin_id,
                "last_updated_by_id": current_admin_id,
                "template_id": web_template.id,
                "event_id": event.id
            }
            start_page = PageContent(**start_page_form)
            start_page.save()
            start_page_element_answers = ElementsAnswers.objects.filter(page_id=default_page[0].id).exclude(
                element_question__question_key__in=exclude_plugin_settings)
            for element_answers in start_page_element_answers:
                element_answers_dict = {
                    "answer": element_answers.answer,
                    "description": element_answers.description,
                    "box_id": element_answers.box_id,
                    "created_by_id": current_admin_id,
                    "last_updated_by_id": current_admin_id,
                    "element_question_id": element_answers.element_question_id,
                    "page_id": start_page.id
                }
                if element_answers.element_question.question_key == 'request_login_email_send':
                    if default_login_email_id != 0:
                        element_answers_dict['answer'] = default_login_email_id
                if element_answers.element_question.question_key == 'reset_password_email_send':
                    if reset_password_email_id != 0:
                        element_answers_dict['answer'] = reset_password_email_id
                start_element_answer_data = ElementsAnswers(**element_answers_dict)
                start_element_answer_data.save()
            start_element_classes = PageContentClasses.objects.filter(page_id=default_page[0].id)
            for element_classes in start_element_classes:
                element_classes_dict = {
                    "box_id": element_classes.box_id,
                    "classname_id": element_classes.classname_id,
                    "page_id": start_page.id
                }
                start_element_classes_data = PageContentClasses(**element_classes_dict)
                start_element_classes_data.save()
            response['page_id'] = start_page.id
        else:
            response['page_id'] = ''
        return response

    def create_default_confirmation(default_confirmation, email_template, current_admin_id, current_language_id):
        response = {}
        if default_confirmation.exists():
            confirmation_form = {
                "subject": default_confirmation[0].subject,
                "subject_lang": str({current_language_id: default_confirmation[0].subject}).replace("'", '"'),
                "name": default_confirmation[0].name,
                "content": default_confirmation[0].content,
                "template_id": email_template.id,
                "created_by_id": current_admin_id,
                "last_updated_by_id": current_admin_id,
            }
            email_confirmation = EmailContents(**confirmation_form)
            email_confirmation.save()
            response['email_id'] = email_confirmation.id
        else:
            response['email_id'] = ''
        return response

    def get_all_events(request):

        if request.session['event_auth_user']['type'] == 'super_admin':
            all_event = Events.objects.filter(is_show=1)
        else:
            all_event = EventAdmin.objects.filter(admin_id=request.session['event_auth_user']['id'], event__is_show=1)

        context = {
            'all_event': all_event,

        }
        return render(request, 'dashboard/events.html', context)

    def change_event(request):
        response_data = {}
        event_id = request.POST.get('event_id')
        eventName = Events.objects.get(id=event_id)
        request.session['event_auth_user']['event_id'] = int(event_id)
        request.session['event_auth_user']['event_name'] = eventName.name
        event_url = eventName.url

        base_url = 'http://127.0.0.1:8003/' + str(event_url)
        request.session['event_auth_user']['event_url'] = event_url
        request.session['event_auth_user']['base_url'] = base_url
        find_users_in_attendee = Attendee.objects.filter(event_id=event_id, email=request.session['event_auth_user']['email'])
        is_attendee = False
        if find_users_in_attendee.exists():
            is_attendee = True
        request.session['event_auth_user']['is_attendee'] = is_attendee
        admin_id = request.session['event_auth_user']['id']

        # update database

        CurrentEvent.objects.filter(admin_id=admin_id).update(event_id=event_id)
        admin_permission = Login.get_admin_permissions(request,event_id,admin_id)
        request.session['admin_permission'] = admin_permission
        request.session.modified = True
        response_data['success'] = 'Change Event Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_events(request):
        response_data = {}
        val = request.POST.get('q')
        event_all = Events.objects.values('name', 'id').filter(name__icontains=val, is_show=1)
        events = event_all.all()
        event_list = []
        for event in events:
            arr_data = {}
            arr_data['id'] = event['id']
            arr_data['text'] = event['name']
            event_list.append(arr_data)
        response_data['results'] = event_list
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def check_permissions(request, content):
        access = False
        try:
            if "event_auth_user" in request.session:
                if request.session['event_auth_user']['type'] == 'super_admin':
                    access = True
                else:
                    if content in request.session['admin_permission']['content_permission'] and \
                                    request.session['admin_permission']['content_permission'][content][
                                        'access_level'] == 'write':
                        access = True
        except Exception as e:
            ErrorR.efail(e)
        return access

    def check_read_permissions(request, content):
        access = False
        try:
            if "event_auth_user" in request.session:
                if request.session['event_auth_user']['type'] == 'super_admin':
                    access = True
                else:
                    if content in request.session['admin_permission']['content_permission']:
                        if request.session['admin_permission']['content_permission'][content]['access_level'] == 'write' or request.session['admin_permission']['content_permission'][content]['access_level'] == 'read':
                            access = True
        except Exception as e:
            ErrorR.efail(e)
        if access:
            return access
        else:
            raise Http404

    def delete(request):
        response_data = {}
        try:
            event_id = request.POST.get('id')
            if str(event_id) == '1':
                response_data['warning'] = "You can't delete the Default Project"
            elif str(event_id) == str(request.session['event_auth_user']['event_id']):
                response_data['warning'] = "You can't delete you current event. Please change your event first"
            else:
                MessageHistory.objects.filter(activityhistory__event_id=event_id).delete()
                Cookie.objects.filter(cookiepage__page__event_id=event_id).delete()
                Events.objects.get(id=event_id).delete()
                response_data['success'] = "Event Deleted Successfully"
        except Exception as e:
            ErrorR.efail(e)
            response_data['error'] = "Something went wrong. Please try again"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def attendee_logged_in(request):
        response_data = {}
        try:
            email = request.POST.get('email')
            event_id = request.POST.get('event_id')
            attendee = Attendee.objects.filter(email=email, event_id=event_id)
            if attendee.exists():
                already_logged_in = True
                if 'event_user' in request.session:
                    if request.session['event_user']['email'] != attendee[0].email:
                        already_logged_in = False
                else:
                    already_logged_in = False
                if already_logged_in:
                    response_data['success'] = True
                else:
                    if EventView.add_public_logged_in_data(request, event_id, attendee[0]):
                        response_data['success'] = True
                    else:
                        response_data['success'] = False
            else:
                response_data['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def attendee_logged_out(request):
        response_data = {}
        try:
            if 'is_user_login' in request.session:
                del request.session['is_user_login']
            if 'event_user' in request.session:
                del request.session['event_user']
            if 'language_id' in request.session:
                del request.session['language_id']
            if 'event_id' in request.session:
                del request.session['event_id']
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add_public_logged_in_data(request, event_id, attendee):
        success = True
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                user_key = attendee.secret_key
                if user_key != request.session['event_user']['secret_key']:
                    del request.session['event_user']
                    del request.session['is_user_login']
                    first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                        user_id=attendee.id)
                    last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                       user_id=attendee.id)
                    attending = 'Yes'
                    if first_name.exists():
                        fname = first_name[0].value
                    else:
                        fname = attendee.firstname
                    if last_name.exists():
                        lname = last_name[0].value
                    else:
                        lname = attendee.lastname
                    avatar = ''
                    type = attendee.type
                    if SeminarSpeakers.objects.filter(speaker_id=attendee.id).count() > 0:
                        type = "speaker"
                    auth_user = {
                        "id": attendee.id,
                        "name": fname + ' ' + lname,
                        "email": attendee.email,
                        "type": type,
                        "attending": attending,
                        "avatar": avatar,
                        "secret_key": attendee.secret_key,
                        "event_id": attendee.event_id
                    }
                    request.session['event_user'] = auth_user
                    request.session['event_user']['new_sessions_finished'] = []
                    request.session['event_user']['new_sessions_next_up'] = []
                    request.session['is_user_login'] = True

            else:
                first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                    user_id=attendee.id)
                last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                   user_id=attendee.id)
                attending = 'Yes'
                if first_name.exists():
                    fname = first_name[0].value
                else:
                    fname = attendee.firstname
                if last_name.exists():
                    lname = last_name[0].value
                else:
                    lname = attendee.lastname
                avatar = ''
                type = attendee.type
                if SeminarSpeakers.objects.filter(speaker_id=attendee.id).count() > 0:
                    type = "speaker"
                auth_user = {
                    "id": attendee.id,
                    "name": fname + ' ' + lname,
                    "email": attendee.email,
                    "type": type,
                    "attending": attending,
                    "avatar": avatar,
                    "secret_key": attendee.secret_key,
                    "event_id": attendee.event_id
                }
                request.session['event_user'] = auth_user
                request.session['event_user']['new_sessions_finished'] = []
                request.session['event_user']['new_sessions_next_up'] = []
                request.session['is_user_login'] = True

            request.session['event_id'] = event_id
            request.session.modified = True
        except Exception as e:
            ErrorR.efail(e)
            success = False
        return success

    def check_current_event(request):
        response = {}
        event_id = request.GET.get('event_id')
        current_event = request.session['event_auth_user']['event_id']
        response['change_event'] = False
        if int(event_id) != int(current_event):
            response['change_event'] = True
        return HttpResponse(json.dumps(response), content_type="application/json")

    def copy_language(request, event_id, current_admin_id):
        try:
            language_en = Presets.objects.get(id=6)
            new_en = Presets(preset_name=language_en.preset_name,date_format=language_en.date_format,datetime_format=language_en.datetime_format,language_code=language_en.language_code,time_format=language_en.time_format,datetime_language=language_en.datetime_language, event_id=event_id, created_by_id=current_admin_id)
            new_en.save()

            default_event_language = PresetEvent(event_id=event_id, preset_id=new_en.id)
            default_event_language.save()

            element_language_en = ElementPresetLang.objects.filter(preset_id=6)
            en_lang = []
            for element_lang_en in element_language_en:
                en_lang.append(ElementPresetLang(value=element_lang_en.value,
                                                 element_default_lang_id=element_lang_en.element_default_lang_id,
                                                 preset_id=new_en.id))
            language_se = Presets.objects.get(id=7)
            new_se = Presets(preset_name=language_se.preset_name,date_format=language_se.date_format,datetime_format=language_se.datetime_format,language_code=language_se.language_code,time_format=language_se.time_format,datetime_language=language_se.datetime_language, event_id=event_id, created_by_id=current_admin_id)
            new_se.save()
            element_language_se = ElementPresetLang.objects.filter(preset_id=7)
            se_lang = []
            for element_lang_se in element_language_se:
                se_lang.append(ElementPresetLang(value=element_lang_se.value,
                                                 element_default_lang_id=element_lang_se.element_default_lang_id,
                                                 preset_id=new_se.id))
            languages = en_lang + se_lang
            ElementPresetLang.objects.bulk_create(languages)
        except Exception as e:
            print(e)
        return ""


class EventDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return Events.objects.get(pk=pk)
        except Events.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        event = Events.objects.get(pk=pk)
        event_admins = EventAdmin.objects.filter(event_id=pk)
        admin_list = []
        for admin in event_admins:
            admin_data = {}
            admin_data['id'] = admin.admin.id
            admin_data['text'] = admin.admin.firstname + ' ' + admin.admin.lastname
            admin_list.append(admin_data)
        response = {
            'success': True,
            'event': event.as_dict(),
            'admin_list': admin_list
        }
        return HttpResponse(json.dumps(response), content_type='application/json')


class Mailer():
    from_addr = settings.EMAIL_SENDER
    subject = ""
    to = ""

    def __init__(self, subject, to, from_addr=settings.EMAIL_SENDER):
        self.from_addr = from_addr
        self.subject = subject
        self.to = to
        access_key = settings.AWS_ACCESS_KEY_ID
        secret_key = settings.AWS_SECRET_ACCESS_KEY
        region = settings.SES_REGION
        self.conn = boto.ses.connect_to_region(
            region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    def send(self, message):
        # call this to send an email
        # it takes html string as a message
        from_email_address = self.from_addr
        subject = self.subject
        to = self.to
        if settings.LOCAL_ENV:
            to = 'workspaceinfotech@gmail.com'
        self.conn.send_email(
            from_email_address,
            subject,
            message,
            to,
            format='html'
        )


class PrintView():
    def printPage(request):
        questionGroup = GroupView.get_questionGroup(request)
        for group in questionGroup:
            group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
        context = {'question_groups': questionGroup}
        return render(request, 'print/index.html', context)


from django_datatables_view.base_datatable_view import BaseDatatableView


class AttendeeListJson(BaseDatatableView):
    # The model we're going to show
    model = Attendee
    columns = ['firstname', 'lastname', 'email', '']
    order_columns = ['photo']
    max_display_length = 50

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(attendee__event_id=self.get_event_id(), is_approved=1)

    def get_event_id(self):
        return self.request.session['event_user']['event_id']


class DescriptionView(generic.DetailView):
    def show_description_preview(request):
        from .template_view import EmailTemplateView
        from django.conf import settings
        content = request.POST.get('content')
        event_id = request.session['event_auth_user']['event_id']
        event_url = request.session['event_auth_user']['event_url']
        css_version_obj = StyleSheet.objects.get(event_id=event_id)
        css_version = css_version_obj.version
        styles = EmailTemplateView.get_style(event_id)
        style_files = ""
        for style in styles['css']:
            style_files += """<link rel="stylesheet" type="text/css" href='""" + style + """' />"""
        content = style_files + content
        # For Wsit S3
        content = content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
        content = content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
        content = content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))

        # For Wsit Event
        # content = content.replace('[[file]]', "[[static]]public/files")
        # content = content.replace('[[files]]', "[[static]]public/files/")
        # content = content.replace('[[css]]',
        #                           "[[static]]public/compiled_css/style.css?v=" + str(css_version))

        content = content.replace('[[static]]', settings.STATIC_URL_ALT)
        content = content.replace('[[event_url]]', event_url)
        content = content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
        base_url = request.session['event_auth_user']['base_url']
        webcal_url = base_url.replace('https:','webcal:')
        webcal_url = base_url.replace('http:','webcal:')
        calendar_content = webcal_url + "/webcal/?uid={secret_key}"
        content = content.replace('{calendar}', calendar_content)
        context = {
            'email_contents': content
        }
        return render(request, 'message/description_preview.html', context)


class TimeDetailView(generic.DetailView):
    def utc_to_local(request, date_input):
        setting_timezone = Setting.objects.filter(name='timezone',
                                                  event_id=request.session['event_auth_user']['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value

        import datetime
        import pytz
        from pytz import timezone
        date_input = date_input.split('.')[0].split('+')[0]
        unaware_est = datetime.datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
        utctz = timezone("UTC")
        aware_est = utctz.localize(unaware_est)
        convertedtz = timezone(tzname)
        convertedtime = aware_est.astimezone(convertedtz)
        return convertedtime
