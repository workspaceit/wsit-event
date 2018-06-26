from datetime import datetime
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views import generic
from app.models import Travel, Session, RuleSet, \
    Answers, TravelAttendee, Booking, \
    AttendeeGroups, AttendeeTag, Elements, Presets, PresetEvent, \
    ElementPresetLang, ElementDefaultLang, Photo, Setting, Orders
from app.views.gbhelper.economy_library import EconomyLibrary
from app.views.gbhelper.error_report_helper import ErrorR
# from publicfront.views.lang_key import LanguageKey
from .common_views import GroupView
import re
import json
import os
import qrcode
import base64
import io
from django.conf import settings
from app.views.gbhelper.language_helper import LanguageH
from app.views.gbhelper.details_helper import DetailsH


class EmailContentDetailView(generic.DetailView):

    def show_message_preview(request):
        content = request.POST.get('content')
        base_url = request.session['event_auth_user']['base_url']
        # calendar_content = """<a href=""" + base_url + """/webcal/?uid={secret_key}>""" + base_url + """/webcal/?uid={secret_key}</a>"""
        webcal_url = base_url.replace('https:','webcal:')
        webcal_url = base_url.replace('http:','webcal:')
        calendar_content = webcal_url + "/webcal/?uid={secret_key}"
        content = content.replace('{calendar}', calendar_content)
        Uid_link_content = base_url + """/?uid={secret_key}"""
        content = content.replace('{uid_link}', Uid_link_content)
        context = {
            'email_contents': content
        }
        return render(request, 'message/email_preview.html', context)

    def get_filterGroup(request):
        filterGroup = GroupView.get_filterGroup(request)
        for group in filterGroup:
            group.filters = RuleSet.objects.all().filter(group_id=group.id)
        return filterGroup

    def get_sessions_data_by_attendee(request, sessions, session_rules, attendee, language_id, language):
        context = DetailsH.get_sessions_data_by_attendee(attendee.event_id, language_id, sessions, session_rules, attendee.id, language)
        # element = Elements.objects.filter(slug="sessions")
        # language = EmailContentDetailView.get_lang_key(request, element[0].id, 0, attendee.event_id)
        # for session in sessions:
        #     session.speakers = SeminarSpeakers.objects.filter(session=session.id)
        #     session.tags = SessionTags.objects.filter(session=session.id)
        #     session.status = ""
        #     status = SeminarsUsers.objects.filter(session_id=session.id, attendee_id=attendee.id)
        #     if status.exists():
        #         session.status = status[0].status
        #
        # context = {
        #     'sessions': sessions,
        #     'session_rules': session_rules,
        #     'preview': False,
        #     "language": language
        # }
        context['preview'] = False
        if language is not None:
            context['language'] = language
        return render_to_string('message/email_sessions.html', context)

    def get_travel_data_by_attendee(request, travels, travel_rules, attendee, language_id):
        # element = Elements.objects.filter(slug="travels")
        # if event_id is not None:
        #     language = EmailContentDetailView.get_lang_key(request, element[0].id, 0, event_id)
        # else:
        #     language = EmailContentDetailView.get_lang_key(request, element[0].id)
        # context = {
        #     'travels': travels,
        #     'travel_rules': travel_rules,
        #     'preview': False,
        #     "language": language
        # }
        context = DetailsH.get_travel_data_by_attendee(attendee.event_id, language_id, travels, travel_rules)
        context['preview'] = False
        return render_to_string('message/email_travels.html', context)

    def get_hotels_data_by_attendee(request, hotels, hotel_rules, attendee, language_id, language):
        # element = Elements.objects.filter(slug="hotels")
        # if event_id is not None:
        #     language = EmailContentDetailView.get_lang_key(request, element[0].id, 0, event_id)
        # else:
        #     language = EmailContentDetailView.get_lang_key(request, element[0].id)
        # for hotel in hotels:
        #     hotel.buddy = RequestedBuddy.objects.filter(booking_id=hotel.id)
        #     actual_buddy = MatchLine.objects.filter(booking_id=hotel.id)
        #     if actual_buddy.exists():
        #         hotel.actualbuddy = MatchLine.objects.filter(match_id=actual_buddy[0].match_id).exclude(
        #             id=actual_buddy[0].id)
        # context = {
        #     'hotels': hotels,
        #     'hotel_rules': hotel_rules,
        #     'preview': False,
        #     "language": language
        # }
        context = DetailsH.get_hotels_data_by_attendee(attendee.event_id, language_id, hotels, hotel_rules, attendee.id, language)
        context['preview'] = False
        if language is not None:
            context['language'] = language
        return render_to_string('message/email_hotels.html', context)

    def get_question_data_by_attendee(request, questionAnswer, question_rules, attendee, language_id):
        context = DetailsH.get_question_data_by_attendee(attendee.event_id, language_id, questionAnswer, question_rules)
        # element = Elements.objects.filter(slug="questions")
        # if event_id is None:
        #     language = EmailContentDetailView.get_lang_key(request, element[0].id)
        # else:
        #     language = EmailContentDetailView.get_lang_key(request, element[0].id, 0, event_id)
        # context = {
        #     'questionAnswer': questionAnswer,
        #     'question_rules': question_rules,
        #     'preview': False,
        #     "language": language
        # }
        context['preview'] = False
        return render_to_string('message/email_question.html', context)

    def replace_questions_variable(request, message, attendee, language_id, default_date_time_format=None, preview=False):
        if attendee:
            event_id = attendee.event_id
        else:
            event_id = request.session['event_auth_user']['event_id']
        # default_date_format = EmailContentDetailView.get_default_date_format(event_id)
        if default_date_time_format is None:
            default_date_time_format = EmailContentDetailView.get_language_date_format(event_id)
        default_date_format = default_date_time_format['default_datetime']
        question_default = '{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"' + default_date_format + '"}]}'
        if '{"questions"}' in message:
            message = message.replace('{"questions"}', question_default)
        question_regex = r"({\"questions\":)(.|\s|\n)*?(]})"
        question_matches = re.finditer(question_regex, message)

        for question_match in question_matches:
            attendee_questions = ""
            question_id = []
            question_group_id = []
            question_rules = {}
            question_json_data = json.loads(question_match.group())
            if "id" in question_json_data["questions"][0]:
                question_id = [int(s) for s in question_json_data["questions"][0]["id"].split(',') if
                               s.isdigit()]
                question_rules["data_title"] = question_json_data["questions"][0]["id"].split(',')
            if 'group-id' in question_json_data["questions"][0]:
                if question_json_data["questions"][0]['group-id'] != "":
                    question_group_id = [int(s) for s in question_json_data["questions"][0]["group-id"].split(',') if
                                         s.isdigit()]
            if 'columns' in question_json_data["questions"][0]:
                question_columns = question_json_data["questions"][0]['columns']
                question_rules["columns"] = question_columns
            if 'date-time' in question_json_data["questions"][0]:
                question_time_date = question_json_data["questions"][0]['date-time']
                question_rules["timedate"] = question_time_date
            question_rules["now"] = datetime.now()

            if preview:
                attendee_questions = EmailContentDetailView.get_question_data_preview(request, {True},
                                                                                      question_rules,
                                                                                      True)
                message = message.replace(question_match.group(), attendee_questions)
            else:
                # ****QUESTION START****
                questionAnswer = {}
                questionAnswer["registration_date"] = attendee.created
                questionAnswer["last_update_date"] = attendee.updated
                attendee_groups_data = AttendeeGroups.objects.filter(attendee_id=attendee.id)
                attendee_groups_list = []
                for attendee_group in attendee_groups_data:
                    attendee_group.group = LanguageH.get_group_data_by_language(attendee.language_id, attendee_group.group)
                    attendee_groups_list.append(attendee_group.group.name)
                attendee_groups = ','.join(attendee_groups_list)
                tags_data = AttendeeTag.objects.filter(attendee_id=attendee.id)
                tags = ','.join(tag.tag.name for tag in tags_data)
                questionAnswer["attendee_groups"] = attendee_groups
                questionAnswer["tags"] = tags
                if len(question_id):
                    if (len(question_group_id)):
                        answers = Answers.objects.filter(question_id__in=question_id, user_id=attendee.id,
                                                         question__group_id__in=question_group_id)
                    else:
                        answers = Answers.objects.filter(question_id__in=question_id, user_id=attendee.id)
                else:
                    if (len(question_group_id)):
                        answers = Answers.objects.filter(user_id=attendee.id, question__group_id__in=question_group_id)
                    else:
                        answers = Answers.objects.filter(user_id=attendee.id)
                if answers:
                    questionAnswer["answers"] = answers
                    attendee_questions = EmailContentDetailView.get_question_data_by_attendee(request,
                                                                                              questionAnswer,
                                                                                              question_rules, attendee, language_id)
                message = message.replace(question_match.group(), attendee_questions)
                # ****QUESTION END****
        return message

    def replace_sessions(request, message, attendee, language_id, language=None, default_date_time_format=None, preview=False):
        if attendee:
            event_id = attendee.event_id
        else:
            event_id = request.session['event_auth_user']['event_id']
        # default_date_format = EmailContentDetailView.get_default_date_format(event_id)
        if default_date_time_format is None:
            default_date_time_format = EmailContentDetailView.get_language_date_format(event_id)
        default_date_format = default_date_time_format['default_datetime']
        session_default = '{"sessions":[{"columns":"name,start,end","sort-column":"start","status":"attending","time-date":"' + default_date_format + '"}]}'
        if '{"sessions"}' in message:
            message = message.replace('{"sessions"}', session_default)
        session_regex = r"({\"sessions\":)(.|\s|\n)*?(]})"
        session_matches = re.finditer(session_regex, message)

        for session_match in session_matches:
            attendee_sessions = ""
            session_id = []
            session_group_id = []
            session_rules = {}
            session_obj = Session.objects.filter(group__event_id=event_id)
            session_json_data = json.loads(session_match.group())
            if 'id' in session_json_data["sessions"][0]:
                if session_json_data["sessions"][0]['id'] != "":
                    session_id = session_json_data["sessions"][0]['id'].split(',')
                    if len(session_id):
                        session_obj = session_obj.filter(id__in=session_id)
            if 'group-id' in session_json_data["sessions"][0]:
                if session_json_data["sessions"][0]['group-id'] != "":
                    session_group_id = session_json_data["sessions"][0]['group-id'].split(',')
                    if len(session_group_id):
                        session_obj = session_obj.filter(group__in=session_group_id)
            if 'columns' in session_json_data["sessions"][0]:
                session_columns = session_json_data["sessions"][0]['columns']
                session_rules["columns"] = session_columns
            if 'sort-column' in session_json_data["sessions"][0]:
                session_sort_column = session_json_data["sessions"][0]['sort-column']
                if session_sort_column == "name":
                    session_obj = session_obj.order_by("name")
                elif session_sort_column == "group":
                    session_obj = session_obj.order_by("group__group_order")
                elif session_sort_column == "start":
                    session_obj = session_obj.order_by("start")
                elif session_sort_column == "end":
                    session_obj = session_obj.order_by("end")
                elif session_sort_column == "order":
                    session_obj = session_obj.order_by("session_order")
            if 'status' in session_json_data["sessions"][0]:
                if session_json_data["sessions"][0]['status'] != "":
                    session_status = session_json_data["sessions"][0]['status'].split(',')
                    session_rules["status"] = session_status
            if 'time-date' in session_json_data["sessions"][0]:
                session_time_date = session_json_data["sessions"][0]['time-date']
                session_rules["timedate"] = session_time_date
            session_rules["now"] = datetime.now()
            # ****SESSION START****
            if preview:
                attendee_sessions = EmailContentDetailView.get_sessions_data_preview(request, {True}, session_rules,
                                                                                     True)
                message = message.replace(session_match.group(), attendee_sessions)
            else:
                session_obj2 = session_obj
                if "status" in session_rules and "always" not in session_rules["status"]:
                    session_obj2 = session_obj2.filter(seminarsusers__status__in=session_rules["status"],
                                                       seminarsusers__attendee_id=attendee.id)
                if session_obj2:
                    attendee_sessions = EmailContentDetailView.get_sessions_data_by_attendee(request,
                                                                                             session_obj2,
                                                                                             session_rules,
                                                                                             attendee, language_id, language)
                message = message.replace(session_match.group(), attendee_sessions)
                # ****SESSION END****
        return message

    def replace_travels(request, message, attendee, language_id, default_date_time_format=None, preview=False):
        if attendee:
            event_id = attendee.event_id
        else:
            event_id = request.session['event_auth_user']['event_id']
        # default_date_format = EmailContentDetailView.get_default_date_format(event_id)
        if default_date_time_format is None:
            default_date_time_format = EmailContentDetailView.get_language_date_format(event_id)
        default_date_format = default_date_time_format['default_datetime']
        travel_default = '{"travels":[{"columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"' + default_date_format + '"}]}'
        if '{"travels"}' in message:
            message = message.replace('{"travels"}', travel_default)
        travel_regex = r"({\"travels\":)(.|\s|\n)*?(]})"
        travel_matches = re.finditer(travel_regex, message)

        for travel_match in travel_matches:
            attendee_travels = ""
            travel_id = []
            travel_group_id = []
            travel_rules = {}
            travel_obj = Travel.objects.filter(group__event_id=event_id)
            travel_json_data = json.loads(travel_match.group())
            if 'id' in travel_json_data["travels"][0]:
                if travel_json_data["travels"][0]['id'] != "":
                    travel_id = travel_json_data["travels"][0]['id'].split(',')
                    if len(travel_id):
                        travel_obj = travel_obj.filter(id__in=travel_id)
            if 'group-id' in travel_json_data["travels"][0]:
                if travel_json_data["travels"][0]['group-id'] != "":
                    travel_group_id = travel_json_data["travels"][0]['group-id'].split(',')
                    if len(travel_group_id):
                        travel_obj = travel_obj.filter(group__in=travel_group_id)
            if 'columns' in travel_json_data["travels"][0]:
                travel_columns = travel_json_data["travels"][0]['columns']
                travel_rules["columns"] = travel_columns
            if 'sort-column' in travel_json_data["travels"][0]:
                travel_sort_column = travel_json_data["travels"][0]['sort-column']
                if travel_sort_column == "departure-date-time":
                    travel_obj = travel_obj.order_by("departure")
                elif travel_sort_column == "arrival-date-time":
                    travel_obj = travel_obj.order_by("arrival")
                elif travel_sort_column == "arrival-city":
                    travel_obj = travel_obj.order_by("arrival_city")
                elif travel_sort_column == "departure-city":
                    travel_obj = travel_obj.order_by("departure_city")
                elif travel_sort_column == "group":
                    travel_obj = travel_obj.order_by("group")
                elif travel_sort_column == "order":
                    travel_obj = travel_obj.order_by("travel_order")
                elif travel_sort_column == "name":
                    travel_obj = travel_obj.order_by("name")
            if 'date-time' in travel_json_data["travels"][0]:
                travel_time_date = travel_json_data["travels"][0]['date-time']
                travel_rules["timedate"] = travel_time_date
            travel_rules["now"] = datetime.now()

            if preview:
                attendee_travels = EmailContentDetailView.get_travel_data_preview(request, {True},
                                                                                  travel_rules,
                                                                                  True)
                message = message.replace(travel_match.group(), attendee_travels)
            else:
                # ****TRAVEL START****
                travel_filter_by_attendee = TravelAttendee.objects.filter(attendee=attendee.id).values_list(
                    'travel', flat=True)
                travel_obj2 = travel_obj
                travel_obj2 = travel_obj2.filter(id__in=travel_filter_by_attendee)
                if travel_obj2:
                    attendee_travels = EmailContentDetailView.get_travel_data_by_attendee(request, travel_obj2,
                                                                                          travel_rules, attendee, language_id)
                message = message.replace(travel_match.group(), attendee_travels)
                # ****TRAVEL END****
        return message

    def replace_hotels(request, message, attendee, language_id, language=None, default_date_time_format=None, preview=False):
        if attendee:
            event_id = attendee.event_id
        else:
            event_id = request.session['event_auth_user']['event_id']
        # default_date_format = EmailContentDetailView.get_default_date_format(event_id)
        if default_date_time_format is None:
            default_date_time_format = EmailContentDetailView.get_language_date_format(event_id)
        default_date_format = default_date_time_format['default_date']
        hotel_default = '{"hotels":[{"columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"' + default_date_format + '"}]}'
        if '{"hotels"}' in message:
            message = message.replace('{"hotels"}', hotel_default)
        hotel_regex = r"({\"hotels\":)(.|\s|\n)*?(]})"
        hotel_matches = re.finditer(hotel_regex, message)
        for hotel_match in hotel_matches:
            attendee_hotels = ""
            hotel_id = []
            hotel_group_id = []
            hotel_rules = {}
            hotel_obj = Booking.objects.filter(room__hotel__group__event_id=event_id)
            hotel_json_data = json.loads(hotel_match.group())
            if 'id' in hotel_json_data["hotels"][0]:
                if hotel_json_data["hotels"][0]['id'] != "":
                    hotel_id = hotel_json_data["hotels"][0]['id'].split(',')
                    if len(hotel_id):
                        hotel_obj = hotel_obj.filter(room__in=hotel_id)
            if 'group-id' in hotel_json_data["hotels"][0]:
                if hotel_json_data["hotels"][0]['group-id'] != "":
                    hotel_group_id = hotel_json_data["hotels"][0]['group-id'].split(',')
                    if len(hotel_group_id):
                        hotel_obj = hotel_obj.filter(room__hotel__group__in=hotel_group_id)
            if 'columns' in hotel_json_data["hotels"][0]:
                hotel_columns = hotel_json_data["hotels"][0]['columns']
                hotel_rules["columns"] = hotel_columns
            if 'sort-column' in hotel_json_data["hotels"][0]:
                hotel_sort_column = hotel_json_data["hotels"][0]['sort-column']
                if hotel_sort_column == "check-in":
                    hotel_obj = hotel_obj.order_by("check_in")
                elif hotel_sort_column == "check-out":
                    hotel_obj = hotel_obj.order_by("check_out")
                elif hotel_sort_column == "group":
                    hotel_obj = hotel_obj.order_by("room__hotel__group__group_order")
                elif hotel_sort_column == "order":
                    hotel_obj = hotel_obj.order_by("room__room_order")
                elif hotel_sort_column == "name":
                    hotel_obj = hotel_obj.order_by("room__hotel__name")
                elif hotel_sort_column == "room-description":
                    hotel_obj = hotel_obj.order_by("room__description")
            if 'date' in hotel_json_data["hotels"][0]:
                hotel_time_date = hotel_json_data["hotels"][0]['date']
                hotel_rules["timedate"] = hotel_time_date
            hotel_rules["now"] = datetime.now()
            if preview:
                attendee_hotels = EmailContentDetailView.get_hotels_data_preview(request, {True},
                                                                                 hotel_rules,
                                                                                 True)
                message = message.replace(hotel_match.group(), attendee_hotels)
            else:
                # ****BOOKING START****
                hotel_obj2 = hotel_obj
                hotel_obj2 = hotel_obj2.filter(attendee=attendee.id)
                if hotel_obj2:
                    attendee_hotels = EmailContentDetailView.get_hotels_data_by_attendee(request,
                                                                                         hotel_obj2,
                                                                                         hotel_rules, attendee, language_id, language)
                message = message.replace(hotel_match.group(), attendee_hotels)
                # ****BOOKING END****
        return message

    def replace_general_tags(request, message, attendee, language_id, preview=False):
        if attendee:
            event_id = attendee.event_id
            base_url = EmailContentDetailView.get_base_url(request, attendee.event.url)
        else:
            event_id = request.session['event_auth_user']['event_id']
            base_url = request.session['event_auth_user']['base_url']
        registration_date = ""
        updated_date = ""
        attendee_groups = ""
        tags = ""
        uid = ''
        bid = ''
        bidqr = ''
        first_name = ''
        last_name = ''
        email_address = ''
        if attendee:
            # if '{base_url}' in message:
            #     base_url = EmailContentDetailView.get_base_url(request, attendee.event.url)
            if '{first_name}' in message:
                first_name = str(attendee.firstname)
            if '{last_name}' in message:
                last_name = str(attendee.lastname)
            if '{email_address}' in message:
                email_address = str(attendee.email)
            if '{registration_date}' in message:
                registration_date = str(attendee.created)
            if '{updated_date}' in message:
                updated_date = str(attendee.updated)
            if '{attendee_groups}' in message:
                attendee_groups_data = AttendeeGroups.objects.filter(attendee_id=attendee.id)
                attendee_groups_list = []
                for attendee_group in attendee_groups_data:
                    attendee_group.group = LanguageH.get_group_data_by_language(language_id, attendee_group.group)
                    attendee_groups_list.append(attendee_group.group.name)
                attendee_groups = ','.join(attendee_groups_list)
                # attendee_groups = ','.join(attendee_group.group.name for attendee_group in attendee_groups_data)
            if '{tags}' in message:
                tags_data = AttendeeTag.objects.filter(attendee_id=attendee.id)
                tags = ','.join(tag.tag.name for tag in tags_data)
            # if '{uid}' in message:
            uid = attendee.secret_key
            # if '{bid}' in message:
            bid = attendee.bid
            if '{bidqr}' in message:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=2
                )
                qr.add_data(bid)
                qr.make(fit=True)
                img = qr.make_image()
                output = io.BytesIO()
                img.save(output, format='PNG')
                output.seek(0)
                output_s = output.read()
                b64 = base64.b64encode(output_s).decode("utf-8")
                bidqr = b64
        elif preview:
            base_url = request.session['event_auth_user']['base_url']
            registration_date = "{registration_date}"
            updated_date = "{updated_date}"
            attendee_groups = "{attendee_groups}"
            tags = "{tags}"
            uid = '{uid}'
            bid = '{bid}'
            bidqr = '{bidqr}'
            first_name = '{first_name}'
            last_name = '{last_name}'
            email_address = '{email_address}'
        # else:
        #     base_url = request.session['event_auth_user']['base_url']
        #     registration_date = ""
        #     updated_date = ""
        #     attendee_groups = ""
        #     tags = ""
        #     uid = ''
        #     bid = ''
        #     bidqr = ''
        #     first_name = ''
        #     last_name = ''
        #     email_address = ''
        uid_link = base_url + """/?uid={uid}"""
        # calender_content = """<a href=""" + base_url + """/webcal/?uid={uid}>""" + base_url + """/webcal/?uid={uid}</a>"""
        webcal_url = base_url.replace('https:','webcal:')
        webcal_url = base_url.replace('http:','webcal:')
        calender_content = webcal_url + "/webcal/?uid={uid}"
        message_link = "{base_url}/messages/?uid={uid}"
        message = message.replace('{messages_link}', message_link)
        message = message.replace('{registration_date}', registration_date)
        message = message.replace('{updated_date}', updated_date)
        message = message.replace('{attendee_groups}', attendee_groups)
        message = message.replace('{tags}', tags)
        message = message.replace('{uid_link}', uid_link)
        message = message.replace('{calendar}', calender_content)
        message = message.replace('{first_name}', first_name)
        message = message.replace('{last_name}', last_name)
        message = message.replace('{email_address}', email_address)
        message = message.replace('{uid}', uid)
        bid_link = "{base_url}/qr-to-png?bid={bid}"
        message = message.replace('{bidqr}', '<img src="{0}"/ class="qr-code">'.format(bid_link))
        message = message.replace('{bid}', bid)
        # message = message.replace('{bidqr}', '<img src="data:image/png;base64,{0}"/ class="qr-code">'.format(bidqr))
        message = message.replace('{base_url}', base_url)
        # print(message)
        return message

    def replace_economy_tags(request, message, attendee, language_id, preview=False):
        if attendee:
            event_id = attendee.event_id
        else:
            event_id = request.session['event_auth_user']['event_id']

        order_owner = ""
        order_table = ""
        multiple_order_table = ""
        balance_table = ""
        order_value_paid_order = ""
        multiple_order_value_paid_order = ''
        order_value_pending_order = ''
        multiple_order_value_pending_order = ''
        order_value_open_order = ''
        multiple_order_value_open_order = ''
        order_value_all_order = ''
        multiple_order_value_all_order = ''
        order_value_credit_order = ''
        multiple_order_value_credit_order = ''
        receipt= ''

        if attendee:
            language = LanguageH.catch_lang_key_obj(event_id, language_id, 'economy')
            # generating order owner tag
            order_owner_regex = r"({order_owner})"
            oder_owner_matches = re.findall(order_owner_regex, message)
            if len(oder_owner_matches) > 0:
                user_id = attendee.id
                orders = Orders.objects.filter(attendee_id=user_id).exclude(status='cancelled')
                if orders.exists():
                    if orders[0].attendee.registration_group:
                        owner = orders[0].attendee.registration_group.registrationgroupowner_set.get().owner
                        order_owner = owner.firstname + ' ' + owner.lastname
                    else:
                        order_owner = orders[0].attendee.firstname + ' ' + orders[0].attendee.lastname
            else:
                order_owner = ''
            # generating order table tag
            order_table_regex = r"({order_table})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                context = {}
                user_id = attendee.id

                economy_data = EconomyLibrary.get_order_tables(user_id, event_id, True)
                if economy_data['order_type'] == 'attendee-order':
                    orders = economy_data['order_list']
                else:
                    orders = []

                context['language'] = language
                context['orders'] = orders
                context['order_table_type'] = 'attendee-order'
                order_table = render_to_string('public/tags/order_table_tag.html', context)

            else:
                order_table = ''

            # generating multiple order table tag
            order_table_regex = r"({multiple_order_table})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                context = {}
                user_id = attendee.id

                economy_data = EconomyLibrary.get_order_tables(user_id, event_id, True)
                if economy_data['order_type'] == 'group-order':
                    orders = economy_data['order_list']
                else:
                    orders = []

                context['language'] = language
                context['orders'] = orders
                # context['order_table_type'] = 'attendee-order'
                multiple_order_table = render_to_string('public/tags/order_table_tag.html', context)

            else:
                multiple_order_table = ''

            # generating balance table tag
            order_table_regex = r"({balance_table})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                context = {}
                user_id = attendee.id
                balance_tables = EconomyLibrary.get_balance_tables(user_id, event_id)
                context['language'] = language
                context['balance_tables'] = balance_tables
                context['download'] = False
                # context['order_table_type'] = 'attendee-order'
                balance_table = render_to_string('public/tags/balance_table_tag.html', context)

            else:
                balance_table = ''

            # generating order value paid order tag
            order_table_regex = r"({order_value_paid_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'paid')
                if value is not None:
                    order_value_paid_order = str(value)
                else:
                    order_value_paid_order = str(0)

            else:
                order_value_paid_order = ''

            # generating multiple order value paid order tag
            order_table_regex = r"({multiple_order_value_paid_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'paid', 'group-order')
                if value is not None:
                    multiple_order_value_paid_order = str(value)
                else:
                    multiple_order_value_paid_order = str(0)

            else:
                multiple_order_value_paid_order = ''

            # generating order value pending order tag
            order_table_regex = r"({order_value_pending_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'pending')
                if value is not None:
                    order_value_pending_order = str(value)
                else:
                    order_value_pending_order = str(0)
            else:
                order_value_pending_order = ''

            # generating multiple order value pending order tag
            order_table_regex = r"({multiple_order_value_pending_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'pending', 'group-order')
                if value is not None:
                    multiple_order_value_pending_order = str(value)
                else:
                    multiple_order_value_pending_order = str(0)
            else:
                multiple_order_value_pending_order = ''

            # generating order value open order tag
            order_table_regex = r"({order_value_open_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'open')
                if value is not None:
                    order_value_open_order = str(value)
                else:
                    order_value_open_order = str(0)

            else:
                order_value_open_order = ''

            # generating multiple order value open order tag
            order_table_regex = r"({multiple_order_value_open_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'open', 'group-order')
                if value is not None:
                    multiple_order_value_open_order = str(value)
                else:
                    multiple_order_value_open_order = str(0)
            else:
                multiple_order_value_open_order = ''

            # generating order value all order tag
            order_table_regex = r"({order_value_all_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'all')
                if value is not None:
                    order_value_all_order = str(value)
                else:
                    order_value_all_order = str(0)
            else:
                order_value_all_order = ''

            # generating multiple order value all order tag
            order_table_regex = r"({multiple_order_value_all_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'all', 'group-order')
                if value is not None:
                    multiple_order_value_all_order = str(value)
                else:
                    multiple_order_value_all_order = str(0)

            else:
                multiple_order_value_all_order = ''

            # generating order value credit order tag
            order_table_regex = r"({order_value_credit_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'open', 'attendee-order', 'credit-order')
                if value is not None:
                    order_value_credit_order = str(value)
                else:
                    order_value_credit_order = str(0)
            else:
                order_value_credit_order = ''

            # generating multiple order value credit order tag
            order_table_regex = r"({multiple_order_value_credit_order})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                user_id = attendee.id
                value = EconomyLibrary.get_order_value(user_id, 'open', 'group-order', 'credit-order')
                if value is not None:
                    multiple_order_value_credit_order = str(value)
                else:
                    multiple_order_value_credit_order = str(0)
            else:
                multiple_order_value_credit_order = ''

            # generating receipt tag
            order_table_regex = r"({receipt})"
            oder_table_matches = re.findall(order_table_regex, message)
            if len(oder_table_matches) > 0:
                context = {}
                user_id = attendee.id
                event_id = attendee.event_id
                value = EconomyLibrary.get_receipt_data(event_id, user_id)
                context['language'] = language
                context['receipts'] = value
                # # context['order_table_type'] = 'attendee-order'
                receipt = render_to_string('public/tags/receipt_tag.html', context)

            else:
                receipt = ''



        elif preview:
            order_owner = "{order_owner}"
            order_table = "{order_table}"
            multiple_order_table = "{multiple_order_table}"
            balance_table = "{balance_table}"
            order_value_paid_order = "{order_value_paid_order}"
            multiple_order_value_paid_order = '{multiple_order_value_paid_order}'
            order_value_pending_order = '{order_value_pending_order}'
            multiple_order_value_pending_order = '{multiple_order_value_pending_order}'
            order_value_open_order = '{order_value_open_order}'
            multiple_order_value_open_order = '{multiple_order_value_open_order}'
            order_value_all_order = '{order_value_all_order}'
            multiple_order_value_all_order = '{multiple_order_value_all_order}'
            order_value_credit_order = '{order_value_credit_order}'
            multiple_order_value_credit_order = '{multiple_order_value_credit_order}'
            receipt = '{receipt}'
        else:
            order_owner = ""
            order_table = ""
            multiple_order_table = ""
            balance_table = ""
            order_value_paid_order = ""
            multiple_order_value_paid_order = ''
            order_value_pending_order = ''
            multiple_order_value_pending_order = ''
            order_value_open_order = ''
            multiple_order_value_open_order = ''
            order_value_all_order = ''
            multiple_order_value_all_order = ''
            order_value_credit_order = ''
            multiple_order_value_credit_order = ''
            receipt=''

        message = message.replace('{order_owner}', order_owner)
        message = message.replace('{order_table}', order_table)
        message = message.replace('{multiple_order_table}', multiple_order_table)
        message = message.replace('{balance_table}', balance_table)
        message = message.replace('{order_value_paid_order}', order_value_paid_order)
        message = message.replace('{multiple_order_value_paid_order}', multiple_order_value_paid_order)
        message = message.replace('{order_value_pending_order}', order_value_pending_order)
        message = message.replace('{multiple_order_value_pending_order}', multiple_order_value_pending_order)
        message = message.replace('{order_value_open_order}', order_value_open_order)
        message = message.replace('{multiple_order_value_open_order}', multiple_order_value_open_order)
        message = message.replace('{order_value_all_order}', order_value_all_order)
        message = message.replace('{multiple_order_value_all_order}', multiple_order_value_all_order)
        message = message.replace('{order_value_credit_order}', order_value_credit_order)
        message = message.replace('{multiple_order_value_credit_order}', multiple_order_value_credit_order)
        message = message.replace('{receipt}', receipt)
        return message

    def replace_general_message_tags(request, message, attendee, preview=False):
        if attendee:
            event_id = attendee.event_id
        else:
            event_id = request.session['event_auth_user']['event_id']
        base_url = request.session['event_auth_user']['base_url']
        if attendee:
            first_name = str(attendee.firstname)
            last_name = str(attendee.lastname)
            email_address = str(attendee.email)
            registration_date = str(attendee.created)
            updated_date = str(attendee.updated)
            attendee_groups_data = AttendeeGroups.objects.filter(attendee_id=attendee.id)
            attendee_groups_list = []
            for attendee_group in attendee_groups_data:
                attendee_group.group = LanguageH.get_group_data_by_language(attendee.language_id, attendee_group.group)
                attendee_groups_list.append(attendee_group.group.name)
            attendee_groups = ','.join(attendee_groups_list)
            # attendee_groups = ','.join(attendee_group.group.name for attendee_group in attendee_groups_data)
            tags_data = AttendeeTag.objects.filter(attendee_id=attendee.id)
            tags = ','.join(tag.tag.name for tag in tags_data)
            uid = attendee.secret_key
            bid = attendee.bid
        elif preview:
            registration_date = "{registration_date}"
            updated_date = "{updated_date}"
            attendee_groups = "{attendee_groups}"
            tags = "{tags}"
            uid = '{uid}'
            bid = '{bid}'
            first_name = '{first_name}'
            last_name = '{last_name}'
            email_address = '{email_address}'
        else:
            registration_date = ""
            updated_date = ""
            attendee_groups = ""
            tags = ""
            uid = ''
            bid = ''
            first_name = ''
            last_name = ''
            email_address = ''

        uid_link = base_url + """/?uid={uid}"""
        webcal_url = base_url.replace('https:','webcal:')
        webcal_url = base_url.replace('http:','webcal:')
        calender_content = webcal_url + """/webcal/?uid={uid}"""

        message = message.replace('{registration_date}', registration_date)
        message = message.replace('{updated_date}', updated_date)
        message = message.replace('{attendee_groups}', attendee_groups)
        message = message.replace('{tags}', tags)
        message = message.replace('{uid_link}', uid_link)
        message = message.replace('{calendar}', calender_content)

        message = message.replace('{first_name}', first_name)
        message = message.replace('{last_name}', last_name)
        message = message.replace('{email_address}', email_address)

        message = message.replace('{uid}', uid)
        message = message.replace('{bid}', bid)

        return message

    def replace_general_questions(request, message, attendee, language_id, preview=False):
        try:
            questions = []
            match = re.findall("qid:\d+", message)
            for q in match:
                data = {
                    'qid': q.split(':')[1]
                }
                questions.append(data)
            if attendee:
                for question in questions:
                    answer = Answers.objects.filter(question_id=question['qid'], user_id=attendee.id)
                    if answer.exists():
                        answer_data = DetailsH.get_answer_data_by_attendee(attendee.event_id, language_id, answer[0])
                        message = message.replace('{qid:' + question['qid'] + '}', answer_data.value)
                    else:
                        # message = message.replace('{qid:' + question['qid'] + '}', 'N/A')
                        message = message.replace('{qid:' + question['qid'] + '}', '')
            elif not preview:
                for question in questions:
                    message = message.replace('{qid:' + question['qid'] + '}', '')
            return message
        except Exception as e:
            print(e)
            return message

    def replace_photos(request, pageContents, attendee, language_id, preview=False):
        message = pageContents
        photo_regex = r"({\"photo\":)(.|\s|\n)*?(]})"
        try:
            photo_default = '{"photo":[{"groups":""}]}'
            if '{"photo"}' in message:
                message = message.replace('{"photo"}', photo_default)
            photo_matches = re.finditer(photo_regex, message)
            for photo_match in photo_matches:
                photo_json_data = json.loads(photo_match.group())
                if "group" in photo_json_data['photo'][0] and photo_json_data['photo'][0]['group'] != '':
                    photo_groups = photo_json_data['photo'][0]['group'].split(',')
                    photos = Photo.objects.filter(group__name__in=photo_groups)
                    if photos:
                        photo_lists = []
                        for photo in photos:
                            photo_lists.append({
                                'photo_id': photo.id,
                                'src': settings.STATIC_URL_ALT + photo.thumb_image,
                                'group': re.sub(r"\s+", '-', photo.group.name)
                            })
                        context = {
                            'photos': photo_lists,
                        }
                        photo_tag = render_to_string('public/element/photo_tag.html', context)
                        message = message.replace(photo_match.group(),
                                                  '<div class="variable-tag">' + photo_tag + '</div>')
                    else:
                        message = message.replace(photo_match.group(), "")
                else:
                    message = message.replace(photo_match.group(), "")
            return message
        except Exception as e:
            print(e)
            photo_matches = re.finditer(photo_regex, message)
            for photo_match in photo_matches:
                message.replace(photo_match.group(), "")
            return message

    def get_sessions_data_preview(request, sessions, session_rules, preview):
        element = Elements.objects.filter(slug="sessions")
        language = EmailContentDetailView.get_lang_key(request, element[0].id)
        element_economy = Elements.objects.filter(slug="economy")
        language_for_economy = EmailContentDetailView.get_lang_key(request, element_economy[0].id)
        language['langkey'].update(language_for_economy['langkey'])
        context = {
            'sessions': sessions,
            'session_rules': session_rules,
            'preview': preview,
            'language': language
        }
        return render_to_string('message/email_sessions.html', context)

    def get_travel_data_preview(request, travels, travel_rules, preview):
        element = Elements.objects.filter(slug="travels")
        language = EmailContentDetailView.get_lang_key(request, element[0].id)
        context = {
            'travels': travels,
            'travel_rules': travel_rules,
            'preview': preview,
            'language': language
        }
        return render_to_string('message/email_travels.html', context)

    def get_hotels_data_preview(request, hotels, hotel_rules, preview):
        element = Elements.objects.filter(slug="hotels")
        language = EmailContentDetailView.get_lang_key(request, element[0].id)
        element_economy = Elements.objects.filter(slug="economy")
        language_for_economy = EmailContentDetailView.get_lang_key(request, element_economy[0].id)
        language['langkey'].update(language_for_economy['langkey'])
        context = {
            'hotels': hotels,
            'hotel_rules': hotel_rules,
            'preview': preview,
            'language': language
        }
        return render_to_string('message/email_hotels.html', context)

    def get_question_data_preview(request, questionAnswer, question_rules, preview):
        element = Elements.objects.filter(slug="questions")
        language = EmailContentDetailView.get_lang_key(request, element[0].id)
        context = {
            'questionAnswer': questionAnswer,
            'question_rules': question_rules,
            'preview': preview,
            'language': language
        }
        return render_to_string('message/email_question.html', context)

    def get_lang_key(request, element_id, preset=0, event_id=None):
        response_data = {}
        elementObj = Elements.objects.filter(id=element_id)
        if elementObj.exists():
            if event_id is None:
                event_id = request.session["event_auth_user"]["event_id"]
            presetsEvent = PresetEvent.objects.filter(event_id=event_id)
            if presetsEvent.exists():
                lang_data = ElementPresetLang.objects.filter(preset_id=presetsEvent[0].preset_id,
                                                             element_default_lang__element_id=elementObj[0].id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.element_default_lang.lang_key] = lang.value

                response_data['langkey'] = lang_key
                response_data['lang_preset'] = Presets.objects.get(id=presetsEvent[0].preset_id)
            else:
                lang_data = ElementDefaultLang.objects.filter(element_id=elementObj[0].id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.lang_key] = lang.default_value
                response_data['langkey'] = lang_key
        else:
            response_data = {
                'error': True,
                'message': 'Something went wrong. Please try again.'
            }
        return response_data

    def import_clipboard(request):
        response_data = {}
        data = []
        error = 0
        clipboard_data = request.POST.get('import_clipboard').split("\n")
        if clipboard_data:
            for clipboard in clipboard_data:
                clipboard_data = {}
                if clipboard != "":
                    clip = clipboard.split(",")
                    if len(clip) == 3:
                        clipboard_data['firstname'] = clip[0]
                        clipboard_data['lastname'] = clip[1]
                        regex = r"([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)"
                        matches = re.match(regex, clip[2])
                        if matches:
                            clipboard_data['email'] = clip[2]
                            data.append(clipboard_data)
                        else:
                            error += 1
                    elif len(clip) == 1:
                        clipboard_data['firstname'] = ""
                        clipboard_data['lastname'] = ""
                        regex = r"([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)"
                        matches = re.match(regex, clip[0])
                        if matches:
                            clipboard_data['email'] = clip[0]
                            data.append(clipboard_data)
                        else:
                            error += 1
                    else:
                        error += 1
        response_data['data'] = data
        if error:
            response_data['error'] = str(error) + " wrong input clipboard fromate"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_base_url(request, event_url):
        base_url = 'http://127.0.0.1:8000/'+str(event_url)
        return base_url

    def get_default_date_format(event_id):
        try:
            default_date_format = Setting.objects.filter(name='default_date_format', event_id=event_id)
            if default_date_format:
                default_date_format = json.loads(default_date_format[0].value)['python']
            else:
                default_date_format = 'm-d-Y'
        except:
            default_date_format = 'm-d-Y'
        return default_date_format

    def get_language_date_format(event_id):
        response = {}
        try:
            event_preset = PresetEvent.objects.filter(event_id=event_id).first()
            user_language = Presets.objects.get(id=event_preset.preset_id)
            response['default_date'] = user_language.date_format
            response['default_time'] = user_language.time_format
            response['default_datetime'] = user_language.datetime_format
        except:
            response['default_date'] = 'Y-m-d'
            response['default_time'] = 'H:i'
            response['default_datetime'] = 'Y-m-d H:i'
        return response