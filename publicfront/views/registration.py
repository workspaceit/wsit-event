from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey
from publicfront.views.profile import SessionDetail
from publicfront.views.rule import UserRule
from publicfront.views.send_email import UserEmail
from publicfront.views.hotel_reservation_plugin import HotelReservationPlugin
from app.views.gbhelper.economy_library import EconomyLibrary
from publicfront.views.helper import HelperData

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

from django.shortcuts import render, redirect
from django.http import HttpResponse
from app.models import Attendee, Session, SeminarsUsers, Questions, \
    ActivityHistory, AttendeeSubmitButton, ElementsAnswers, PageContent, RuleSet, MenuItem, Setting, PresetEvent, \
    EmailContents, EmailLanguageContents, MessageContents, MessageLanguageContents, RegistrationGroups, \
    RegistrationGroupOwner, \
    AttendeeGroups, Answers, Elements, ElementHtml,Orders, Events, EmailTemplates, Presets
import json, os, sys, time, string, random
from django.db import transaction
from django.views.generic import TemplateView
from publicfront.views.attendee import AttendeeRegistration as AttRegistration
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from publicfront.views.user_login import UserLogin
from django.db.models import Q
from datetime import datetime


class Registration(TemplateView):
    @transaction.atomic
    def save_or_update_data(request, *args, **kwargs):
        response_data = {}
        response_event = {}
        try:
            if 'event_url' in kwargs:
                event_url = kwargs['event_url']
                event_response = HelperData.checkEventSession(request,event_url)
                if 'event_response' in event_response:
                    ErrorR.ilog(event_response['event_response'])
                    response_event['event_response'] = event_response['event_response']
            response_data['redirect_url'] = ''
            event_id = request.session['event_id']
            ErrorR.warn(event_id)
            button_id = request.POST.get('button_id')
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            language_id = int(request.POST.get('language_id'))
            if not Presets.objects.filter(id=language_id, event_id=event_id).exists():
                language_id = 0
            form_data = {}

            answers = json.loads(request.POST.get('answers'))
            # attendee_session = json.loads(request.POST.get('sessions'))
            hotel_reservation = json.loads(request.POST.get('hotel_reservation'))
            economy_data = json.loads(request.POST.get('economy_data'))

            if 'is_user_login' in request.session and request.session['is_user_login']:
                # print('######### user logged in found #########')
                attendee_data = Attendee.objects.filter(id=request.session['event_user']['id'])
                if attendee_data.exists():
                    attendee = attendee_data[0]
                email_exists = False
                exist_email = ''
                if "firstname" in request.POST:
                    form_data['firstname'] = request.POST.get('firstname')
                if "lastname" in request.POST:
                    form_data['lastname'] = request.POST.get('lastname')
                if "phonenumber" in request.POST:
                    form_data['phonenumber'] = request.POST.get('phonenumber')
                if "email" in request.POST:
                    if Registration.emailExist(request.POST.get('email'), event_id, attendee.id):
                        exist_email = request.POST.get('email')
                        email_exists = True
                    else:
                        form_data['email'] = request.POST.get('email')
                if language_id != 0 and language_id != None:
                    form_data['language_id'] = language_id
                if not email_exists:
                    try:
                        with transaction.atomic():
                            form_data['updated'] = datetime.now()
                            Attendee.objects.filter(id=attendee.id).update(**form_data)
                            activity = ActivityHistory(attendee_id=attendee.id, activity_type="update", category="profile",
                                                       event_id=event_id)
                            activity.save()
                            Registration.setAttendeeAnswers(answers, attendee, event_id)
                            # Registration.setAttendeeSessions(attendee_session, attendee, event_id)
                            if hotel_reservation:
                                hotel_result = HotelReservationPlugin.make_reservation('exist', attendee.id,
                                                                                       request.session['event_id'],
                                                                                       hotel_reservation)
                                if not hotel_result:
                                    try:
                                        raise ValueError('Hotel reservation failed exception')
                                    except Exception as e:
                                        response_data['success'] = False
                                        ErrorR.efail(e)
                                        ErrorR.elog(e)
                                        response_data['redirect_url'] = ''
                                        response_data = {'message': LanguageKey.catch_lang_key(request, 'submit-button',
                                                                                               'submit_button_notify_er_registration_failed')}

                            if economy_data['rebates']:
                                order_id = None
                                order_info = EconomyLibrary.get_open_order_by_attendee(attendee.id)
                                if order_info and order_info.get('order_id'):
                                    order_id = order_info['order_id']
                                else:
                                    new_order = EconomyLibrary.create_order_for_rebate(event_id, attendee.id)
                                    if new_order and new_order.get('id'):
                                        order_id = new_order.get('id')
                                if order_id:
                                    Registration.check_and_apply_rebate(request, economy_data, attendee.id, order_id)
                                    EconomyLibrary.delete_empty_order(order_id)

                            # if 'deleted_sessions' in request.POST:
                            #     deletedSession = json.loads(request.POST.get('deleted_sessions'))
                            #     for del_session in deletedSession:
                            #         SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=del_session).delete()
                            settings_data = Registration.submit_button_settings(request, button_id, page_id, box_id,
                                                                                attendee.id)

                            Registration.autoAddSessionUsingSubmitButton(request,settings_data)

                            economy_data_len = len(economy_data['sessions'])+len(economy_data['hotels'])+len(economy_data['travels'])
                            if (economy_data_len > 0 or settings_data['change_order_status']) and not attendee.registration_group:
                                order_info = EconomyLibrary.get_open_order_by_attendee(attendee.id)
                                if order_info:
                                    response_data['order_number'] = order_info['order_number']
                                    response_data['order_id'] = order_info['order_id']
                                    response_data['status'] = order_info['status']
                                    response_data['due_date'] = order_info['due_date']
                                    response_data['attendee_id'] = attendee.id

                                    if settings_data['change_order_status']:
                                        result = EconomyLibrary.change_order_status(order_number=order_info['order_number'], status='pending', event_id=event_id, attendee_id=attendee.id)
                                        if result:
                                            response_data['download_flag'] = result['status_changed'] if settings_data['download_invoice'] else False
                                            response_data['status'] = result['status']
                                            response_data['status_lang'] = Registration.get_order_language_status_text(request, result['status'])
                                            response_data['due_date'] = result['due_date']
                                            response_data['amount_due'] = result['amount_due']

                            response_data['redirect_url'] = settings_data['page']
                            response_data['success'] = True
                            response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button',
                                                                                  'submit_button_notify_update_success')
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                    except Exception as e:
                        response_data['success'] = False
                        ErrorR.efail(e)
                        response_data['redirect_url'] = ''
                        response_data = {'message': LanguageKey.catch_lang_key(request, 'submit-button',
                                                                               'submit_button_notify_update_fail')}
                        ErrorR.elog(e)
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data['success'] = False
                    response_data['redirect_url'] = ''
                    message = LanguageKey.catch_lang_key(request, 'submit-button','submit_button_notify_er_registration_email')
                    message = message.replace("{email}",exist_email)
                    response_data['message'] = message
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

            else:
                form_data["event_id"] = event_id
                print('######## New user found #########')
                exist_email = request.POST.get('email')
                form_data['email'] = request.POST.get('email')
                form_data['firstname'] = request.POST.get('firstname')
                form_data['lastname'] = request.POST.get('lastname')
                if "phonenumber" in request.POST:
                    form_data['phonenumber'] = request.POST.get('phonenumber')
                current_language = LanguageKey.get_current_language(request)
                form_data['language_id'] = current_language.preset_id
                if language_id != 0 and language_id != None:
                    form_data['language_id'] = language_id
                run = True
                if Attendee.objects.filter(email=form_data['email'], event_id=event_id).exists():
                    allow_same_email_multiple = HelperData.get_allow_same_email_multiple_registration(event_id)
                    if not allow_same_email_multiple:
                        run = False
                if run:
                    form_data["type"] = "user"
                    flag = True

                    setting_uid_length = Setting.objects.filter(name='uid_length', event_id=event_id)
                    if setting_uid_length:
                        uid_length = int(setting_uid_length[0].value)
                    else:
                        uid_length = 16

                    while flag:
                        secret_key = ''.join(
                            random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
                            range(uid_length))
                        checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
                        if checkUniquity < 1:
                            flag = False
                    form_data["secret_key"] = secret_key
                    bid_flag = True
                    while (bid_flag):
                        badge_key = ''.join(
                            random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
                            range(uid_length))
                        checkUniquity = Attendee.objects.filter(bid__contains=badge_key).count()
                        if checkUniquity < 1:
                            bid_flag = False
                    form_data["bid"] = badge_key
                    password_character = '!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
                    password = ''.join(
                        random.choice(password_character) for _ in range(6))
                    form_data["password"] = make_password(password)
                    attendee = Attendee(**form_data)
                    try:
                        with transaction.atomic():
                            if 'temporary_attendee_id' in request.POST:
                                temporary_attendee_id = request.POST.get('temporary_attendee_id')
                                if temporary_attendee_id.isdigit():
                                    attendee.id = int(temporary_attendee_id)
                                    attendee.created = datetime.now()
                            attendee.save()
                            attendee_session = UserLogin.add_attendee_to_session(request, attendee)
                            request.session['event_user'] = attendee_session
                            request.session['event_id'] = attendee_session['event_id']
                            request.session['is_user_login'] = True
                            activity = ActivityHistory(attendee_id=attendee.id, activity_type="register", category="event",
                                                       event_id=event_id)
                            activity.save()
                            Registration.setAttendeeAnswers(answers, attendee, event_id)
                            # Registration.setAttendeeSessions(attendee_session, attendee, event_id)

                            if hotel_reservation:
                                hotel_result = HotelReservationPlugin.make_reservation('new', attendee.id,
                                                                                       request.session['event_id'],
                                                                                       hotel_reservation)
                                if not hotel_result:
                                    raise ValueError('Hotel reservation failed exception')

                            if economy_data['rebates']:
                                order_id = None
                                order_info = EconomyLibrary.get_open_order_by_attendee(attendee.id)
                                if order_info and order_info.get('order_id'):
                                    order_id = order_info['order_id']
                                else:
                                    new_order = EconomyLibrary.create_order_for_rebate(event_id, attendee.id)
                                    if new_order and new_order.get('id'):
                                        order_id = new_order.get('id')
                                if order_id:
                                    Registration.check_and_apply_rebate(request, economy_data, attendee.id, order_id)
                                    EconomyLibrary.delete_empty_order(order_id)

                            response_data['success'] = True
                            response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button',
                                                                                  'submit_button_notify_registration_success')
                            response_data['key'] = secret_key
                            settings_data = Registration.submit_button_settings(request, button_id, page_id, box_id,
                                                                                attendee.id)
                            Registration.autoAddSessionUsingSubmitButton(request, settings_data)

                            economy_data_len = len(economy_data['sessions']) + len(economy_data['hotels']) + len(economy_data['travels'])
                            if economy_data_len > 0 or settings_data['change_order_status']:
                                order_info = EconomyLibrary.get_open_order_by_attendee(attendee.id)
                                if order_info:
                                    response_data['order_number'] = order_info['order_number']
                                    response_data['order_id'] = order_info['order_id']
                                    response_data['status'] = order_info['status']
                                    response_data['due_date'] = order_info['due_date']
                                    response_data['attendee_id'] = attendee.id

                                    if settings_data['change_order_status']:
                                        result = EconomyLibrary.change_order_status(order_number=order_info['order_number'], status='pending', event_id=event_id, attendee_id=attendee.id)
                                        if result:
                                            response_data['download_flag'] = result['status_changed'] if settings_data['download_invoice'] else False
                                            response_data['status'] = result['status']
                                            response_data['status_lang'] = Registration.get_order_language_status_text(request, result['status'])
                                            response_data['due_date'] = result['due_date']

                            response_data['redirect_url'] = settings_data['page']
                            return HttpResponse(json.dumps(response_data), content_type="application/json")
                    except Exception as e:
                        ErrorR.efail(e)
                        ErrorR.elog(e)
                        if 'event_user' in request.session:
                            del request.session['event_user']
                        if 'is_user_login' in request.session:
                            del request.session['is_user_login']
                        response_data['success'] = False
                        response_data['redirect_url'] = ''
                        if 'event_response' in response_event:
                            response_data['event_response'] = response_event['event_response']
                        if str(e) == 'Hotel reservation failed exception':
                            response_data['message'] = LanguageKey.catch_lang_key(request, 'hotel-reservation',
                                                                                  'hotelreservation_notify_room_validation_msg')
                        else:
                            response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button',
                                                                                  'submit_button_notify_er_registration_failed')
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data['success'] = False
                    response_data['redirect_url'] = ''
                    message = LanguageKey.catch_lang_key(request, 'submit-button','submit_button_notify_er_registration_email')
                    message = message.replace("{email}",exist_email)
                    response_data['message'] = message
                    if 'event_response' in response_event:
                        response_data['event_response'] = response_event['event_response']
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            ErrorR.efail(e)
            ErrorR.elog(e)
            response_data['success'] = False
            response_data['redirect_url'] = ''
            if 'event_response' in response_event:
                response_data['event_response'] = response_event['event_response']
            response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button','submit_button_notify_er_registration_failed')
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def check_and_apply_rebate(request, economy_data, attendee_id, order_id):
        if economy_data['rebate_type'] == 'filter':
            rebates = economy_data['rebates']
            else_rebate = rebates.pop()
            rebate_found = []
            for rebate_item in rebates:
                rule_set = RuleSet.objects.filter(id=rebate_item['filter_id']).first()
                if rule_set:
                    filters = json.loads(rule_set.preset)
                    q = Q()
                    match_condition = '0'
                    if 'matchFor' in filters[0][0]:
                        match_condition = filters[0][0]['matchFor']
                    elif rule_set.matchfor:
                        match_condition = rule_set.matchfor
                    if match_condition == '2':
                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    else:
                        q = Q(id=-11)
                    filtered_attendee = Attendee.objects.filter(q)
                    ErrorR.okblue(len(filtered_attendee))
                    filtered_attendee = filtered_attendee.filter(id=attendee_id)
                    if filtered_attendee:
                        rebate_found = rebate_item['rebate_id']
                        ErrorR.okgreen(rebate_found)
                        break
            if not rebate_found:
                rebate_found = else_rebate['rebate_id']
            for reb_item in rebate_found:
                EconomyLibrary.apply_rebate(user_id=attendee_id, order_id=order_id, rebate_id=int(reb_item))
        else:
            for rebate in economy_data['rebates']:
                EconomyLibrary.apply_rebate(user_id=attendee_id, order_id=order_id, rebate_id=rebate['rebate_id'],
                                            rebate_item_type=rebate['item_type'], rebate_item_id=rebate['rebate_for'])

    def emailExist(email, event_id, attendee_id):
        allow = False
        if Attendee.objects.filter(email=email, event_id=event_id).exclude(id=attendee_id).exists():
            allow_same_email_multiple_registration = HelperData.get_allow_same_email_multiple_registration(event_id)
            if not allow_same_email_multiple_registration:
                allow = True
        return allow

    def get_order_language_status_text(request, status):
        status_lang = status
        if status == 'open':
            status_lang = LanguageKey.catch_lang_key_multiple(request, 'economy', ['economy_txt_status_open'])['langkey']['economy_txt_status_open']
        elif status == 'pending':
            status_lang = LanguageKey.catch_lang_key_multiple(request, 'economy', ['economy_txt_status_pending'])['langkey']['economy_txt_status_pending']
        elif status == 'paid':
            status_lang = LanguageKey.catch_lang_key_multiple(request, 'economy', ['economy_txt_status_paid'])['langkey']['economy_txt_status_paid']
        elif status == 'cancelled':
            status_lang = LanguageKey.catch_lang_key_multiple(request, 'economy', ['economy_txt_status_cancelled'])['langkey']['economy_txt_status_cancelled']
        return status_lang

    def setAttendeeAnswers(answers, attendee, event_id):
        import time
        start_time = time.time()
        for answer in answers:
            if answer['id'] != '' and answer['answer'] != False:
                question = Questions.objects.filter(id=answer['id'])
            if question.exists():
                if question[0].actual_definition == "firstname":
                    Attendee.objects.filter(id=attendee.id).update(firstname=answer['answer'])
                if question[0].actual_definition == "lastname":
                    Attendee.objects.filter(id=attendee.id).update(lastname=answer['answer'])
                if question[0].actual_definition == "email":
                    if not Registration.emailExist(answer['answer'], event_id, attendee.id):
                        Attendee.objects.filter(id=attendee.id).update(email=answer['answer'])
                if question[0].actual_definition == "phone":
                    Attendee.objects.filter(id=attendee.id).update(phonenumber=answer['answer'])
                AttRegistration.saveAnswers(attendee.id, answer)
        print("--- %s seconds ---" % (time.time() - start_time))
        return True

    def setAttendeeSessions(attendee_session, attendee, event_id):
        for session in attendee_session:
            session_exist = SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=session)
            if session_exist.exists():
                seminar_user = session_exist[0]
                if seminar_user.status == 'not-attending':
                    sessionAttendees = Session.objects.get(id=session)
                    bookedSessions = SeminarsUsers.objects.filter(session_id=session).exclude(
                        status='not-attending').count()
                    if sessionAttendees.max_attendees > bookedSessions:
                        SeminarsUsers.objects.filter(id=seminar_user.id).update(status='attending')
                    else:
                        if not sessionAttendees.receive_answer and sessionAttendees.allow_attendees_queue:
                            seminar_data = {
                                "status": "in-queue"
                            }
                            all_queue = SeminarsUsers.objects.filter(session_id=session,
                                                                     status='in-queue').order_by('queue_order')
                            if all_queue.exists():
                                seminar_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                            SeminarsUsers.objects.filter(id=seminar_user.id).update(**seminar_data)
            else:
                sessionAttendees = Session.objects.get(id=session)
                bookedSessions = SeminarsUsers.objects.filter(session_id=session).exclude(
                    status='not-attending').count()
                if sessionAttendees.max_attendees > bookedSessions:
                    attendeeSessions = SeminarsUsers(attendee_id=attendee.id, session_id=session)
                    attendeeSessions.save()
                else:
                    if not sessionAttendees.receive_answer and sessionAttendees.allow_attendees_queue:
                        seminar_data = {
                            "attendee_id": attendee.id,
                            "session_id": session,
                            "status": "in-queue"
                        }
                        all_queue = SeminarsUsers.objects.filter(session_id=session,
                                                                 status='in-queue').order_by('queue_order')
                        if all_queue.exists():
                            seminar_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                        attendeeSessions = SeminarsUsers(**seminar_data)
                        attendeeSessions.save()
        return True

    def submit_button_settings(request, button_id, page_id, box_id, user_id, attendee_owner_id=None):
        response = {'result': True, 'page': '', 'email': {}, 'sessions': [], 'remove_conflict_session': False, 'change_order_status': False, 'download_invoice': False}
        try:
            att_submit = AttendeeSubmitButton.objects.filter(button_id=button_id, attendee_id=user_id)
            if att_submit:
                att_submit[0].hit_count += 1
                att_submit[0].save()
            else:
                att_submit = AttendeeSubmitButton(button_id=button_id, hit_count=1, attendee_id=user_id)
                att_submit.save()
            elemet_answer = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            if elemet_answer:
                for answer in elemet_answer:
                    if answer.element_question.question_key == 'submit_button_redirect_page':
                        btn_page_answer = json.loads(answer.answer)[0]
                        custom_query = ''
                        custom_url_query = elemet_answer.filter(element_question__question_key='submit_button_custom_value')
                        if custom_url_query.exists():
                            custom_query = custom_url_query[0].answer.replace('?','')
                        if btn_page_answer['state'] == 1:
                            response['result'] = True
                        elif btn_page_answer['state'] == 2:
                            response['result'] = True
                            page_url = PageContent.objects.get(id=int(btn_page_answer['data']['page_id'])).url
                            response['page'] = Registration.get_redirect_page(request, page_url, custom_query)
                        elif btn_page_answer['state'] == 3:
                            response['result'] = True
                            p_counter = 0
                            p_length = len(btn_page_answer['data'])
                            for prerequisite in btn_page_answer['data']:
                                if p_counter < p_length - 1:
                                    rule_set = RuleSet.objects.get(id=prerequisite['filter_id'])
                                    filters = json.loads(rule_set.preset)
                                    q = Q()
                                    match_condition = '0'
                                    if 'matchFor' in filters[0][0]:
                                        match_condition = filters[0][0]['matchFor']
                                    elif rule_set.matchfor:
                                        match_condition = rule_set.matchfor
                                    if match_condition == '2':
                                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                                    elif match_condition == '1':
                                        q = Q(id=-11)
                                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                                    else:
                                        q = Q(id=-11)
                                    attendees = Attendee.objects.filter(q)
                                    att_existence = '1' if attendees.filter(id=user_id).count() > 0 else '0'
                                    if prerequisite['match'] == att_existence:
                                        if prerequisite['page_id'] != '':
                                            page_url = PageContent.objects.get(
                                                id=int(prerequisite['page_id'])).url
                                            response['page'] = Registration.get_redirect_page(request, page_url, custom_query)
                                        break
                                else:
                                    if prerequisite['page_id'] != '':
                                        page_url = PageContent.objects.get(id=int(prerequisite['page_id'])).url
                                        response['page'] = Registration.get_redirect_page(request, page_url, custom_query)
                                p_counter += 1

                    elif answer.element_question.question_key == 'submit_button_email_send':
                        btn_email_answer = json.loads(answer.answer)[0]
                        if btn_email_answer['state'] == 1:
                            response['result'] = True
                        elif btn_email_answer['state'] == 2:
                            # queue = UserEmail.email_connection(request)
                            user_att = Attendee.objects.get(id=user_id)
                            ErrorR.okblue(attendee_owner_id)
                            if attendee_owner_id is None:
                                UserEmail.send_email_to_user(request, int(btn_email_answer['data']['email_id']),
                                                             user_att, attendee_owner_id)
                            response['result'] = True
                            response['email']['attendee'] = btn_email_answer['data']['email_id']
                            response['email']['owner'] = btn_email_answer['data']['email_id']
                        elif btn_email_answer['state'] == 3:
                            # queue = UserEmail.email_connection(request)
                            if type(btn_email_answer['data']) is list:
                                # for previous submit button settings, where both share same email
                                response['result'] = True
                                response['email']['attendee'] = Registration.email_confirmation_filter(request, user_id,btn_email_answer['data'],attendee_owner_id, True)
                                response['email']['owner'] = response['email']['attendee']
                            else:
                                # for new submit-btn settings
                                response['result'] = True
                                response['email']['attendee'] = Registration.email_confirmation_filter(request, user_id, btn_email_answer['data']['attendee'], attendee_owner_id, True)
                                response['email']['owner'] = Registration.email_confirmation_filter(request, user_id, btn_email_answer['data']['owner'], attendee_owner_id, False)
                    elif answer.element_question.question_key == 'submit_button_add_session':
                        btn_session_answer = json.loads(answer.answer)[0]
                        if btn_session_answer['state'] == 1:
                            response['result'] = True
                        elif btn_session_answer['state'] == 2:
                            response['result'] = True
                            btn_sessions = btn_session_answer['data']['session_id']
                            response['sessions'] = btn_sessions
                        elif btn_session_answer['state'] == 3:
                            response['result'] = True
                            s_counter = 0
                            s_length = len(btn_session_answer['data'])
                            for prerequisite_session in btn_session_answer['data']:
                                if s_counter < s_length - 1:
                                    rule_set = RuleSet.objects.get(id=prerequisite_session['filter_id'])
                                    filters = json.loads(rule_set.preset)
                                    q = Q()
                                    match_condition = '0'
                                    if 'matchFor' in filters[0][0]:
                                        match_condition = filters[0][0]['matchFor']
                                    elif rule_set.matchfor:
                                        match_condition = rule_set.matchfor
                                    if match_condition == '2':
                                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                                    elif match_condition == '1':
                                        q = Q(id=-11)
                                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                                    else:
                                        q = Q(id=-11)
                                    attendees = Attendee.objects.filter(q)
                                    att_existence = '1' if attendees.filter(id=user_id).count() > 0 else '0'
                                    if prerequisite_session['match'] == att_existence:
                                        if len(prerequisite_session['session_id']) > 0:
                                            btn_sessions = prerequisite_session['session_id']
                                            response['sessions'] = btn_sessions
                                        break
                                else:
                                    if len(prerequisite_session['session_id']) > 0:
                                        btn_sessions = prerequisite_session['session_id']
                                        response['sessions'] = btn_sessions
                                s_counter += 1
                    elif answer.element_question.question_key == 'submit_button_remove_conflict_session':
                        response['remove_conflict_session'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'submit_button_open_to_pending_order':
                        response['change_order_status'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'submit_button_download_invoice':
                        response['download_invoice'] = eval(answer.answer)
            return response

        except Exception as e:
            ErrorR.efail(e)
            ErrorR.elog(e)
            return response

    def email_confirmation_filter(request, user_id, btn_email_answer, attendee_owner_id, send_mail):
        response_email = None
        e_counter = 0
        e_length = len(btn_email_answer)
        for e_prerequisite in btn_email_answer:
            if e_counter < e_length - 1:
                rule_set = RuleSet.objects.get(id=e_prerequisite['filter_id'])
                filters = json.loads(rule_set.preset)
                q = Q()
                match_condition = '0'
                if 'matchFor' in filters[0][0]:
                    match_condition = filters[0][0]['matchFor']
                elif rule_set.matchfor:
                    match_condition = rule_set.matchfor
                if match_condition == '2':
                    q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                elif match_condition == '1':
                    q = Q(id=-11)
                    q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                else:
                    q = Q(id=-11)
                attendees = Attendee.objects.filter(q)
                att_existence = '1' if attendees.filter(id=user_id).count() > 0 else '0'
                if e_prerequisite['match'] == att_existence:
                    if e_prerequisite['email_id'] != '':
                        user_att = Attendee.objects.get(id=user_id)
                        if attendee_owner_id is None and send_mail:
                            UserEmail.send_email_to_user(request, int(e_prerequisite['email_id']),
                                                         user_att, attendee_owner_id)
                    response_email = e_prerequisite['email_id']
                    break
            else:
                if e_prerequisite['email_id'] != '':
                    user_att = Attendee.objects.get(id=user_id)
                    if attendee_owner_id is None and send_mail:
                        UserEmail.send_email_to_user(request, int(e_prerequisite['email_id']),
                                                     user_att, attendee_owner_id)
                    response_email = e_prerequisite['email_id']
            e_counter += 1
        return response_email

    def get_redirect_page(request, page_url, custom_query=""):
        event_id = request.session['event_id']
        page_menu = MenuItem.objects.filter(url=page_url, event_id=event_id)
        page_url = page_url + "/"
        if page_menu.exists():
            if page_menu[0].uid_include:
                if custom_query:
                    custom_query = "&" + custom_query
                return page_url + "?uid=" + request.session['event_user']['secret_key'] + custom_query
            else:
                if custom_query:
                    custom_query = "?" + custom_query
                return page_url + custom_query
        else:
            if custom_query:
                custom_query = "?" + custom_query
            return page_url + custom_query

    # def get_outbound_sessions(request, *args, **kwargs):
    #     city = request.POST.get('city')
    #     group_list = []
    #     travel_group = Group.objects.filter(travel__departure_city=city, travel__travel_bound='outbound').distinct()
    #     print(travel_group.count())
    #     for group in travel_group:
    #         travels = Travel.objects.filter(departure_city=city, travel_bound='outbound', group_id=group.id)
    #         travels_list = []
    #         for travel in travels:
    #             booked = TravelAttendee.objects.filter(travel_id=travel.id).count()
    #             outTravel = travel.as_dict()
    #             outTravel['full'] = True
    #             if travel.max_attendees > booked:
    #                 outTravel['full'] = False
    #             travels_list.append(outTravel)
    #         travel_obj = {
    #             'group': group.as_dict(),
    #             'travels': travels_list
    #         }
    #         group_list.append(travel_obj)
    #     data = {
    #         'travel_groups': group_list
    #     }
    #     return HttpResponse(json.dumps(data), content_type="application/json")

    # def get_homebound_sessions(request, *args, **kwargs):
    #     outbound_id = request.POST.get('outbound_id')
    #     group_list = []
    #     homebound_list = []
    #     homebound_travel = TravelBoundRelation.objects.filter(travel_outbound_id=outbound_id)
    #     for h_travel in homebound_travel:
    #         homebound_list.append(h_travel.travel_homebound_id)
    #     travel_group = Group.objects.filter(travel__id__in=homebound_list).distinct()
    #     for group in travel_group:
    #         travels = Travel.objects.filter(id__in=homebound_list, group_id=group.id)
    #         travels_list = []
    #         for travel in travels:
    #             booked = TravelAttendee.objects.filter(travel_id=travel.id).count()
    #             homeTravel = travel.as_dict()
    #             homeTravel['full'] = True
    #             if travel.max_attendees > booked:
    #                 homeTravel['full'] = False
    #             travels_list.append(homeTravel)
    #         travel_obj = {
    #             'group': group.as_dict(),
    #             'travels': travels_list
    #         }
    #         group_list.append(travel_obj)
    #     data = {
    #         'travel_groups': group_list
    #     }
    #     return HttpResponse(json.dumps(data), content_type="application/json")

    def add_default_session(attendee_id, *args, **kwargs):
        if os.environ['ENVIRONMENT_TYPE'] == 'master':
            group_id = 161
        elif os.environ['ENVIRONMENT_TYPE'] == 'staging':
            group_id = 161
        else:
            group_id = 160
        default_sessions = Session.objects.filter(group_id=group_id)
        for session in default_sessions:
            seminar_attend = SeminarsUsers(attendee_id=attendee_id, session_id=session.id, status='attending')
            seminar_attend.save()

    @transaction.atomic
    def multiple_attendee_save_or_update(request, *args, **kwargs):
        economy_data = None
        if 'economy_data' in request.POST:
            economy_data = json.loads(request.POST.get('economy_data'))
        ErrorR.ex_time_init()
        response_data = {}
        response_event = {}
        if 'event_url' in kwargs:
            event_url = kwargs['event_url']
            event_response = HelperData.checkEventSession(request, event_url)
            if 'event_response' in event_response:
                ErrorR.ilog(event_response['event_response'])
                response_event['event_response'] = event_response['event_response']
        response_data['redirect_url'] = ''
        event_id = request.session['event_id']
        button_id = request.POST.get('button_id')
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        form_box_id = request.POST.get('form_box_id')
        language_id = int(request.POST.get('language_id'))
        if not Presets.objects.filter(id=language_id, event_id=event_id).exists():
            language_id = 0

        multiple_attendees = json.loads(request.POST.get('attendee_ids'))
        ErrorR.okblue(len(multiple_attendees))
        attendee_owner_id = int(request.POST.get('attendee_owner_id'))
        ErrorR.okgreen(attendee_owner_id)
        multiple_group_id = 0
        error_lang = LanguageKey.catch_lang_key(request, 'multiple-registration', 'multiple_registration_failed')
        success_lang = LanguageKey.catch_lang_key(request, 'multiple-registration', 'multiple_registration_success')
        element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=form_box_id)
        order_owner_groups = []
        attendee_groups = []
        inherit_questions = []
        confirmations = ''
        selected_columns = []
        for setting in element_settings:
            if setting.element_question.question_key == 'multiple_registration_order_owner_group':
                order_owner_groups = json.loads(setting.answer)
            elif setting.element_question.question_key == 'multiple_registration_attendee_group':
                attendee_groups = json.loads(setting.answer)
            elif setting.element_question.question_key == 'multiple_registration_inherit_answers':
                selected_columns_data = json.loads(json.loads(setting.answer))
                if selected_columns_data['question'][0]['id'] != "":
                    selected_columns = selected_columns_data['question'][0]['id'].split(',')
                ErrorR.c_yellow(selected_columns)
            elif setting.element_question.question_key == 'multiple_registration_confirmations':
                confirmations = setting.answer
        ErrorR.ex_time()
        activity_history = []
        group_name = ""

        try:
            with transaction.atomic():
                multiple_attendee_groups = []
                if attendee_owner_id > 0:
                    attendee_owner = Attendee.objects.get(id=attendee_owner_id)
                    if attendee_owner:
                        if attendee_owner.status == "pending":
                            ErrorR.ex_time()
                            [secret_key, attendee_password, badge_key] = Registration.create_secret_password(request)
                            ErrorR.ex_time()
                            attendee_owner.status = "registered"
                            attendee_owner.secret_key = secret_key
                            attendee_owner.password = attendee_password
                            attendee_owner.bid = badge_key
                            if language_id != 0 and language_id != None:
                                attendee_owner.language_id = language_id
                            attendee_owner.save()
                            if len(multiple_attendees) > 0:
                                group_name = 'Registration-group-' + str(attendee_owner_id)
                                registration_group = RegistrationGroups(name=group_name, event_id=event_id)
                                registration_group.save()
                                group_owner = RegistrationGroupOwner(group_id=registration_group.id, owner_id=attendee_owner_id)
                                group_owner.save()
                                activity_history.append(ActivityHistory(attendee_id=attendee_owner_id, activity_type='update', category='registration_group',
                                                                        registration_group_id=registration_group.id, new_value='as Order owner', event_id=event_id))
                                multiple_group_id = registration_group.id

                            for grp in order_owner_groups:
                                multiple_attendee_groups.append(AttendeeGroups(attendee_id=attendee_owner_id, group_id=int(grp)))
                        else:
                            if RegistrationGroupOwner.objects.filter(owner_id=attendee_owner_id).exists():
                                multiple_group_id = RegistrationGroupOwner.objects.get(owner_id=attendee_owner.id).group_id
                                group_name = RegistrationGroups.objects.get(id=multiple_group_id).name
                            elif len(multiple_attendees) > 0:
                                group_name = 'registration-group-' + str(attendee_owner_id)
                                new_group = RegistrationGroups(name=group_name, event_id=event_id)
                                new_group.save()
                                group_id = new_group.id
                                group_owner = RegistrationGroupOwner(group_id=group_id, owner_id=attendee_owner_id)
                                group_owner.save()
                                multiple_group_id = group_id
                        # settings_data = Registration.submit_button_settings(request, button_id, page_id, box_id,
                        #                                                     attendee_owner_id)

                        attendee_session = UserLogin.add_attendee_to_session(request, attendee_owner)
                        request.session['event_user'] = attendee_session
                        request.session['event_id'] = attendee_session['event_id']
                        request.session.modified = True
                        settings_data = Registration.submit_button_settings(request, button_id, page_id, box_id,
                                                                            attendee_owner_id, attendee_owner_id)
                        email_id = {}
                        if settings_data.get('email'):
                            email_id['attendee'] = int(settings_data['email']['attendee'])
                            if settings_data['email']['owner']:
                                email_id['owner'] = int(settings_data['email']['owner'])
                            else:
                                email_id['owner'] = 0

                        response_data['redirect_url'] = settings_data['page']
                        response_data['key'] = attendee_owner.secret_key
                        ErrorR.ex_time()
                        attendees = Attendee.objects.filter(id__in=multiple_attendees, status="pending")
                        if len(attendees) > 0:
                            owner_id = RegistrationGroupOwner.objects.get(group_id=multiple_group_id).owner_id
                            order_owner_order = Orders.objects.filter(attendee_id=owner_id, status__in=['open','pending'])
                            if order_owner_order.exists():
                                order_info = order_owner_order.last()
                        for attendee in attendees:
                            ErrorR.okgreen(attendee.id)
                            [secret_key, attendee_password, badge_key] = Registration.create_secret_password(request)
                            attendee.status = "registered"
                            attendee.secret_key = secret_key
                            attendee.password = attendee_password
                            attendee.bid = badge_key
                            attendee.registration_group_id = multiple_group_id
                            if language_id != 0 and language_id != None:
                                attendee.language_id = language_id
                            attendee.save()

                            activity_history.append(ActivityHistory(attendee_id=attendee.id, activity_type='update', category='registration_group',
                                                                    registration_group_id=multiple_group_id, new_value='as Attendee', event_id=event_id))

                            if order_owner_order.exists():
                                attendee_orders = Orders.objects.filter(is_preselected=True, attendee_id=attendee.id)
                                for orders in attendee_orders:
                                    orders.order_number = order_info.order_number
                                    orders.status = order_info.status
                                    orders.due_date = order_info.due_date
                                    orders.invoice_date = order_info.invoice_date
                                    orders.invoice_ref = order_info.invoice_ref
                                    orders.is_preselected = False
                                    orders.save()
                            for grp in attendee_groups:
                                multiple_attendee_groups.append(
                                    AttendeeGroups(attendee_id=attendee.id, group_id=int(grp)))
                        ErrorR.c_bipurple(selected_columns)
                        ErrorR.c_bipurple(attendee_owner_id)
                        questions = Answers.objects.filter(question_id__in=selected_columns,
                                                           user_id=attendee_owner_id).exclude(value="")
                        for ques in questions:
                            Answers.objects.filter(question_id=ques.question_id, user_id__in=multiple_attendees,
                                                   value="").update(value=ques.value)
                        AttendeeGroups.objects.bulk_create(multiple_attendee_groups)
                        ErrorR.ex_time_init()
                        print('email_gt')
                        print(email_id)
                        print('att len')
                        print(len(attendees))
                        if len(attendees) > 0 and email_id.get('attendee'):
                            # email_id{'attendee', 'owner'} will be both
                            all_multi_attendees = []
                            all_multi_attendees += multiple_attendees
                            # queue = UserEmail.email_connection(request)
                            print("confirmations")
                            print(confirmations)
                            if confirmations == 'send-to-all':
                                print('email')
                                print(email_id)
                                if email_id['attendee'] == email_id['owner']:
                                    all_multi_attendees.append(attendee_owner_id)
                                    print('if')
                                    print(all_multi_attendees)
                                    UserEmail.send_email_to_multiple_user(request, email_id['attendee'], all_multi_attendees)
                                else:
                                    print('else')
                                    print('atts:')
                                    print(all_multi_attendees)
                                    UserEmail.send_email_to_multiple_user(request, email_id['attendee'], all_multi_attendees)
                                    UserEmail.send_email_to_multiple_user(request, email_id['owner'], [], attendee_owner_id)
                            else:
                                ErrorR.okgreen(all_multi_attendees)
                                if email_id['attendee'] == email_id['owner']:
                                    UserEmail.send_email_to_multiple_user(request, email_id['owner'], all_multi_attendees, attendee_owner_id)
                                else:
                                    UserEmail.send_email_to_multiple_user(request, email_id['owner'], all_multi_attendees, attendee_owner_id, email_id['attendee'])
                        elif email_id.get('attendee'):
                            # queue = UserEmail.email_connection(request)
                            UserEmail.send_email_to_multiple_user(request, email_id['owner'], [], attendee_owner_id)

                        # print('*** Merge Order Number ***')
                        # EconomyLibrary.update_order_number_for_group_reg(attendee_owner_id)

                        ErrorR.ex_time()

                        if economy_data['rebates']:
                            group_info = EconomyLibrary.get_group_registration_info(attendee_owner.id)
                            all_attendees = group_info['grp-atts']
                            for t_attendee_id in all_attendees:
                                order_id = None
                                order_info = EconomyLibrary.get_open_order_by_attendee(t_attendee_id)
                                if order_info and order_info.get('order_id'):
                                    order_id = order_info['order_id']
                                else:
                                    order_number = None
                                    if 'order_number' in request.POST:
                                        order_number = request.POST.get('order_number')
                                    if not order_number:
                                        order_number = economy_data['multiple']['order_number']

                                    order_number = order_info.get('order_number') if order_info else order_number
                                    new_order = EconomyLibrary.create_order_for_rebate(event_id, t_attendee_id, order_number)
                                    if new_order and new_order.get('id'):
                                        order_id = new_order.get('id')
                                        response_data['order_number'] = new_order.get('order_number')
                                if order_id:
                                    economy_data = json.loads(request.POST.get('economy_data'))
                                    Registration.check_and_apply_rebate(request, economy_data, t_attendee_id, order_id)
                                    EconomyLibrary.delete_empty_order(order_id)

                        if 'sessions' in settings_data and len(settings_data['sessions']) > 0:
                            group_info = EconomyLibrary.get_group_registration_info(attendee_owner.id)
                            all_attendees = group_info['grp-atts']
                            for t_attendee_id in all_attendees:
                                temp_session = HelperData.tem_login_make(request,t_attendee_id)
                                Registration.autoAddSessionUsingSubmitButton(request, settings_data)
                                HelperData.tem_login_clean(request, temp_session)
                            attendee_session = UserLogin.add_attendee_to_session(request, attendee_owner)
                            request.session['event_user'] = attendee_session
                            request.session['event_id'] = attendee_session['event_id']
                            request.session.modified = True

                        if settings_data['change_order_status']:
                            order_detail = EconomyLibrary.get_open_order_by_attendee(attendee_owner_id)
                            if order_detail:
                                result = EconomyLibrary.change_order_status(order_detail['order_number'], 'pending',
                                                                            event_id, attendee_owner_id)
                                if result and result['status_changed'] and settings_data['download_invoice']:
                                    response_data['download_flag'] = True
                                    response_data['order_number'] = result['order_number']
                    else:
                        response_data['success'] = False
                        response_data['message'] = error_lang
                        if 'event_response' in response_event:
                            response_data['event_response'] = response_event['event_response']
                        return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data['success'] = False
                    response_data['message'] = error_lang
                    if 'event_response' in response_event:
                        response_data['event_response'] = response_event['event_response']
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                response_data['success'] = True
                response_data['message'] = success_lang
                request.session['is_user_login'] = True
                request.session.modified = True
                if "temp_attendee_id_array" in request.session:
                    del request.session["temp_attendee_id_array"]
                if "temp_inline_page_url" in request.session and response_data['redirect_url'] != "":
                    del request.session["temp_inline_page_url"]
                response_data['group_name'] = group_name

                ActivityHistory.objects.bulk_create(activity_history)

        except Exception as e:
            ErrorR.efail(e)
            ErrorR.elog(e)
            response_data['success'] = False
            response_data['message'] = error_lang
            if 'event_response' in response_event:
                response_data['event_response'] = response_event['event_response']
        ErrorR.ex_time()
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def multiple_attendee_save_or_update_inline(request, *args, **kwargs):
        response_data = {}
        response_event = {}
        if 'event_url' in kwargs:
            event_url = kwargs['event_url']
            event_response = HelperData.checkEventSession(request, event_url)
            if 'event_response' in event_response:
                ErrorR.ilog(event_response['event_response'])
                response_event['event_response'] = event_response['event_response']
        try:
            attendee_datas = json.loads(request.POST.get('attendee_datas'))
            for attendee_data in attendee_datas:
                ErrorR.c_purple(attendee_datas[attendee_data])
                response_data_save_or_update = Registration.save_or_update_multiple_attendee(request, attendee_datas[attendee_data])
                if not response_data_save_or_update["success"]:
                    return HttpResponse(json.dumps(response_data_save_or_update), content_type="application/json")
                if not request.POST.get('order_number'):
                    request.POST._mutable = True
                    request.POST['order_number'] = response_data_save_or_update.get('order_number')
            request.POST._mutable = False
            return Registration.multiple_attendee_save_or_update(request, *args, **kwargs)
        except Exception as e:
            ErrorR.efail(e)
            ErrorR.elog(e)
            response_data['success'] = False
            if 'event_response' in response_event:
                response_data['event_response'] = response_event['event_response']
            response_data['message'] = LanguageKey.catch_lang_key(request, 'multiple-registration', 'multiple_registration_failed')
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_or_update_multiple_attendee(request, multiple_attendee, group_id=None):
        response_data = {}
        event_id = request.session['event_id']
        language_id = 0
        if 'language_id' in request.POST:
            language_id = int(request.POST.get('language_id'))
            if not Presets.objects.filter(id=language_id, event_id=event_id).exists():
                language_id = 0
        form_data = {}
        # economy_data = json.loads(request.POST.get('economy_data'))
        owner_answers = multiple_attendee['answers']
        owner_hotel_reservations = None
        if "hotel_reservation" in multiple_attendee:
            owner_hotel_reservations = json.loads(multiple_attendee['hotel_reservation'])
        if 'attendee_id' in multiple_attendee:
            # print('######### user logged in found #########')
            attendee_data = Attendee.objects.filter(id=multiple_attendee['attendee_id'])
            if attendee_data.exists():
                attendee = attendee_data[0]
            email_exists = False
            exist_email=''
            if "firstname" in multiple_attendee:
                form_data['firstname'] = multiple_attendee['firstname']
            if "lastname" in multiple_attendee:
                form_data['lastname'] = multiple_attendee['lastname']
            if "phonenumber" in multiple_attendee:
                form_data['phonenumber'] = multiple_attendee['phonenumber']
            if "email" in multiple_attendee:
                if Registration.emailExist(multiple_attendee['email'], event_id, attendee.id):
                    email_exists = True
                    exist_email = multiple_attendee['email']
                else:
                    form_data['email'] = multiple_attendee['email']
            if language_id != 0 and language_id != None:
                form_data['language_id'] = language_id
            if not email_exists:
                try:
                    with transaction.atomic():
                        form_data['updated'] = datetime.now()
                        Attendee.objects.filter(id=attendee.id).update(**form_data)
                        activity = ActivityHistory(attendee_id=attendee.id, activity_type="update", category="profile",
                                                   event_id=event_id)
                        activity.save()
                        Registration.setAttendeeAnswers(owner_answers, attendee, event_id)
                        if owner_hotel_reservations:
                            order_number = request.POST.get('order_number')
                            print('ORDER NUMBER {}'.format(order_number))
                            hotel_result = HotelReservationPlugin.make_reservation('exist', attendee.id,
                                                                                   request.session['event_id'], owner_hotel_reservations, order_number)
                            if hotel_result and hotel_result.get('result') and hotel_result.get('order_number'):
                                response_data['order_number'] = hotel_result.get('order_number')
                            else:
                                try:
                                    raise ValueError('Hotel reservation failed exception')
                                except Exception as e:
                                    response_data['success'] = False
                                    ErrorR.efail(e)
                                    ErrorR.elog(e)
                                    response_data['redirect_url'] = ''
                                    response_data = {'message': LanguageKey.catch_lang_key(request, 'submit-button',
                                                                                           'submit_button_notify_er_registration_failed')}

                        response_data['success'] = True
                        response_data['attendee_id'] = attendee.id
                        response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button',
                                                                              'submit_button_notify_update_success')
                except Exception as e:
                    response_data['success'] = False
                    ErrorR.efail(e)
                    ErrorR.elog(e)
                    response_data['redirect_url'] = ''
                    response_data = {'message': LanguageKey.catch_lang_key(request, 'submit-button',
                                                                           'submit_button_notify_update_fail')}
            else:
                response_data['success'] = False
                response_data['redirect_url'] = ''
                message = LanguageKey.catch_lang_key(request, 'submit-button','submit_button_notify_er_registration_email')
                message = message.replace("{email}",exist_email)
                response_data['message'] = message
        else:
            form_data['event_id'] = event_id
            print('######## Attendee Owner found #########')
            if "email" in multiple_attendee:
                form_data['email'] = multiple_attendee['email']
            else:
                form_data['email'] = ""
            form_data['firstname'] = multiple_attendee['firstname']
            form_data['lastname'] = multiple_attendee['lastname']
            if "phonenumber" in multiple_attendee:
                form_data['phonenumber'] = multiple_attendee['phonenumber']
            current_language = LanguageKey.get_current_language(request)
            form_data['language_id'] = current_language.preset_id
            if language_id != 0 and language_id != None:
                form_data['language_id'] = language_id
            exist_email = form_data['email']
            run = True
            # if not (Attendee.objects.filter(email=form_data['email'], event_id=event_id).exists()):
            if run:
                form_data["type"] = "user"
                flag = True

                setting_uid_length = Setting.objects.filter(name='uid_length', event_id=event_id)
                if setting_uid_length:
                    uid_length = int(setting_uid_length[0].value)
                else:
                    uid_length = 16

                while (flag):
                    secret_key = ''.join(
                        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
                        range(uid_length))
                    checkUniquity = Attendee.objects.filter(secret_key__contains=secret_key).count()
                    if checkUniquity < 1:
                        flag = False
                form_data["secret_key"] = secret_key
                bid_flag = True
                while (bid_flag):
                    badge_key = ''.join(
                        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
                        range(uid_length))
                    checkUniquity = Attendee.objects.filter(bid__contains=badge_key).count()
                    if checkUniquity < 1:
                        bid_flag = False
                form_data["bid"] = badge_key
                password_character = '!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
                password = ''.join(
                    random.choice(password_character) for _ in range(6))
                form_data["password"] = make_password(password)
                if group_id:
                    form_data["registration_group_id"] = group_id

                attendee = Attendee(**form_data)
                try:
                    with transaction.atomic():
                        if 'temporary_attendee_id' in request.POST:
                            temporary_attendee_id = request.POST.get('temporary_attendee_id')
                            if temporary_attendee_id.isdigit():
                                attendee.id = int(temporary_attendee_id)
                                attendee.created = datetime.now()
                        attendee.save()
                        attendee_session = UserLogin.add_attendee_to_session(request, attendee)
                        request.session['event_user'] = attendee_session
                        request.session['event_id'] = attendee_session['event_id']
                        request.session['is_user_login'] = True
                        activity = ActivityHistory(attendee_id=attendee.id, activity_type="register", category="event",
                                                   event_id=event_id)
                        activity.save()
                        Registration.setAttendeeAnswers(owner_answers, attendee, event_id)

                        if owner_hotel_reservations:
                            order_number = request.POST.get('order_number')
                            print('ORDER NUMBER {}'.format(order_number))
                            hotel_result = HotelReservationPlugin.make_reservation('new', attendee.id, request.session['event_id'], owner_hotel_reservations, order_number)
                            if hotel_result and hotel_result.get('result') and hotel_result.get('order_number'):
                                response_data['order_number'] = hotel_result.get('order_number')
                            else:
                                raise ValueError('Hotel reservation failed exception')

                        response_data['success'] = True
                        response_data['attendee_id'] = attendee.id
                        response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button',
                                                                              'submit_button_notify_registration_success')
                        response_data['key'] = secret_key
                except Exception as e:
                    ErrorR.efail(e)
                    ErrorR.elog(e)
                    if 'event_user' in request.session:
                        del request.session['event_user']
                    if 'is_user_login' in request.session:
                        del request.session['is_user_login']
                    response_data['success'] = False
                    response_data['redirect_url'] = ''
                    if str(e) == 'Hotel reservation failed exception':
                        response_data['message'] = LanguageKey.catch_lang_key(request, 'hotel-reservation',
                                                                              'hotelreservation_notify_room_validation_msg')
                    else:
                        response_data['message'] = LanguageKey.catch_lang_key(request, 'submit-button',
                                                                              'submit_button_notify_er_registration_failed')
            else:
                response_data['success'] = False
                response_data['redirect_url'] = ''
                message = LanguageKey.catch_lang_key(request, 'submit-button','submit_button_notify_er_registration_email')
                message = message.replace("{email}",exist_email)
                response_data['message'] = message
        return response_data

    def create_secret_password(request):
        setting_uid_length = Setting.objects.filter(name='uid_length', event_id=request.session['event_id'])
        if setting_uid_length:
            uid_length = int(setting_uid_length[0].value)
        else:
            uid_length = 16
        secret_key = ''.join(
            random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
            range(uid_length))
        password_character = '!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        password = ''.join(
            random.choice(password_character) for _ in range(6))
        attendee_password = make_password(password)
        badge_key = ''.join(
            random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in
            range(uid_length))
        return [secret_key, attendee_password, badge_key]

    def autoAddSessionUsingSubmitButton(request,settings_data):
        response = {}
        if 'sessions' in settings_data and len(settings_data['sessions']) > 0:
            auto_add_sessions = settings_data['sessions']
            event_id = request.session['event_id']
            user_id = request.session['event_user']['id']
            if settings_data['remove_conflict_session']:
                if not request.POST._mutable:
                    request.POST._mutable = True
                request.POST['conflict_session_setting'] = '1'
            for session_id in auto_add_sessions:
                response = SessionDetail.status_type_attend_act_radio(request, session_id, [])
                if response['result'] and not response['exists']:
                    ## Economy Start
                    if response['status'] == 'attending':
                        order_number = request.POST.get('order_number')
                        if not order_number or order_number == 'None':
                            order_number = None
                        order_values = EconomyLibrary.place_order(event_id=event_id, user_id=user_id,
                                                                  item_type='session',
                                                                  item_id=session_id, admin_id=None,
                                                                  order_number=order_number)
                        if order_values:
                            response['order_number'] = order_values['order_number']
                            rebate_type = request.POST.get('rebate_type')
                            rebates = request.POST.get('rebates')
                            if rebate_type and rebates:
                                Registration.check_and_apply_rebate(request, rebate_type, rebates, user_id, order_values)
                        else:
                            response['order_number'] = None
                    ## Economy End
        return response

class AutoLoginView(TemplateView):
    # def auto_login_user(request, user_key, *args, **kwargs):
    #     from publicfront.gt_views.login import UserLogin
    #     login_user = UserLogin.loginUser(request, user_key)
    #     return login_user

    # def update_tags(request, *args, **kwargs):
    #     from django.db import connection
    #     from app.models import Tag, GeneralTag
    #     sql = "SELECT attendees.event_id, attendee_tags.tag_id FROM attendees,  `attendee_tags` WHERE attendee_tags.attendee_id = attendees.id GROUP BY attendee_tags.tag_id"
    #     cursor = connection.cursor()
    #
    #     cursor.execute(sql)
    #     rows = cursor.fetchall()
    #     data = []
    #     for row in rows:
    #         event_id = row[0]
    #         tag_id = row[1]
    #         data.append({'event_id':event_id,'tag_id':tag_id})
    #     for d in data:
    #         Tag.objects.filter(id=d['tag_id']).update(event_id=d['event_id'])
    #
    #     general_sql = "SELECT groups.event_id,session_has_tags.tag_id from groups,sessions,session_has_tags where sessions.id=session_has_tags.session_id and groups.id=sessions.group_id GROUP BY session_has_tags.tag_id"
    #     cursor.execute(general_sql)
    #     general_rows = cursor.fetchall()
    #     general_data = []
    #     for general_row in general_rows:
    #         event_id = general_row[0]
    #         tag_id = general_row[1]
    #         general_data.append({'event_id':event_id,'tag_id':tag_id})
    #     for g_d in general_data:
    #         GeneralTag.objects.filter(id=d['tag_id']).update(event_id=d['event_id'])
    #
    #     response_data = {
    #         'data': data,
    #         'general_data': general_data
    #     }
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def insert_ques(request, *args, **kwargs):
    #     import time
    #     from app.models import Answers
    #     total_time= time.time()
    #     answers_array = []
    #     question_277_attendees_1 = [3229,3245,3258,3267,3273,3278,3284,3293,3316,3317,3325,3345,3348,3350,3363,3388,3390,3391,3392,3393]
    #     question_277_attendees_2 = [3241,3253,3272,3280,3286,3291,3297,3301,3305,3319,3343,3352,3366,3367,3370,3372,3418]
    #     question_277_attendees_3 = [3232,3254,3287,3323,3327,3328,3329,3330,3331,3332,3334,3335,3336,3337,3338,3339,3341,3342,3344,3346,3347,3349,3353,3355,3356,3357,3358,3359,3362,3364,3365,3368,3369,3373,3374,3375,3376,3377,3378,3379,3381,3382,3383,3384,3385,3389,3398,3399,3401,3403,3405,3407,3408,3410,3412,3413,3414,3417,3422]
    #     question_277_attendees_4 = [3230,3233,3234,3235,3236,3237,3238,3239,3240,3242,3243,3244,3246,3247,3248,3249,3251,3252,3255,3256,3257,3259,3260,3262,3263,3264,3265,3266,3268,3270,3271,3274,3275,3277,3279,3281,3282,3283,3285,3288,3290,3292,3294,3295,3296,3298,3299,3300,3302,3303,3304,3306,3307,3308,3310,3311,3312,3313,3314,3315,3318,3320,3321,3322,3424]
    #     question_277_attendees_Egen_utresa = [3269,3289,3361,3380,3386,3423]
    #
    #     answers_277_1 = AutoLoginView.set_ques_answers(question_277_attendees_1,277,'1',answers_array)
    #     answers_277_2 = AutoLoginView.set_ques_answers(question_277_attendees_2,277,'2',answers_277_1)
    #     answers_277_3 = AutoLoginView.set_ques_answers(question_277_attendees_3,277,'3',answers_277_2)
    #     answers_277_4 = AutoLoginView.set_ques_answers(question_277_attendees_4,277,'4',answers_277_3)
    #     answers_277_5 = AutoLoginView.set_ques_answers(question_277_attendees_Egen_utresa,277,'Egen utresa',answers_277_4)
    #
    #
    #     question_278_attendees_1 = [3229,3258,3267,3269,3273,3278,3284,3289,3316,3317,3325,3345,3361,3363,3380,3388,3390,3391,3392,3393]
    #     question_278_attendees_2 = [3241,3253,3272,3280,3286,3291,3297,3301,3305,3319,3343,3366,3367,3370,3372]
    #     question_278_attendees_3 = [3232,3254,3287,3323,3327,3328,3329,3330,3331,3332,3334,3335,3336,3337,3338,3339,3341,3342,3344,3346,3347,3349,3353,3355,3356,3357,3358,3359,3362,3364,3365,3368,3369,3373,3374,3375,3376,3377,3378,3379,3381,3382,3383,3384,3385,3389,3398,3399,3401,3403,3405,3407,3408,3410,3412,3413,3414,3417,3422,3423]
    #     question_278_attendees_4 = [3230,3233,3234,3235,3236,3237,3238,3239,3240,3242,3243,3244,3246,3247,3248,3249,3251,3252,3255,3256,3257,3259,3260,3262,3263,3264,3265,3266,3268,3270,3271,3274,3275,3277,3279,3281,3282,3283,3285,3288,3290,3292,3294,3295,3296,3298,3299,3300,3302,3303,3304,3306,3307,3308,3310,3311,3312,3313,3314,3315,3318,3320,3321,3322,3352,3386,3424]
    #     question_278_attendees_Egen_hemresa = [3245,3293,3348,3350,3418]
    #
    #     answers_278_1 = AutoLoginView.set_ques_answers(question_278_attendees_1,278,'1',answers_277_5)
    #     answers_278_2 = AutoLoginView.set_ques_answers(question_278_attendees_2,278,'2',answers_278_1)
    #     answers_278_3 = AutoLoginView.set_ques_answers(question_278_attendees_3,278,'3',answers_278_2)
    #     answers_278_4 = AutoLoginView.set_ques_answers(question_278_attendees_4,278,'4',answers_278_3)
    #     answers_278_5 = AutoLoginView.set_ques_answers(question_278_attendees_Egen_hemresa,278,'Egen hemresa',answers_278_4)
    #
    #     Answers.objects.bulk_create(answers_278_5)
    #     response_data = {
    #         'data': len(answers_278_5)
    #     }
    #     print("--- %s seconds ---" % (time.time() - total_time))
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def set_ques_answers(attendees,question_id,answer,answers_array):
    #     from app.models import Answers
    #     for attendee in attendees:
    #         data = Answers(question_id=question_id,user_id=attendee,value=answer)
    #         answers_array.append(data)
    #     return answers_array

    # def submit_button_lang(request, *args, **kwargs):
    #     response_data = {}
    #     all_submit_buttons = ElementsAnswers.objects.filter(element_question_id=69)
    #     count = 0
    #     for submit_button in all_submit_buttons:
    #         event_id = submit_button.page.event_id
    #         value = submit_button.answer
    #         try:
    #             json_value = json.loads(value,strict=False)
    #         except:
    #             try:
    #                 presetsEvent = PresetEvent.objects.filter(event_id=event_id).first()
    #                 language_id = presetsEvent.preset_id
    #             except:
    #                 language_id = 6
    #             if language_id:
    #                 obj = {}
    #                 obj[str(language_id)]=value
    #                 new_value = str(obj).replace("'",'"')
    #                 submit_button.answer = new_value
    #                 submit_button.save()
    #                 count = count + 1
    #     response_data['count'] = count
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def content_lang(request, *args, **kwargs):
    #     response_data = {}
    #     all_email_contents = []
    #     emails = EmailContents.objects.all()
    #     for email in emails:
    #         language = PresetEvent.objects.filter(event_id=email.template.event_id)
    #         if language.exists():
    #             if not EmailLanguageContents.objects.filter(language_id=language[0].preset_id,
    #                                                         email_content_id=email.id).exists():
    #                 if email.content != '':
    #                     language_content = EmailLanguageContents(language_id=language[0].preset_id,
    #                                                              email_content_id=email.id, content=email.content)
    #                     language_content.save()
    #                     all_email_contents.append(language_content.as_dict())
    #     response_data['all_email_contents'] = all_email_contents
    #     response_data['count_email'] = len(all_email_contents)
    #
    #     all_message_contents = []
    #     messages = MessageContents.objects.all()
    #     for message in messages:
    #         message_language = PresetEvent.objects.filter(event_id=message.event_id)
    #         if message_language.exists():
    #             if not MessageLanguageContents.objects.filter(language_id=message_language[0].preset_id,
    #                                                           message_content_id=message.id).exists():
    #                 if message.content != '':
    #                     language_content = MessageLanguageContents(language_id=message_language[0].preset_id,
    #                                                                message_content_id=message.id,
    #                                                                content=message.content)
    #                     language_content.save()
    #                     all_message_contents.append(language_content.as_dict())
    #     response_data['all_message_contents'] = all_message_contents
    #     response_data['count_message'] = len(all_message_contents)
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")

    def update_page_content(request, *args, **kwargs):
        response_data = {}
        if 'event_id' in request.GET:
            event_id= request.GET.get('event_id')
            all_pages = PageContent.objects.filter(event_id=event_id)
            response_data['total_page'] = len(all_pages)
            for page in all_pages:
                page.content = page.content.replace('{qid:','{questionid:')
                page.save()
            all_editor = ElementHtml.objects.filter(page__event_id=event_id)
            response_data['total_editor'] = len(all_editor)
            for editor in all_editor:
                editor.compiled = editor.compiled.replace('{answer:','{qid:')
                editor.uncompiled = editor.uncompiled.replace('{answer:','{qid:')
                editor.save()
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add_attendee_bid(request, *args, **kwargs):
        response_data = {}
        if 'id' in request.GET and 'last_id' in request.GET:
            attendee_id = request.GET.get('id')
            last_attendee_id = request.GET.get('last_id')
            all_attendees = Attendee.objects.filter(bid=None,id__gte=attendee_id, id__lte=last_attendee_id)
            response_data['attendee_length'] = len(all_attendees)
            data_ids = []
            sql_bid_case = ''
            for attendee in all_attendees:
                badge_key = ''.join(
                    random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _
                    in
                    range(16))
                sql_bid_case += "WHEN id = " + str(attendee.id) + " THEN '" + badge_key + "' "
                data_ids.append(attendee.id)
            sql_case = 'bid = CASE ' + sql_bid_case + 'END'
            sql = 'update attendees set ' + sql_case + ' WHERE id IN (' + str(data_ids).replace("[", "").replace(
                "]", "") + ')'
            response_data['sql'] = sql
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(sql)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add_new_pages(request, *args, **kwargs):
        response_data = {}
        # try:
        #     events = Events.objects.all()
        #     pages = []
        #     for event in events:
        #         template = EmailTemplates.objects.filter(name='default-web-template', event_id=event.id)
        #         template_id = 1
        #         if template.exists():
        #             template_id = template[0].id
        #         if not PageContent.objects.filter(url='404-not-found',event_id=event.id).exists():
        #             page_form_1 = {
        #                 "url": '404-not-found',
        #                 "content": '',
        #                 "created_by_id": 1,
        #                 "last_updated_by_id": 1,
        #                 "template_id": template_id,
        #                 "event_id": event.id
        #             }
        #             page_1 = PageContent(**page_form_1)
        #             pages.append(page_1)
        #         if not PageContent.objects.filter(url='403-forbidden-registered', event_id=event.id).exists():
        #             page_form_2 = {
        #                 "url": '403-forbidden-registered',
        #                 "content": '',
        #                 "created_by_id": 1,
        #                 "last_updated_by_id": 1,
        #                 "template_id": template_id,
        #                 "event_id": event.id
        #             }
        #             page_2 = PageContent(**page_form_2)
        #             pages.append(page_2)
        #         if not PageContent.objects.filter(url='403-forbidden-unregistered', event_id=event.id).exists():
        #             page_form_3 = {
        #                 "url": '403-forbidden-unregistered',
        #                 "content": '',
        #                 "created_by_id": 1,
        #                 "last_updated_by_id": 1,
        #                 "template_id": template_id,
        #                 "event_id": event.id
        #             }
        #             page_3 = PageContent(**page_form_3)
        #             pages.append(page_3)
        #     PageContent.objects.bulk_create(pages)
        #     response_data['success'] = True
        #     response_data['events_length'] = len(events)
        #     response_data['pages_length'] = len(pages)
        # except Exception as e:
        #     ErrorR.efail(e)
        #     response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def delete_act(request, *args, **kwargs):
    #     response_data = {}
    #     if 'id' in request.GET and 'last_id' in request.GET:
    #         id_array = []
    #         attendee_id = request.GET.get('id')
    #         last_attendee_id = request.GET.get('last_id')
    #         attendees = Attendee.objects.filter(id__gte=attendee_id, id__lte=last_attendee_id, event_id=26)
    #         for att in attendees:
    #             activities = ActivityHistory.objects.filter(attendee_id=att.id).values('id')[:5]
    #             id_array.append(activities[0]['id'])
    #             id_array.append(activities[1]['id'])
    #             id_array.append(activities[2]['id'])
    #             id_array.append(activities[3]['id'])
    #             id_array.append(activities[4]['id'])
    #             # ActivityHistory.objects.filter(attendee_id=att.id,id__gt=activities[4]['id']).delete()
    #         response_data['id_array'] = id_array
    #         response_data['total_attendee'] = len(attendees)
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")

    def logged_in_using_admin_email(request, *args, **kwargs):
        print('here')
        return HttpResponse(json.dumps({}), content_type="application/json")
