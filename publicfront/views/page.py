from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from app.models import PageContent, EmailTemplates, Questions, Option, Elements, \
    Setting, Answers, Session, Attendee, AttendeeGroups, AttendeeTag, TravelAttendee, Booking, Travel, \
    Presets, PagePermission, RuleSet, Cookie, CookiePage, Photo, PageContentClasses
import json
from datetime import datetime
import re
from django.template.loader import render_to_string
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from django.http import Http404
from slugify import slugify
from pytz import timezone
from django.db.models import Q
from publicfront.views.lang_key import LanguageKey
from publicfront.views.rule import UserRule
import django
from app.views.cms_view import CmsPageView
from publicfront.views.plugin import Plugins
from publicfront.views.details import DetailsData
from app.views.gbhelper.error_report_helper import ErrorR


class StaticPage(generic.DeleteView):
    def get(self, request, *args, **kwargs):
        return render(request, '', *args, **kwargs)

    def get_object(request, pk, *args, **kwargs):
        try:
            page_list = PageContent.objects.filter(url=pk, event_id=request.session['event_id'])
            if page_list.exists():
                rule_list = PagePermission.objects.filter(page=page_list[0].id)
                if rule_list.exists():
                    page_permission = StaticPage.get_page_permissions(request, rule_list)
                    if page_permission:
                        return page_list[0]
                else:
                    return page_list[0]
            raise Http404
        except Exception as e:
            raise Http404

    def get_page_permissions(request, rule_list):
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                attendee_id = request.session['event_user']['id']
                for rule in rule_list:
                    filters = json.loads(rule.rule.preset)
                    q = Q()
                    match_condition = filters[0][0]['matchFor']
                    if match_condition == '2':
                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    attendees = Attendee.objects.filter(q)
                    if attendees.filter(id=attendee_id).count() > 0:
                        return True
            return False
        except Exception as e:
            ErrorR.efail(e)
            return False

    def get_filter_permissions(request, rule_list):
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                attendee_id = request.session['event_user']['id']
                for rule in rule_list:
                    filters = json.loads(rule.preset)
                    q = Q()
                    match_condition = filters[0][0]['matchFor']
                    if match_condition == '2':
                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    attendees = Attendee.objects.filter(q)
                    if attendees.filter(id=attendee_id).count() > 0:
                        return True
            return False
        except Exception as e:
            ErrorR.efail(e)
            return False

    def initialize_cookie(request):
        if 'hitcount' in request.COOKIES:
            value = request.COOKIES['hitcount']
            return value
        else:
            return False

    def count_hit(request, cookie_id, page_id):
        event_id = request.session['event_id']
        event_query = Setting.objects.filter(name="timezone", event=event_id)
        if event_query.exists():
            time_zone_name = event_query[0].value
            timezone_active = timezone(time_zone_name)
            time_now = datetime.now(timezone_active).date()
            f = '%Y-%m-%d'
            now = datetime.strptime(str(time_now).split(".")[0], f)
            cookiePageObj = CookiePage.objects.extra(select={'visit_date': 'date( visit_date )'}).filter(
                cookie_id=cookie_id, page_id=page_id, visit_date=now)
            if cookiePageObj.exists():
                CookiePage.objects.filter(cookie_id=cookie_id, page_id=page_id, visit_date=now).update(
                    visit_count=cookiePageObj[0].visit_count + 1)
            else:
                newCookiePageObj = CookiePage(cookie_id=cookie_id, page_id=page_id, visit_date=now, visit_count=1)
                newCookiePageObj.save()

    def get_bracket(addif, len_filters, i, str):
        if str == "(":
            if addif == 0:
                if i == 0:
                    return str
        elif str == ")":
            if addif == 0:
                if i == len_filters - 1:
                    return str
        return ""

    def get_bracket_with_not(addif, len_filters, i, str):
        if str == "(":
            if addif == 0:
                if i == 0:
                    return "(!" + str + ""
        elif str == ")":
            if addif == 0:
                if i == len_filters - 1:
                    return "" + str + ")"
        return ""

    def get_filter_js(request, filters, match_condition, box_id, addif=0):
        filter_js = ""
        try:

            for i, filter1 in enumerate(filters):
                # if addif != 0:
                #     print(str(i) + " " + str(addif))
                if i == 0 and addif == 0:
                    context_filter_javascript = {'type': 'if'}
                    filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                  context_filter_javascript)
                if isinstance(filter1[0], dict):
                    single_filter = filter1[0]
                    # ErrorR.okgreen(single_filter)
                    js = render_to_string('public/static_pages/filter_javascript.html',
                                          {'single_filter': single_filter})
                    context_filter_javascript = {
                        'type': 'condition',
                        'condition': js.strip(' \n\r\t')
                    }
                    if match_condition == '2':
                        # AND
                        filter_js += StaticPage.get_bracket(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += StaticPage.get_bracket(addif, len(filters), i, ")")

                        if i < len(filters) - 1:
                            filter_js += " && "
                    elif match_condition == '1':
                        # OR
                        filter_js += StaticPage.get_bracket(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += StaticPage.get_bracket(addif, len(filters), i, ")")
                        if i < len(filters) - 1:
                            filter_js += " || "

                    if i == len(filters) - 1 and addif == 0:
                        context_filter_javascript = {'type': 'pre-logic'}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)

                else:
                    match_condition_inner = filter1[0][0]['matchFor']
                    filter_js += "("
                    if match_condition == '2':
                        # And
                        filter_js += StaticPage.get_filter_js(request, filter1, match_condition_inner, box_id,
                                                              addif + 1)
                    elif match_condition == '1':
                        # Or
                        filter_js += StaticPage.get_filter_js(request, filter1, match_condition_inner, box_id,
                                                              addif + 1)
                    filter_js += ")"
                    if i == len(filters) - 1 and addif == 0:
                        filter_js += ")"
                    if addif != 0 and i != len(filters) - 1:
                        filter_js += " && "
                    if addif == 0:
                        context_filter_javascript = {'type': 'pre-logic'}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)

        except Exception as e:
            ErrorR.efail(e)
        return filter_js

    def get_filter_js_not(request, filters, match_condition, box_id, addif=0):
        filter_js = ""
        try:

            for i, filter1 in enumerate(filters):
                # if addif != 0:
                #     print(str(i) + " " + str(addif))
                if i == 0 and addif == 0:
                    context_filter_javascript = {'type': 'if'}
                    filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                  context_filter_javascript)
                if isinstance(filter1[0], dict):
                    single_filter = filter1[0]
                    ErrorR.okgreen(single_filter)
                    js = render_to_string('public/static_pages/not_filter_javascript.html',
                                          {'single_filter': single_filter})
                    context_filter_javascript = {
                        'type': 'condition',
                        'condition': js.strip(' \n\r\t')
                    }
                    if match_condition == '2':
                        # AND
                        filter_js += StaticPage.get_bracket_with_not(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += StaticPage.get_bracket_with_not(addif, len(filters), i, ")")

                        if i < len(filters) - 1:
                            filter_js += " && "
                    elif match_condition == '1':
                        # OR
                        filter_js += StaticPage.get_bracket_with_not(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += StaticPage.get_bracket_with_not(addif, len(filters), i, ")")
                        if i < len(filters) - 1:
                            filter_js += " || "

                    if i == len(filters) - 1 and addif == 0:
                        context_filter_javascript = {'type': 'pre-logic'}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)

                else:
                    match_condition_inner = filter1[0][0]['matchFor']
                    filter_js += "("
                    if match_condition == '2':
                        # And
                        filter_js += StaticPage.get_filter_js_not(request, filter1, match_condition_inner, box_id,
                                                                  addif + 1)
                    elif match_condition == '1':
                        # Or
                        filter_js += StaticPage.get_filter_js_not(request, filter1, match_condition_inner, box_id,
                                                                  addif + 1)
                    filter_js += ")"
                    if i == len(filters) - 1 and addif == 0:
                        filter_js += "))"
                    if addif != 0 and i != len(filters) - 1:
                        filter_js += " && "
                    if addif == 0:
                        context_filter_javascript = {'type': 'pre-logic'}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)

        except Exception as e:
            ErrorR.efail(e)
        return filter_js

    def check_hash_auth(request):
        try:
            if request.session['reset_have_auth'] == "newpasstrue":
                del request.session['reset_have_auth']
                return True
        except KeyError:
            pass
        return False

    def get_static_page(request, staticPage=None, *args, **kwargs):
        try:
            page = StaticPage.get_object(request, staticPage)
            if staticPage == "new-password-page":
                if not StaticPage.check_hash_auth(request):
                    return redirect('welcome', event_url=request.session['event_url'])
            cookie_key = StaticPage.initialize_cookie(request)
            if cookie_key:
                cookieObj = Cookie.objects.filter(cookie_key=cookie_key)
                if cookieObj.exists():
                    StaticPage.count_hit(request, cookieObj[0].id, page.id)
                else:
                    newCookieObj = Cookie(cookie_key=cookie_key)
                    newCookieObj.save()
                    StaticPage.count_hit(request, newCookieObj.id, page.id)
            # Need to recheck unlimited loop may occur
            if page.is_show:
                kendo_plugin_flag = False
                if page.login_required and page.url != 'logout':
                    if 'is_user_login' not in request.session:
                        return redirect('welcome', event_url=request.session['event_url'])
                    elif 'is_user_login' in request.session and request.session['is_user_login'] == False:
                        return redirect('welcome', event_url=request.session['event_url'])
                current_language = request.session['language_id']
                current_preset = Presets.objects.get(id=current_language)
                pageContents = page.content
                template = EmailTemplates.objects.get(id=page.template_id)
                page_content = template.content.replace('{content}',
                                                        '<div id="content" class="loading-page">' + pageContents + '</div>')
                position_head = page_content.index('</head>')
                head_content = render_to_string('public/static_pages/cms_header.html',
                                                {'csrf_token': django.middleware.csrf.get_token(request)})
                page_content = page_content[:position_head] + head_content + page_content[position_head:]
                import time
                start_time = time.time()
                menu_find = re.findall(r'{(menu)}', page_content)
                if len(menu_find) > 0:
                    menu = StaticPage.get_menu(request)
                    page_content = page_content.replace('{menu}', menu)
                print("--- %s seconds ---" % (time.time() - start_time))

                language_find = re.findall(r'{(language)}', page_content)
                if len(language_find) > 0:
                    all_languages = StaticPage.get_all_language(request, current_preset)
                    page_content = page_content.replace('{language}', all_languages)
                # page_content = PageDetailsWithLanguage.get_page_with_language(request,page,page_content,current_language)
                page_content = CmsPageView.replace_section(request, page_content,page.id,True)
                page_content = CmsPageView.replace_row(request, page_content,page.id,True)
                page_content = CmsPageView.replace_col(request, page_content,page.id,True)
                page_content = CmsPageView.replace_editor_html(request, page_content, page.id, current_language,True)
                page_content = StaticPage.replace_questions(request, page_content,page.id)
                page_content = StaticPage.replace_questions_variable(request, page_content)
                page_content = StaticPage.replace_answers(request, page_content)
                page_content = StaticPage.replace_sessions(request, page_content)
                page_content = StaticPage.replace_travels(request, page_content)
                page_content = StaticPage.replace_hotels(request, page_content)
                page_content = StaticPage.replace_photos(request, page_content)
                page_content = StaticPage.replace_general_tags(request, page_content)

                if page.element_filter == '' or page.element_filter == None:
                    element_filters = []
                else:
                    element_filters = json.loads(page.element_filter)
                # Function which are already decleared are listed here N.B.:Now bellow code can be unreadable
                get_element_content_obj = {
                    'evaluations': 'get_evaluation',
                    'messages': 'get_messages',
                    'next-up': 'get_session_next_up',
                    'location-list': 'get_location_list',
                    'session-radio-button': 'get_session_radio',
                    'session-checkbox': 'get_session_checkbox',
                    'login-form': 'get_login_form',
                    'request-login': 'get_request_login',
                    'submit-button': 'get_submit_button',
                    'reset-password': 'get_reset_password',
                    'new-password': 'get_new_password',
                    'attendee-list': 'get_attendee_plugin',
                    'hotel-reservation': 'get_plugin_hotel_reservation',
                    'session-scheduler': 'get_session_scheduler',
                    'archive-messages': 'get_archive_messages',
                    'photo-upload': 'get_photo_upload',
                    'photo-gallery': 'get_photo_gallery',
                    'logout': 'get_logout',
                    'multiple-registration': 'get_multiple_registration'
                }
                for element in element_filters:
                    get_element = Elements.objects.filter(id=int(element['element_id']))
                    if get_element.exists():
                        if get_element[0].slug == 'hotel-reservation' or get_element[0].slug == 'session-scheduler':
                            kendo_plugin_flag = True
                        element_name = get_element[0].slug
                        if get_element[0].slug in get_element_content_obj:
                            function_to_eval = 'Plugins.' + get_element_content_obj[
                                get_element[0].slug] + '(request, page.id, element)'
                            get_element_content = eval(function_to_eval)
                        else:
                            get_element_content = ''
                        if element_name == 'submit-button' or element_name == 'photo-upload':
                            page_content = page_content.replace(
                                '{element:' + element_name + ',box:' + element['box_id'].split('-')[1] + ',button_id:' +
                                element['button_id'] + '}', get_element_content)
                        else:
                            page_content = page_content.replace(
                                '{element:' + element_name + ',box:' + element['box_id'].split('-')[1] + '}',
                                get_element_content)
                page_content = CmsPageView.replace_enddiv(request, page_content)
                page_classes = PageContentClasses.objects.filter(page_id=page.id)
                class_list = []
                for page_class in page_classes:
                    box_class = {"box_id": page_class.box_id, "class_name": page_class.classname.classname}
                    class_list.append(box_class)
                page_content = page_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                page_content = page_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                page_content = page_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css")
                page_content = page_content.replace('[[static]]', settings.STATIC_URL_ALT)
                page_content = page_content.replace('public/js/jquery.min.js',
                                                    static('public/js/jquery.min.js'))
                page_content = page_content.replace('[[event_url]]', page.template.event.url)
                page_content = page_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
                footer_content = {
                    "class_list": class_list,
                    "static_page": page,
                    "footer_ajax_page_id": page.id,
                    "request": request
                }
                filter_store = []
                filter_ids = []
                registration_date_filter_javascript = ""
                updated_date_filter_javascript = ""
                attendee_group_filter_javascript = ""
                attendee_tag_filter_javascript = ""
                session_filter_javascript = ""
                question_filter_javascript = ""
                app_filter_javascript = ""
                hotel_filter_javascript = ""
                speaker_filter_javascript = ""
                email_filter_javascript = ""
                message_filter_javascript = ""
                page_filter_javascript = ""
                language_filter_javascript = ""
                if page.filter:
                    footer_content['static_page_filter'] = json.loads(page.filter)
                    for filterId in footer_content['static_page_filter']:
                        if 'filter_id' in filterId:
                            ErrorR.okblue("--------------RULE-----------")
                            ErrorR.okgreen(filterId)
                            filter_action = True
                            if 'action' in filterId:
                                if filterId['action'] == '0':
                                    filter_action = False
                            ErrorR.okblue(filter_action)
                            filter_ids.append(filterId['filter_id'])
                            rule_list = RuleSet.objects.filter(id=filterId['filter_id'])
                            if not rule_list.exists():
                                footer_content['static_page_filter'].remove(filterId)
                            for rule in rule_list:
                                filter_store_data = {}
                                filter_store_data['rule'] = json.loads(rule.preset)
                                filter_store_data['rule_id'] = rule.id
                                filter_store_data['box'] = filterId['box_id']
                                filter_store.append(filter_store_data)
                                field_condition = filter_store_data['rule'][0][0]['field']
                                match_condition = filter_store_data['rule'][0][0]['matchFor']
                                filter_permission = StaticPage.get_filter_permissions(request, rule_list)
                                ErrorR.okgreen(filter_permission)
                                div_id = "page-"+str(page.id)+"-"+filterId['box_id']
                                if match_condition == '2':
                                    # AND
                                    if filter_action:
                                        # True
                                        filter_javascript = StaticPage.get_filter_js(request,
                                                                                     filter_store_data['rule'],
                                                                                     match_condition,
                                                                                     div_id)
                                        filter_javascript = filter_javascript.replace('if()', 'if(' + str(
                                            filter_permission).lower() + ')')
                                        filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
                                                                                      str(filter_permission).lower())
                                    else:
                                        # False
                                        filter_javascript = StaticPage.get_filter_js_not(request,
                                                                                         filter_store_data['rule'],
                                                                                         match_condition,
                                                                                         div_id)
                                        filter_javascript = filter_javascript.replace('if()', 'if(' + str(
                                            filter_permission).lower() + ')')
                                        filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
                                                                                      str(filter_permission).lower())

                                    if field_condition == "1":
                                        registration_date_filter_javascript += filter_javascript
                                    elif field_condition == "2":
                                        updated_date_filter_javascript += filter_javascript
                                    elif field_condition == "3":
                                        attendee_group_filter_javascript += filter_javascript
                                    elif field_condition == "4":
                                        attendee_tag_filter_javascript += filter_javascript
                                    elif field_condition == "6":
                                        session_filter_javascript += filter_javascript
                                    elif field_condition == "7":
                                        question_filter_javascript += filter_javascript
                                    elif field_condition == "8":
                                        app_filter_javascript += filter_javascript
                                    elif field_condition == "9":
                                        hotel_filter_javascript += filter_javascript
                                    elif field_condition == "10":
                                        speaker_filter_javascript += filter_javascript
                                    elif field_condition == "11":
                                        email_filter_javascript += filter_javascript
                                    elif field_condition == "12":
                                        message_filter_javascript += filter_javascript
                                    elif field_condition == "13":
                                        page_filter_javascript += filter_javascript
                                    elif field_condition == "14":
                                        language_filter_javascript += filter_javascript

                                elif match_condition == '1':
                                    # OR
                                    if filter_action:
                                        # TURE
                                        filter_javascript = StaticPage.get_filter_js(request,
                                                                                     filter_store_data['rule'],
                                                                                     match_condition,
                                                                                     div_id)
                                        filter_javascript = filter_javascript.replace('if()', 'if(' + str(
                                            filter_permission).lower() + ')')
                                        filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
                                                                                      str(filter_permission).lower())
                                    else:
                                        # FLASE
                                        filter_javascript = StaticPage.get_filter_js_not(request,
                                                                                         filter_store_data['rule'],
                                                                                         match_condition,
                                                                                         div_id)
                                        filter_javascript = filter_javascript.replace('if()', 'if(' + str(
                                            filter_permission).lower() + ')')
                                        filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
                                                                                      str(filter_permission).lower())

                                    if field_condition == "1":
                                        registration_date_filter_javascript += filter_javascript
                                    elif field_condition == "2":
                                        updated_date_filter_javascript += filter_javascript
                                    elif field_condition == "3":
                                        attendee_group_filter_javascript += filter_javascript
                                    elif field_condition == "4":
                                        attendee_tag_filter_javascript += filter_javascript
                                    elif field_condition == "6":
                                        session_filter_javascript += filter_javascript
                                    elif field_condition == "7":
                                        question_filter_javascript += filter_javascript
                                    elif field_condition == "8":
                                        app_filter_javascript += filter_javascript
                                    elif field_condition == "9":
                                        hotel_filter_javascript += filter_javascript
                                    elif field_condition == "10":
                                        speaker_filter_javascript += filter_javascript
                                    elif field_condition == "11":
                                        email_filter_javascript += filter_javascript
                                    elif field_condition == "12":
                                        message_filter_javascript += filter_javascript
                                    elif field_condition == "13":
                                        page_filter_javascript += filter_javascript
                                    elif field_condition == "14":
                                        language_filter_javascript += filter_javascript
                                        # ErrorR.okblue(filter_javascript)

                footer_content['registration_date_filter_javascript'] = registration_date_filter_javascript
                footer_content['updated_date_filter_javascript'] = updated_date_filter_javascript
                footer_content['attendee_group_filter_javascript'] = attendee_group_filter_javascript
                footer_content['attendee_tag_filter_javascript'] = attendee_tag_filter_javascript
                footer_content['session_filter_javascript'] = session_filter_javascript
                footer_content['question_filter_javascript'] = question_filter_javascript
                footer_content['app_filter_javascript'] = app_filter_javascript
                footer_content['hotel_filter_javascript'] = hotel_filter_javascript
                footer_content['speaker_filter_javascript'] = speaker_filter_javascript
                footer_content['email_filter_javascript'] = email_filter_javascript
                footer_content['message_filter_javascript'] = message_filter_javascript
                footer_content['page_filter_javascript'] = page_filter_javascript
                footer_content['language_filter_javascript'] = language_filter_javascript
                footer_content['page_id'] = page.id
                footer_content['static_url'] = settings.STATIC_URL_ALT
                position_footer = page_content.index('</body>')
                foot_content = render_to_string('public/static_pages/cms_footer.html', footer_content)
                page_content = page_content[:position_footer] + foot_content + page_content[position_footer:]

                # page_content = page_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css")
                # page_content = page_content.replace('public/js/jquery.min.js',
                #                                     static('public/js/jquery.min.js'))
                # page_content = page_content.replace('<body', '<body style="display:none;"')

                if kendo_plugin_flag:
                    position_head = page_content.index('</head>')
                    head_content = render_to_string('public/static_pages/cms_header_optional.html', {})
                    page_content = page_content[:position_head] + head_content + page_content[position_head:]

                    position_footer = page_content.index('</body>')
                    foot_content = render_to_string('public/static_pages/cms_footer_optional.html', {})
                    page_content = page_content[:position_footer] + foot_content + page_content[position_footer:]
                position_head = page_content.index('</body>')
                head_content = render_to_string('public/static_pages/cms_csrf_token.html',
                                                {'csrf_token': django.middleware.csrf.get_token(request)})
                page_content = page_content[:position_head] + head_content + page_content[position_head:]

                # return render(request, 'public/static_pages/cms_page.html', context)
                # str_test = render_to_string('public/static_pages/cms_page.html', context)
                str_test = page_content.replace('\n\n', '')
                str_test = str_test.replace('\r', '')
                str_test = str_test.replace('\t\t', '')
                return HttpResponse(str_test)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        except Exception as e:
            ErrorR.efail(e)
            raise Http404

    def replace_questions(request, pageContents,page_id):
        try:
            questions = []
            match = re.findall("qid:\d+,box:\d+", pageContents)
            for q in match:
                question_datas = q.split(',')
                qids = question_datas[0]
                box = question_datas[1]
                data = {
                    'qid': qids.split(':')[1],
                    'box_id': str(box.split(":")[1])
                }
                questions.append(data)
            event_id = request.session['event_id']
            select_text = LanguageKey.catch_lang_key(request, "questions", "th_question_select_option")
            if 'event_user' not in request.session:
                for qid in questions:
                    question_data = Questions.objects.filter(id=qid['qid'], group__event_id=event_id)
                    if question_data.exists():
                        question = question_data[0]
                        question = LanguageKey.get_question_data_by_language(request, question)
                        slug_title = slugify(question.title)
                        description = ''
                        # if question.description != '' and question.description != None:
                        if question.show_description:
                            description = """<span class="event-question-label-description">""" + question.description + """</span>"""
                        if question.type == 'select':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = """<option value="">- {} -</option>""".format(select_text)
                            for opt in options:
                                option_value = opt.option
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if opt.default_value:
                                    option += """<option value='""" + option_value + """' selected>""" + opt.option + """</option>"""
                                else:
                                    option += """<option value='""" + option_value + """'>""" + opt.option + """</option>"""

                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                    <div class="event-plugin-select">
                                    <select data-filter-id=""" + str(
                                question.id) + """ id="attendee-question-""" + str(question.id) + """" class="given-answer">
                                    """ + option + """
                                    </select>
                                    </div>"""
                        elif question.type == 'radio_button':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if opt.default_value:
                                    option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + str(
                                        question.id) + """ name="attendee-question-""" + str(
                                        question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """" class="given-answer" checked><label for="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """" class="radio-label">""" + opt.option + """</label></div>"""
                                else:
                                    option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + str(
                                        question.id) + """ name="attendee-question-""" + str(
                                        question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """" class="given-answer"><label for="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """" class="radio-label">""" + opt.option + """</label></div>"""

                            content = """<label class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                    """ + """<div class="event-question-radio">""" + option + """</div>"""
                        elif question.type == 'text':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                      <input type="text" id="attendee-question-""" + str(
                                question.id) + """" class="given-answer" data-filter-id=""" + str(
                                question.id) + """>"""
                        elif question.type == 'checkbox':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if opt.default_value:
                                    option += """<div class="checkbox-wrapper"><input class="given-answer" type="checkbox" data-filter-id=""" + str(
                                        question.id) + """ name="attendee-question-""" + str(
                                        question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """" checked><label class="checkbox-label" for="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """">""" + opt.option + """</label></div>"""
                                else:
                                    option += """<div class="checkbox-wrapper"><input class="given-answer" type="checkbox" data-filter-id=""" + str(
                                        question.id) + """ name="attendee-question-""" + str(
                                        question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """"><label class="checkbox-label" for="attendee-question-""" + str(
                                        question.id) + """-""" + str(
                                        counter) + """">""" + opt.option + """</label></div>"""

                                content = """<label  class="event-question-label" for="attendee-""" + slug_title + """">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label><br/>
                                        """ + """<div class="event-question-checkbox">""" + option + """</div>"""
                        elif question.type == 'textarea':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                      <textarea  data-filter-id=""" + str(
                                question.id) + """ id="attendee-question-""" + str(
                                question.id) + """" class="given-answer"></textarea>"""
                        else:
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                      <input type="text" data-filter-id=""" + str(
                                question.id) + """ id="attendee-question-""" + str(
                                question.id) + """" class="given-answer">"""

                        lang = LanguageKey.catch_lang_key(request, "questions",
                                                          "th_question_select_ur_ques")
                        box_data = "page-"+str(page_id)+"-box-" + qid["box_id"]
                        required = ""
                        question_required = 0
                        actual_def = "null"
                        if question.required:
                            question_required = 1
                            required = " required"
                        if question.actual_definition:
                            actual_def = str(question.actual_definition)
                        error_text = lang.replace("{question}", question.title)
                        element = """<div class="event-question element box""" + required + """" data-id=""" + str(
                            question.id) + """ data-req=""" + str(
                            question_required) + """ data-def=""" + actual_def + """ id=""" + box_data + """ type=""" + question.type + """>""" + \
                                  content + """
                                <div class="error-on-validate">""" + error_text + """</div></div>"""
                    else:
                        element = ""
                    pageContents = pageContents.replace('{qid:' + qid['qid'] + ',box:' + qid['box_id'] + '}', element)
            else:
                attendee_id = request.session['event_user']['id']
                for qid in questions:
                    question_data = Questions.objects.filter(id=qid['qid'], group__event_id=event_id)
                    if question_data.exists():
                        question = question_data[0]
                        question = LanguageKey.get_question_data_by_language(request, question)
                        answer = Answers.objects.filter(question_id=qid['qid'], user_id=attendee_id)
                        slug_title = slugify(question.title)
                        description = ''
                        # if question.description != '' and question.description != None:
                        if question.show_description:
                            description = """<span class="event-question-label-description">""" + question.description + """</span>"""
                        if question.type == 'select':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = """<option value="">- {} -</option>""".format(select_text)

                            if not answer.exists():
                                for opt in options:
                                    option_value = opt.option
                                    opt = LanguageKey.get_option_data_by_language(request, opt)
                                    if opt.default_value:
                                        option += """<option value='""" + option_value + """' selected>""" + opt.option + """</option>"""
                                    else:
                                        option += """<option value='""" + option_value + """'>""" + opt.option + """</option>"""
                            else:
                                value = answer[0].value
                                for opt in options:
                                    option_value = opt.option
                                    opt = LanguageKey.get_option_data_by_language(request, opt)
                                    if option_value == value:
                                        option += """<option value='""" + option_value + """' selected>""" + opt.option + """</option>"""
                                    else:
                                        option += """<option value='""" + option_value + """'>""" + opt.option + """</option>"""

                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                    <div class="event-plugin-select">
                                    <select data-filter-id=""" + str(
                                question.id) + """  id="attendee-question-""" + str(question.id) + """" class="given-answer">
                                    """ + option + """
                                    </select>
                                    </div>"""
                        elif question.type == 'radio_button':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if not answer.exists():
                                    if opt.default_value:
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + str(
                                            question.id) + """  name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="given-answer" checked><label for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="radio-label">""" + opt.option + """</label></div>"""
                                    else:
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + str(
                                            question.id) + """  name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="given-answer"><label for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="radio-label">""" + opt.option + """</label></div>"""
                                else:
                                    value = answer[0].value
                                    if option_value == value:
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + str(
                                            question.id) + """  name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="given-answer" checked><label for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="radio-label">""" + opt.option + """</label></div>"""
                                    else:
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + str(
                                            question.id) + """  name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="given-answer"><label for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" class="radio-label">""" + opt.option + """</label></div>"""

                            content = """<label class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label><br/>
                                    """ + """<div class="event-question-radio">""" + option + """</div>"""
                        elif question.type == 'text':
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <input type="text" data-filter-id=""" + str(
                                    question.id) + """  id="attendee-question-""" + str(
                                    question.id) + """" class="given-answer">"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <input type="text" data-filter-id=""" + str(
                                    question.id) + """  value='""" + value + """' id="attendee-question-""" + str(
                                    question.id) + """" class="given-answer">"""
                        elif question.type == 'checkbox':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if not answer.exists():
                                    if opt.default_value:
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + str(
                                            question.id) + """  type="checkbox" name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" checked><label class="checkbox-label" for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """">""" + opt.option + """</label></div>"""
                                    else:
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + str(
                                            question.id) + """  type="checkbox" name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """"><label class="checkbox-label" for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """">""" + opt.option + """</label></div>"""
                                else:
                                    value = answer[0].value
                                    values = value.split("<br>")
                                    if option_value in values:
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + str(
                                            question.id) + """  type="checkbox" name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """" checked><label class="checkbox-label" for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """">""" + opt.option + """</label></div>"""
                                    else:
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + str(
                                            question.id) + """  type="checkbox" name="attendee-question-""" + str(
                                            question.id) + """" value='""" + option_value + """' id="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """"><label class="checkbox-label" for="attendee-question-""" + str(
                                            question.id) + """-""" + str(
                                            counter) + """">""" + opt.option + """</label></div>"""

                                content = """<label class="event-question-label" for="attendee-""" + slug_title + """">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label><br/>
                                    """ + """<div class="event-question-checkbox">""" + option + """</div>"""
                        elif question.type == 'textarea':
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <textarea  data-filter-id=""" + str(
                                    question.id) + """ id="attendee-question-""" + str(
                                    question.id) + """" class="given-answer"></textarea>"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <textarea data-filter-id=""" + str(
                                    question.id) + """  id="attendee-question-""" + str(
                                    question.id) + """" class="given-answer">""" + value + """</textarea>"""
                        else:
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <input type="text" data-filter-id=""" + str(
                                    question.id) + """  id="attendee-question-""" + str(
                                    question.id) + """" class="given-answer">"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="event-question-label">""" + """<span class="event-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <input type="text" data-filter-id=""" + str(
                                    question.id) + """  value=""" + value + """ id="attendee-question-""" + str(
                                    question.id) + """" class="given-answer">"""

                        lang = LanguageKey.catch_lang_key(request, "questions",
                                                          "th_question_select_ur_ques")
                        error_text = lang.replace("{question}", question.title)
                        box_data = "page-"+str(page_id)+"-box-" + qid["box_id"]
                        required = ""
                        question_required = 0
                        actual_def = "null"
                        if question.required:
                            question_required = 1
                            required = " required"
                        if question.actual_definition:
                            actual_def = str(question.actual_definition)
                        element = """<div class="event-question element box""" + required + """" data-id=""" + str(
                            question.id) + """ data-req=""" + str(
                            question_required) + """ data-def=""" + actual_def + """ id=""" + box_data + """ type=""" + question.type + """>""" + \
                                  content + """
                                <div class="error-on-validate">""" + error_text + """</div></div>"""
                    else:
                        element = ""
                    pageContents = pageContents.replace('{qid:' + qid['qid'] + ',box:' + qid['box_id'] + '}', element)

            return pageContents
        except Exception as e:
            ErrorR.efail(e)
            return pageContents

    def replace_questions_variable(request, pageContents):
        question_regex = r"({\"questions\":)(.|\s|\n)*?(]})"
        message = pageContents
        try:
            event_id = request.session['event_id']
            default_date_format = StaticPage.get_default_date_format(event_id)
            question_default = '{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"' + default_date_format + ' H:m"}]}'
            if '{"questions"}' in message:
                message = message.replace('{"questions"}', question_default)
            question_matches = re.finditer(question_regex, message)
            for question_match in question_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    attendee_questions = ""
                    question_id = []
                    question_group_id = []
                    question_rules = {}
                    attendee = Attendee.objects.filter(id=request.session['event_user']['id'])
                    question_json_data = json.loads(question_match.group())

                    if "id" in question_json_data["questions"][0]:
                        question_id = [int(s) for s in question_json_data["questions"][0]["id"].split(',') if
                                       s.isdigit()]
                        question_rules["data_title"] = question_json_data["questions"][0]["id"].split(',')
                    if 'group-id' in question_json_data["questions"][0]:
                        if question_json_data["questions"][0]['group-id'] != "":
                            question_group_id = [int(s) for s in
                                                 question_json_data["questions"][0]["group-id"].split(',') if
                                                 s.isdigit()]
                    if 'columns' in question_json_data["questions"][0]:
                        question_columns = question_json_data["questions"][0]['columns']
                        question_rules["columns"] = question_columns
                    if 'date-time' in question_json_data["questions"][0]:
                        question_time_date = question_json_data["questions"][0]['date-time']
                        question_rules["timedate"] = question_time_date
                        # ****QUESTION START****

                        questionAnswer = {}
                        questionAnswer["registration_date"] = attendee[0].created
                        questionAnswer["last_update_date"] = attendee[0].updated
                        attendee_groups_data = AttendeeGroups.objects.filter(attendee_id=attendee[0].id)
                        attendee_groups_list = []
                        for attendee_group in attendee_groups_data:
                            attendee_group.group = LanguageKey.get_group_data_by_language(request, attendee_group.group)
                            attendee_groups_list.append(attendee_group.group.name)
                        attendee_groups = ','.join(attendee_groups_list)
                        tags_data = AttendeeTag.objects.filter(attendee_id=attendee[0].id)
                        tags = ','.join(tag.tag.name for tag in tags_data)
                        questionAnswer["attendee_groups"] = attendee_groups
                        questionAnswer["tags"] = tags
                        if len(question_id):
                            if (len(question_group_id)):
                                answers = Answers.objects.filter(question_id__in=question_id, user_id=attendee[0].id,
                                                                 question__group_id__in=question_group_id)
                            else:
                                answers = Answers.objects.filter(question_id__in=question_id, user_id=attendee[0].id)
                        else:
                            if (len(question_group_id)):
                                answers = Answers.objects.filter(user_id=attendee[0].id,
                                                                 question__group_id__in=question_group_id)
                            else:
                                answers = Answers.objects.filter(user_id=attendee[0].id)
                        if answers:
                            questionAnswer["answers"] = answers

                            attendee_questions = DetailsData.get_question_data_by_attendee(request,
                                                                                           questionAnswer,
                                                                                           question_rules)
                        message = message.replace(question_match.group(),
                                                  '<span class="variable-tag">' + attendee_questions + '</span>')
                        # ****QUESTION END****
                else:
                    message = message.replace(question_match.group(), "")
            return message
        except Exception as e:
            ErrorR.efail(e)
            question_matches = re.finditer(question_regex, message)
            for question_match in question_matches:
                message.replace(question_match.group(), "")
            return message

    def replace_answers(request, pageContents):
        try:
            questions = []
            match = re.findall("answer:\d+", pageContents)
            for q in match:
                data = {
                    'qid': q.split(':')[1]
                }
                questions.append(data)
            if 'event_user' not in request.session:
                for qid in questions:
                    pageContents = pageContents.replace('{answer:' + qid['qid'] + '}', "N/A")
            else:
                attendee_id = request.session['event_user']['id']
                for qid in questions:
                    question = Questions.objects.filter(id=qid['qid'])
                    if question.exists():
                        answer = Answers.objects.filter(question_id=qid['qid'], user_id=attendee_id)
                        if answer.exists():
                            pageContents = pageContents.replace('{answer:' + qid['qid'] + '}', answer[0].value)
            return pageContents
        except Exception as e:
            ErrorR.efail(e)
            return pageContents

    def replace_sessions(request, pageContents):
        session_regex = r"({\"sessions\":)(.|\s|\n)*?(]})"
        message = pageContents
        try:
            event_id = request.session['event_id']
            default_date_format = StaticPage.get_default_date_format(event_id)
            session_default = '{"sessions":[{"columns":"name,start,end","sort-column":"start","status":"attending","time-date":"' + default_date_format + ' H:m"}]}'
            if '{"sessions"}' in message:
                message = message.replace('{"sessions"}', session_default)
            session_matches = re.finditer(session_regex, message)
            for session_match in session_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    attendee_sessions = ""
                    session_id = []
                    session_group_id = []
                    session_rules = {}
                    session_obj = Session.objects.filter(group__event_id=event_id)
                    attendee = Attendee.objects.filter(id=request.session['event_user']['id'])
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

                    # ****SESSION START****
                    session_obj2 = session_obj
                    if "always" not in session_rules["status"]:
                        session_obj2 = session_obj2.filter(seminarsusers__status__in=session_rules["status"],
                                                           seminarsusers__attendee_id=attendee[0].id)
                    if session_obj2:
                        attendee_sessions = DetailsData.get_sessions_data_by_attendee(request,
                                                                                      session_obj2,
                                                                                      session_rules,
                                                                                      attendee[0].id)
                    message = message.replace(session_match.group(),
                                              '<span class="variable-tag">' + attendee_sessions + '</span>')
                    # ****SESSION END****
                else:
                    message = message.replace(session_match.group(), "")
            return message
        except Exception as e:
            ErrorR.efail(e)
            session_matches = re.finditer(session_regex, message)
            for session_match in session_matches:
                message.replace(session_match.group(), "")
            return message

    def replace_travels(request, pageContents):
        message = pageContents
        travel_regex = r"({\"travels\":)(.|\s|\n)*?(]})"
        try:
            event_id = request.session['event_id']
            default_date_format = StaticPage.get_default_date_format(event_id)
            travel_default = '{"travels":[{"columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"' + default_date_format + ' H:m"}]}'
            if '{"travels"}' in message:
                message = message.replace('{"travels"}', travel_default)
            travel_matches = re.finditer(travel_regex, message)
            for travel_match in travel_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    attendee_travels = ""
                    travel_id = []
                    travel_group_id = []
                    travel_rules = {}
                    travel_obj = Travel.objects.filter(group__event_id=event_id)
                    attendee = Attendee.objects.filter(id=request.session['event_user']['id'])
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

                    # ****TRAVEL START****
                    travel_filter_by_attendee = TravelAttendee.objects.filter(attendee=attendee[0].id).values_list(
                        'travel', flat=True)

                    travel_obj2 = travel_obj
                    travel_obj2 = travel_obj2.filter(id__in=travel_filter_by_attendee)
                    if travel_obj2:
                        attendee_travels = DetailsData.get_travel_data_by_attendee(request, travel_obj2,
                                                                                   travel_rules)

                    message = message.replace(travel_match.group(),
                                              '<span class="variable-tag">' + attendee_travels + '</span>')
                    # ****TRAVEL END****
                else:
                    message = message.replace(travel_match.group(), "")
            return message
        except Exception as e:
            ErrorR.efail(e)
            travel_matches = re.finditer(travel_regex, message)
            for travel_match in travel_matches:
                message.replace(travel_match.group(), "")
            return message

    def replace_hotels(request, pageContents):
        message = pageContents
        hotel_regex = r"({\"hotels\":)(.|\s|\n)*?(]})"
        try:
            event_id = request.session['event_id']
            default_date_format = StaticPage.get_default_date_format(event_id)
            hotel_default = '{"hotels":[{"columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"' + default_date_format + '"}]}'
            if '{"hotels"}' in message:
                message = message.replace('{"hotels"}', hotel_default)
            hotel_matches = re.finditer(hotel_regex, message)
            for hotel_match in hotel_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    attendee_hotels = ""
                    hotel_id = []
                    hotel_group_id = []
                    hotel_rules = {}
                    hotel_obj = Booking.objects.filter(room__hotel__group__event_id=event_id)
                    attendee = Attendee.objects.filter(id=request.session['event_user']['id'])
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

                    # ****BOOKING START****
                    hotel_obj2 = hotel_obj
                    hotel_obj2 = hotel_obj2.filter(attendee=attendee[0].id)
                    if hotel_obj2:
                        attendee_hotels = DetailsData.get_hotels_data_by_attendee(request,
                                                                                  hotel_obj2,
                                                                                  hotel_rules)

                    message = message.replace(hotel_match.group(),
                                              '<span class="variable-tag">' + attendee_hotels + '</span>')
                    # ****BOOKING END****
                else:
                    message = message.replace(hotel_match.group(), "")

            return message
        except Exception as e:
            ErrorR.efail(e)
            hotel_matches = re.finditer(hotel_regex, message)
            for hotel_match in hotel_matches:
                message.replace(hotel_match.group(), "")
            return message

    def replace_photos(request, pageContents):
        message = pageContents
        photo_regex = r"({\"photo\":)(.|\s|\n)*?(]})"
        try:
            event_id = request.session['event_id']
            photo_default = '{"photo":[{"groups":""}]}'
            if '{"photo"}' in message:
                message = message.replace('{"photo"}', photo_default)
            photo_matches = re.finditer(photo_regex, message)
            for photo_match in photo_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    photo_json_data = json.loads(photo_match.group())
                    if "group" in photo_json_data['photo'][0] and photo_json_data['photo'][0]['group'] != '':
                        photo_groups = photo_json_data['photo'][0]['group'].split(',')
                        photos = Photo.objects.filter(group__name__in=photo_groups, group__page__event_id=event_id,
                                                      is_approved=1)
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
                else:
                    message = message.replace(photo_match.group(), "")
            return message
        except Exception as e:
            ErrorR.efail(e)
            photo_matches = re.finditer(photo_regex, message)
            for photo_match in photo_matches:
                message.replace(photo_match.group(), "")
            return message

    def replace_general_tags(request, pageContents):
        base_url = request.session['base_url']
        if 'is_user_login' in request.session and request.session['is_user_login'] == True:
            attendee = Attendee.objects.get(id=request.session['event_user']['id'])

            first_name = str(attendee.firstname)
            last_name = str(attendee.lastname)
            email_address = str(attendee.email)

            registration_date = str(attendee.created)
            updated_date = str(attendee.updated)
            attendee_groups_data = AttendeeGroups.objects.filter(attendee_id=attendee.id)
            attendee_groups_list = []
            for attendee_group in attendee_groups_data:
                attendee_group.group = LanguageKey.get_group_data_by_language(request, attendee_group.group)
                attendee_groups_list.append(attendee_group.group.name)
            attendee_groups = ','.join(attendee_groups_list)
            tags_data = AttendeeTag.objects.filter(attendee_id=attendee.id)
            tags = ', '.join(tag.tag.name for tag in tags_data)
            uid = request.session['event_user']['secret_key']
        else:
            registration_date = ""
            updated_date = ""
            password = ""
            attendee_groups = ""
            tags = ""
            uid = ''

            first_name = ''
            last_name = ''
            email_address = ''

        uid_link = """<a href=""" + base_url + """/?uid={uid}>""" + base_url + """/?uid={uid}</a>"""
        calender_content = """<a href=""" + base_url + """/webcal/?uid={uid}>""" + base_url + """/webcal/?uid={uid}</a>"""

        pageContents = pageContents.replace('{registration_date}',
                                            '<span class="variable-tag">' + registration_date + '</span>')
        pageContents = pageContents.replace('{updated_date}', '<span class="variable-tag">' + updated_date + '</span>')
        pageContents = pageContents.replace('{attendee_groups}',
                                            '<span class="variable-tag">' + attendee_groups + '</span>')
        pageContents = pageContents.replace('{tags}', '<span class="variable-tag">' + tags + '</span>')
        pageContents = pageContents.replace('{uid_link}', '<span class="variable-tag">' + uid_link + '</span>')
        pageContents = pageContents.replace('{calendar}', '<span class="variable-tag">' + calender_content + '</span>')

        pageContents = pageContents.replace('{first_name}', '<span class="variable-tag">' + first_name + '</span>')
        pageContents = pageContents.replace('{last_name}', '<span class="variable-tag">' + last_name + '</span>')
        pageContents = pageContents.replace('{email_address}',
                                            '<span class="variable-tag">' + email_address + '</span>')

        pageContents = pageContents.replace('{uid}', uid)
        return pageContents

    def get_menu(request, *args, **kwargs):
        context = {
            'request': request
        }
        return render_to_string('public/content/menu_head.html', context)

    def get_all_language(request, current_language, *args, **kwargs):
        event_id = request.session["event_id"]
        languages = Presets.objects.filter(Q(event_id=event_id) | Q(event_id=None))
        for language in languages:
            language.preset_class = slugify(language.preset_name.lower())
        if current_language == None:
            current_language = Presets.objects.get(id=6)
            current_language.id = current_language.preset.id
            current_language.preset_name = current_language.preset.preset_name
        current_language.preset_class = slugify(current_language.preset_name.lower())
        context = {
            'request': request,
            'languages': languages,
            "current_language": current_language
        }
        return render_to_string('public/content/language.html', context)

    def get_eval_next_up_msg(request, *args, **kwargs):
        response_data = {}
        try:
            response_data['evaluation_html'] = {}
            response_data['messages_html'] = {}
            response_data['next_up_html'] = {}
            response_data['evaluation_status'] = False
            response_data['messages_status'] = False
            response_data['next_up_status'] = False
            if 'page_id' in request.POST:
                page_id = request.POST.get('page_id')
                page = PageContent.objects.get(id=page_id)
                if page.element_filter == '' or page.element_filter == None:
                    element_filters = []
                else:
                    element_filters = json.loads(page.element_filter)

                for element in element_filters:
                    get_element = Elements.objects.filter(id=int(element['element_id']))
                    if get_element.exists():
                        if get_element[0].slug == 'evaluations':
                            response_data['evaluation_status'] = True
                            response_data['evaluation_html'][element['box_id']] = Plugins.get_evaluation(request,
                                                                                                         page_id,
                                                                                                         element)
                        elif get_element[0].slug == 'messages':
                            response_data['messages_status'] = True
                            response_data['messages_html'][element['box_id']] = Plugins.get_messages(request,
                                                                                                     page_id,
                                                                                                     element)
                        elif get_element[0].slug == 'archive-messages':
                            response_data['archive_messages_status'] = True
                            response_data['messages_html'][element['box_id']] = Plugins.get_archive_messages(request,
                                                                                                             page_id,
                                                                                                             element)
                        elif get_element[0].slug == 'next-up':
                            response_data['next_up_status'] = True
                            response_data['next_up_html'][element['box_id']] = Plugins.get_session_next_up(request,
                                                                                                           page_id,
                                                                                                           element)
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

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

# class PageDetailsWithLanguage(generic.DetailView):
#
#
#     def get_page_with_language(request,page,page_content,current_language):
#         page_content = CmsPageView.replace_section(request, page_content)
#         page_content = CmsPageView.replace_row(request, page_content)
#         page_content = CmsPageView.replace_col(request, page_content)
#         page_content = CmsPageView.replace_editor_html(request, page_content, page.id, current_language)
#         page_content = StaticPage.replace_questions(request, page_content)
#         page_content = StaticPage.replace_questions_variable(request, page_content)
#         page_content = StaticPage.replace_answers(request, page_content)
#         page_content = StaticPage.replace_sessions(request, page_content)
#         page_content = StaticPage.replace_travels(request, page_content)
#         page_content = StaticPage.replace_hotels(request, page_content)
#         page_content = StaticPage.replace_photos(request, page_content)
#         page_content = StaticPage.replace_general_tags(request, page_content)
#
#         if page.element_filter == '' or page.element_filter == None:
#             element_filters = []
#         else:
#             element_filters = json.loads(page.element_filter)
#         # Function which are already decleared are listed here N.B.:Now bellow code can be unreadable
#         get_element_content_obj = {
#             'evaluations': 'get_evaluation',
#             'messages': 'get_messages',
#             'next-up': 'get_session_next_up',
#             'location-list': 'get_location_list',
#             'session-radio-button': 'get_session_radio',
#             'session-checkbox': 'get_session_checkbox',
#             'login-form': 'get_login_form',
#             'request-login': 'get_request_login',
#             'submit-button': 'get_submit_button',
#             'reset-password': 'get_reset_password',
#             'new-password': 'get_new_password',
#             'attendee-list': 'get_attendee_plugin',
#             'hotel-reservation': 'get_plugin_hotel_reservation',
#             'session-scheduler': 'get_session_scheduler',
#             'archive-messages': 'get_archive_messages',
#             'photo-upload': 'get_photo_upload',
#             'photo-gallery': 'get_photo_gallery',
#             'logout': 'get_logout',
#             'multiple-registration': 'get_multiple_registration'
#         }
#         for element in element_filters:
#             get_element = Elements.objects.filter(id=int(element['element_id']))
#             if get_element.exists():
#                 if get_element[0].slug == 'hotel-reservation' or get_element[0].slug == 'session-scheduler':
#                     kendo_plugin_flag = True
#                 element_name = get_element[0].slug
#                 if get_element[0].slug in get_element_content_obj:
#                     function_to_eval = 'Plugins.' + get_element_content_obj[
#                         get_element[0].slug] + '(request, page.id, element)'
#                     get_element_content = eval(function_to_eval)
#                 else:
#                     get_element_content = ''
#                 if element_name == 'submit-button' or element_name == 'photo-upload':
#                     page_content = page_content.replace(
#                         '{element:' + element_name + ',box:' + element['box_id'].split('-')[1] + ',button_id:' +
#                         element['button_id'] + '}', get_element_content)
#                 else:
#                     page_content = page_content.replace(
#                         '{element:' + element_name + ',box:' + element['box_id'].split('-')[1] + '}',
#                         get_element_content)
#         page_content = CmsPageView.replace_enddiv(request, page_content)
#
#
#         page_content = page_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
#         page_content = page_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
#         page_content = page_content.replace('[[static]]', settings.STATIC_URL_ALT)
#         # page_content = page_content.replace('public/js/jquery.min.js',
#         #                                     static('public/js/jquery.min.js'))
#         page_content = page_content.replace('[[event_url]]', page.template.event.url)
#         page_content = page_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
#
#         return page_content
#
#     def get_content_javascript(request,page):
#         page_classes = PageContentClasses.objects.filter(page_id=page.id)
#         class_list = []
#         for page_class in page_classes:
#             box_class = {"box_id": page_class.box_id, "class_name": page_class.classname.classname}
#             class_list.append(box_class)
#         footer_content = {
#             "class_list": class_list,
#             "static_page": page,
#             "footer_ajax_page_id": page.id,
#             "request": request
#         }
#         filter_store = []
#         filter_ids = []
#         registration_date_filter_javascript = ""
#         updated_date_filter_javascript = ""
#         attendee_group_filter_javascript = ""
#         attendee_tag_filter_javascript = ""
#         session_filter_javascript = ""
#         question_filter_javascript = ""
#         app_filter_javascript = ""
#         hotel_filter_javascript = ""
#         speaker_filter_javascript = ""
#         email_filter_javascript = ""
#         message_filter_javascript = ""
#         page_filter_javascript = ""
#         language_filter_javascript = ""
#         if page.filter:
#             footer_content['static_page_filter'] = json.loads(page.filter)
#             for filterId in footer_content['static_page_filter']:
#                 if 'filter_id' in filterId:
#                     ErrorR.okblue("--------------RULE-----------")
#                     ErrorR.okgreen(filterId)
#                     filter_action = True
#                     if 'action' in filterId:
#                         if filterId['action'] == '0':
#                             filter_action = False
#                     ErrorR.okblue(filter_action)
#                     filter_ids.append(filterId['filter_id'])
#                     rule_list = RuleSet.objects.filter(id=filterId['filter_id'])
#                     if not rule_list.exists():
#                         footer_content['static_page_filter'].remove(filterId)
#                     for rule in rule_list:
#                         filter_store_data = {}
#                         filter_store_data['rule'] = json.loads(rule.preset)
#                         filter_store_data['rule_id'] = rule.id
#                         filter_store_data['box'] = filterId['box_id']
#                         filter_store.append(filter_store_data)
#                         field_condition = filter_store_data['rule'][0][0]['field']
#                         match_condition = filter_store_data['rule'][0][0]['matchFor']
#                         filter_permission = StaticPage.get_filter_permissions(request, rule_list)
#                         ErrorR.okgreen(filter_permission)
#                         if match_condition == '2':
#                             # AND
#                             if filter_action:
#                                 # True
#                                 filter_javascript = StaticPage.get_filter_js(request,
#                                                                              filter_store_data['rule'],
#                                                                              match_condition,
#                                                                              filterId['box_id'])
#                                 filter_javascript = filter_javascript.replace('if()', 'if(' + str(
#                                     filter_permission).lower() + ')')
#                                 filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
#                                                                               str(filter_permission).lower())
#                             else:
#                                 # False
#                                 filter_javascript = StaticPage.get_filter_js_not(request,
#                                                                                  filter_store_data['rule'],
#                                                                                  match_condition,
#                                                                                  filterId['box_id'])
#                                 filter_javascript = filter_javascript.replace('if()', 'if(' + str(
#                                     filter_permission).lower() + ')')
#                                 filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
#                                                                               str(filter_permission).lower())
#
#                             if field_condition == "1":
#                                 registration_date_filter_javascript += filter_javascript
#                             elif field_condition == "2":
#                                 updated_date_filter_javascript += filter_javascript
#                             elif field_condition == "3":
#                                 attendee_group_filter_javascript += filter_javascript
#                             elif field_condition == "4":
#                                 attendee_tag_filter_javascript += filter_javascript
#                             elif field_condition == "6":
#                                 session_filter_javascript += filter_javascript
#                             elif field_condition == "7":
#                                 question_filter_javascript += filter_javascript
#                             elif field_condition == "8":
#                                 app_filter_javascript += filter_javascript
#                             elif field_condition == "9":
#                                 hotel_filter_javascript += filter_javascript
#                             elif field_condition == "10":
#                                 speaker_filter_javascript += filter_javascript
#                             elif field_condition == "11":
#                                 email_filter_javascript += filter_javascript
#                             elif field_condition == "12":
#                                 message_filter_javascript += filter_javascript
#                             elif field_condition == "13":
#                                 page_filter_javascript += filter_javascript
#                             elif field_condition == "14":
#                                 language_filter_javascript += filter_javascript
#
#                         elif match_condition == '1':
#                             # OR
#                             if filter_action:
#                                 # TURE
#                                 filter_javascript = StaticPage.get_filter_js(request,
#                                                                              filter_store_data['rule'],
#                                                                              match_condition,
#                                                                              filterId['box_id'])
#                                 filter_javascript = filter_javascript.replace('if()', 'if(' + str(
#                                     filter_permission).lower() + ')')
#                                 filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
#                                                                               str(filter_permission).lower())
#                             else:
#                                 # FLASE
#                                 filter_javascript = StaticPage.get_filter_js_not(request,
#                                                                                  filter_store_data['rule'],
#                                                                                  match_condition,
#                                                                                  filterId['box_id'])
#                                 filter_javascript = filter_javascript.replace('if()', 'if(' + str(
#                                     filter_permission).lower() + ')')
#                                 filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
#                                                                               str(filter_permission).lower())
#
#                             if field_condition == "1":
#                                 registration_date_filter_javascript += filter_javascript
#                             elif field_condition == "2":
#                                 updated_date_filter_javascript += filter_javascript
#                             elif field_condition == "3":
#                                 attendee_group_filter_javascript += filter_javascript
#                             elif field_condition == "4":
#                                 attendee_tag_filter_javascript += filter_javascript
#                             elif field_condition == "6":
#                                 session_filter_javascript += filter_javascript
#                             elif field_condition == "7":
#                                 question_filter_javascript += filter_javascript
#                             elif field_condition == "8":
#                                 app_filter_javascript += filter_javascript
#                             elif field_condition == "9":
#                                 hotel_filter_javascript += filter_javascript
#                             elif field_condition == "10":
#                                 speaker_filter_javascript += filter_javascript
#                             elif field_condition == "11":
#                                 email_filter_javascript += filter_javascript
#                             elif field_condition == "12":
#                                 message_filter_javascript += filter_javascript
#                             elif field_condition == "13":
#                                 page_filter_javascript += filter_javascript
#                             elif field_condition == "14":
#                                 language_filter_javascript += filter_javascript
#                                 # ErrorR.okblue(filter_javascript)
#
#         footer_content['registration_date_filter_javascript'] = registration_date_filter_javascript
#         footer_content['updated_date_filter_javascript'] = updated_date_filter_javascript
#         footer_content['attendee_group_filter_javascript'] = attendee_group_filter_javascript
#         footer_content['attendee_tag_filter_javascript'] = attendee_tag_filter_javascript
#         footer_content['session_filter_javascript'] = session_filter_javascript
#         footer_content['question_filter_javascript'] = question_filter_javascript
#         footer_content['app_filter_javascript'] = app_filter_javascript
#         footer_content['hotel_filter_javascript'] = hotel_filter_javascript
#         footer_content['speaker_filter_javascript'] = speaker_filter_javascript
#         footer_content['email_filter_javascript'] = email_filter_javascript
#         footer_content['message_filter_javascript'] = message_filter_javascript
#         footer_content['page_filter_javascript'] = page_filter_javascript
#         footer_content['language_filter_javascript'] = language_filter_javascript
#         footer_content['page_id'] = page.id
#         return footer_content

