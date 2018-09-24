from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from app.models import PageContent, Questions, ElementsAnswers, \
    SeminarsUsers, Setting, Answers, Notification, Session, SessionTags, SeminarSpeakers, Group, Locations, Attendee, \
    Booking, RequestedBuddy, \
    PluginSubmitButton, Room, ActivityHistory, Events, PhotoGroup, Photo, PresetEvent
from app.views.hotel_view import RoomView
from publicfront.views.attendee_plugin import AttendeePluginList
import json
from datetime import datetime, timedelta
import re
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from pytz import timezone
from django.db.models import Q
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey
from publicfront.views.profile import SessionDetail
from publicfront.views.session_seat_availability import SessionSeatAvailability
import time, math
from publicfront.views.details import DetailsData
from publicfront.views.helper import HelperData


class Plugins(generic.TemplateView):
    def get_evaluation(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-evaluations" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="evaluations">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
                    time_now = HelperData.getTimezoneNow(request)
                    f = '%Y-%m-%d %H:%M:%S'
                    today = datetime.strptime(str(time_now).split(".")[0], f)
                    title = ''
                    appear_time = 11
                    message = ''
                    for setting in element_settings:
                        if setting.element_question.question_key == 'evaluation_title':
                            title = setting.answer
                        elif setting.element_question.question_key == 'evaluation_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            message = setting.description
                        elif setting.element_question.question_key == 'evaluation_appear':
                            appear_time = setting.answer
                    current_time = today + timedelta(minutes=-int(appear_time))
                    sql = "SELECT `seminars_has_users`.`id`, `seminars_has_users`.`attendee_id`, `seminars_has_users`.`session_id`, `seminars_has_users`.`status`, `seminars_has_users`.`created`, `seminars_has_users`.`queue_order` FROM `seminars_has_users` INNER JOIN `sessions` ON ( `seminars_has_users`.`session_id` = `sessions`.`id` ) WHERE (`sessions`.`end` < '" + str(
                        current_time) + "' AND `seminars_has_users`.`attendee_id` =" + str(
                        user_id) + " AND `sessions`.`show_on_evaluation` = True AND `seminars_has_users`.`status` = 'attending' AND NOT ((`seminars_has_users`.`session_id`) IN (SELECT U0.`session_id` FROM `session_ratings` U0 WHERE U0.`attendee_id` = " + str(
                        user_id) + ")))"
                    sessions = SeminarsUsers.objects.raw(
                        sql
                    )
                    sessions_data = list(sessions)
                    for session in sessions_data:
                        session.session = LanguageKey.get_session_data_by_language(request, session.session)
                    context = {
                        "title": title,
                        "sessions": sessions_data,
                        "message": message,
                        "language": language,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id']
                    }
                    return render_to_string('public/element/session_evaluation.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        language['langkey']['evaluation_txt_empty'])
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['evaluation_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['evaluation_txt_misconfigured'])

    def get_messages(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-messages" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="messages">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
                    title = ''
                    message = ''
                    archive_messages = 'True'
                    archive_button = 'True'
                    show_archive_button = 'False'
                    mark_all_button = 'True'
                    for setting in element_settings:
                        if setting.element_question.question_key == 'message_title':
                            title = setting.answer
                        elif setting.element_question.question_key == 'message_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            message = setting.description
                        elif setting.element_question.question_key == 'message_allow_archive':
                            archive_messages = setting.answer
                        elif setting.element_question.question_key == 'message_archive_button':
                            archive_button = setting.answer
                        elif setting.element_question.question_key == 'message_read_button':
                            mark_all_button = setting.answer
                    notification = Notification.objects.filter(to_attendee_id=user_id, status=0).order_by('-id')
                    total_seconds = HelperData.get_timout(request.session['event_id'])
                    for nt in notification:
                        first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                            user_id=nt.sender_attendee_id)
                        last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                           user_id=nt.sender_attendee_id)
                        if first_name.exists():
                            nt.sender_attendee.firstname = first_name[0].value
                        if last_name.exists():
                            nt.sender_attendee.lastname = last_name[0].value
                        nt.expire_at = nt.created_at + timedelta(seconds=total_seconds)
                        nt.created_at = HelperData.utc_to_local(request, str(nt.created_at))
                    if Notification.objects.filter(to_attendee_id=user_id, status=1).exists():
                        show_archive_button = 'True'
                    # language = LanguageKey.get_lang_key(request.session['event_id'], element['element_id'])
                    language['langkey']['pre_message_countdown'] = \
                        language['langkey']['messages_txt_countdown'].split('{countdown}')[0]
                    language['langkey']['post_message_countdown'] = \
                        language['langkey']['messages_txt_countdown'].split('{countdown}')[1]
                    context = {
                        "title": title,
                        "message": message,
                        "archive_messages": archive_messages,
                        "archive_button": archive_button,
                        "mark_all_button": mark_all_button,
                        "notifications": list(notification),
                        "language": language,
                        "show_archive_button": show_archive_button,
                        "request": request,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id']
                    }

                    return render_to_string('public/element/messages.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        language['langkey']['messages_txt_empty'])
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['messages_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['messages_txt_misconfigured'])

    def get_archive_messages(request, page_id, element):
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    box_id = element['box_id'].split('-')[1]
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
                    message = ''
                    for setting in element_settings:
                        if setting.element_question.question_key == 'archive_messages_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            message = setting.description

                    archived_messages = Notification.objects.filter(to_attendee_id=user_id).order_by('-id')
                    total_seconds = HelperData.get_timout(request.session['event_id'])
                    for nt in archived_messages:
                        first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                            user_id=nt.sender_attendee_id)
                        last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                           user_id=nt.sender_attendee_id)
                        if first_name.exists():
                            nt.sender_attendee.firstname = first_name[0].value
                        if last_name.exists():
                            nt.sender_attendee.lastname = last_name[0].value
                        nt.expire_at = nt.created_at + timedelta(seconds=total_seconds)
                        nt.created_at = HelperData.utc_to_local(request, str(nt.created_at))

                    language = LanguageKey.get_lang_key(request, element['element_id'])
                    language['langkey']['pre_message_countdown'] = \
                        language['langkey']['archive_messages_txt_countdown'].split('{countdown}')[0]
                    language['langkey']['post_message_countdown'] = \
                        language['langkey']['archive_messages_txt_countdown'].split('{countdown}')[1]
                    context = {
                        "message": message,
                        "archived_messages": archived_messages,
                        "language": language,
                        "request": request,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id']
                    }
                    return render_to_string('public/element/archived_messages.html', context)
                else:
                    return ''
            else:
                return ''
        except Exception as e:
            ErrorR.efail(e)
            return ''

    def get_photo_gallery(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-messages" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="messages">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    box_id = element['box_id'].split('-')[1]
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    context = {
                        "request": request,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id']
                    }
                    context['photo_groups'] = None
                    context['photo_per_page'] = ''
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
                    for setting in element_settings:
                        if setting.element_question.question_key == 'photo_gallery_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            context['message'] = setting.description
                        elif setting.element_question.question_key == 'photo_gallery_groups':
                            context['photo_groups'] = [eval(p_g) for p_g in json.loads(setting.answer)]
                        elif setting.element_question.question_key == 'photo_gallery_photo_per_page':
                            context['photo_per_page'] = setting.answer
                        elif setting.element_question.question_key == 'photo_gallery_full_size_photo':
                            context['full_size_photo'] = setting.answer
                        elif setting.element_question.question_key == 'photo_gallery_only_my_photos':
                            context['only_my_photos'] = setting.answer
                        elif setting.element_question.question_key == 'photo_gallery_show_comment':
                            context['show_comment'] = setting.answer
                        elif setting.element_question.question_key == 'photo_gallery_show_submitter_name':
                            context['submitter_name'] = setting.answer
                    if context['photo_groups']:
                        if len(context['photo_groups']) > 0:
                            no_of_images = Photo.objects.filter(attendee__event_id=event_id, is_approved=1,
                                                                attendee_id=user_id,
                                                                group__in=context['photo_groups']).count() if eval(
                                context['only_my_photos']) else Photo.objects.filter(group__page__event_id=event_id,
                                                                                     is_approved=1, group__in=context[
                                    'photo_groups']).count()
                        else:
                            no_of_images = Photo.objects.filter(attendee__event_id=event_id, is_approved=1,
                                                                attendee_id=user_id).count() if eval(
                                context['only_my_photos']) else Photo.objects.filter(group__page__event_id=event_id,
                                                                                     is_approved=1).count()
                    else:
                        no_of_images = 0
                    context['language'] = language
                    if context['photo_per_page'].isdigit():
                        context['no_of_pagination'] = range(math.ceil(no_of_images / int(context['photo_per_page'])))
                        if no_of_images == 0:
                            context['no_photo_exists'] = True
                            context['pagination'] = False
                        else:
                            context['no_photo_exists'] = False
                            context['pagination'] = True
                    else:
                        context['pagination'] = False
                        context['no_photo_exists'] = True if no_of_images == 0 else False
                    return render_to_string('public/element/photo_gallery.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        'Photo gallery is empty')
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % ('Photo gallery is empty')
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                'Photo gallery is misconfigured')

    def get_photo_gallery_image(request, *args, **kwargs):
        photoList = []
        no_of_images = 0
        all_photho_no = 0
        language = None
        if 'is_user_login' in request.session and request.session['is_user_login']:
            event_id = request.session['event_id']
            user_id = request.session['event_user']['id']
            try:
                element_id = int(request.GET['element_id'])
                language = LanguageKey.get_lang_key(request, element_id)
                skip = int(request.GET['skip'])
                photo_per_page = request.GET['photo_per_page']
                photo_groups = json.loads(request.GET['photo_groups'])
                if photo_per_page.isdigit():
                    photo_per_page = int(request.GET['photo_per_page'])
                    max = skip * photo_per_page
                    skip = (skip - 1) * photo_per_page
                else:
                    max = 100
                    skip = 0

                full_size_photo = eval(request.GET['full_size_photo'])
                only_my_photos = eval(request.GET['only_my_photos'])
                show_comment = request.GET['show_comment']
                uploader_name = request.GET['uploader_name']

                if only_my_photos:
                    photos = Photo.objects.filter(attendee__event_id=event_id, is_approved=1, attendee_id=user_id,
                                                  group__in=photo_groups).order_by('-id')
                    all_photho_no = len(photos)
                else:
                    photos = Photo.objects.filter(group__page__event_id=event_id, is_approved=1,
                                                  group__in=photo_groups).order_by('-id')
                    all_photho_no = len(photos)
                counter = 0
                for photo in photos:
                    if counter > skip - 1:
                        if max == counter:
                            break
                        if full_size_photo:
                            comment = photo.comment if show_comment in ['full-size', 'both'] else None
                            uploader = photo.attendee.firstname + ' ' + photo.attendee.lastname if uploader_name in [
                                'full-size', 'both'] else None
                        else:
                            comment = photo.comment if show_comment in ['thumbnail', 'both'] else None
                            uploader = photo.attendee.firstname + ' ' + photo.attendee.lastname if uploader_name in [
                                'thumbnail', 'both'] else None

                        photoList.append({
                            'photo_id': photo.id,
                            'photo_group': re.sub(r"\s+", '-', photo.group.name),
                            'src': settings.STATIC_URL_ALT + photo.photo if full_size_photo else settings.STATIC_URL_ALT + photo.thumb_image,
                            'comment': comment,
                            'uploader': uploader,
                            'full_size_photo': full_size_photo
                        })
                        no_of_images += 1
                    counter += 1
            except Exception as exception:
                print(exception)
                pass

        photo_items = render_to_string('public/element/photo_gallery_item.html',
                                       {'items': photoList, 'language': language})
        context = {'photo_items': photo_items, 'no_of_images': no_of_images,
                   'from': skip + 1 if all_photho_no > 0 else 0, 'to': max if max < all_photho_no else all_photho_no,
                   'all_photo_no': all_photho_no}
        return HttpResponse(json.dumps(context), content_type="application/json")

    def get_gallery_photo_details(request, *args, **kwargs):
        data = {'src': '', 'comment': '', 'uploader': ''}
        if 'is_user_login' in request.session and request.session['is_user_login']:
            try:
                photo_id = request.GET['id']
                show_comment = request.GET['show_comment']
                uploader_name = request.GET['uploader_name']
                photo = Photo.objects.get(id=photo_id)
                data['src'] = settings.STATIC_URL_ALT + photo.photo
                data['photo_group'] = re.sub(r"\s+", '-', photo.group.name)
                if show_comment in ['full-size', 'both']:
                    data['comment'] = photo.comment if photo.comment else ''

                if uploader_name in ['full-size', 'both']:
                    data['uploader'] = photo.attendee.firstname + ' ' + photo.attendee.lastname

            except Exception as exception:
                print(exception)
                ErrorR.efail(exception)
                pass
        return JsonResponse(data)

    def get_session_next_up(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-next-up" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="next-up">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)

                    time_now = HelperData.getTimezoneNow(request)
                    f = '%Y-%m-%d %H:%M:%S'
                    now = datetime.strptime(str(time_now).split(".")[0], f)
                    title = ''
                    message = ''
                    appear_before = 60
                    disappear_after = 15
                    start_time_appear = 'True'
                    start_date_appear = 'True'
                    location_appear = 'True'
                    location_link_appear = 'True'
                    speaker_appear = 'True'
                    speaker_link_appear = 'True'
                    for setting in element_settings:
                        if setting.element_question.question_key == 'next_up_title':
                            title = setting.answer
                        elif setting.element_question.question_key == 'next_up_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            message = setting.description
                        elif setting.element_question.question_key == 'next_up_appear':
                            appear_before = setting.answer
                        elif setting.element_question.question_key == 'next_up_disappear':
                            disappear_after = setting.answer
                        elif setting.element_question.question_key == 'next_up_start_time':
                            start_time_appear = setting.answer
                        elif setting.element_question.question_key == 'next_up_start_date':
                            start_date_appear = setting.answer
                        elif setting.element_question.question_key == 'next_up_location':
                            location_appear = setting.answer
                        elif setting.element_question.question_key == 'next_up_link_location':
                            location_link_appear = setting.answer
                        elif setting.element_question.question_key == 'next_up_speaker':
                            speaker_appear = setting.answer
                        elif setting.element_question.question_key == 'next_up_link_speaker':
                            speaker_link_appear = setting.answer
                    time_before = now + timedelta(minutes=int(appear_before))
                    time_after = now - timedelta(minutes=int(disappear_after))
                    time_before = datetime.strptime(str(time_before).split(".")[0], f)
                    time_after = datetime.strptime(str(time_after).split(".")[0], f)
                    # Searchable removed
                    sql = 'select DISTINCT sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                        user_id) + ' and sessions.group_id = groups.id and (sessions.start <= "' + str(
                        time_before) + '" and sessions.start >="' + str(time_after) + '")'
                    sessions = Session.objects.raw(
                        sql
                    )
                    nextUpSessions = []
                    if len(list(sessions)) > 0:
                        for session in sessions:
                            session = LanguageKey.get_session_data_by_language(request, session)
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
                                    badge_firstname = Answers.objects.filter(question__actual_definition='firstname',
                                                                             user_id=speaker.speaker.id)
                                    if badge_firstname.exists():
                                        firstname = badge_firstname[0].value
                                    else:
                                        firstname = speaker.speaker.firstname

                                    badge_lastname = Answers.objects.filter(question__actual_definition='lastname',
                                                                            user_id=speaker.speaker.id)
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
                            difference = (datetime.strptime(str(session.start).split("+")[0], f) - now).total_seconds()
                            if difference > 0:
                                difference = difference / 60
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
                            nextUpSessions.append(session_obj)

                    context = {
                        "title": title,
                        "nextUpSessions": nextUpSessions,
                        "message": message,
                        "start_time_appear": start_time_appear,
                        "start_date_appear": start_date_appear,
                        "location_appear": location_appear,
                        "location_link_appear": location_link_appear,
                        "speaker_appear": speaker_appear,
                        "speaker_link_appear": speaker_link_appear,
                        "language": language,
                        "request": request,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id']
                    }
                    return render_to_string('public/element/session_next_up.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        language['langkey']['nextup_txt_empty'])
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['nextup_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['nextup_txt_misconfigured'])

    def get_attendee_plugin(request, page_id, element):
        language = LanguageKey.catch_lang_key_obj(request, "attendee-list")
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-attendee-list" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="attendee-list">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                element_answers = ElementsAnswers.objects.filter(box_id=box_id, page_id=page_id)
                context = {}
                selected_columns = []
                filter_id = 0
                for answer in element_answers:
                    if answer.element_question.question_key == 'attendee_list_title':
                        context['title'] = answer.answer
                    elif answer.element_question.question_key == 'attendee_list_message':
                        answer.description = LanguageKey.get_plugin_description_by_language(request, answer.description)
                        context['message'] = answer.description
                    elif answer.element_question.question_key == 'attendee_list_allow_excel_export':
                        context['excel_button'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'attendee_list_show_search_field':
                        context['search_field'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'attendee_list_filter_id':
                        filter_id = eval(answer.answer)
                        context['filter_id'] = filter_id
                    elif answer.element_question.question_key == 'attendee_list_selected_columns':
                        selected_columns_data = json.loads(answer.answer)
                        selected_columns = selected_columns_data['selected_sorted']
                        context['column_ids'] = selected_columns
                        col_ques = Questions.objects.filter(id__in=selected_columns).values("id", "title",
                                                                                            "actual_definition")
                        visible_columns = []
                        for item in selected_columns:
                            visible_columns.append(col_ques.get(id=item))
                        for ids, col_question in enumerate(visible_columns):
                            if col_question['actual_definition'] == None or col_question['actual_definition'] == '':
                                visible_columns[ids]['actual_definition'] = col_question['title'].replace(' ', '_')
                        context['columns'] = visible_columns

                x_y_z = 'Showing {0}-{1} from {2} data items'
                if 'attendee_list_txt_x_y_of_z' in language['langkey']:
                    x_y_z = language['langkey']['attendee_list_txt_x_y_of_z']
                    x_y_z = x_y_z.replace('{X}', '{0}').replace('{Y}', '{1}').replace('{Z}', '{2}')
                language['langkey']['attendee_list_txt_x_y_of_z'] = x_y_z
                context['language'] = language

                # new

                column_ids = selected_columns
                if filter_id != 0:
                    attendees = AttendeePluginList.get_all_attendee(request, filter_id)
                    attendee_data = AttendeePluginList.get_attendee(request, attendees, column_ids)
                    columns = []
                    for column_id in column_ids:
                        question = Questions.objects.get(id=column_id)
                        question = LanguageKey.get_question_data_by_language(request, question)
                        columns.append(question.title)

                    context["attendee_datas"] = attendee_data
                    context["column_names"] = columns
                    context["page_id"] = page_id
                    context["box_id"] = box_id
                    context["element_id"] = element['element_id']
                    return render_to_string('public/element/attendee_list.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        language['langkey']['attendee_list_txt_empty'])
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['attendee_list_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['attendee_list_txt_misconfigured'])

    def get_plugin_hotel_reservation(request, page_id, element):
        language = LanguageKey.catch_lang_key_obj(request, "hotel-reservation")
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-hotel-reservation" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="hotel-reservation">"""
        att_bookings = None
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                existig_bookings = Booking.objects.filter(attendee_id=request.session['event_user']['id'])
                # 'done' is for checker that a booking does not appear twice (checked in js)
                att_bookings = [
                    {'room': booking.room_id, 'done': 'no', 'checkin': booking.check_in.strftime('%Y-%m-%d'),
                     'checkout': booking.check_out.strftime('%Y-%m-%d'),
                     'buddies': [buddy.buddy.firstname + ' ' + buddy.buddy.lastname if buddy.exists else buddy.email for
                                 buddy in RequestedBuddy.objects.filter(booking_id=booking.id)]} for booking in
                    existig_bookings]

            element_answers = ElementsAnswers.objects.filter(box_id=box_id, page_id=page_id)
            context = {}
            hotel_group = None
            for answer in element_answers:
                if answer.element_question.question_key == 'hotel_reservation_title':
                    context['title'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_message':
                    answer.description = LanguageKey.get_plugin_description_by_language(request, answer.description)
                    context['message'] = answer.description
                elif answer.element_question.question_key == 'hotel_reservation_default_check_in_date':
                    context['default_check_in_date'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_default_check_out_date':
                    context['default_check_out_date'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_force_default_dates':
                    context['force_default_dates'] = answer.answer
                    context['a_remove_btn_hide'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_require_room_buddy':
                    context['require_room_buddy'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_require_room_selection':
                    context['require_room_selection'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_hotel_groups':
                    hotel_group = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_force_hotel_room_type':
                    context['force_hotel_room_type'] = answer.answer
                elif answer.element_question.question_key == 'hotel_reservation_allow_partial_stays':
                    if context['force_default_dates'] == "True":
                        context['allow_partial_stays'] = '1'
                        context['allow_partial_stays_range'] = range(0, 1)
                    else:
                        if answer.answer == '1':
                            # if partial allow is 1, then not to show add-remove button
                            context['a_remove_btn_hide'] = True
                        context['allow_partial_stays'] = answer.answer
                        context['allow_partial_stays_range'] = range(0, 1)
            context['language'] = language
            context['page_id'] = page_id
            context['element_id'] = box_id
            context['box_id'] = box_id
            context['plugin_id'] = element['element_id']
            try:
                week_start_day = Setting.objects.get(name='week_start_day', event_id=request.session['event_id']).value
                if week_start_day == 'sun':
                    context['week_start_day'] = 0
                elif week_start_day == 'mon':
                    context['week_start_day'] = 1
            except:
                context['week_start_day'] = 1

            try:
                setting_default_date_format = Setting.objects.filter(name='default_date_format',
                                                                     event_id=request.session['event_id'])
                if setting_default_date_format:
                    context['default_date_format'] = json.loads(setting_default_date_format[0].value)['kendo']
                else:
                    context['default_date_format'] = "MM-dd-yyyy"
            except:

                context['default_date_format'] = "MM-dd-yyyy"

            try:
                kendo_language_select = Setting.objects.get(name='plugin_language',
                                                            event_id=request.session['event_id']).value
                context['kendo_language_select'] = kendo_language_select
            except:
                context['kendo_language_select'] = ''

            hotel_info = []
            if hotel_group:
                if hotel_group and context['force_hotel_room_type'] == 'do-not-force':
                    hotel_rooms = Room.objects.filter(hotel__group__in=json.loads(hotel_group))
                    for h_room_item in hotel_rooms:
                        h_room_item = LanguageKey.get_room_data_by_language(request, h_room_item)
                        result = RoomView.find_booking(str(h_room_item.id))
                        result_oc = True if result['total_occupancy'] > 99 else False
                        room_allotmentsDates = []
                        for ra in result['details']:
                            if ra['occupancy'] < 100:
                                room_allotmentsDates.append(ra['available_date'])

                        # adding 1 extra date for more than allotment 1 check-out date
                        if room_allotmentsDates:
                            extra_date = datetime.strptime(room_allotmentsDates[-1], '%Y-%m-%d')
                            extra_date = extra_date + timedelta(days=1)
                            extra_date = extra_date.strftime('%Y-%m-%d')
                            room_allotmentsDates.append(extra_date)
                        else:
                            result_oc = True

                        hotel_info.append(
                            {'id': h_room_item.id, 'hotel': h_room_item.hotel.name,
                             'description': h_room_item.description, 'beds': h_room_item.beds,
                             'location': h_room_item.hotel.location.name, 'occupancy': result_oc,
                             'available_dates': json.dumps(room_allotmentsDates)})

                    context['hotel_info'] = hotel_info
                elif context['force_hotel_room_type'] != 'do-not-force':
                    context['force_hotel_room_selection'] = True
                    hotel_room = Room.objects.filter(id=context['force_hotel_room_type'])[0]
                    hotel_room = LanguageKey.get_room_data_by_language(request, hotel_room)
                    result = RoomView.find_booking(str(hotel_room.id))
                    result_oc = True if result['total_occupancy'] > 99 else False
                    room_allotmentsDates = []
                    for ra in result['details']:
                        if ra['occupancy'] < 100:
                            room_allotmentsDates.append(ra['available_date'])

                    # adding 1 extra date for more than allotment 1 check-out date
                    if room_allotmentsDates:
                        extra_date = datetime.strptime(room_allotmentsDates[-1], '%Y-%m-%d')
                        extra_date = extra_date + timedelta(days=1)
                        extra_date = extra_date.strftime('%Y-%m-%d')
                        room_allotmentsDates.append(extra_date)
                    else:
                        result_oc = True

                    context['hotel_info'] = [
                        {'id': hotel_room.id, 'hotel': hotel_room.hotel.name, 'description': hotel_room.description,
                         'beds': hotel_room.beds,
                         'location': hotel_room.hotel.location.name, 'occupancy': result_oc,
                         'available_dates': json.dumps(room_allotmentsDates)}]
                if att_bookings:
                    context['bookings'] = json.dumps(att_bookings)
                    partial_allow = 0
                    for booking in att_bookings:
                        if booking['room'] in [room['id'] for room in context['hotel_info']]:
                            partial_allow += 1
                    if partial_allow > 1:
                        context['allow_partial_stays_range'] = range(0, partial_allow)
                return render_to_string('public/element/hotel_reservation.html', context)
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['hotelreservation_txt_empty'])

        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['hotelreservation_txt_misconfigured'])

    def get_location_list(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-location-list" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="location-list">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
                title = ''
                message = ''
                list_searchable = 'True'
                location_groups = ''
                location_title = 'True'
                location_details = 'True'
                description = 'True'
                link_map = 'True'
                address_details = 'True'
                contact_details = 'True'
                for setting in element_settings:
                    if setting.element_question.question_key == 'location_title':
                        title = setting.answer
                    elif setting.element_question.question_key == 'location_message':
                        setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                             setting.description)
                        message = setting.description
                    elif setting.element_question.question_key == 'location_list_searchable':
                        list_searchable = setting.answer
                    elif setting.element_question.question_key == 'location_location_groups':
                        location_groups = json.loads(setting.answer)
                    elif setting.element_question.question_key == 'location_list_title':
                        location_title = setting.answer
                    elif setting.element_question.question_key == 'location_link_location_details':
                        location_details = setting.answer
                    elif setting.element_question.question_key == 'location_description':
                        description = setting.answer
                    elif setting.element_question.question_key == 'location_link_map':
                        link_map = setting.answer
                    elif setting.element_question.question_key == 'location_address_details':
                        address_details = setting.answer
                    elif setting.element_question.question_key == 'location_contact_details':
                        contact_details = setting.answer
                if location_groups != '':
                    locationGroups = Group.objects.filter(type="location", is_show=1, is_searchable=1,
                                                          event_id=request.session['event_id'],
                                                          id__in=location_groups).order_by('group_order')
                    for group in locationGroups:
                        group.location = Locations.objects.filter(group_id=group.id).order_by('location_order')
                        for location in group.location:
                            location = LanguageKey.get_location_data_by_language(request, location)
                            location.address = location.address.replace(',', '<br/>')

                    context = {
                        "title": title,
                        "locationGroups": locationGroups,
                        "message": message,
                        "list_searchable": list_searchable,
                        "location_title": location_title,
                        "location_details": location_details,
                        "description": description,
                        "link_map": link_map,
                        "address_details": address_details,
                        "contact_details": contact_details,
                        "language": language,
                        "request": request,
                        "page_id": page_id,
                        "box_id": box_id,
                        "element_id": element['element_id']
                    }
                    return render_to_string('public/element/location_list.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        language['langkey']['locationlist_txt_empty'])
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['locationlist_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['locationlist_txt_misconfigured'])

    def get_session_radio(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-session-radio" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-radio">"""
        try:
            # if 'is_user_login' in request.session and request.session['is_user_login']:
            event_id = request.session["event_id"]
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            message = ''
            session_enable = 'True'
            session_groups = ''
            session_choose = 'True'
            description = 'True'
            start_time = 'True'
            start_date = 'True'
            end_time = 'True'
            end_date = 'True'
            rvsp_date = 'True'
            speaker = 'True'
            speaker_link = 'True'
            tags = 'True'
            group_appear = 'True'
            location = 'True'
            location_link = 'True'
            session_option = ''
            preselected_session = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'session_radio_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'session_radio_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                elif setting.element_question.question_key == 'session_radio_session_enable':
                    session_enable = setting.answer
                elif setting.element_question.question_key == 'session_radio_session_groups':
                    session_groups = json.loads(setting.answer)
                elif setting.element_question.question_key == 'session_radio_session_choose':
                    session_choose = setting.answer
                elif setting.element_question.question_key == 'session_radio_description':
                    description = setting.answer
                elif setting.element_question.question_key == 'session_radio_start_time':
                    start_time = setting.answer
                elif setting.element_question.question_key == 'session_radio_start_date':
                    start_date = setting.answer
                elif setting.element_question.question_key == 'session_radio_end_time':
                    end_time = setting.answer
                elif setting.element_question.question_key == 'session_radio_end_date':
                    end_date = setting.answer
                elif setting.element_question.question_key == 'session_radio_rvsp_date':
                    rvsp_date = setting.answer
                elif setting.element_question.question_key == 'session_radio_speaker':
                    speaker = setting.answer
                elif setting.element_question.question_key == 'session_radio_link_speaker':
                    speaker_link = setting.answer
                elif setting.element_question.question_key == 'session_radio_tags':
                    tags = setting.answer
                elif setting.element_question.question_key == 'session_radio_session_group':
                    group_appear = setting.answer
                elif setting.element_question.question_key == 'session_radio_location':
                    location = setting.answer
                elif setting.element_question.question_key == 'session_radio_link_location':
                    location_link = setting.answer
                elif setting.element_question.question_key == 'session_radio_session_available':
                    session_option = setting.answer
                elif setting.element_question.question_key == 'session_radio_preselected':
                    preselected_session = setting.answer
            if session_groups != '':
                sessionGroups = Group.objects.filter(type="session", is_show=1, is_searchable=1,
                                                     event_id=request.session['event_id'],
                                                     id__in=session_groups).order_by('group_order')
                if preselected_session != '':
                    SessionDetail.status_type_attend(request, int(preselected_session))
                session_details = Plugins.get_session_details(request, sessionGroups, event_id, session_option)
                context = {
                    "title": title,
                    "sessionGroups": list(session_details['sessionGroups']),
                    "message": message,
                    "session_enable": session_enable,
                    "session_choose": session_choose,
                    "description": description,
                    "start_time": start_time,
                    "start_date": start_date,
                    "end_time": end_time,
                    "end_date": end_date,
                    "rvsp_date": rvsp_date,
                    "speaker": speaker,
                    "speaker_link": speaker_link,
                    "tags": tags,
                    "group_appear": group_appear,
                    "location": location,
                    "location_link": location_link,
                    "session_option": session_option,
                    "language": language,
                    "session_details_language": session_details['session_details_lang']["langkey"],
                    "box_id": box_id,
                    "request": request,
                    "page_id": page_id,
                    "element_id": element['element_id']

                }
                ErrorR.warn(preselected_session)
                setting_temporary_attendee_expire_time = Setting.objects.filter(name='temporary_attendee_expire_time',
                                                                                event_id=request.session['event_id'])
                if setting_temporary_attendee_expire_time.exists():
                    temporary_attendee_expire_time = setting_temporary_attendee_expire_time[0].value
                else:
                    # setting default 5 min
                    temporary_attendee_expire_time = '300000'
                context['temporary_attendee_expire_time'] = temporary_attendee_expire_time

                if 'is_user_login' not in request.session or not request.session['is_user_login']:
                    # context['session_enable'] = False
                    context['session_enable'] = 'True'
                return render_to_string('public/element/session_radio.html', context)
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['sessionradiobutton_txt_empty'])
                # else:
                #     return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                #     language['langkey']['sessionradiobutton_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['sessionradiobutton_txt_misconfigured'])

    def get_session_checkbox(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-session-checkbox" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-checkbox">"""
        try:

            event_id = request.session["event_id"]
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            message = ''
            session_enable = 'True'
            session_groups = ''
            session_choose_least = ''
            session_choose_heighest = ''
            description = 'True'
            start_time = 'True'
            start_date = 'True'
            end_time = 'True'
            end_date = 'True'
            rvsp_date = 'True'
            speaker = 'True'
            speaker_link = 'True'
            tags = 'True'
            group_appear = 'True'
            location = 'True'
            location_link = 'True'
            session_option = ''
            preselected_session = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'session_checkbox_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                elif setting.element_question.question_key == 'session_checkbox_session_seletion_enabled':
                    session_enable = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_session_groups':
                    session_groups = json.loads(setting.answer)
                elif setting.element_question.question_key == 'session_checkbox_session_choose_at_least':
                    session_choose_least = setting.answer
                    if session_choose_least == "":
                        session_choose_least = 0
                elif setting.element_question.question_key == 'session_checkbox_session_choose_more_than':
                    session_choose_heighest = setting.answer
                    if session_choose_heighest == "":
                        session_choose_heighest = 0
                elif setting.element_question.question_key == 'session_checkbox_description':
                    description = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_start_time':
                    start_time = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_start_date':
                    start_date = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_end_time':
                    end_time = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_end_date':
                    end_date = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_rvsp_date':
                    rvsp_date = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_speaker':
                    speaker = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_link_speaker':
                    speaker_link = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_tags':
                    tags = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_session_group':
                    group_appear = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_location':
                    location = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_link_location':
                    location_link = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_session_available':
                    session_option = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_preselected':
                    preselected_session = json.loads(setting.answer)
            if session_groups != '':
                sessionGroups = Group.objects.filter(type="session", is_show=1, is_searchable=1,
                                                     event_id=request.session['event_id'],
                                                     id__in=session_groups).order_by('group_order')
                if preselected_session != '':
                    for pre_session in preselected_session:
                        SessionDetail.status_type_attend(request, int(pre_session))
                session_details = Plugins.get_session_details(request, sessionGroups, event_id, session_option)
                context = {
                    "title": title,
                    "sessionGroups": list(session_details['sessionGroups']),
                    "message": message,
                    "session_enable": session_enable,
                    "session_choose_least": session_choose_least,
                    "session_choose_heighest": session_choose_heighest,
                    "description": description,
                    "start_time": start_time,
                    "start_date": start_date,
                    "end_time": end_time,
                    "end_date": end_date,
                    "rvsp_date": rvsp_date,
                    "speaker": speaker,
                    "speaker_link": speaker_link,
                    "tags": tags,
                    "group_appear": group_appear,
                    "location": location,
                    "location_link": location_link,
                    "session_option": session_option,
                    "language": language,
                    "session_details_language": session_details['session_details_lang']["langkey"],
                    "box_id": box_id,
                    "request": request,
                    "page_id": page_id,
                    "element_id": element['element_id']
                }

                setting_temporary_attendee_expire_time = Setting.objects.filter(name='temporary_attendee_expire_time',
                                                                                event_id=request.session['event_id'])
                if setting_temporary_attendee_expire_time.exists():
                    temporary_attendee_expire_time = setting_temporary_attendee_expire_time[0].value
                else:
                    # setting default 5 min
                    temporary_attendee_expire_time = '300000'
                context['temporary_attendee_expire_time'] = temporary_attendee_expire_time

                if 'is_user_login' not in request.session or not request.session['is_user_login']:
                    # context['session_enable'] = False
                    context['session_enable'] = 'True'
                return render_to_string('public/element/session_checkbox.html', context)
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['sessioncheckbox_txt_empty'])
                # else:
                #     return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                #     language['langkey']['sessioncheckbox_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['sessioncheckbox_txt_misconfigured'])

    def get_login_form(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-login-form" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="login-form">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            message = ''
            show_reset_password_link = 'True'
            for setting in element_settings:
                if setting.element_question.question_key == 'login_form_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'login_form_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                elif setting.element_question.question_key == 'login_form_password_link':
                    show_reset_password_link = setting.answer
            context = {
                "title": title,
                "message": message,
                "show_reset_password_link": show_reset_password_link,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/email_password_verification.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['login_form_txt_misconfigured'])

    def get_request_login(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-request-login" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="request-login">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            message = ''
            email_id = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'request_login_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'request_login_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                elif setting.element_question.question_key == 'request_login_email_send':
                    email_id = setting.answer
            context = {
                "title": title,
                "message": message,
                "email_id": email_id,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/request_login.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['request_login_txt_misconfigured'])

    def get_submit_button(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        language_id = request.session["language_id"]
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-submit-button" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="submit-button">"""
        try:
            submit_button = PluginSubmitButton.objects.get(id=int(element['button_id']))
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'submit_button_title':
                    title_new = ''
                    try:
                        title_lang = json.loads(setting.answer, strict=False)
                        if title_lang[str(language_id)]:
                            title_new = title_lang[str(language_id)]
                    except ValueError:
                        title_new = setting.answer
                    except Exception as e:
                        try:
                            presetsEvent = PresetEvent.objects.filter(event_id=request.session["event_id"])
                            if presetsEvent.exists():
                                current_language = presetsEvent[0]
                                title_lang = json.loads(setting.answer, strict=False)
                                if title_lang[str(current_language.preset_id)]:
                                    title_new = title_lang[str(current_language.preset_id)]
                        except:
                            pass
                    title = title_new
            context = {
                "title": title,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "submit_button": submit_button,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/submit_button.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['submit_button_txt_misconfigured'])

    def get_photo_upload(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-photo-upload" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="photo-upload">"""
        try:
            photo_group = PhotoGroup.objects.get(id=int(element['button_id']))
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            message = ''
            comment = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'photo_upload_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                if setting.element_question.question_key == 'photo_upload_add_comment':
                    comment = setting.answer
            context = {
                "comment": comment,
                "message": message,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "photo_group": photo_group,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/photo_upload.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['photo_upload_txt_misconfigured'])

    def get_logout(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-logout" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="logout">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            message = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'logout_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
            context = {
                "message": message,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/logout.html', context)
        except Exception as e:
            ErrorR.efail(e)
            # return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
            # language['langkey']['photo_upload_txt_misconfigured'])

    def get_reset_password(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-reset-password" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="reset-password">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            message = ''
            email_id = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'reset_password_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'reset_password_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                elif setting.element_question.question_key == 'reset_password_email_send':
                    email_id = setting.answer
            context = {
                "title": title,
                "message": message,
                "email_id": email_id,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/reset_password.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['reset_password_txt_misconfigured'])

    def get_new_password(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-new-password" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="new-password">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            title = ''
            message = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'new_password_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'new_password_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
            context = {
                "title": title,
                "message": message,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/new_password.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['new_password_txt_misconfigured'])

    def get_multiple_registration(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-multiple-registration" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="multiple-registration">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            message = ''
            min_attendees = 1
            max_attendees = 1
            default_attendees = 1
            display_form = 'loop'
            order_owner_page = ''
            attendee_page = ''
            questions_display = ''
            number_of_attendees = 'include-owner'
            total_attendees = 0
            selected_columns = []
            columns = ''
            order_owner_page = ''
            attendee_page = ''
            for setting in element_settings:
                if setting.element_question.question_key == 'multiple_registration_message':
                    setting.description = LanguageKey.get_plugin_description_by_language(request, setting.description)
                    message = setting.description
                elif setting.element_question.question_key == 'multiple_registration_min_attendees':
                    min_attendees = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_max_attendees':
                    max_attendees = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_default_attendees':
                    default_attendees = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_form':
                    display_form = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_order_owner_page':
                    order_owner_page = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_attendee_page':
                    attendee_page = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_attendee_numbers':
                    number_of_attendees = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_order_owner_page':
                    order_owner_page = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_attendee_page':
                    attendee_page = setting.answer
                elif setting.element_question.question_key == 'multiple_registration_table_questions':
                    ErrorR.okgreen(setting.answer)
                    selected_columns_data = json.loads(json.loads(setting.answer))
                    ErrorR.okgreen(selected_columns_data)

                    selected_columns = selected_columns_data['question'][0]['id'].split(',')
                    ErrorR.okgreen(selected_columns)
                    # col_ques = Questions.objects.filter(id__in=selected_columns).values("id", "title",
                    #                                                                     "actual_definition")
                    # visible_columns = []
                    # for item in selected_columns:
                    #     visible_columns.append(col_ques.get(id=item))
                    # for ids, col_question in enumerate(visible_columns):
                    #     if col_question['actual_definition'] == None or col_question['actual_definition'] == '':
                    #         visible_columns[ids]['actual_definition'] = col_question['title'].replace(' ', '_')
                    # columns = visible_columns
            column_ids = selected_columns
            ErrorR.okgreen(column_ids)
            columns = []
            for column_id in column_ids:
                question = Questions.objects.get(id=column_id)
                question = LanguageKey.get_question_data_by_language(request, question)
                columns.append(question.title)
            ErrorR.okgreen(columns)
            if number_of_attendees == 'include-owner':
                total_attendees = int(default_attendees) + 1
            else:
                total_attendees = int(default_attendees)
            context = {
                "message": message,
                "min_attendees": min_attendees,
                "max_attendees": max_attendees,
                "default_attendees": range(int(default_attendees)),
                "display_form": display_form,
                "order_owner_page": order_owner_page,
                "attendee_page": attendee_page,
                "questions_display": questions_display,
                "number_of_attendees": number_of_attendees,
                "total_attendees": total_attendees,
                "column_names": columns,
                "language": language,
                "box_id": box_id,
                "request": request,
                "page_id": page_id,
                "element_id": element['element_id']
            }
            return render_to_string('public/element/multiple_registration.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['multiple_registration_misconfigured'])

    def check_multiple_registration_attendee(request, *args, **kwargs):
        response_data = {}
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        current_attendee = request.POST.get('current_attendee')
        element_settings = ElementsAnswers.objects.filter(Q(page_id=page_id, box_id=box_id) & Q(
            Q(element_question__question_key='multiple_registration_min_attendees') | Q(
                element_question__question_key='multiple_registration_max_attendees')))
        min_attendees = 1
        max_attendees = 1
        for setting in element_settings:
            if setting.element_question.question_key == 'multiple_registration_min_attendees':
                min_attendees = setting.answer
            elif setting.element_question.question_key == 'multiple_registration_max_attendees':
                max_attendees = setting.answer
        response_data['success'] = True
        if current_attendee > max_attendees:
            response_data['success'] = False
            response_data['message'] = "Max Attendee exceeds"
        elif current_attendee < min_attendees:
            response_data['success'] = False
            response_data['message'] = "Min Attendee reduced"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def page_search_location(request, *args, **kwargs):
        try:
            search_key = request.GET.get('search_key')
            element_id = request.GET.get('element_id')
            all_locations_groups = []
            box_id = request.GET.get('box_id')
            page_name = request.GET.get('page')
            page_info = PageContent.objects.filter(url=page_name, event_id=request.session['event_id'])
            page_id = 0
            if page_info.exists():
                page_id = page_info[0].id
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            message = ''
            list_searchable = 'True'
            location_groups = ''
            title = ''
            location_details = 'True'
            location_title = 'True'
            description = 'True'
            link_map = 'True'
            address_details = 'True'
            contact_details = 'True'
            for setting in element_settings:
                if setting.element_question.question_key == 'location_title':
                    title = setting.answer
                elif setting.element_question.question_key == 'location_message':
                    message = setting.description
                elif setting.element_question.question_key == 'location_list_searchable':
                    list_searchable = setting.answer
                elif setting.element_question.question_key == 'location_location_groups':
                    location_groups = json.loads(setting.answer)
                elif setting.element_question.question_key == 'location_list_title':
                    location_title = setting.answer
                elif setting.element_question.question_key == 'location_link_location_details':
                    location_details = setting.answer
                elif setting.element_question.question_key == 'location_description':
                    description = setting.answer
                elif setting.element_question.question_key == 'location_link_map':
                    link_map = setting.answer
                elif setting.element_question.question_key == 'location_address_details':
                    address_details = setting.answer
                elif setting.element_question.question_key == 'location_contact_details':
                    contact_details = setting.answer
            if search_key == '':
                locations_group = Group.objects.filter(type="location", is_show=1, is_searchable=1,
                                                       id__in=location_groups,
                                                       event_id=request.session['event_id']).order_by(
                    'group_order').distinct()
            else:
                locations_group = Group.objects.filter(type="location", is_show=1, is_searchable=1,
                                                       id__in=location_groups,
                                                       event_id=request.session['event_id'],
                                                       locations__name__icontains=search_key).order_by(
                    'group_order').distinct()
            for group in locations_group:
                group.location = Locations.objects.filter(group_id=group.id, name__icontains=search_key)
                for location in group.location:
                    location = LanguageKey.get_location_data_by_language(request, location)
                    location.address = location.address.replace(',', '<br/>')

            context = {
                "locationGroups": locations_group,
                "message": message,
                "list_searchable": list_searchable,
                "title": title,
                "location_title": location_title,
                "location_details": location_details,
                "description": description,
                "link_map": link_map,
                "address_details": address_details,
                "contact_details": contact_details,
                "language": LanguageKey.get_lang_key(request, element_id),
                "request": request,
                "page_id": page_id,
                "box_id": box_id
            }
            return render(request, 'public/element/locations.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return ''

    def get_session_scheduler(request, page_id, element):
        lang = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="event-plugin element event-plugin-session-scheduler" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-scheduler">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    event = Events.objects.get(id=event_id)
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
                    browsing_modes = []
                    element_settings_info = {}
                    groups = []
                    session_option = ''
                    session_scheduler_session_start_time = ''
                    session_scheduler_session_start_date = ''
                    session_scheduler_session_end_time = ''
                    session_scheduler_session_end_date = ''
                    session_scheduler_session_rvsp_date = ''
                    session_scheduler_session_speaker = ''
                    session_scheduler_session_link_speaker = ''
                    session_scheduler_session_tags = ''
                    session_scheduler_session_session_groups = ''
                    session_scheduler_session_location = ''
                    session_scheduler_session_limk_location = ''
                    session_scheduler_column_session_group_available_in_agenda_view = ''
                    session_scheduler_column_date_available_in_agenda_view = ''
                    session_scheduler_column_time_available_in_agenda_view = ''
                    session_scheduler_one_hour_height = ''
                    session_scheduler_session_width = ''
                    session_scheduler_disable_grouping = ''
                    group_length = 1
                    for setting in element_settings:
                        if setting.element_question.question_key == 'session_scheduler_session_enable':
                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False


                        elif setting.element_question.question_key == 'session_scheduler_session_groups':

                            # Collect Group Infomation for scheduler

                            group_data = []
                            groups = json.loads(setting.answer)
                            for group in groups:
                                grp = Group.objects.get(id=group)
                                grp = LanguageKey.get_group_data_by_language(request, grp)
                                obj = {
                                    'value': grp.id,
                                    'text': grp.name,
                                }
                                group_data.append(obj)
                            element_settings_info[setting.element_question.question_key] = group_data
                            group_length = len(group_data)


                        elif setting.element_question.question_key == 'session_scheduler_default_browse_date':

                            if setting.answer:
                                element_settings_info[setting.element_question.question_key] = setting.answer
                            else:
                                element_settings_info[setting.element_question.question_key] = str(event.start)

                        elif setting.element_question.question_key == 'session_scheduler_day_starts_at':
                            if setting.answer:
                                element_settings_info[setting.element_question.question_key] = setting.answer
                            else:
                                element_settings_info[setting.element_question.question_key] = '10:00 AM'

                        elif setting.element_question.question_key == 'session_scheduler_day_ends_at':

                            if setting.answer:
                                element_settings_info[setting.element_question.question_key] = setting.answer
                            else:
                                element_settings_info[setting.element_question.question_key] = '05:00 PM'

                        elif setting.element_question.question_key == 'session_scheduler_allow_browsing_week_modes':
                            if setting.answer == 'True':
                                browsing_modes.append("week")

                        elif setting.element_question.question_key == 'session_scheduler_allow_browsing_work_week_modes':
                            if setting.answer == 'True':
                                browsing_modes.append("workWeek")

                        elif setting.element_question.question_key == 'session_scheduler_allow_browsing_day_modes':
                            if setting.answer == 'True':
                                browsing_modes.append("day")

                        elif setting.element_question.question_key == 'session_scheduler_allow_browsing_agenda_modes':
                            if setting.answer == 'True':
                                browsing_modes.append("agenda")


                        elif setting.element_question.question_key == 'session_scheduler_show_toolbar_today_button':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_toolbar_currently_selected_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_toolbar_change_browse_mode_buttons':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_toolbar_move_day_forward_or_backwards_buttons':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_toolbar_business_hours_toggle':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_all_or_my_sessions':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_subscribe_to_calender':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_show_session_group_toggle':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_column_session_group_available_in_agenda_view':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_column_session_group_available_in_agenda_view = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_column_session_group_available_in_agenda_view = False

                        elif setting.element_question.question_key == 'session_scheduler_column_date_available_in_agenda_view':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_column_date_available_in_agenda_view = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_column_date_available_in_agenda_view = False

                        elif setting.element_question.question_key == 'session_scheduler_column_time_available_in_agenda_view':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_column_time_available_in_agenda_view = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_column_time_available_in_agenda_view = False

                        elif setting.element_question.question_key == 'session_scheduler_agenda_view_sort_on':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_session_start_time':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_start_time = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_start_time = False

                        elif setting.element_question.question_key == 'session_scheduler_session_start_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_start_date = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_start_date = False

                        elif setting.element_question.question_key == 'session_scheduler_session_end_time':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_end_time = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_end_time = False

                        elif setting.element_question.question_key == 'session_scheduler_session_end_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_end_date = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_end_date = False

                        elif setting.element_question.question_key == 'session_scheduler_session_rvsp_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_rvsp_date = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_rvsp_date = False

                        elif setting.element_question.question_key == 'session_scheduler_session_speaker':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_speaker = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_speaker = False

                        elif setting.element_question.question_key == 'session_scheduler_session_link_speaker':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_link_speaker = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_link_speaker = False

                        elif setting.element_question.question_key == 'session_scheduler_session_tags':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_tags = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_tags = False

                        elif setting.element_question.question_key == 'session_scheduler_session_session_groups':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_session_groups = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_session_groups = False

                        elif setting.element_question.question_key == 'session_scheduler_session_location':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_location = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_location = False

                        elif setting.element_question.question_key == 'session_scheduler_session_limk_location':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_session_limk_location = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_session_limk_location = False

                        elif setting.element_question.question_key == 'session_scheduler_session_available':

                            element_settings_info[setting.element_question.question_key] = setting.answer
                            session_option = setting.answer

                        elif setting.element_question.question_key == 'session_scheduler_width':

                            element_settings_info[setting.element_question.question_key] = setting.answer

                        elif setting.element_question.question_key == 'session_scheduler_session_width':

                            element_settings_info[setting.element_question.question_key] = setting.answer
                            session_scheduler_session_width = setting.answer



                        elif setting.element_question.question_key == 'session_scheduler_one_hour_height':

                            element_settings_info[setting.element_question.question_key] = setting.answer
                            session_scheduler_one_hour_height = setting.answer

                        elif setting.element_question.question_key == 'session_scheduler_title':

                            element_settings_info[setting.element_question.question_key] = setting.answer

                        elif setting.element_question.question_key == 'session_scheduler_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            element_settings_info[setting.element_question.question_key] = setting.description

                        elif setting.element_question.question_key == 'session_scheduler_disable_grouping':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_scheduler_disable_grouping = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_scheduler_disable_grouping = False

                    element_settings_info['session_scheduler_browsing_modes'] = browsing_modes
                    timezone = Setting.objects.filter(event_id=request.session['event_id'], name='timezone')
                    timezone_of_event = "UTC"
                    if timezone.exists():
                        timezone_of_event = timezone[0].value
                    element_settings_info['session_scheduler_timezone'] = timezone_of_event

                    group_list = Group.objects.filter(id__in=groups)
                    for group in group_list:
                        group = LanguageKey.get_group_data_by_language(request, group)

                    # languages
                    messages = {}
                    messages["today"] = lang['langkey']['sessionscheduler_btn_today']
                    views = {}
                    views["day"] = lang['langkey']['sessionscheduler_btn_day']
                    views["week"] = lang['langkey']['sessionscheduler_btn_week']
                    views["agenda"] = lang['langkey']['sessionscheduler_btn_agenda']
                    views["workWeek"] = lang['langkey']['sessionscheduler_btn_work_week']
                    messages['views'] = views
                    messages['showFullDay'] = lang['langkey']['sessionscheduler_btn_full_day']
                    messages['showWorkDay'] = lang['langkey']['sessionscheduler_btn_business_hours']

                    element_settings_info['session_scheduler_session_languages'] = messages
                    element_settings_info['session_scheduler_session_notifications'] = lang['langkey'][
                        'sessionscheduler_notify_track']
                    session_scheduler_width = 0
                    if session_scheduler_session_width:
                        session_scheduler_width = int(session_scheduler_session_width) * int(group_length)

                    element_settings_info['session_scheduler_width'] = session_scheduler_width
                    context = {
                        "messages": messages,
                        'session_group_list': group_list,
                        'session_scheduler_session_start_time': session_scheduler_session_start_time,
                        'session_scheduler_session_start_date': session_scheduler_session_start_date,
                        'session_scheduler_session_end_time': session_scheduler_session_end_time,
                        'session_scheduler_session_end_date': session_scheduler_session_end_date,
                        'session_scheduler_session_rvsp_date': session_scheduler_session_rvsp_date,
                        'session_scheduler_session_speaker': session_scheduler_session_speaker,
                        'session_scheduler_session_link_speaker': session_scheduler_session_link_speaker,
                        'session_scheduler_session_tags': session_scheduler_session_tags,
                        'session_scheduler_session_session_groups': session_scheduler_session_session_groups,
                        'session_scheduler_session_location': session_scheduler_session_location,
                        'session_scheduler_session_limk_location': session_scheduler_session_limk_location,
                        "element_settings_info": json.dumps(element_settings_info),
                        "language": lang,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id'],
                        "request": request,
                        "session_scheduler_column_session_group_available_in_agenda_view": session_scheduler_column_session_group_available_in_agenda_view,
                        "session_scheduler_column_date_available_in_agenda_view": session_scheduler_column_date_available_in_agenda_view,
                        "session_scheduler_column_time_available_in_agenda_view": session_scheduler_column_time_available_in_agenda_view,
                        "session_scheduler_one_hour_height": str(session_scheduler_one_hour_height) + "px",
                        "session_scheduler_width": str(session_scheduler_width) + "px",
                        "session_scheduler_disable_grouping": session_scheduler_disable_grouping
                    }
                    return render_to_string('public/element/session_scheduler_test.html', context)
                else:
                    return ''
            else:
                return ""
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                lang['langkey']['sessionscheduler_txt_misconfigured'])

    def getSchedulerEvents(request, *args, **kwargs):
        tab = request.GET.get('tab')
        box_id = request.GET.get('box_id')
        page_id = request.GET.get('page_id')
        element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id,
                                                          element_question__question_key='session_scheduler_session_available')

        attendee_id = request.session['event_user']['id']
        sessions = Session.objects.all().select_related("group").filter(group__is_show=1, group__is_searchable=1,
                                                                        group__event_id=request.session['event_user'][
                                                                            'event_id'])

        if tab == "all-session":
            sessions = Session.objects.all().select_related("group").filter(group__is_show=1,
                                                                            group__is_searchable=1,
                                                                            group__event_id=
                                                                            request.session['event_user'][
                                                                                'event_id'])
        elif tab == "my-session":
            query_string = 'SELECT ssn.*, shu.status FROM sessions ssn left join seminars_has_users shu on ssn.id = shu.session_id left join seminars_has_speakers shs on ssn.id=shs.session_id left join groups grp on ssn.group_id = grp.id where (( shu.attendee_id=' + str(
                attendee_id) + ' and shu.status="attending") or shs.speaker_id=' + str(
                attendee_id) + ') and grp.is_searchable = 1 group by ssn.id order by grp.group_order'
            sessions = Session.objects.raw(query_string)
        response_data = []
        if len(list(sessions)) > 0:
            for session in sessions:
                session = LanguageKey.get_session_data_by_language(request, session)
                id = session.id
                name = session.name
                group = session.group_id
                location = session.location.name
                location_id = session.location.id
                session_attendees = SeminarsUsers.objects.filter(session_id=session.id,
                                                                 status='attending').count()
                seats_remain = session.max_attendees - session_attendees
                capacity = session.max_attendees
                count = SeminarsUsers.objects.filter(session_id=id).exclude(status='not-attending').count()
                full = False
                if capacity != 0:
                    if capacity <= count:
                        full = True
                full_queue_open = False
                if full:
                    if session.allow_attendees_queue:
                        full_queue_open = True

                start = str(session.start)
                end = str(session.end)
                rsvp_date = str(session.reg_between_end)
                allday = session.all_day
                if allday:
                    start = session.start.strftime("%Y-%m-%d")
                    end = session.end.strftime("%Y-%m-%d")

                background = Group.objects.get(id=group)
                background = LanguageKey.get_group_data_by_language(request, background)
                color = background.color
                status = "not-attending"
                tags = SessionTags.objects.filter(session_id=session.id)
                taglist = []
                for tag in tags:
                    taglist.append(tag.tag.name)

                speakers = SeminarSpeakers.objects.filter(session_id=id)
                speakersData = []
                if speakers.count() > 0:
                    for speaker in speakers:
                        badge_firstname = Answers.objects.filter(question__actual_definition='firstname',
                                                                 user_id=speaker.speaker.id)
                        if badge_firstname.exists():
                            firstname = badge_firstname[0].value
                        else:
                            firstname = speaker.speaker.firstname

                        badge_lastname = Answers.objects.filter(question__actual_definition='lastname',
                                                                user_id=speaker.speaker.id)
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

                session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
                session_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id, session_id=session.id)
                if session_attendee.count() > 0:
                    if session_attendee[0].status == 'attending':
                        status = "attending"
                    elif session_attendee[0].status == 'in-queue':
                        status = "in-queue"
                    elif session_attendee[0].status == 'deciding':
                        status = "deciding"
                    elif session_attendee[0].status == 'not-attending':
                        session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                                                                           status="attending",
                                                                           session__allow_overlapping=0) & (
                                                                             Q(session__start__lte=session.start,
                                                                               session__end__gt=session.start) | Q(
                                                                                 session__start__lt=session.end,
                                                                                 session__end__gte=session.end)))

                        if session_attending.count() > 0:
                            status = 'time-conflict'
                        else:
                            status = 'not-attending'
                else:

                    session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                                                                       status="attending",
                                                                       session__allow_overlapping=0) & (
                                                                         Q(session__start__lte=session.start,
                                                                           session__end__gt=session.start) | Q(
                                                                             session__start__lt=session.end,
                                                                             session__end__gte=session.end)))

                    if session_attending.count() > 0:
                        status = 'time-conflict'
                    else:
                        status = 'not-answered'
                if session_speaker.count() > 0:
                    status = "attending"

                time_now = datetime.now().date()
                setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_id'])
                if setting_timezone:
                    tzname = setting_timezone[0].value
                    timezone_active = timezone(tzname)
                    time_now = datetime.now(timezone_active)
                    time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
                    time_now = datetime.strptime(time_now,"%Y-%m-%d %H:%M:%S")
                    time_now = time_now.date()
                session_expire = False
                reg_between_end = session.reg_between_end
                if reg_between_end < time_now:
                    session_expire = True

                session_option = element_settings[0].answer
                session = SessionSeatAvailability.get_seats_availability(request, session, session_option,
                                                                         request.session['event_id'])
                session_obj = {
                    'id': id,
                    'Title': name,
                    'groupId': group,
                    'groupName': background.name,
                    'Start': start,
                    'End': end,
                    'rsvp_date': rsvp_date,
                    'color': color,
                    'IsAllDay': allday,
                    'full': full,
                    'session_expire': session_expire,
                    'full_queue_open': full_queue_open,
                    'status': status,
                    'location': location,
                    'speakers': speakersData,
                    'taglist': taglist,
                    'location_id': location_id,
                    'seat_availability': session.availability
                }
                response_data.append(session_obj)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_scheduler_session_details(request, *args, **kwargs):
        session_id = request.POST.get('session_id')
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
        title = ''
        message = ''
        session_enable = 'True'
        session_choose_least = ''
        session_choose_heighest = ''
        description = 'True'
        start_time = 'True'
        start_date = 'True'
        end_time = 'True'
        end_date = 'True'
        rvsp_date = 'True'
        speaker = 'True'
        speaker_link = 'True'
        tags = 'True'
        group_appear = 'True'
        location = 'True'
        location_link = 'True'
        session_option = ''

        for setting in element_settings:
            if setting.element_question.question_key == 'session_scheduler_session_enable':
                session_enable = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_description':
                description = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_start_time':
                start_time = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_start_date':
                start_date = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_end_time':
                end_time = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_end_date':
                end_date = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_rvsp_date':
                rvsp_date = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_speaker':
                speaker = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_link_speaker':
                speaker_link = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_tags':
                tags = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_session_groups':
                group_appear = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_location':
                location = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_details_limk_location':
                location_link = setting.answer
            elif setting.element_question.question_key == 'session_scheduler_session_available':
                session_option = setting.answer

        session = Session.objects.get(id=session_id)
        session = LanguageKey.get_session_data_by_language(request, session)
        attendee_id = request.session['event_user']['id']
        speakers = SeminarSpeakers.objects.filter(session_id=session.id)
        spkFlag = False
        if speakers.count() > 0:
            for speaker_item in speakers:
                if speaker_item.speaker_id == attendee_id:
                    spkFlag = True
        session.speakers = speakers
        attendee = Attendee.objects.filter(id=attendee_id)
        status_text = LanguageKey.catch_lang_key(request, "session-details",
                                                 "sessiondetails_txt_status_not_attending")
        status = 'not-answered'
        session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
        if session_attendee.count() > 0:
            status = session_attendee[0].status
            if session_attendee[0].status == 'attending':
                status_text = LanguageKey.catch_lang_key(request, "session-details",
                                                         "sessiondetails_txt_status_attending")
            elif session_attendee[0].status == 'in-queue':
                status_text = LanguageKey.catch_lang_key(request, "session-details",
                                                         "sessiondetails_txt_status_in_queue")
            elif session_attendee[0].status == 'not-attending':
                status_text = LanguageKey.catch_lang_key(request, "session-details",
                                                         "sessiondetails_txt_status_not_attending")
            elif session_attendee[0].status == 'deciding':
                status_text = LanguageKey.catch_lang_key(request, "session-details",
                                                         "sessiondetails_txt_status_deciding")
                status = 'in-queue'
        session.is_speaker = False
        if spkFlag:
            status = 'attending'
            status_text = LanguageKey.catch_lang_key(request, "session-details",
                                                     "sessiondetails_txt_status_attending")
            session.is_speaker = True

        tags_list = SessionTags.objects.filter(session_id=session.id)
        session.tags = tags_list
        session_full = True
        session_attendee_count = SeminarsUsers.objects.filter(session_id=session.id).exclude(
            status='not-attending').count()
        if session.max_attendees > session_attendee_count:
            session_full = False
        session.full = session_full
        time_now = datetime.now().date()
        setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_id'])
        if setting_timezone:
            tzname = setting_timezone[0].value
            timezone_active = timezone(tzname)
            time_now = datetime.now(timezone_active)
            time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
            time_now = datetime.strptime(time_now,"%Y-%m-%d %H:%M:%S")
            time_now = time_now.date()
        session_expire = False
        reg_between_end = session.reg_between_end
        if reg_between_end < time_now:
            session_expire = True
        session.session_expire = session_expire
        session.session_conflict = Plugins.check_session_clash(attendee_id, session)
        session_details_lang = LanguageKey.get_session_details_lang(request)
        session_details_lang['langkey']['status_full'] = LanguageKey.catch_lang_key(request,
                                                                                    "session-details",
                                                                                    "sessiondetails_txt_status_full")
        session_details_lang['langkey']['status_queue_open'] = LanguageKey.catch_lang_key(request,
                                                                                          "session-details",
                                                                                          "sessiondetails_txt_status_queue_open")
        session_details_lang['langkey']['status_queue_close'] = LanguageKey.catch_lang_key(request,
                                                                                           "session-details",
                                                                                           "sessiondetails_txt_status_queue_close")
        session_details_lang['langkey']['status_rsvp_passed'] = LanguageKey.catch_lang_key(request,
                                                                                           "session-details",
                                                                                           "sessiondetails_txt_status_rsvp_passed")
        session_details_lang['langkey']['status_time_conflict'] = LanguageKey.catch_lang_key(
            request.session['event_id'], "session-details", "sessiondetails_txt_status_time_conflict")
        session_details_lang['langkey']['status_in_queue'] = LanguageKey.catch_lang_key(request,
                                                                                        "session-details",
                                                                                        "sessiondetails_txt_status_in_queue")
        session = SessionSeatAvailability.get_seats_availability(request, session, session_option,
                                                                 request.session['event_id'])
        context = {
            "session": session,
            "status": status,
            "status_text": status_text,
            "title": title,
            'isSpeaker': spkFlag,
            "message": message,
            "session_enable": session_enable,
            "session_choose_least": session_choose_least,
            "session_choose_heighest": session_choose_heighest,
            "description": description,
            "start_time": start_time,
            "start_date": start_date,
            "end_time": end_time,
            "end_date": end_date,
            "rvsp_date": rvsp_date,
            "speaker": speaker,
            "speaker_link": speaker_link,
            "tags": tags,
            "group_appear": group_appear,
            "location": location,
            "location_link": location_link,
            "session_option": session_option,
            "session_details_language": session_details_lang["langkey"],
            "box_id": box_id,
            "page_id": page_id,
            "request": request,
        }
        return render(request, 'public/element/session_scheduler_session_details.html', context)
        # return render_to_string('public/element/session_scheduler_session_details.html', context)

    def get_location_details(request, pk, *args, **kwargs):
        box_id = request.POST.get('box_id')
        page_id = request.POST.get('page_id')
        response = {}
        try:
            response['details'] = ''
            location = Locations.objects.get(id=pk)
            location = LanguageKey.get_location_data_by_language(request, location)
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).order_by(
                'element_question_id')
            location_title = 'False'
            location_details = 'False'
            description = 'False'
            link_map = 'False'
            address_details = 'False'
            contact_details = 'False'
            custom_location = False
            for setting in element_settings:
                if setting.element_question.question_key == 'session_scheduler_custom_location_settings' or setting.element_question.question_key == 'session_radio_custom_location_settings' or setting.element_question.question_key == 'session_checkbox_custom_location_settings' or setting.element_question.question_key == 'next_up_custom_location_settings':
                    if setting.answer == 'True':
                        custom_location = True
                if custom_location:
                    if setting.element_question.question_key == 'session_scheduler_location_list_title' or setting.element_question.question_key == 'session_radio_location_list_title' or setting.element_question.question_key == 'session_checkbox_location_list_title' or setting.element_question.question_key == 'next_up_location_list_title':
                        location_title = setting.answer
                    elif setting.element_question.question_key == 'session_scheduler_location_link_location_details' or setting.element_question.question_key == 'session_radio_location_link_location_details' or setting.element_question.question_key == 'session_checkbox_location_link_location_details' or setting.element_question.question_key == 'next_up_location_link_location_details':
                        location_details = setting.answer
                    elif setting.element_question.question_key == 'ssession_scheduler_location_description' or setting.element_question.question_key == 'session_radio_location_description' or setting.element_question.question_key == 'session_checkbox_location_description' or setting.element_question.question_key == 'next_up_location_description':
                        description = setting.answer
                    elif setting.element_question.question_key == 'session_scheduler_location_link_map' or setting.element_question.question_key == 'session_radio_location_link_map' or setting.element_question.question_key == 'session_checkbox_location_link_map' or setting.element_question.question_key == 'next_up_location_link_map':
                        link_map = setting.answer
                    elif setting.element_question.question_key == 'session_scheduler_location_address_details' or setting.element_question.question_key == 'session_radio_location_address_details' or setting.element_question.question_key == 'session_checkbox_location_address_details' or setting.element_question.question_key == 'next_up_location_address_details':
                        address_details = setting.answer
                    elif setting.element_question.question_key == 'session_scheduler_location_contact_details' or setting.element_question.question_key == 'session_radio_location_contact_details' or setting.element_question.question_key == 'session_checkbox_location_contact_details' or setting.element_question.question_key == 'next_up_location_contact_details':
                        contact_details = setting.answer
            if not custom_location:
                try:
                    location_global_settings = Setting.objects.filter(name='location_global_settings',
                                                                      event_id=request.session[
                                                                          'event_id']).first().value
                    location_settings = json.loads(location_global_settings)
                    for details in location_settings:
                        if details == 'title':
                            location_title = 'True'
                        if details == 'title_as_link':
                            location_details = 'True'
                        if details == 'description':
                            description = 'True'
                        if details == 'link_to_map':
                            link_map = 'True'
                        if details == 'address_details':
                            address_details = 'True'
                        if details == 'contact_details':
                            contact_details = 'True'
                except Exception as e:
                    ErrorR.efail(e)
            location_language = LanguageKey.catch_lang_key_obj(request, 'location-list')
            context = {
                "location_title": location_title,
                "location_details": location_details,
                "description": description,
                "link_map": link_map,
                "address_details": address_details,
                "contact_details": contact_details,
                "language": location_language,
                "location": location,
            }
            response['details'] = render_to_string('public/element/location_modal.html', context)
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            ErrorR.efail(e)
            return HttpResponse(json.dumps(response), content_type='application/json')

    def get_attendee_details(request, pk, *args, **kwargs):
        box_id = request.POST.get('box_id')
        page_id = request.POST.get('page_id')
        response = {}
        try:
            response['details'] = ''
            attendee = Attendee.objects.filter(id=pk)
            attendee_questions = []
            custom_keys = ['session_scheduler_custom_attendee_settings', 'session_radio_custom_attendee_settings',
                           'session_checkbox_custom_attendee_settings', 'next_up_custom_attendee_settings']
            question_keys = ['session_scheduler_attendee_selected_columns', 'session_radio_attendee_selected_columns',
                             'session_checkbox_attendee_selected_columns', 'next_up_attendee_selected_columns']
            temp_keys = custom_keys
            custom_keys.extend(question_keys)
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id,
                                                              element_question__question_key__in=custom_keys).order_by(
                'element_question_id')
            custom_attendee = False
            custom_keys = temp_keys
            for setting in element_settings:
                if setting.element_question.question_key in custom_keys:
                    if setting.answer == 'True':
                        custom_attendee = True
                if custom_attendee:
                    if setting.element_question.question_key in question_keys:
                        attendee_question_settings = json.loads(setting.answer)
                        attendee_questions = json.loads(attendee_question_settings)['question'][0]['id'].split(',')
            if not custom_attendee:
                try:
                    attendee_global_settings = Setting.objects.filter(name='attendee_global_settings',
                                                                      event_id=request.session[
                                                                          'event_id']).first().value
                    attendee_questions = json.loads(json.loads(attendee_global_settings))['question'][0]['id'].split(
                        ',')
                except:
                    attendee_questions = []
            question_rules = {}
            questionAnswer = {}
            for question in attendee_questions:
                question_rules["data_title"] = int(question)
            if len(attendee_questions):
                answers = Answers.objects.filter(question_id__in=attendee_questions, user_id=attendee[0].id)
            else:
                answers = ''

            if answers:
                questionAnswer["answers"] = answers

                attendee_details = DetailsData.get_question_data_by_attendee(request,
                                                                             questionAnswer,
                                                                             question_rules)
                response['details'] = '<span class="variable-tag">' + attendee_details + '</span>'
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            ErrorR.efail(e)
            return HttpResponse(json.dumps(response), content_type='application/json')

    def check_session_clash(attendee_id, session):
        already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                           session__allow_overlapping=0).exclude(session_id=session.id)
        already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id).exclude(
            session_id=session.id)
        Inbetween = False
        if session.allow_overlapping == 0:
            for sessionlist in already_has_session:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = True
                    break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = True
                    break
                if session.start <= sessionlist.session.start < session.end:
                    Inbetween = True
                    break
                elif session.start < sessionlist.session.end <= session.end:
                    Inbetween = True
                    break

            for sessionlist in already_has_session_as_speaker:
                if sessionlist.session.start <= session.start < sessionlist.session.end:
                    Inbetween = True
                    break
                elif sessionlist.session.start < session.end <= sessionlist.session.end:
                    Inbetween = True
                    break
                if session.start <= sessionlist.session.start < session.end:
                    Inbetween = True
                    break
                elif session.start < sessionlist.session.end <= session.end:
                    Inbetween = True
                    break
        else:
            Inbetween = False
        return Inbetween

    def get_session_details(request, sessionGroups, event_id, session_option):
        response = {}
        for group in sessionGroups:
            group.sessions = Session.objects.filter(group_id=group.id).order_by('session_order')
            for session in group.sessions:
                session.tags = SessionTags.objects.filter(session_id=session.id)
                session.speakers = SeminarSpeakers.objects.filter(session_id=session.id)
                session = SessionSeatAvailability.get_seats_availability(request, session, session_option, event_id)
                session = LanguageKey.get_session_data_by_language(request, session)
        session_details_lang = LanguageKey.get_session_details_lang(request)
        response['sessionGroups'] = sessionGroups
        response['session_details_lang'] = session_details_lang
        return response

    def check_session_availability(request, *args, **kwargs):
        operation = request.POST.get('operation')
        response = {}
        event_id = request.session['event_id']
        if 'is_user_login' in request.session and request.session['is_user_login']:
            user_id = request.session['event_user']['id']
        else:
            user_id = request.POST.get('temp_user_id')
            print('temp_att_: ' + user_id)
            if not user_id.isdigit():
                temp_attendee = Attendee(status='pending', event_id=event_id,
                                         language_id=request.session["language_id"])
                temp_attendee.save()
                user_id = temp_attendee.id
                request.POST._mutable = True
                request.POST['temp_user_id'] = user_id
                request.POST._mutable = False
            response['temp_user_id'] = user_id
            # response['result'] = False
            # response['message'] = 'user not logged in'

        session_id = request.POST.get('session_id')
        seats_option = request.POST.get('seats_option')
        if operation == 'checked':
            response = SessionDetail.status_type_attend(request, session_id)

            sessionAttendees = Session.objects.get(id=session_id)
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        seats_option,
                                                                                        event_id)
            response['seats_availability'] = session_seats_availability.availability
        elif operation == 'unchecked':
            response = Plugins.remove_session(request, session_id, user_id, event_id, seats_option)
        elif operation == 'radio':
            previous_id = request.POST.get('previous_id')
            response = SessionDetail.status_type_attend(request, session_id, previous_id)
            sessionAttendees = Session.objects.get(id=session_id)
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        seats_option,
                                                                                        event_id)
            response['seats_availability'] = session_seats_availability.availability
            if response['result']:
                seats_response = Plugins.remove_session(request, previous_id, user_id, event_id, seats_option)
                if 'seats_availability' in seats_response:
                    response['previous_session_seats_availability'] = seats_response['seats_availability']
            else:
                print('Session is full.')

        return HttpResponse(json.dumps(response), content_type='application/json')

    def attend_session(request, session_id, user_id, event_id, session_option):
        response = {}
        session_exist = SeminarsUsers.objects.filter(attendee_id=user_id, session_id=session_id)
        notification_language = LanguageKey.catch_lang_key_obj(request, 'notification')
        if session_exist.exists():
            seminar_user = session_exist[0]
            sessionAttendees = Session.objects.get(id=session_id)
            if seminar_user.status == 'not-attending':
                bookedSessions = SeminarsUsers.objects.filter(session_id=session_id).exclude(
                    status='not-attending').count()
                if sessionAttendees.max_attendees > bookedSessions:
                    SeminarsUsers.objects.filter(id=seminar_user.id).update(status='attending')
                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                               session_id=session_id, old_value="Not Attending", new_value="Attending",
                                               event_id=event_id)
                    activity.save()
                    response['result'] = True
                    response['message'] = notification_language['langkey']['notify_registered_session']
                else:
                    if not sessionAttendees.allow_attendees_queue:
                        response['result'] = False
                        response['message'] = notification_language['langkey']['notify_session_queue_not_open']

                    elif not sessionAttendees.receive_answer and sessionAttendees.allow_attendees_queue:
                        seminar_data = {
                            "status": "in-queue"
                        }
                        all_queue = SeminarsUsers.objects.filter(session_id=session_id,
                                                                 status='in-queue').order_by('queue_order')
                        if all_queue.exists():
                            seminar_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                        SeminarsUsers.objects.filter(id=seminar_user.id).update(**seminar_data)
                        activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                                   session_id=session_id, old_value="Not Attending",
                                                   new_value="In Queue", event_id=event_id)
                        activity.save()
                        response['result'] = False
                        response['message'] = notification_language['langkey']['notify_queue_session']

                    else:
                        response['result'] = False
                        response['message'] = notification_language['langkey']['notify_session_not_available']
            elif seminar_user.status == 'attending':
                response['result'] = True
                response['message'] = notification_language['langkey']['notify_session_already_attend']
            elif seminar_user.status == 'in-queue':
                response['result'] = False
                response['message'] = notification_language['langkey']['notify_session_already_queue']
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        session_option, event_id)
            response['seats_availability'] = session_seats_availability.availability
        else:
            sessionAttendees = Session.objects.get(id=session_id)
            bookedSessions = SeminarsUsers.objects.filter(session_id=session_id).exclude(
                status='not-attending').count()
            if sessionAttendees.max_attendees > bookedSessions:
                attendeeSessions = SeminarsUsers(attendee_id=user_id, session_id=session_id)
                attendeeSessions.save()
                activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                           session_id=session_id, old_value="Not Answered", new_value="Attending",
                                           event_id=event_id)
                activity.save()
                response['result'] = True
                response['message'] = notification_language['langkey']['notify_registered_session']
            else:
                if not sessionAttendees.allow_attendees_queue:
                    response['result'] = False
                    response['message'] = notification_language['langkey']['notify_session_queue_not_open']
                elif not sessionAttendees.receive_answer and sessionAttendees.allow_attendees_queue:
                    seminar_data = {
                        "attendee_id": user_id,
                        "session_id": session_id,
                        "status": "in-queue"
                    }
                    all_queue = SeminarsUsers.objects.filter(session_id=session_id,
                                                             status='in-queue').order_by('queue_order')
                    if all_queue.exists():
                        seminar_data['queue_order'] = all_queue[all_queue.count() - 1].queue_order + 1
                    attendeeSessions = SeminarsUsers(**seminar_data)
                    attendeeSessions.save()
                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                               session_id=session_id, old_value="Not Answered", new_value="In Queue",
                                               event_id=event_id)
                    activity.save()
                    response['result'] = False
                    response['message'] = notification_language['langkey']['notify_queue_session']
                else:
                    response['result'] = False
                    response['message'] = notification_language['langkey']['notify_session_not_available']
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        session_option, event_id)
            response['seats_availability'] = session_seats_availability.availability
        return response

    def remove_session(request, previous_id, user_id, event_id, seats_option):
        response = {}
        session = SeminarsUsers.objects.filter(session_id=previous_id, attendee_id=user_id)
        if session.exists():
            SeminarsUsers.objects.filter(id=session[0].id).update(status='not-attending')
            status = "Attending"
            if session[0].status == 'in-queue':
                status = "In Queue"
            elif session[0].status == 'deciding':
                status = "Deciding"
            activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                       session_id=previous_id, old_value=status, new_value="Not Attending",
                                       event_id=session[0].session.group.event_id)
            activity.save()
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, session[0].session,
                                                                                        seats_option, event_id)
            response['seats_availability'] = session_seats_availability.availability
        response['result'] = False
        response['message'] = 'Session status not-attending set'
        return response

    def delete_temporary_attendee(request, *args, **kwargs):
        response = {}
        try:
            attendee_id = request.POST.get('id')
            if attendee_id.isdigit():
                attendee = Attendee.objects.get(id=attendee_id)
                if attendee.status == 'pending':
                    attendee.delete()
                    response['result'] = True
                    notification_message = LanguageKey.catch_lang_key(request, 'notification',
                                                                      'notify_attendee_registration_time_expire')
                    response['message'] = notification_message
                    # print('*****************Temporary Attendee Delete {} ! *****************'.format(attendee_id))
        except Exception as e:
            # ErrorR.efail(e)
            response['result'] = False
            response['message'] = ''
        return JsonResponse(response)

    def delete_temporary_attendee_session(request, *args, **kwargs):
        response = {}
        try:
            if "temp_attendee_id_array" in request.session:
                ErrorR.warn("Deleting temporary attendees")
                if len(request.session["temp_attendee_id_array"]):
                    attendee = Attendee.objects.filter(status="pending",
                                                       id__in=request.session["temp_attendee_id_array"])
                    attendee.delete()
                    request.session["temp_attendee_id_array"] = []
                    if "temp_inline_page_url" in request.session:
                        del request.session["temp_inline_page_url"]
                    request.session.modified = True
                    response['result'] = True
                    notification_message = LanguageKey.catch_lang_key(request, 'notification',
                                                                      'notify_attendee_registration_time_expire')
                    response['message'] = notification_message
        except Exception as e:
            ErrorR.efail(e)
            response['result'] = False
            response['message'] = ''
        return JsonResponse(response)
