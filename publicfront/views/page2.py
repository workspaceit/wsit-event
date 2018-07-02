import os

from app.views.gbhelper.pdf_generator import EconomyPDFGenerator
from app.views.hotel_view import RoomView
from publicfront.views.attendee_plugin import AttendeePluginList
from datetime import timedelta
from django.http import JsonResponse
from django.db.models import Count, Max

from publicfront.views.economy_page_replace import EconomyPageReplace
from publicfront.views.notify_view import NotifyView
from publicfront.views.profile import SessionDetail
from publicfront.views.session_seat_availability import SessionSeatAvailability
import math
from publicfront.views.helper import HelperData
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from app.models import PageContent, Questions, Elements, \
    Setting, Answers, Session, Attendee, Booking, \
    Presets, PagePermission, Cookie, CookiePage, Photo, PageContentClasses, ElementsAnswers, SeminarsUsers, \
    Notification, SessionTags, SeminarSpeakers, Group, Locations, RequestedBuddy, PluginSubmitButton, Room, \
    ActivityHistory, Events, PhotoGroup, PresetEvent, RuleSet, RegistrationGroupOwner, MenuPermission, \
    RegistrationGroups, Rebates, SessionClasses, StyleSheet, ExportRule, MatchLine, PluginPdfButton, Orders
import json
import re
from django.template.loader import render_to_string
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from django.http import Http404
from slugify import slugify
from pytz import timezone
from django.db.models import Q, Func, F, TimeField, ExpressionWrapper
from publicfront.views.lang_key import LanguageKey
from publicfront.views.page_replace import PageReplace
from publicfront.views.page_replace import UpdatableObj
from publicfront.views.rule import UserRule
from app.views.cms_view import CmsPageView
from publicfront.views.details import DetailsData
from publicfront.views.registration import Registration
from app.views.gbhelper.error_report_helper import ErrorR
from django.db import transaction
from datetime import datetime
from app.views.gbhelper.economy_library import EconomyLibrary
import hashlib
import time
from django.views.decorators.csrf import csrf_exempt
import logging
import boto
from boto.s3.key import Key
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
import boto3
from django.http import HttpResponseForbidden


class DynamicPage(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, '', *args, **kwargs)

    def get_object(request, pk, *args, **kwargs):
        try:
            page_list = PageContent.objects.filter(url=pk, event_id=request.session['event_id'])
            if page_list.exists():
                # print(request.session.__dict__)
                if page_list[0].disallow_logged_in:
                    if 'is_user_login' in request.session and request.session['is_user_login']:
                        context = {
                            'page': page_list[0],
                            'permission': False,
                            'not_has_permission_registered': True
                        }
                        return context
                        # raise Http404
                if page_list[0].login_required and page_list[0].url != 'logout':
                    if 'is_user_login' not in request.session:
                        context = {
                            'page': page_list[0],
                            'permission': False,
                            'not_has_permission_unregistered': True
                        }
                        return context
                    elif request.session['is_user_login'] == False:
                        context = {
                            'page': page_list[0],
                            'permission': False,
                            'not_has_permission_unregistered': True
                        }
                        return context
                rule_list = PagePermission.objects.filter(page=page_list[0].id)
                if rule_list.exists():
                    page_permission = DynamicPage.get_page_permissions(request, rule_list)
                    if page_permission:
                        context = {
                            'page': page_list[0],
                            'permission': True
                        }
                        return context
                        # return page_list[0]
                    else:
                        context = {
                            'page': page_list[0],
                            'permission': False,
                            'not_has_permission_unregistered': True
                        }
                        return context
                else:
                    context = {
                        'page': page_list[0],
                        'permission': True
                    }
                    return context
                    # return page_list[0]
            # raise Http404
            context = {
                'permission': False,
                'not_page_found': True
            }
            return context
        except Exception as e:
            ErrorR.efail(e)
            # raise Http404
            context = {
                'permission': False,
                'not_page_found': True
            }
            return context

    def get_page_permissions(request, rule_list):
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                attendee_id = request.session['event_user']['id']
                for rule in rule_list:
                    filters = json.loads(rule.rule.preset)
                    q = Q()
                    match_condition = '0'
                    if 'matchFor' in filters[0][0]:
                        match_condition = filters[0][0]['matchFor']
                    elif rule.rule.matchfor:
                        match_condition = rule.rule.matchfor
                    if match_condition == '2':
                        q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                    else:
                        q = Q(id=-11)
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
        time_zone_time = HelperData.getTimezoneNow(request)
        # event_id = request.session['event_id']
        # event_query = Setting.objects.filter(name="timezone", event=event_id)
        if time_zone_time != None:
            # time_zone_name = event_query[0].value
            # timezone_active = timezone(time_zone_name)
            now = time_zone_time.date()
            # f = '%Y-%m-%d'
            # now = datetime.strptime(str(time_now).split(".")[0], f)
            cookiePageObj = CookiePage.objects.extra(select={'visit_date': 'date( visit_date )'}).filter(
                cookie_id=cookie_id, page_id=page_id, visit_date=now)
            if cookiePageObj.exists():
                # CookiePage.objects.filter(cookie_id=cookie_id, page_id=page_id, visit_date=now).update(
                #     visit_count=cookiePageObj[0].visit_count + 1)
                CookiePage.objects.filter(id=cookiePageObj[0].id).update(
                    visit_count=cookiePageObj[0].visit_count + 1)
            else:
                newCookiePageObj = CookiePage(cookie_id=cookie_id, page_id=page_id, visit_date=now, visit_count=1)
                newCookiePageObj.save()

    def check_hash_auth(request):
        try:
            if request.session['reset_have_auth'] == "newpasstrue":
                del request.session['reset_have_auth']
                return True
        except KeyError:
            pass
        return False

    def primary_value_set(request, staticPage, page_id):
        if staticPage == "new-password-page":
            if not DynamicPage.check_hash_auth(request):
                return redirect('welcome', event_url=request.session['event_url'])
        cookie_key = DynamicPage.initialize_cookie(request)
        if cookie_key:
            cookieObj = Cookie.objects.filter(cookie_key=cookie_key)
            if cookieObj.exists():
                DynamicPage.count_hit(request, cookieObj[0].id, page_id)
            else:
                newCookieObj = Cookie(cookie_key=cookie_key)
                newCookieObj.save()
                DynamicPage.count_hit(request, newCookieObj.id, page_id)

    def get_dynamic_page_filtered(request, staticPage=None, *args, **kwargs):
        ErrorR.c_cyan("Dynamic Page Filter")
        ErrorR.c_purple(staticPage)
        [html, js] = DynamicPage.get_dynamic_page_filtered_obj(request, staticPage, *args, **kwargs)
        return HttpResponse(
            json.dumps({"html": html, "js": js}),
            content_type="application/json")

    def get_dynamic_page_filtered_obj(request, staticPage=None, *args, **kwargs):
        ErrorR.warn("Dynamic Attendee Manupulation")
        try:
            [html, jsobj] = DynamicPage.get_static_page(request, staticPage, motive=False, *args, **kwargs)
            footer_content = jsobj.format_object()
            footer_content["class_list"] = json.dumps(jsobj.class_list)
            js = render_to_string('public/static_pages/cms_footer_filter.html', footer_content)
            return [html, js]
        except Exception as e:
            ErrorR.efail(e)
            return ["", ""]

    def tem_login_make(request, attendee_id):
        try:
            attendee = Attendee.objects.get(id=attendee_id)
            tem_session = {}
            if "event_user" in request.session:
                tem_session["event_user"] = request.session['event_user']
            tem_session["event_id"] = request.session['event_id']
            if "is_user_login" in request.session:
                tem_session["is_user_login"] = request.session['is_user_login']
            auth_user = {
                "id": attendee.id,
                "name": '',
                "email": "",
                "type": attendee.type,
                "attending": "",
                "avatar": "",
                "secret_key": "",
                "event_id": request.session['event_id']
            }
            if attendee.firstname and attendee.firstname:
                auth_user["name"] = attendee.firstname + " " + attendee.lastname
            if attendee.email:
                auth_user["email"] = attendee.email
            if attendee.status:
                auth_user["attending"] = attendee.status
            if attendee.avatar:
                auth_user["avatar"] = attendee.avatar
            if attendee.secret_key:
                auth_user["secret_key"] = attendee.secret_key
            request.session['event_user'] = auth_user
            request.session['event_id'] = auth_user['event_id']
            request.session['is_user_login'] = True
            request.session.modified = True
            return tem_session
        except Exception as e:
            del request.session["event_user"]
            del request.session["is_user_login"]
            del request.session["event_id"]
            del request.session["is_user_login"]
            ErrorR.efail(e)

    def tem_login_clean(request, tem_session):
        try:
            if "event_user" in tem_session:
                request.session['event_user'] = tem_session["event_user"]
            else:
                del request.session['event_user']
            request.session['event_id'] = tem_session["event_id"]
            if "is_user_login" in tem_session:
                request.session['is_user_login'] = tem_session["is_user_login"]
            else:
                del request.session['is_user_login']
            request.session.modified = True
        except Exception as e:
            del request.session["event_user"]
            del request.session["is_user_login"]
            del request.session["event_id"]
            del request.session["is_user_login"]
            ErrorR.efail(e)

    def get_dynamic_attendee_page(request, staticPage=None, attendee_id=None, objmotive=False, *args, **kwargs):
        ErrorR.warn("Dynamic Attendee Manupulation")
        try:
            tem_session = DynamicPage.tem_login_make(request, attendee_id)
            [html, jsobj] = DynamicPage.get_static_page(request, staticPage, False, *args, **kwargs)
            DynamicPage.tem_login_clean(request, tem_session)
            ErrorR.c_purple("Dynamic Attendee Manupulation End")
            if objmotive:
                return [html, jsobj]
            else:
                footer_content = jsobj.format_object()
                footer_content["class_list"] = json.dumps(jsobj.class_list)
                js = render_to_string('public/static_pages/cms_footer_filter.html', footer_content)
                return [html, js]
        except Exception as e:
            ErrorR.efail(e)
            return ["", ""]

    def get_static_page(request, staticPage=None, motive=True, *args, **kwargs):
        ErrorR.c_cyan("Static Page")
        ErrorR.c_cyan(staticPage)
        logger = logging.getLogger(__name__)
        start_time = time.time()
        class_list = []
        try:
            updated_variable = UpdatableObj()
            page_context = DynamicPage.get_object(request, staticPage)
            if motive:
                if 'permission' in page_context and not page_context['permission']:
                    if 'not_page_found' in page_context and page_context['not_page_found']:
                        return DynamicPage.get_static_page(request, '404-not-found', True, *args, **kwargs)
                    elif 'not_has_permission_registered' in page_context and page_context[
                        'not_has_permission_registered']:
                        return DynamicPage.get_static_page(request, '403-forbidden-registered', True, *args, **kwargs)
                    elif 'not_has_permission_unregistered' in page_context and page_context[
                        'not_has_permission_unregistered']:
                        return DynamicPage.get_static_page(request, '403-forbidden-unregistered', True, *args, **kwargs)
            page = page_context['page']
            if motive:
                DynamicPage.primary_value_set(request, staticPage, page.id)
            # Need to recheck unlimited loop may occur
            if page.is_show:
                data_user_id = ''
                kendo_plugin_flag = False
                # if page.login_required and page.url != 'logout':
                #     if 'is_user_login' not in request.session:
                #         return redirect('welcome', event_url=request.session['event_url'])
                #     elif 'is_user_login' in request.session and request.session['is_user_login'] == False:
                #         return redirect('welcome', event_url=request.session['event_url'])
                current_language = request.session['language_id']
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    data_user_id = "-u-" + str(request.session['event_user']['id'])
                logger.debug("=====replace template header Start=======")
                pageContents = page.content
                # if motive:
                # pageContents += DynamicPage.get_static_page(request, "testu2", False, *args, **kwargs)
                page_content = PageReplace.replace_template(request, motive, page, pageContents)
                page_content = PageReplace.replace_menu(request, motive, page_content)
                page_content = PageReplace.replace_language(request, motive, page_content, current_language)

                logger.debug("=====Replace template header End=======")
                logger.debug("=====Replace html Structure Start=======")

                # Motive Check Start
                if not motive:
                    # page_content = PageDetailsWithLanguage.get_page_with_language(request,page,page_content,current_language)
                    page_content = CmsPageView.replace_section(request, page_content, page.id, True, data_user_id)
                    page_content = CmsPageView.replace_row(request, page_content, page.id, True, data_user_id)
                    page_content = CmsPageView.replace_col(request, page_content, page.id, True, data_user_id)
                    page_content = CmsPageView.replace_editor_html(request, page_content, page.id, current_language,
                                                                   True,
                                                                   data_user_id)
                    logger.debug("=====Replace html Structure End=======")
                # Motive Check End

                logger.debug("=====Replace General Tags Start=======")
                tag_time = time.time()
                page_content = PageReplace.replace_questions(request, page_content, page.id)
                page_content = PageReplace.replace_questions_variable(request, page_content)
                page_content = PageReplace.replace_answers(request, page_content)
                page_content = PageReplace.replace_sessions(request, page_content)
                page_content = PageReplace.replace_travels(request, page_content)
                page_content = PageReplace.replace_hotels(request, page_content)
                page_content = PageReplace.replace_photos(request, page_content)
                page_content = PageReplace.replace_general_tags(request, page_content)
                logger.debug("=====Replace General Tags End=======")
                logger.debug("=====Replace General Tags takes " + str(time.time() - tag_time) + " seconds=======")
                logger.debug("=====Replace Economy Tags Start=======")
                # economy tags
                eco_time = time.time()
                page_content = EconomyPageReplace.replace_order_owner(request, page_content)
                page_content = EconomyPageReplace.replace_order_table(request, page_content)
                page_content = EconomyPageReplace.replace_multiple_order_table(request, page_content)
                page_content = EconomyPageReplace.replace_balance_table(request, page_content)
                page_content = EconomyPageReplace.replace_order_value_paid_order(request, page_content)
                page_content = EconomyPageReplace.replace_multiple_order_value_paid_order(request, page_content)
                page_content = EconomyPageReplace.replace_order_value_pending_order(request, page_content)
                page_content = EconomyPageReplace.replace_multiple_order_value_pending_order(request, page_content)
                page_content = EconomyPageReplace.replace_order_value_open_order(request, page_content)
                page_content = EconomyPageReplace.replace_multiple_order_value_open_order(request, page_content)
                page_content = EconomyPageReplace.replace_order_value_all_order(request, page_content)
                page_content = EconomyPageReplace.replace_multiple_order_value_all_order(request, page_content)
                page_content = EconomyPageReplace.replace_order_value_credit_order(request, page_content)
                page_content = EconomyPageReplace.replace_multiple_order_value_credit_order(request, page_content)
                page_content = EconomyPageReplace.replace_reciept(request, page_content)
                logger.debug("=====Replace Economy Tags End=======")
                logger.debug("=====Replace Economy Tags End " + str(time.time() - eco_time) + " seconds=======")

                # Motive Check Start
                if not motive:
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
                        'logout': 'get_logout_page',
                        'multiple-registration': 'get_multiple_registration',
                        'economy': 'get_economy_plugin',
                        'rebate': 'get_rebates',
                        'session-agenda': 'get_session_agenda',
                        'pdf-button': 'get_pdf_button',
                        'log-out': 'get_logout'
                    }
                    # Plugins.get_rebates(request,1,1)
                    for element in element_filters:
                        get_element = Elements.objects.filter(id=int(element['element_id']))
                        if get_element.exists():
                            ErrorR.ex_time_init()
                            plugin_time = time.time()
                            logger.debug("=====Replace Element " + str(get_element[0].slug) + " Start=======")
                            if get_element[0].slug == 'session-scheduler':
                                kendo_plugin_flag = True
                            element_name = get_element[0].slug
                            if get_element[0].slug in get_element_content_obj and get_element[
                                0].slug == "multiple-registration":
                                function_to_eval = 'Plugins.' + get_element_content_obj[
                                    get_element[0].slug] + '(request, page.id, element)'
                                [get_element_content, updated_variable] = eval(function_to_eval)
                            elif get_element[0].slug in get_element_content_obj:
                                function_to_eval = 'Plugins.' + get_element_content_obj[
                                    get_element[0].slug] + '(request, page.id, element)'
                                get_element_content = eval(function_to_eval)
                                updated_variable.plugin_js_need[get_element_content_obj[get_element[0].slug]] = True
                            else:
                                get_element_content = ''
                            if element_name == 'submit-button' or element_name == 'photo-upload' or element_name == 'pdf-button':
                                page_content = page_content.replace(
                                    '{element:' + element_name + ',box:' + element['box_id'].split('-')[
                                        1] + ',button_id:' +
                                    element['button_id'] + '}', get_element_content)
                            else:
                                page_content = page_content.replace(
                                    '{element:' + element_name + ',box:' + element['box_id'].split('-')[1] + '}',
                                    get_element_content)
                            ErrorR.warn(get_element[0].slug)
                            ErrorR.ex_time()
                            logger.debug("=====Replace Element " + str(get_element[0].slug) + " End=======")
                            logger.debug("=====Replace Element " + str(get_element[0].slug) + " takes " + str(
                                time.time() - plugin_time) + "=======")
                    logger.debug("=====Replace template files Start=======")
                    page_content = CmsPageView.replace_enddiv(request, page_content)
                    page_classes = PageContentClasses.objects.filter(page_id=page.id)
                    for page_class in page_classes:
                        box_class = {"page_id": page.id, "box_id": page_class.box_id,
                                     "class_name": page_class.classname.classname}
                        class_list.append(box_class)
                # else:
                #     ErrorR.okblue(page.element_filter)
                #     if page.element_filter == '' or page.element_filter == None:
                #         element_filters = []
                #     else:
                #         element_filters = json.loads(page.element_filter)
                #     ErrorR.okgreen(len(element_filters))
                #     ErrorR.okgreen(element_filters)
                #     for element in element_filters:
                #         ErrorR.warn(int(element['element_id']))
                #         get_element = Elements.objects.filter(id=int(element['element_id']))
                #         ErrorR.warn(get_element)
                #         if get_element.exists():
                #             ErrorR.warn(get_element[0].slug)
                #             if get_element[0].slug == 'hotel-reservation':
                #                 updated_variable.plugin_js_need['get_plugin_hotel_reservation'] = True
                #             elif get_element[0].slug == 'photo-gallery':
                #                 updated_variable.plugin_js_need['get_photo_gallery'] = True
                #             elif get_element[0].slug == 'photo-upload':
                #                 updated_variable.plugin_js_need['get_photo_upload'] = True
                #             ErrorR.okblue(updated_variable.plugin_js_need)
                # ErrorR.okblue(updated_variable.plugin_js_need)

                # Motive Check End

                # Motive Check Start
                if motive:
                    # get css version
                    css_version_obj = StyleSheet.objects.get(event_id=request.session['event_id'])
                    css_version = css_version_obj.version

                    # page_content = page_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                    # page_content = page_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                    # page_content = page_content.replace('[[css]]',
                    #                                     "[[static]]public/[[event_url]]/compiled_css/style.css?v=" + str(
                    #                                         css_version))

                    # For Wsit Event
                    page_content = page_content.replace('[[file]]', "[[static]]public/files")
                    page_content = page_content.replace('[[files]]', "[[static]]public/files/")
                    page_content = page_content.replace('[[css]]',
                                                        "[[static]]public/compiled_css/style.css?v=" + str(
                                                            css_version))

                    page_content = page_content.replace('[[static]]', settings.STATIC_URL_ALT)
                    page_content = page_content.replace('public/js/jquery.min.js',
                                                        static('public/js/jquery.min.js'))
                    page_content = page_content.replace('[[event_url]]', page.template.event.url)
                    page_content = page_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')

                # Motive Check End

                kendo = {}
                kendo["kendo_content_js"] = ""
                kendo["kendo_content"] = ""

                # Motive Check Start
                if not motive:
                    if kendo_plugin_flag:
                        kendo["kendo_content_js"] = render_to_string(
                            'public/static_pages/cms_footer_optional_filter.html',
                            {"filter": "js"})
                        kendo["kendo_content"] = render_to_string(
                            'public/static_pages/cms_footer_optional.html',
                            {"filter": "script"})

                # Motive Check End
                [page_content, updatable_variable] = PageReplace.replace_footer_content(request, motive, class_list,
                                                                                        page, page_content, kendo,
                                                                                        updated_variable)
                updated_variable += updatable_variable

                # page_content = page_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css")
                # page_content = page_content.replace('public/js/jquery.min.js',
                #                                     static('public/js/jquery.min.js'))
                # page_content = page_content.replace('<body', '<body style="display:none;"')

                page_content = PageReplace.replace_kendo_plugin(request, motive, kendo_plugin_flag,
                                                                page_content)

                # return render(request, 'public/static_pages/cms_page.html', context)
                # str_test = render_to_string('public/static_pages/cms_page.html', context)
                final_page_content = page_content.replace('\n\n', '')
                final_page_content = final_page_content.replace('\r', '')
                final_page_content = final_page_content.replace('\t\t', '')
                logger.debug("=====Replace template files End=======")
                total_time = time.time() - start_time
                logger.debug("=====Total time in page preapare " + str(total_time) + "=======")
                if not motive:
                    return [final_page_content, updated_variable]
                return HttpResponse(final_page_content)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        except Exception as e:
            ErrorR.efail(e)
            raise Http404

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
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    data_user_id = "-u-" + str(request.session['event_user']['id'])
                else:
                    data_user_id = "0"

                for element in element_filters:
                    get_element = Elements.objects.filter(id=int(element['element_id']))
                    box_id = "page-" + str(page_id) + "-" + element['box_id'] + data_user_id
                    if get_element.exists():
                        if get_element[0].slug == 'evaluations':
                            response_data['evaluation_status'] = True
                            response_data['evaluation_html'][box_id] = Plugins.get_evaluation(request,
                                                                                              page_id,
                                                                                              element)
                        elif get_element[0].slug == 'messages':
                            response_data['messages_status'] = True
                            response_data['messages_html'][box_id] = Plugins.get_messages(request,
                                                                                          page_id,
                                                                                          element)
                        elif get_element[0].slug == 'archive-messages':
                            response_data['archive_messages_status'] = True
                            response_data['messages_html'][box_id] = Plugins.get_archive_messages(request,
                                                                                                  page_id,
                                                                                                  element)
                        elif get_element[0].slug == 'next-up':
                            response_data['next_up_status'] = True
                            response_data['next_up_html'][box_id] = Plugins.get_session_next_up(request,
                                                                                                page_id,
                                                                                                element)
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
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


class Plugins(generic.TemplateView):
    def get_evaluation(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-evaluations" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="evaluations">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                        'element_question')
                    today = HelperData.getTimezoneNow(request)
                    # f = '%Y-%m-%d %H:%M:%S'
                    # today = datetime.strptime(str(time_now).split(".")[0], f)
                    title = ''
                    appear_time = 11
                    message = ''
                    session_link = 'True'
                    for setting in element_settings:
                        if setting.element_question.question_key == 'evaluation_title':
                            title = setting.answer
                        elif setting.element_question.question_key == 'evaluation_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            message = setting.description
                        elif setting.element_question.question_key == 'evaluation_appear':
                            appear_time = setting.answer
                        elif setting.element_question.question_key == 'evaluation_session_details_link':
                            session_link = setting.answer
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
                        "session_link": session_link,
                        "language": language,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id'],
                        "data_user_id": str(user_id)
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
        plugin_div = """<div class="form-plugin element form-plugin-messages" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="messages">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                        'element_question')
                    title = ''
                    message = ''
                    archive_messages = 'True'
                    archive_button = 'True'
                    show_archive_button = 'False'
                    mark_all_button = 'True'
                    session_link = 'True'
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
                        elif setting.element_question.question_key == 'message_session_details_link':
                            session_link = setting.answer
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
                        datetime_field = HelperData.convert_datetime_to_date_and_time(str(nt.created_at))
                        nt.date_field = datetime_field['date_field']
                        nt.time_field = datetime_field['time_field']
                        if nt.type == 'session_attend' or nt.type == 'session':
                            try:
                                data_status = ''
                                if nt.type == 'session':
                                    data_status = 'deciding'
                                match = re.finditer("session_id:\d+", nt.message)
                                for q in match:
                                    s_id = q.group().split(':')[1]
                                    try:
                                        session_data = Session.objects.values('id', 'name').get(id=s_id)
                                        session_msg = session_data['name']
                                        if session_link == "True":
                                            session_msg = "<span class='message-session-details session-detail-link' data-id='" + str(
                                                session_data['id']) + "' data-status='" + data_status + "'>" + str(session_data['name']) + "</span>"
                                    except:
                                        session_msg = ""
                                        pass
                                    nt.message = nt.message.replace("{" + q.group() + "}", session_msg)
                            except Exception as e:
                                ErrorR.efail(e)
                                pass
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
                        "session_link": session_link,
                        "notifications": list(notification),
                        "language": language,
                        "show_archive_button": show_archive_button,
                        "request": request,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id'],
                        "data_user_id": str(user_id)
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
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                        'element_question')
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
                        datetime_field = HelperData.convert_datetime_to_date_and_time(str(nt.created_at))
                        nt.date_field = datetime_field['date_field']
                        nt.time_field = datetime_field['time_field']
                        if nt.type == 'session_attend' or nt.type == 'session':
                            try:
                                match = re.finditer("session_id:\d+", nt.message)
                                for q in match:
                                    s_id = q.group().split(':')[1]
                                    try:
                                        session_data = Session.objects.values('id', 'name').get(id=s_id)
                                        session_msg = session_data['name']
                                    except:
                                        session_msg = ""
                                        pass
                                    nt.message = nt.message.replace("{" + q.group() + "}", session_msg)
                            except Exception as e:
                                ErrorR.efail(e)
                                pass

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
                        "element_id": element['element_id'],
                        "data_user_id": str(user_id)
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
        plugin_div = """<div class="form-plugin element form-plugin-messages" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="messages">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                user_id = request.session['event_user']['id']
                event_id = request.session['event_id']
                context = {
                    "request": request,
                    "box_id": box_id,
                    "page_id": page_id,
                    "element_id": element['element_id'],
                    "data_user_id": str(user_id)
                }
                context['photo_groups'] = None
                context['photo_per_page'] = ''
                element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                    'element_question')
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
        prev_lang = language['langkey']['photo_gallery_previous_text']
        next_lang = language['langkey']['photo_gallery_next_text']
        context = {'photo_items': photo_items, 'no_of_images': no_of_images,
                   'from': skip + 1 if all_photho_no > 0 else 0, 'to': max if max < all_photho_no else all_photho_no,
                   'all_photo_no': all_photho_no, 'prev_lang': prev_lang, 'next_lang': next_lang}
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
                ErrorR.efail(exception)
                pass
        return JsonResponse(data)

    def get_session_next_up(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-next-up" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="next-up">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                        'element_question')

                    now = HelperData.getTimezoneNow(request)
                    f = '%Y-%m-%d %H:%M:%S'
                    # now = datetime.strptime(str(time_now).split(".")[0], f)
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
                    session_link = 'True'
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
                        elif setting.element_question.question_key == 'next_up_session_details_link':
                            session_link = setting.answer
                    if disappear_after == '-1':
                        time_before = now + timedelta(minutes=int(appear_before))
                        time_after = now
                        sql = 'select DISTINCT sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                            user_id) + ' and sessions.group_id = groups.id and (sessions.start <= "' + str(
                            time_before) + '" and sessions.end > "' + str(time_after) + '")'
                    else:
                        time_before = now + timedelta(minutes=int(appear_before))
                        time_after = now - timedelta(minutes=int(disappear_after))
                        # time_before = datetime.strptime(str(time_before).split(".")[0], f)
                        # time_after = datetime.strptime(str(time_after).split(".")[0], f)
                        # Searchable removed
                        sql = 'select DISTINCT sessions.*, seminars_has_users.status from seminars_has_users, sessions, groups where seminars_has_users.session_id = sessions.id and seminars_has_users.status ="attending" and seminars_has_users.attendee_id=' + str(
                            user_id) + ' and sessions.group_id = groups.id and (sessions.start <= "' + str(
                            time_before) + '" and sessions.start >= "' + str(time_after) + '")'
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
                        "session_link": session_link,
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
                        "element_id": element['element_id'],
                        "data_user_id": str(user_id)
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
        plugin_div = """<div class="form-plugin element form-plugin-attendee-list" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="attendee-list">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                element_answers = ElementsAnswers.objects.filter(box_id=box_id, page_id=page_id).select_related(
                    'element_question')
                context = {
                    'display_total_attendees': True,
                    'display_table': True,
                    'attendees_per_page': 10
                }
                attendee_export_id = 0
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
                    elif answer.element_question.question_key == 'attendee_list_show_counting_column':
                        context['counting_column'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'attendee_export_list':
                        context['attendee_export_id'] = eval(answer.answer)
                        attendee_export_id = eval(answer.answer)
                    elif answer.element_question.question_key == 'attendee_list_show_total_attendees':
                        context['display_total_attendees'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'attendee_list_show_attendee_table':
                        context['display_table'] = eval(answer.answer)
                    elif answer.element_question.question_key == 'attendee_list_attendee_per_page':
                        context['attendees_per_page'] = int(answer.answer)
                    # elif answer.element_question.question_key == 'attendee_list_filter_id':
                    #     filter_id = eval(answer.answer)
                    #     context['filter_id'] = filter_id
                    # elif answer.element_question.question_key == 'attendee_list_selected_columns':
                    #     selected_columns_data = json.loads(answer.answer)
                    #     selected_columns = selected_columns_data['selected_sorted']
                    #     context['column_ids'] = selected_columns
                    #     col_ques = Questions.objects.filter(id__in=selected_columns).values("id", "title",
                    #                                                                         "actual_definition")
                    #     visible_columns = []
                    #     for item in selected_columns:
                    #         visible_columns.append(col_ques.get(id=item))
                    #     for ids, col_question in enumerate(visible_columns):
                    #         if col_question['actual_definition'] == None or col_question['actual_definition'] == '':
                    #             visible_columns[ids]['actual_definition'] = col_question['title'].replace(' ', '_')
                    #     context['columns'] = visible_columns

                x_y_z = 'Showing {0}-{1} from {2} data items'
                if 'attendee_list_txt_x_y_of_z' in language['langkey']:
                    x_y_z = language['langkey']['attendee_list_txt_x_y_of_z']
                    x_y_z = x_y_z.replace('{X}', '_START_').replace('{Y}', '_END_').replace('{Z}', '_TOTAL_')
                language['langkey']['attendee_list_txt_x_y_of_z'] = x_y_z
                context['language'] = language

                if attendee_export_id != 0:
                    context["page_id"] = page_id
                    context["box_id"] = box_id
                    context["element_id"] = element['element_id']
                    context["data_user_id"] = str(request.session['event_user']['id'])

                    return render_to_string('public/element/attendee_list.html', context)
                else:
                    return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                        language['langkey']['attendee_list_txt_empty'])
            else:
                return ''
                # return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                #     language['langkey']['attendee_list_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['attendee_list_txt_misconfigured'])

    def get_attendee_plugin_data(request, *args, **kwargs):
        response_data = {}
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                # selected_columns = request.POST.get('column_ids')
                # filter_id = request.POST.get('filter_id')
                attendee_export_id = request.POST.get('attendee_export_id')
                show_counting_column_header = request.POST.get('show_counting_column_header')
                show_counting_column = request.POST.get('show_counting_column')
                show_counting_column = eval(show_counting_column) if show_counting_column else False
                # column_ids = json.loads(selected_columns)

                export_rule = ExportRule.objects.filter(id=attendee_export_id)
                table_headers = []
                filter_id = 0
                # preset_data = None
                general_ques = []
                question_ids = []
                sessions = []
                hotels = []
                max_booking_number = 1
                max_actual_room_buddy = 1
                if export_rule:
                    preset_data = json.loads(export_rule[0].preset)
                    filter_id = preset_data['rule_id']
                    question_ids = preset_data['questions'].split(',')
                    if '' in question_ids:
                        question_ids.remove('')
                    question_ids = [int(c_i) for c_i in question_ids]

                    if preset_data.get('uid'):
                        general_ques.append('uid')
                        table_headers.append('Uid')
                    if preset_data.get('rdate'):
                        general_ques.append('att-reg-date')
                        table_headers.append('Registration')
                    if preset_data.get('udate'):
                        general_ques.append('att-update')
                        table_headers.append('Updated')
                    if preset_data.get('secret'):
                        general_ques.append('uid-secret')
                        table_headers.append('UID-External')
                    if preset_data.get('bid'):
                        general_ques.append('bid')
                        table_headers.append('BID-Badge')
                    if preset_data.get('attGroup'):
                        general_ques.append('att-grp')
                        table_headers.append('Group')
                    if preset_data.get('attTag'):
                        general_ques.append('att-tag')
                        table_headers.append('Tags')

                    sessions = preset_data['sessions'].split(',')
                    if '' in sessions:
                        sessions.remove('')
                    hotels = preset_data.get('hotel_columns')
                if filter_id != 0:
                    attendees = AttendeePluginList.get_all_attendee(request, filter_id)

                    if hotels not in [None, '']:
                        max_b_number_obj = Booking.objects.filter(attendee_id__in=attendees).values(
                            'attendee_id').annotate(
                            total=Count('attendee_id')).aggregate(max_booking_number=Max('total'))
                        if max_b_number_obj['max_booking_number']:
                            max_booking_number = max_b_number_obj['max_booking_number']
                        if 'rba-col' in hotels or 'rba-checkin-col' in hotels or 'rba-checkout-col' in hotels:
                            match_ids = MatchLine.objects.filter(booking__attendee_id__in=attendees).values('match_id')
                            max_a_room_bud = MatchLine.objects.filter(match_id__in=match_ids).values(
                                'match_id').annotate(total=Count('match_id')).aggregate(max_total=Max('total'))
                            if max_a_room_bud['max_total']:
                                max_actual_room_buddy = max_a_room_bud['max_total'] - 1

                    attendee_data = AttendeePluginList.get_attendee(request, attendees, general_ques, question_ids,
                                                                    sessions, hotels, max_booking_number,
                                                                    max_actual_room_buddy)

                    for column_id in question_ids:
                        question = Questions.objects.get(id=column_id)
                        question = LanguageKey.get_question_data_by_language(request, question)
                        table_headers.append(question.title)

                    for session in sessions:
                        sn_obj = Session.objects.filter(id=session).first()
                        table_headers.append(sn_obj.name if sn_obj else '')

                    if hotels not in [None, '']:
                        for max_booking_i in range(0, max_booking_number):
                            if 'booking-id-col' in hotels:
                                table_headers.append('Booking-Id')
                            if 'match-id-col' in hotels:
                                table_headers.append('Match-Id')
                            if 'hotel-name-col' in hotels:
                                table_headers.append('Hotel')
                            if 'description-col' in hotels:
                                table_headers.append('Description')
                            if 'room-id-col' in hotels:
                                table_headers.append('Room-Id')
                            if 'check-in-col' in hotels:
                                table_headers.append('Check-in')
                            if 'check-out-col' in hotels:
                                table_headers.append('Check-out')
                            if 'beds-col' in hotels:
                                table_headers.append('Beds')
                            if 'location-col' in hotels:
                                table_headers.append('Location')
                            if 'rbr-col' in hotels:
                                table_headers.append('Requested room buddy')
                            for i in range(0, max_actual_room_buddy):
                                if 'rba-col' in hotels:
                                    table_headers.append('Actual room buddy')
                                if 'rba-checkin-col' in hotels:
                                    table_headers.append('Actual room buddy check-in')
                                if 'rba-checkout-col' in hotels:
                                    table_headers.append('Actual room buddy check-out')
                    context = {}
                    context["attendee_datas"] = attendee_data
                    context["column_names"] = table_headers
                    context["show_counting_column_header"] = show_counting_column_header
                    context["show_counting_column"] = show_counting_column
                    html = render_to_string('public/element/attendee_list_partial.html', context)
                    response_data['status'] = True
                    response_data['html'] = html
                else:
                    response_data['status'] = True
            else:
                response_data['status'] = False
        except Exception as e:
            ErrorR.efail(e)
            response_data['status'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_attendee_plugin_data_2(request, *args, **kwargs):
        response_data = {}
        event_id = request.session['event_id']
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                attendee_export_id = request.POST.get('attendee_export_id')
                export_rule = ExportRule.objects.filter(id=attendee_export_id)
                show_counting_column_header = request.POST.get('show_counting_column_header')
                show_counting_column = request.POST.get('show_counting_column')
                show_counting_column = eval(show_counting_column) if show_counting_column else False
                filter_id = 0
                json_data = []
                general_ques = []
                table_headers = []
                session_headers = []
                hotel_headers = []
                economy_headers = []
                question_ids = []
                sessions = []
                hotels = []
                max_booking_number = 1
                max_actual_room_buddy = 1
                if export_rule:
                    preset_data = json.loads(export_rule[0].preset)
                    filter_id = preset_data['rule_id']
                    question_ids = preset_data['questions'].split(',')
                    if '' in question_ids:
                        question_ids.remove('')
                    question_ids = [int(c_i) for c_i in question_ids]
                    questions = Questions.objects.filter(id__in=question_ids).order_by('id')

                    if preset_data.get('uid'):
                        general_ques.append('uid')
                    if preset_data.get('rdate'):
                        general_ques.append('rdate')
                    if preset_data.get('udate'):
                        general_ques.append('udate')
                    if preset_data.get('secret'):
                        general_ques.append('secret')
                    if preset_data.get('bid'):
                        general_ques.append('bid')
                    if preset_data.get('attGroup'):
                        general_ques.append('att_grp')
                    if preset_data.get('attTag'):
                        general_ques.append('att_tag')

                    if 'sessions' in preset_data:
                        sessions = preset_data['sessions'].split(',')
                        for session in sessions:
                            if session != '':
                                sn_obj = Session.objects.filter(id=session).first()
                                session_headers.append(sn_obj.name if sn_obj else '')

                    attendees = []
                    if 'hotel_columns' in preset_data:
                        hotels = preset_data.get('hotel_columns')
                        attendees = AttendeePluginList.get_all_attendee(request, filter_id)
                        if hotels not in [None, '']:
                            max_b_number_obj = Booking.objects.filter(attendee_id__in=attendees).values(
                                'attendee_id').annotate(
                                total=Count('attendee_id')).aggregate(max_booking_number=Max('total'))
                            if max_b_number_obj['max_booking_number']:
                                max_booking_number = max_b_number_obj['max_booking_number']
                            if 'rba-col' in hotels or 'rba-checkin-col' in hotels or 'rba-checkout-col' in hotels:
                                match_ids = MatchLine.objects.filter(booking__attendee_id__in=attendees).values(
                                    'match_id')
                                max_a_room_bud = MatchLine.objects.filter(match_id__in=match_ids).values(
                                    'match_id').annotate(total=Count('match_id')).aggregate(max_total=Max('total'))
                                if max_a_room_bud['max_total']:
                                    max_actual_room_buddy = max_a_room_bud['max_total'] - 1

                            for max_booking_i in range(0, max_booking_number):
                                if 'booking-id-col' in hotels:
                                    hotel_headers.append('Booking-Id')
                                if 'match-id-col' in hotels:
                                    hotel_headers.append('Match-Id')
                                if 'hotel-name-col' in hotels:
                                    hotel_headers.append('Hotel')
                                if 'description-col' in hotels:
                                    hotel_headers.append('Description')
                                if 'room-id-col' in hotels:
                                    hotel_headers.append('Room-Id')
                                if 'check-in-col' in hotels:
                                    hotel_headers.append('Check-in')
                                if 'check-out-col' in hotels:
                                    hotel_headers.append('Check-out')
                                if 'beds-col' in hotels:
                                    hotel_headers.append('Beds')
                                if 'location-col' in hotels:
                                    hotel_headers.append('Location')
                                if 'rbr-col' in hotels:
                                    hotel_headers.append('Requested room buddy')
                                for i in range(0, max_actual_room_buddy):
                                    if 'rba-col' in hotels:
                                        hotel_headers.append('Actual room buddy')
                                    if 'rba-checkin-col' in hotels:
                                        hotel_headers.append('Actual room buddy check-in')
                                    if 'rba-checkout-col' in hotels:
                                        hotel_headers.append('Actual room buddy check-out')

                    if 'economy_columns' in preset_data:
                        economy_columns = preset_data.get('economy_columns')
                        max_attendee_orders = 1
                        event_economy_vats = []
                        if not attendees:
                            attendees = AttendeePluginList.get_all_attendee(request, filter_id)
                        max_order_counter_obj = Orders.objects.filter(attendee_id__in=attendees).values(
                            'attendee_id').annotate(total=Count(
                            'attendee_id')).aggregate(max_order_counter=Max('total'))
                        if max_order_counter_obj["max_order_counter"]:
                            max_attendee_orders = max_order_counter_obj["max_order_counter"]

                        if "vat-xx-percent-sum" in economy_columns:
                            vat_objects = Group.objects.filter(event_id=event_id, type='payment').values('name')
                            for vat in vat_objects:
                                if vat["name"].isdigit():
                                    event_economy_vats.append(int(vat["name"]))
                            event_economy_vats.sort()

                        for i in range(0, max_attendee_orders):
                            if 'order-number' in economy_columns:
                                economy_headers.append('Order Number')
                            if 'order-status' in economy_columns:
                                economy_headers.append('Order Status')
                            if 'invoice-id' in economy_columns:
                                economy_headers.append('Invoice ID')
                            if 'invoice-date' in economy_columns:
                                economy_headers.append('Invoice Date')
                            if 'due-date' in economy_columns:
                                economy_headers.append('Due Date')
                            if 'transaction-id' in economy_columns:
                                economy_headers.append('Transaction ID')
                            if 'transaction-date' in economy_columns:
                                economy_headers.append('Transaction Date')
                            if 'paid-by-card-invoice' in economy_columns:
                                economy_headers.append('Paid by Card / Invoice')
                            if 'vat-xx-percent-sum' in economy_columns:
                                for vat in event_economy_vats:
                                    economy_headers.append("{}%".format(vat))
                            if 'vat-total-sum' in economy_columns:
                                economy_headers.append('VAT Total Sum')
                            if 'rebate-sum' in economy_columns:
                                economy_headers.append('Rebate Sum')
                            if 'credit-usage' in economy_columns:
                                economy_headers.append('Credit Usage')
                            if 'total-order-sum-excl-vat' in economy_columns:
                                economy_headers.append('Total Order Sum excl. VAT')
                            if 'total-order-sum-incl-vat' in economy_columns:
                                economy_headers.append('Total Order Sum incl. VAT')
                            if 'order-group-id' in economy_columns:
                                economy_headers.append('Order Group ID')

                    for q in questions:
                        table_headers.append(q.as_dict())

                    context = dict()
                    context['show_counting_column_header'] = show_counting_column_header
                    context['show_counting_column'] = show_counting_column
                    context['general_ques'] = general_ques
                    context['headers'] = table_headers
                    context['sessions'] = session_headers
                    context['hotels'] = hotel_headers
                    context['economy_headers'] = economy_headers
                    html = render_to_string('public/element/attendee_plugin_partial.html', context)

                    response_data['status'] = True
                    response_data['html'] = html
                else:
                    response_data['status'] = True
            else:
                response_data['status'] = False
        except Exception as e:
            ErrorR.efail(e)
            response_data['status'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_plugin_hotel_reservation(request, page_id, element):
        language = LanguageKey.catch_lang_key_obj(request, "hotel-reservation")
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-hotel-reservation" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="hotel-reservation">"""
        att_bookings = None
        try:
            context = {}
            context['title'] = ''
            context['message'] = ''
            context['force_default_dates'] = 'False'
            context['require_room_selection'] = 'False'
            context['force_hotel_room_type'] = 'do-not-force'
            context['optional_field_name'] = 'True'
            context['optional_field_description'] = 'True'
            context['optional_field_location'] = 'True'
            if 'is_user_login' in request.session and request.session['is_user_login']:
                existig_bookings = Booking.objects.filter(attendee_id=request.session['event_user']['id'])
                # 'done' is for checker that a booking does not appear twice (checked in js)

                att_bookings = []
                for booking in existig_bookings:
                    booking_item = {
                        'user_id': request.session['event_user']['id'],
                        'hotelroomid': booking.room_id, 'done': 'no',
                        'checkin': booking.check_in.strftime('%Y-%m-%d'),
                        'checkout': booking.check_out.strftime('%Y-%m-%d'),
                        'buddyids': []
                    }
                    for buddy in RequestedBuddy.objects.filter(booking_id=booking.id):
                        if buddy.exists:
                            booking_item['buddyids'].append(
                                {'id': buddy.buddy.id, 'text': buddy.buddy.firstname + ' ' + buddy.buddy.lastname})
                        else:
                            booking_item['buddyids'].append({'id': buddy.email, 'text': buddy.email})

                    att_bookings.append(booking_item)

                context['uid_text'] = '-u{}'.format(request.session['event_user']['id'])
            else:
                context['uid_text'] = ''

            element_answers = ElementsAnswers.objects.filter(box_id=box_id, page_id=page_id).select_related(
                'element_question')
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
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_name':
                    context['optional_field_name'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_description':
                    context['optional_field_description'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_location':
                    context['optional_field_location'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_cost_excl_vat':
                    context['optional_field_cost_excl_vat'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_cost_incl_vat':
                    context['optional_field_cost_incl_vat'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_vat_percent':
                    context['optional_field_vat_percent'] = eval(answer.answer)
                elif answer.element_question.question_key == 'hotel_reservation_optional_field_vat_amount':
                    context['optional_field_vat_amount'] = eval(answer.answer)

            context['language'] = language
            context['page_id'] = page_id
            context['element_id'] = box_id
            context['box_id'] = box_id
            context['plugin_id'] = element['element_id']
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
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
                economy_currency_lang = LanguageKey.catch_lang_key_multiple(request, 'economy',
                                                                            ['economy_txt_currency'])
                context['currency_text'] = economy_currency_lang['langkey']['economy_txt_currency']
                if hotel_group and context['force_hotel_room_type'] == 'do-not-force':
                    hotel_rooms = Room.objects.filter(hotel__group__in=json.loads(hotel_group)).order_by(
                        'hotel__group__group_order', 'room_order')
                    for h_room_item in hotel_rooms:
                        room_obj = h_room_item
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
                             'available_dates': json.dumps(room_allotmentsDates),
                             'cost_excl_vat': room_obj.cost_excluded_vat(),
                             'cost_incl_vat': room_obj.cost_included_vat(),
                             'vat_percentage': room_obj.vat, 'vat_amount': room_obj.get_vat_amount()
                             })

                    context['hotel_info'] = hotel_info
                elif context['force_hotel_room_type'] != 'do-not-force':
                    context['force_hotel_room_selection'] = True
                    hotel_room = Room.objects.filter(id=context['force_hotel_room_type'])[0]
                    room_obj = hotel_room
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
                         'available_dates': json.dumps(room_allotmentsDates),
                         'cost_excl_vat': room_obj.cost_excluded_vat(),
                         'cost_incl_vat': room_obj.cost_included_vat(),
                         'vat_percentage': room_obj.vat, 'vat_amount': room_obj.get_vat_amount()
                         }]
                if att_bookings:
                    context['bookings'] = json.dumps(att_bookings)
                    partial_allow = 0
                    for booking in att_bookings:
                        if booking['hotelroomid'] in [room['id'] for room in context['hotel_info']]:
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

    def get_applied_rebate(request, json_data):
        result = {}
        # user_id = None
        prerequisite_filter = []
        # if 'is_user_login' in request.session and request.session['is_user_login']:
        #     user_id = request.session['event_user']['id']
        answer = json_data[0]
        print(answer)
        if answer['state'] == 1:
            # p_counter = 0
            # p_length = len(answer['data'])
            # for prerequisite in answer['data']:
            #     if p_counter < p_length - 1 and user_id:
            #         filters = json.loads(RuleSet.objects.get(id=prerequisite['filter_id']).preset)
            #         q = Q()
            #         match_condition = filters[0][0]['matchFor']
            #         if match_condition == '2':
            #             q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
            #         elif match_condition == '1':
            #             q = Q(id=-11)
            #             q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
            #
            #         attendees = Attendee.objects.filter(q)
            #         att_existence = '1' if attendees.filter(id=user_id).count() > 0 else '0'
            #         if prerequisite['match'] == att_existence:
            #             result["rebate"] = prerequisite["rebate_id"]
            #             break
            #     else:
            #         result["rebate"] = prerequisite["rebate_id"]
            #
            #     p_counter = p_counter + 1
            for item in answer['data']:
                item['action'] = 'filter'
            prerequisite_filter = answer['data']
        elif answer['state'] == 2:
            p_counter = 0
            p_length = len(answer['data'])
            now = datetime.now()
            for prerequisite in answer['data']:
                if p_counter < p_length - 1:

                    from_date = datetime.strptime(prerequisite['from'], '%m/%d/%Y')
                    to_date = datetime.strptime(prerequisite['to'], '%m/%d/%Y')
                    matched = '0'
                    if from_date <= now <= to_date:
                        matched = '1'

                    if prerequisite['match'] == matched:
                        result["rebate"] = prerequisite["rebate_id"]
                        break
                else:
                    result["rebate"] = prerequisite["rebate_id"]

                p_counter = p_counter + 1

        return result, prerequisite_filter

    def get_rebates(request, page_id, element):
        box_id = element['box_id'].split('-')[1]
        # box_id=1
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
            rebate_apply = None
            for setting in element_settings:
                if setting.element_question.question_key == 'rebate_apply':
                    rebate_apply = setting.answer
            pass
            if rebate_apply is not None:
                json_data = json.loads(rebate_apply)

                # json_data = json.loads('[{"state":2,"data":[{"match":"1","from":"08/22/2017","to":"08/24/2017","rebate_id":["1","2"]},{"match":"0","from":"08/22/2017","to":"08/22/2017","rebate_id":["2","3"]},{"match":"1","from":"08/22/2017","to":"08/22/2017","rebate_id":["4"]},{"rebate_id":["5"]}]}]')

                result, prerequisite_filter = Plugins.get_applied_rebate(request, json_data)
                rebate_list = result.get('rebate')
                if prerequisite_filter:
                    prerequisite = dict(prerequisite=prerequisite_filter)
                    html = "<input type='hidden' class='order-rebate-to-apply' value='" + json.dumps(
                        prerequisite) + "'/>"
                elif rebate_list:
                    all_rebates = Rebates.objects.filter(id__in=rebate_list)

                    travel_ids = []
                    room_ids = []
                    session_ids = []
                    travel_rebates = []
                    session_rebates = []
                    room_rebates = []
                    for rebate in all_rebates:
                        rebate_id = rebate.id
                        rebate_value = rebate.value
                        rebate_type = rebate.rebate_type
                        if rebate.type_id is not None:
                            types_and_ids = json.loads(rebate.type_id)
                            # print(types_and_ids)
                            if "travels" in types_and_ids:
                                for travel in types_and_ids["travels"]:
                                    travel_ids.append(travel)
                                    rebate_info = {
                                        'rebate_id': rebate_id,
                                        'travel_id': travel,
                                        'value': rebate_value,
                                        'rebate_type': rebate_type
                                    }
                                    travel_rebates.append(rebate_info)

                            if "rooms" in types_and_ids:
                                for room in types_and_ids["rooms"]:
                                    room_ids.append(room)
                                    rebate_info = {
                                        'rebate_id': rebate_id,
                                        'room_id': room,
                                        'value': rebate_value,
                                        'rebate_type': rebate_type
                                    }
                                    room_rebates.append(rebate_info)
                            if "sessions" in types_and_ids:
                                for session in types_and_ids["sessions"]:
                                    session_ids.append(session)
                                    rebate_info = {
                                        'rebate_id': rebate_id,
                                        'name': rebate.name,
                                        'session_id': session,
                                        'value': rebate_value,
                                        'rebate_type': rebate_type
                                    }
                                    session_rebates.append(rebate_info)

                    obj = {
                        'session_ids': session_ids,
                        'travel_ids': travel_ids,
                        'room_ids': room_ids,
                        'rebates': {
                            "sessions": session_rebates,
                            "travels": travel_rebates,
                            "rooms": room_rebates
                        }
                    }
                    html = "<input type='hidden' class='order-rebate-to-apply' value='" + json.dumps(obj) + "'/>"
                else:
                    html = "<input type='hidden' class='order-rebate-to-apply' value=''/>"
            else:
                html = "<input type='hidden' class='order-rebate-to-apply' value=''/>"

        except Exception as e:
            ErrorR.efail(e)
            html = "<input type='hidden' class='order-rebate-to-apply' value=''/>"
        return html

    def get_location_list(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-location-list" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="location-list">"""
        try:
            # if 'is_user_login' in request.session and request.session['is_user_login']:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    context['data_user_id'] = str(request.session['event_user']['id'])
                return render_to_string('public/element/location_list.html', context)
            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['locationlist_txt_empty'])
                # else:
                #     return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                #         language['langkey']['locationlist_txt_empty'])
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['locationlist_txt_misconfigured'])

    def get_session_radio(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-session-radio" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-radio">"""
        try:
            # if 'is_user_login' in request.session and request.session['is_user_login']:
            event_id = request.session["event_id"]
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            cost = 'True'
            including_vat = 'True'
            count_attending = 'True'
            show_details_link = 'True'
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

                elif setting.element_question.question_key == 'session_radio_cost':
                    cost = setting.answer
                elif setting.element_question.question_key == 'session_radio_incl_vat':
                    including_vat = setting.answer
                elif setting.element_question.question_key == 'session_radio_only_count_status_attending':
                    count_attending = setting.answer
                elif setting.element_question.question_key == 'session_radio_show_link_to_session_details':
                    show_details_link = setting.answer

            if session_groups != '':
                # sessionGroups = Group.objects.filter(type="session", is_show=1, is_searchable=1,
                #                                      event_id=request.session['event_id'],
                #                                      id__in=session_groups).order_by('group_order')
                preselected_order_number = None
                # if preselected_session != '':
                #     session_info=SessionDetail.status_type_attend(request, int(preselected_session))
                #     if 'is_user_login' in request.session and request.session['is_user_login']:
                #         if session_info['success'] and session_info['status'] == 'attending':
                #             if "already_attending" not in session_info:
                #                 user_id = request.session['event_user']['id']
                #                 order_info = EconomyLibrary.place_order(event_id, user_id, 'session', int(preselected_session),
                #                                                         None, preselected_order_number, True)
                #                 preselected_order_number = order_info['order_number']
                economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                # session_details = Plugins.get_session_details(request, sessionGroups, event_id, session_option,economy_currency_txt)
                sessions = Session.objects.select_related('group').select_related('location').filter(
                    group__in=session_groups, group__type="session", group__is_show=1, group__is_searchable=1,
                    group__event_id=request.session['event_id']).order_by('group__group_order', 'session_order')
                session_details = Plugins.get_sessions_details(request, sessions, session_option, economy_currency_txt)
                session_details_lang = LanguageKey.get_session_details_lang(request)
                # # Vat Text Language update
                # lang_vat_included = session_details['session_details_lang']["langkey"]['sessiondetails_txt_session_cost_incl_vat']
                # lang_vat_included = lang_vat_included.replace("{X}","100")
                # session_details['session_details_lang']["langkey"]['sessiondetails_txt_session_cost_incl_vat'] = lang_vat_included
                #
                # lang_vat_excluded = session_details['session_details_lang']["langkey"]['sessiondetails_txt_session_cost_excl_vat']
                # lang_vat_excluded = lang_vat_excluded.replace("{X}", "100")
                # session_details['session_details_lang']["langkey"]['sessiondetails_txt_session_cost_excl_vat'] = lang_vat_excluded

                context = {
                    "title": title,
                    # "sessionGroups": list(session_details['sessionGroups']),
                    "sessionDatas": session_details,
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
                    "cost": cost,
                    "including_vat": including_vat,
                    "count_attending": count_attending,
                    "economy_currency_txt": economy_currency_txt,
                    "speaker_link": speaker_link,
                    "tags": tags,
                    "group_appear": group_appear,
                    "location": location,
                    "location_link": location_link,
                    "session_option": session_option,
                    "language": language,
                    # "session_details_language": session_details['session_details_lang'],
                    "session_details_language": session_details_lang,
                    "box_id": box_id,
                    "request": request,
                    "preselected_order_number": preselected_order_number,
                    "page_id": page_id,
                    "element_id": element['element_id'],
                    "data_session_id": '',
                    "preselected_session": preselected_session,
                    "show_details_link": show_details_link
                }

                if 'is_user_login' not in request.session or not request.session['is_user_login']:
                    # context['session_enable'] = False
                    context['session_enable'] = 'True'
                elif 'is_user_login' in request.session and request.session['is_user_login']:
                    context['data_session_id'] = "_u" + str(request.session['event_user']['id'])
                    context['data_user_id'] = str(request.session['event_user']['id'])
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
        plugin_div = """<div class="form-plugin element form-plugin-session-checkbox" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-checkbox">"""
        try:
            event_id = request.session["event_id"]
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            cost = 'True'
            including_vat = 'True'
            count_attending = 'True'
            show_details_link = 'True'
            act_like_radio_button = 'False'
            session_must_choose = 'False'
            radio_preselected_session = ''
            remove_conflict_sessions = 'False'
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
                elif setting.element_question.question_key == 'session_checkbox_cost':
                    cost = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_incl_vat':
                    including_vat = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_only_count_status_attending':
                    count_attending = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_show_link_to_session_details':
                    show_details_link = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_act_like_radio_button':
                    act_like_radio_button = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_session_must_choose':
                    session_must_choose = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_radio_preselected':
                    radio_preselected_session = setting.answer
                elif setting.element_question.question_key == 'session_checkbox_radio_remove_conflict_session':
                    remove_conflict_sessions = setting.answer
            if session_groups != '':
                preselected_order_number = None
                # sessionGroups = Group.objects.filter(type="session", is_show=1, is_searchable=1,
                #                                      event_id=request.session['event_id'],
                #                                      id__in=session_groups).order_by('group_order')
                # if preselected_session != '':
                #     for pre_session in preselected_session:
                #         session_info=SessionDetail.status_type_attend(request, int(pre_session))
                #         if 'is_user_login' in request.session and request.session['is_user_login']:
                #             if session_info['success'] and session_info['status'] == 'attending':
                #                 if "already_attending" not in session_info:
                #                     user_id = request.session['event_user']['id']
                #                     order_info = EconomyLibrary.place_order(event_id, user_id, 'session', int(pre_session),None,preselected_order_number,True)
                #                     if order_info != False:
                #                         preselected_order_number = order_info['order_number']
                #                     else:
                #                         preselected_order_number = ""
                economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                # session_details = Plugins.get_session_details(request, sessionGroups, event_id, session_option,
                #                                               economy_currency_txt)
                sessions = Session.objects.select_related('group').select_related('location').filter(
                    group__in=session_groups, group__type="session", group__is_show=1, group__is_searchable=1,
                    group__event_id=request.session['event_id']).order_by('group__group_order', 'session_order')
                session_details = Plugins.get_sessions_details(request, sessions, session_option, economy_currency_txt)
                session_details_lang = LanguageKey.get_session_details_lang(request)
                if radio_preselected_session == '' or radio_preselected_session == None:
                    radio_preselected_session = []
                else:
                    try:
                        radio_preselected_session = [int(radio_preselected_session)]
                    except Exception as e:
                        ErrorR.efail(e)
                        radio_preselected_session = []
                        pass
                context = {
                    "title": title,
                    # "sessionGroups": list(session_details['sessionGroups']),
                    "sessionDatas": session_details,
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
                    "cost": cost,
                    "including_vat": including_vat,
                    "count_attending": count_attending,
                    "economy_currency_txt": economy_currency_txt,
                    "speaker_link": speaker_link,
                    "tags": tags,
                    "group_appear": group_appear,
                    "location": location,
                    "location_link": location_link,
                    "session_option": session_option,
                    "language": language,
                    # "session_details_language": session_details['session_details_lang'],
                    "session_details_language": session_details_lang,
                    "box_id": box_id,
                    "request": request,
                    "page_id": page_id,
                    "preselected_order_number": preselected_order_number,
                    "element_id": element['element_id'],
                    "data_session_id": '',
                    "preselected_session": preselected_session,
                    "show_details_link": show_details_link,
                    "radio_preselected_session": radio_preselected_session,
                    "remove_conflict_sessions": remove_conflict_sessions
                }

                if 'is_user_login' not in request.session or not request.session['is_user_login']:
                    # context['session_enable'] = False
                    context['session_enable'] = 'True'
                elif 'is_user_login' in request.session and request.session['is_user_login']:
                    context['data_session_id'] = "_u" + str(request.session['event_user']['id'])
                    context['data_user_id'] = str(request.session['event_user']['id'])
                if act_like_radio_button == "True":
                    context['session_must_choose'] = session_must_choose
                    context['act_like_radio_button'] = act_like_radio_button
                    context['session_checkbox_class_act'] = "session-check-availability-act-radio"
                else:
                    context['session_checkbox_class_act'] = "session-check-availability"
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
        plugin_div = """<div class="form-plugin element form-plugin-login-form" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="login-form">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
            return render_to_string('public/element/email_password_verification.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['login_form_txt_misconfigured'])

    def get_request_login(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-request-login" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="request-login">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
            return render_to_string('public/element/request_login.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['request_login_txt_misconfigured'])

    def get_submit_button(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        language_id = request.session["language_id"]
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-submit-button" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="submit-button">"""
        try:
            submit_button = PluginSubmitButton.objects.get(id=int(element['button_id']))
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
            return render_to_string('public/element/submit_button.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['submit_button_txt_misconfigured'])

    def get_pdf_button(request, page_id, element):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            language = LanguageKey.get_lang_key(request, element['element_id'])
            language_id = request.session["language_id"]
            box_id = element['box_id'].split('-')[1]
            plugin_div = """<div class="form-plugin element form-plugin-pdf-button" box" id="box-""" + str(
                box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="pdf-button">"""
            try:
                pdf_button = PluginPdfButton.objects.get(id=int(element['button_id']))
                element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                    'element_question')
                title = ''
                for setting in element_settings:
                    if setting.element_question.question_key == 'pdf_button_title':
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
                    "pdf_button": pdf_button,
                    "element_id": element['element_id']
                }
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    context['data_user_id'] = str(request.session['event_user']['id'])
                return render_to_string('public/element/pdf_button.html', context)
            except Exception as e:
                ErrorR.efail(e)
                return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                    language['langkey']['pdf_button_txt_misconfigured'])
        else:
            return ''

    def get_logout(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                user_id = request.session['event_user']['id']
                element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                    'element_question')
                manual_button = 'False'
                for setting in element_settings:
                    if setting.element_question.question_key == 'attendee_logout_button':
                        manual_button = setting.answer
                context = {
                    "manual_button": manual_button,
                    "language": language,
                    "request": request,
                    "box_id": box_id,
                    "page_id": page_id,
                    "element_id": element['element_id'],
                    "data_user_id": str(user_id)
                }
                return render_to_string('public/element/attendee_logout.html', context)
            else:
                return ''
        except Exception as e:
            ErrorR.efail(e)
            return ''

    def get_photo_upload(request, page_id, element):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            language = LanguageKey.get_lang_key(request, element['element_id'])
            box_id = element['box_id'].split('-')[1]
            plugin_div = """<div class="form-plugin element form-plugin-photo-upload" box" id="box-""" + str(
                box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="photo-upload">"""
            try:
                photo_group = PhotoGroup.objects.get(id=int(element['button_id']))
                element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                    'element_question')
                message = ''
                comment = ''
                for setting in element_settings:
                    if setting.element_question.question_key == 'photo_upload_message':
                        setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                             setting.description)
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

                context['data_user_id'] = str(request.session['event_user']['id'])
                return render_to_string('public/element/photo_upload.html', context)
            except Exception as e:
                ErrorR.efail(e)
                return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                    language['langkey']['photo_upload_txt_misconfigured'])
        else:
            return ''

    def get_logout_page(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-logout" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="logout">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
            return render_to_string('public/element/logout.html', context)
        except Exception as e:
            ErrorR.efail(e)
            # return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
            # language['langkey']['photo_upload_txt_misconfigured'])

    def get_reset_password(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-reset-password" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="reset-password">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
            return render_to_string('public/element/reset_password.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['reset_password_txt_misconfigured'])

    def get_new_password(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-new-password" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="new-password">"""
        try:
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
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
            if 'is_user_login' in request.session and request.session['is_user_login']:
                context['data_user_id'] = str(request.session['event_user']['id'])
            return render_to_string('public/element/new_password.html', context)
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['new_password_txt_misconfigured'])

    def get_multiple_registration(request, page_id, element):
        has_group = True
        group_id = 0
        owner_id = 0
        group_name = ''
        updated_variable = UpdatableObj()
        event_id = request.session['event_id']
        single_user = False
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            current_attendee = Attendee.objects.get(id=attendee_id)
            owner_group = RegistrationGroupOwner.objects.filter(owner_id=attendee_id).select_related('group')
            if owner_group.exists():
                group_id = owner_group[0].group_id
                owner_id = owner_group[0].owner_id
                group_name = owner_group[0].group.name
            elif current_attendee.registration_group_id == None:
                # group_name = 'registration-group-' + str(attendee_id)
                # new_group = RegistrationGroups(name=group_name, event_id=event_id)
                # new_group.save()
                # group_id = new_group.id
                # group_owner = RegistrationGroupOwner(group_id=group_id, owner_id=attendee_id)
                # group_owner.save()
                owner_id = attendee_id
                has_group = True
                single_user = True
            else:
                has_group = False
        if has_group:
            language = LanguageKey.get_lang_key(request, element['element_id'])
            box_id = element['box_id'].split('-')[1]
            plugin_div = """<div class="form-plugin element form-plugin-multiple-registration" box" id="box-""" + str(
                box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="multiple-registration">"""
            try:
                with transaction.atomic():
                    context = {}
                    attendee_answer = {}
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                        'element_question')
                    message = ''
                    min_attendees = 1
                    max_attendees = 1
                    default_attendees = 1
                    display_form = 'loop'
                    questions_display = ''
                    number_of_attendees = 'include-owner'
                    total_attendees = 0
                    selected_columns = []
                    columns = ''
                    order_owner_page = ''
                    attendee_page = ''
                    for setting in element_settings:
                        if setting.element_question.question_key == 'multiple_registration_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            message = setting.description
                        elif setting.element_question.question_key == 'multiple_registration_min_attendees':
                            min_attendees = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_max_attendees':
                            max_attendees = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_default_attendees':
                            default_attendees = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_form':
                            display_form = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_attendee_numbers':
                            number_of_attendees = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_order_owner_page':
                            order_owner_page = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_attendee_page':
                            attendee_page = setting.answer
                        elif setting.element_question.question_key == 'multiple_registration_table_questions':
                            selected_columns_data = json.loads(json.loads(setting.answer))
                            if selected_columns_data['question'][0]['id'] != "":
                                selected_columns = selected_columns_data['question'][0]['id'].split(',')

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
                    columns = []
                    questions = Questions.objects.filter(id__in=column_ids)
                    for question in questions:
                        ques = LanguageKey.get_question_data_by_language(request, question)
                        columns.append({"id": ques.id, "title": ques.title})

                    attendee_datas = ''
                    owner_data = ''
                    is_owner = False
                    temp_attendee_array = []
                    temp_attendee_array_sess = []
                    if group_id != 0:
                        order_owner = Attendee.objects.get(id=owner_id)
                        multiple_attendees = Attendee.objects.filter(registration_group_id=group_id)
                        default_attendees = len(multiple_attendees)
                        is_owner = True
                    elif single_user:
                        order_owner = Attendee.objects.get(id=owner_id)
                        is_owner = True
                        multiple_attendees = Attendee.objects.filter(registration_group_id=group_id)
                    else:

                        order_owner = Attendee.objects.create(status="pending", event_id=event_id,
                                                              language_id=request.session['language_id'])

                        for temp_attendee in range(int(default_attendees)):
                            temp_attendee_obj = Attendee.objects.create(status="pending",
                                                                        event_id=request.session['event_id'],
                                                                        language_id=request.session['language_id'])
                            temp_attendee_array.append(temp_attendee_obj.id)
                            temp_attendee_array_sess.append(temp_attendee_obj.id)
                        multiple_attendees = Attendee.objects.filter(id__in=temp_attendee_array)
                        temp_attendee_array_sess.append(order_owner.id)
                        is_owner = False
                    attendee_datas = AttendeePluginList.get_single_attendee(request, multiple_attendees, column_ids)
                    owner_data = AttendeePluginList.get_single_attendee_data(request, order_owner, column_ids)
                    attemdees = multiple_attendees.values("id")
                    attendee_answer = AttendeePluginList.get_attendee_answer(attemdees, order_owner.id)
                    if number_of_attendees == 'include-owner':
                        total_attendees = int(default_attendees) + 1
                    else:
                        total_attendees = int(default_attendees)
                    order_owner_page_data = PageContent.objects.get(id=int(order_owner_page))
                    [owner_page, updated_variable] = DynamicPage.get_dynamic_attendee_page(request,
                                                                                           order_owner_page_data.url,
                                                                                           order_owner.id, True)
                    if display_form == 'inline':
                        multiple_attendee_html = []
                        attendee_page_data = PageContent.objects.get(id=int(attendee_page))
                        request.session["temp_inline_page_url"] = attendee_page_data.url
                        for temp_attendee in multiple_attendees:
                            [attendee_page_html, attendee_updated_variable] = DynamicPage.get_dynamic_attendee_page(
                                request, attendee_page_data.url, temp_attendee.id, True)
                            updated_variable += attendee_updated_variable
                            multiple_attendee_html.append({"user_id": temp_attendee.id, "status": temp_attendee.status,
                                                           "html": attendee_page_html})
                        updated_variable.plugin_js_need["get_multiple_registration"]["inline_registration"] = True
                    else:
                        updated_variable.plugin_js_need["get_multiple_registration"]["loop_registration"] = True
                    context["message"] = message
                    context["min_attendees"] = min_attendees
                    context["max_attendees"] = max_attendees
                    context["default_attendees"] = range(int(default_attendees))
                    context["attendees_without_owner"] = str(default_attendees)
                    context["display_form"] = display_form
                    context["order_owner_page"] = order_owner_page
                    context["attendee_page"] = attendee_page
                    context["columns"] = columns
                    context["questions_display"] = questions_display
                    context["attendee_answer"] = json.dumps(attendee_answer)
                    if display_form == 'inline':
                        context["multiple_attendee_html"] = multiple_attendee_html
                    context["number_of_attendees"] = number_of_attendees
                    context["total_attendees"] = total_attendees
                    context["owner_page"] = owner_page
                    context["attendee_datas"] = attendee_datas
                    context["owner_data"] = owner_data
                    context["is_owner"] = is_owner
                    context["owner_id"] = owner_id
                    context["group_name"] = group_name
                    context["language"] = language
                    context["box_id"] = box_id
                    context["request"] = request
                    context["page_id"] = page_id
                    context["element_id"] = element['element_id']
                    if 'is_user_login' in request.session and request.session['is_user_login']:
                        context['data_user_id'] = str(request.session['event_user']['id'])
                    if "temp_attendee_id_array" in request.session:
                        request.session["temp_attendee_id_array"] += temp_attendee_array_sess
                    else:
                        request.session["temp_attendee_id_array"] = temp_attendee_array_sess
                    request.session.modified = True

                    return [render_to_string('public/element/multiple_registration.html', context), updated_variable]
            except Exception as e:
                ErrorR.efail(e)
                return [plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                    language['langkey']['multiple_registration_misconfigured']), updated_variable]

        else:
            return ['', updated_variable]

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
        plugin_div = """<div class="form-plugin element form-plugin-session-scheduler" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-scheduler">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    event = Events.objects.get(id=event_id)
                    element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                        'element_question')
                    browsing_modes = []
                    element_settings_info = {}
                    groups = []
                    session_option = ''
                    session_scheduler_messages = ''
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
                    session_scheduler_session_cost = ''
                    session_scheduler_session_incl_vat = ''
                    group_length = 1
                    for setting in element_settings:
                        if setting.element_question.question_key == 'session_scheduler_message':
                            element_settings_info[
                                setting.element_question.question_key] = LanguageKey.get_plugin_description_by_language(
                                request,
                                setting.description)
                            session_scheduler_messages = element_settings_info[setting.element_question.question_key]
                        elif setting.element_question.question_key == 'session_scheduler_session_enable':
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

                        elif setting.element_question.question_key == 'session_scheduler_session_cost':

                            if setting.answer == 'True':
                                session_scheduler_session_cost = True
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                session_scheduler_session_cost = False
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_scheduler_session_incl_vat':

                            if setting.answer == 'True':
                                session_scheduler_session_incl_vat = True
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                session_scheduler_session_incl_vat = False
                                element_settings_info[setting.element_question.question_key] = False

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
                    economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                    session_details_lang = LanguageKey.get_session_details_lang(request)
                    context = {
                        "messages": messages,
                        "session_scheduler_messages": session_scheduler_messages,
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
                        'session_scheduler_session_cost': session_scheduler_session_cost,
                        'session_scheduler_session_incl_vat': session_scheduler_session_incl_vat,
                        "element_settings_info": json.dumps(element_settings_info),
                        "language": lang,
                        "box_id": box_id,
                        "page_id": page_id,
                        "economy_currency_txt": economy_currency_txt,
                        "element_id": element['element_id'],
                        "request": request,
                        "session_scheduler_column_session_group_available_in_agenda_view": session_scheduler_column_session_group_available_in_agenda_view,
                        "session_scheduler_column_date_available_in_agenda_view": session_scheduler_column_date_available_in_agenda_view,
                        "session_scheduler_column_time_available_in_agenda_view": session_scheduler_column_time_available_in_agenda_view,
                        "session_scheduler_one_hour_height": str(session_scheduler_one_hour_height) + "px",
                        "session_scheduler_width": str(session_scheduler_width) + "px",
                        "session_scheduler_disable_grouping": session_scheduler_disable_grouping,
                        "data_user_id": str(user_id),
                        "session_details_language": session_details_lang
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

    def get_session_agenda(request, page_id, element):
        lang = LanguageKey.get_lang_key(request, element['element_id'])
        session_details_lang = LanguageKey.get_session_details_lang(request)
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-session-agenda" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="session-agenda">"""
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    event = Events.objects.get(id=event_id)
                    element_settings = ElementsAnswers.objects.select_related('element_question').filter(
                        page_id=page_id, box_id=box_id)
                    browsing_modes = []
                    element_settings_info = {}
                    groups = []
                    session_option = 'x'
                    session_agenda_message = ''
                    session_agenda_session_start_time = ''
                    session_agenda_session_start_date = ''
                    session_agenda_session_end_time = ''
                    session_agenda_session_end_date = ''
                    session_agenda_session_rvsp_date = ''
                    session_agenda_session_speaker = ''
                    session_agenda_session_link_speaker = ''
                    session_agenda_session_tags = ''
                    session_agenda_session_session_groups = ''
                    session_agenda_session_location = ''
                    session_agenda_session_limk_location = ''
                    session_agenda_column_session_group_available_in_agenda_view = ''
                    session_agenda_column_date_available_in_agenda_view = ''
                    session_agenda_column_time_available_in_agenda_view = ''
                    session_agenda_session_cost = ''
                    session_agenda_session_incl_vat = ''
                    group_length = 1
                    start_date_at = str(event.start)
                    start_time_at = '12:00 AM'
                    end_time_at = '11:59 PM'
                    start_time = datetime.strptime(start_time_at, '%I:%M %p')
                    start_time = datetime.strftime(start_time, '%H:%M:%S')
                    end_time = datetime.strptime(end_time_at, '%I:%M %p')
                    end_time = datetime.strftime(end_time, '%H:%M:%S')
                    start_date = datetime.strptime(start_date_at, '%Y-%m-%d')
                    start_date = datetime.strftime(start_date, "%Y-%m-%d")
                    session_agenda_searchable = ''
                    session_agenda_display_today = False
                    session_agenda_sort_on = ['time', 'group', 'name']
                    search_group_name = False
                    search_session_name = False
                    search_tag_name = False
                    search_speaker_name = False
                    only_display_attendees_sessions = False
                    element_settings_info['session_agenda_date_range_start'] = str(event.start)
                    element_settings_info['session_agenda_date_range_end'] = str(event.end)
                    element_settings_info['session_agenda_default_browse_date'] = str(event.start)
                    element_settings_info['session_agenda_session_enable'] = True
                    element_settings_info['session_agenda_day_starts_at'] = start_time_at
                    element_settings_info['session_agenda_day_ends_at'] = end_time_at
                    element_settings_info['session_agenda_show_toolbar_today_button'] = True
                    element_settings_info['session_agenda_show_toolbar_currently_selected_date'] = True
                    element_settings_info['session_agenda_show_toolbar_move_day_forward_or_backwards_buttons'] = True
                    element_settings_info['session_agenda_show_all_or_my_sessions'] = True
                    element_settings_info['session_agenda_show_subscribe_to_calender'] = False
                    element_settings_info['session_agenda_show_session_group_toggle'] = False
                    element_settings_info['session_agenda_session_groups'] = groups
                    element_settings_info['session_agenda_view_sort_on'] = session_agenda_sort_on
                    element_settings_info['session_agenda_column_session_group_available_in_agenda_view'] = True
                    element_settings_info['session_agenda_column_date_available_in_agenda_view'] = True
                    element_settings_info['session_agenda_column_time_available_in_agenda_view'] = True
                    element_settings_info['session_agenda_session_start_time'] = True
                    element_settings_info['session_agenda_session_start_date'] = True
                    element_settings_info['session_agenda_session_end_time'] = True
                    element_settings_info['session_agenda_session_end_date'] = True
                    element_settings_info['session_agenda_session_rvsp_date'] = True
                    element_settings_info['session_agenda_session_speaker'] = False
                    element_settings_info['session_agenda_session_link_speaker'] = False
                    element_settings_info['session_agenda_session_tags'] = False
                    element_settings_info['session_agenda_session_session_groups'] = False
                    element_settings_info['session_agenda_session_location'] = False
                    element_settings_info['session_agenda_session_limk_location'] = False
                    element_settings_info['session_agenda_session_available'] = 'X'
                    element_settings_info['session_agenda_session_cost'] = False
                    element_settings_info['session_agenda_session_incl_vat'] = False
                    element_settings_info['session_agenda_searchable'] = False
                    element_settings_info['session_agenda_display_today'] = False
                    element_settings_info['session_agenda_only_display_attendees_sessions'] = False
                    for setting in element_settings:
                        if setting.element_question.question_key == 'session_agenda_message':
                            element_settings_info[
                                setting.element_question.question_key] = LanguageKey.get_plugin_description_by_language(
                                request,
                                setting.description)
                            session_agenda_message = element_settings_info[setting.element_question.question_key]
                        elif setting.element_question.question_key == 'session_agenda_session_enable':
                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False


                        elif setting.element_question.question_key == 'session_agenda_session_groups':

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

                        elif setting.element_question.question_key == 'session_agenda_date_range_start':
                            if setting.answer:
                                date = datetime.strptime(setting.answer, '%m/%d/%Y')
                                date = datetime.strftime(date, "%Y-%m-%d")
                                element_settings_info[setting.element_question.question_key] = str(date)
                            else:
                                element_settings_info[setting.element_question.question_key] = str(event.start)

                        elif setting.element_question.question_key == 'session_agenda_date_range_end':
                            if setting.answer:
                                date = datetime.strptime(setting.answer, '%m/%d/%Y')
                                date = datetime.strftime(date, "%Y-%m-%d")
                                element_settings_info[setting.element_question.question_key] = str(date)
                            else:
                                element_settings_info[setting.element_question.question_key] = str(event.end)

                        elif setting.element_question.question_key == 'session_agenda_default_browse_date':

                            if setting.answer:
                                element_settings_info[setting.element_question.question_key] = setting.answer
                                start_date = datetime.strptime(setting.answer, '%m/%d/%Y')
                                start_date = datetime.strftime(start_date, "%Y-%m-%d")
                                # start_date_at = setting.answer
                                start_date_at = str(start_date)
                                # start += str(start_date)
                            else:
                                element_settings_info[setting.element_question.question_key] = str(event.start)
                                # start += str(event.start)
                                start_date_at = str(event.start)

                        # elif setting.element_question.question_key == 'session_agenda_day_starts_at':
                        #     if setting.answer:
                        #         element_settings_info[setting.element_question.question_key] = setting.answer
                        #         # start += ' ' + setting.answer
                        #         start_time_at = setting.answer
                        #         start_time = datetime.strptime(setting.answer, '%I:%M %p')
                        #         start_time = datetime.strftime(start_time, '%H:%M:%S')
                        #     else:
                        #         element_settings_info[setting.element_question.question_key] = '10:00 AM'
                        #         # start += ' ' + '10:00 AM'
                        #         start_time_at = '10:00 AM'
                        #         start_time = datetime.strptime('10:00 AM', '%I:%M %p')
                        #         start_time = datetime.strftime(start_time, '%H:%M:%S')
                        #
                        # elif setting.element_question.question_key == 'session_agenda_day_ends_at':
                        #
                        #     if setting.answer:
                        #         element_settings_info[setting.element_question.question_key] = setting.answer
                        #         end_time = datetime.strptime(setting.answer, '%I:%M %p')
                        #         end_time = datetime.strftime(end_time, '%H:%M:%S')
                        #         end_time_at = setting.answer
                        #     else:
                        #         element_settings_info[setting.element_question.question_key] = '05:00 PM'
                        #         end_time = datetime.strptime('05:00 PM', '%I:%M %p')
                        #         end_time = datetime.strftime(end_time, '%H:%M:%S')
                        #         end_time_at = '05:00 PM'

                        elif setting.element_question.question_key == 'session_agenda_show_toolbar_today_button':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_show_toolbar_currently_selected_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_show_toolbar_move_day_forward_or_backwards_buttons':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_show_all_or_my_sessions':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_show_subscribe_to_calender':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_show_session_group_toggle':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_column_session_group_available_in_agenda_view':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_column_session_group_available_in_agenda_view = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_column_session_group_available_in_agenda_view = False

                        elif setting.element_question.question_key == 'session_agenda_column_date_available_in_agenda_view':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_column_date_available_in_agenda_view = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_column_date_available_in_agenda_view = False

                        elif setting.element_question.question_key == 'session_agenda_column_time_available_in_agenda_view':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_column_time_available_in_agenda_view = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_column_time_available_in_agenda_view = False

                        elif setting.element_question.question_key == 'session_agenda_view_sort_on':
                            try:
                                if setting.answer != '':
                                    session_agenda_sort_on = eval(setting.answer)
                            except Exception as e:
                                ErrorR.efail(e)
                            element_settings_info[setting.element_question.question_key] = session_agenda_sort_on

                        elif setting.element_question.question_key == 'session_agenda_session_start_time':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_start_time = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_start_time = False

                        elif setting.element_question.question_key == 'session_agenda_session_start_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_start_date = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_start_date = False

                        elif setting.element_question.question_key == 'session_agenda_session_end_time':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_end_time = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_end_time = False

                        elif setting.element_question.question_key == 'session_agenda_session_end_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_end_date = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_end_date = False

                        elif setting.element_question.question_key == 'session_agenda_session_rvsp_date':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_rvsp_date = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_rvsp_date = False

                        elif setting.element_question.question_key == 'session_agenda_session_speaker':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_speaker = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_speaker = False

                        elif setting.element_question.question_key == 'session_agenda_session_link_speaker':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_link_speaker = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_link_speaker = False

                        elif setting.element_question.question_key == 'session_agenda_session_tags':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_tags = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_tags = False

                        elif setting.element_question.question_key == 'session_agenda_session_session_groups':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_session_groups = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_session_groups = False

                        elif setting.element_question.question_key == 'session_agenda_session_location':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_location = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_location = False

                        elif setting.element_question.question_key == 'session_agenda_session_limk_location':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_session_limk_location = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_session_limk_location = False

                        elif setting.element_question.question_key == 'session_agenda_session_available':

                            element_settings_info[setting.element_question.question_key] = setting.answer
                            session_option = setting.answer

                        elif setting.element_question.question_key == 'session_agenda_width':

                            element_settings_info[setting.element_question.question_key] = setting.answer

                        elif setting.element_question.question_key == 'session_agenda_title':

                            element_settings_info[setting.element_question.question_key] = setting.answer

                        elif setting.element_question.question_key == 'session_agenda_message':
                            setting.description = LanguageKey.get_plugin_description_by_language(request,
                                                                                                 setting.description)
                            element_settings_info[setting.element_question.question_key] = setting.description

                        elif setting.element_question.question_key == 'session_agenda_session_cost':

                            if setting.answer == 'True':
                                session_agenda_session_cost = True
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                session_agenda_session_cost = False
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_session_incl_vat':
                            if setting.answer == 'True':
                                session_agenda_session_incl_vat = True
                                element_settings_info[setting.element_question.question_key] = True
                            else:
                                session_agenda_session_incl_vat = False
                                element_settings_info[setting.element_question.question_key] = False

                        elif setting.element_question.question_key == 'session_agenda_searchable':

                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_searchable = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_searchable = False

                        elif setting.element_question.question_key == 'session_agenda_searchable_property':
                            searchable_property = setting.answer
                            element_settings_info[setting.element_question.question_key] = searchable_property
                            if 'group_name' in searchable_property:
                                search_group_name = True
                            if 'name' in searchable_property:
                                search_session_name = True
                            if 'tag' in searchable_property:
                                search_tag_name = True
                            if 'speaker' in searchable_property:
                                search_speaker_name = True

                        elif setting.element_question.question_key == 'session_agenda_display_today':
                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                session_agenda_display_today = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                session_agenda_display_today = False

                        elif setting.element_question.question_key == 'session_agenda_only_display_attendees_sessions':
                            if setting.answer == 'True':
                                element_settings_info[setting.element_question.question_key] = True
                                only_display_attendees_sessions = True
                            else:
                                element_settings_info[setting.element_question.question_key] = False
                                only_display_attendees_sessions = False

                    start = start_date_at + ' ' + start_time_at
                    sDate = datetime.strptime(start, "%Y-%m-%d %I:%M %p")
                    end_t = datetime.strftime(sDate, "%Y-%m-%d")
                    end_t = str(end_t) + ' ' + end_time
                    eDate = datetime.strptime(end_t, "%Y-%m-%d %H:%M:%S")
                    if session_agenda_display_today:
                        time_now = HelperData.getTimezoneNow(request)
                        time_now_date = time_now.date()
                        time_now_start = datetime.strftime(time_now_date, "%Y-%m-%d") + ' ' + start_time
                        time_now_end = datetime.strftime(time_now_date, "%Y-%m-%d") + ' ' + end_time
                        time_now_start = datetime.strptime(time_now_start, "%Y-%m-%d %H:%M:%S")
                        time_now_end = datetime.strptime(time_now_end, "%Y-%m-%d %H:%M:%S")
                        if Session.objects.filter(start__range=(time_now_start, time_now_end), group__event_id=event_id,
                                                  group__in=groups).exists():
                            sDate = time_now_start
                            eDate = time_now_end

                    # raw_sql = "SELECT * FROM sessions WHERE start BETWEEN '" + str(
                    #     sDate) + "' and '"+str(eDate)+"' and CAST(start AS TIME) BETWEEN '" + str(start_time) + "' and '" + str(
                    #     end_time) + "'"
                    # sessions_ids = []
                    # sessions_list = Session.objects.raw(raw_sql)
                    # for session in sessions_list:
                    #     sessions_ids.append(session.id)

                    group_list = Group.objects.filter(id__in=groups)
                    for group in group_list:
                        group = LanguageKey.get_group_data_by_language(request, group)

                    # grp_data = group_list
                    # session_length = 0
                    sort_by_array = []
                    for sort_key in session_agenda_sort_on:
                        if sort_key == 'time':
                            sort_by_array.append('start')
                            sort_by_array.append('end')
                        elif sort_key == 'group':
                            sort_by_array.append('group__name')
                        elif sort_key == 'name':
                            sort_by_array.append('name')

                    # if session_agenda_disable_grouping == False:
                    #     for group in grp_data:
                    #         group.sessions = Session.objects.filter(group_id=group.id,start__range=(sDate,eDate)).order_by('start')
                    #         group.sessions = Plugins.get_sessions_details(request,group.sessions,page_id,box_id)
                    #         session_length += len(group.sessions)
                    # else:
                    if only_display_attendees_sessions:
                        grp_data = Session.objects.select_related('group').select_related('location').filter((Q((Q(seminarsusers__status='attending') | Q(seminarsusers__status='in-queue') | Q(seminarsusers__status='deciding')), seminarsusers__attendee_id=user_id) | Q(seminarspeakers__speaker_id=user_id)))\
                            .filter(group__in=groups, start__range=(sDate, eDate)).order_by(*sort_by_array).distinct()
                    else:
                        grp_data = Session.objects.select_related('group').select_related('location').filter(
                            group__in=groups, start__range=(sDate, eDate)).order_by(*sort_by_array)
                    economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                    grp_data = Plugins.get_sessions_details(request, grp_data, session_option, economy_currency_txt)
                    session_length = len(grp_data)
                    economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                    sessions_data = grp_data
                    context = {
                        # "messages": messages,
                        "session_agenda_message": session_agenda_message,
                        'sessions_data': sessions_data,
                        'session_group_list': group_list,
                        'session_agenda_session_start_time': session_agenda_session_start_time,
                        'session_agenda_session_start_date': session_agenda_session_start_date,
                        'session_agenda_session_end_time': session_agenda_session_end_time,
                        'session_agenda_session_end_date': session_agenda_session_end_date,
                        'session_agenda_session_rvsp_date': session_agenda_session_rvsp_date,
                        'session_agenda_session_speaker': session_agenda_session_speaker,
                        'session_agenda_session_link_speaker': session_agenda_session_link_speaker,
                        'session_agenda_session_tags': session_agenda_session_tags,
                        'session_agenda_session_session_groups': session_agenda_session_session_groups,
                        'session_agenda_session_location': session_agenda_session_location,
                        'session_agenda_session_limk_location': session_agenda_session_limk_location,
                        'session_agenda_session_cost': session_agenda_session_cost,
                        'session_agenda_session_incl_vat': session_agenda_session_incl_vat,
                        "element_settings_info": json.dumps(element_settings_info),
                        "element_settings": element_settings_info,
                        "language": lang,
                        "box_id": box_id,
                        "page_id": page_id,
                        "element_id": element['element_id'],
                        "economy_currency_txt": economy_currency_txt,
                        "request": request,
                        "session_agenda_column_session_group_available_in_agenda_view": session_agenda_column_session_group_available_in_agenda_view,
                        "session_agenda_column_date_available_in_agenda_view": session_agenda_column_date_available_in_agenda_view,
                        "session_agenda_column_time_available_in_agenda_view": session_agenda_column_time_available_in_agenda_view,
                        "data_user_id": str(user_id),
                        "sdate": sDate,
                        "edate": eDate,
                        "session_length": session_length,
                        "search_group_name": search_group_name,
                        "search_session_name": search_session_name,
                        "search_tag_name": search_tag_name,
                        "search_speaker_name": search_speaker_name,
                        "session_details_language": session_details_lang
                    }
                    return render_to_string('public/element/session_agenda.html', context)
                else:
                    return ''
            else:
                return ""
        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                lang['langkey']['session_agenda_txt_misconfigured'])

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
        session_option = element_settings[0].answer
        # response_data = Plugins.get_sessions_details(request, sessions,element_settings[0].answer)
        if len(list(sessions)) > 0:
            all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
            economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
            economy_cost = LanguageKey.catch_lang_key_multiple(request, 'economy', ['economy_txt_cost_excl_vat',
                                                                                    'economy_txt_cost_incl_vat'])
            economy_lang = {
                "economy_currency_txt": economy_currency_txt,
                "economy_cost": economy_cost
            }
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
                status = "not-answered"
                has_conflict = False
                tags = SessionTags.objects.filter(session_id=session.id)
                taglist = []
                for tag in tags:
                    taglist.append(tag.tag.name)

                speakers = SeminarSpeakers.objects.filter(session_id=id)
                speakersData = []
                if speakers.count() > 0:
                    for speaker in speakers:
                        status = 'attending'
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
                # session_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id, session_id=session.id)
                if session_attendee.count() > 0:
                    if session_attendee[0].status == 'attending':
                        status = "attending"
                    elif session_attendee[0].status == 'in-queue':
                        status = "in-queue"
                    elif session_attendee[0].status == 'deciding':
                        status = "deciding"
                    elif session_attendee[0].status == 'not-attending':
                        is_clash = Plugins.check_session_clash(attendee_id, session)
                        # session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                        #                                                    status="attending",
                        #                                                    session__allow_overlapping=0) & (
                        #                                                      Q(session__start__lte=session.start,
                        #                                                        session__end__gt=session.start) | Q(
                        #                                                          session__start__lt=session.end,
                        #                                                          session__end__gte=session.end)))

                        if is_clash:
                            has_conflict = True
                        status = 'not-attending'
                else:
                    is_clash = Plugins.check_session_clash(attendee_id, session)
                    # session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                    #                                                    status="attending",
                    #                                                    session__allow_overlapping=0) & (
                    #                                                      Q(session__start__lte=session.start,
                    #                                                        session__end__gt=session.start) | Q(
                    #                                                          session__start__lt=session.end,
                    #                                                          session__end__gte=session.end)))
                    if is_clash:
                        has_conflict = True
                        # status = 'time-conflict'
                    # else:
                    status = 'not-answered'
                # if session_speaker.count() > 0:
                #     status = "attending"

                # time_now = datetime.now().date()
                # setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_id'])
                # if setting_timezone:
                #     tzname = setting_timezone[0].value
                #     timezone_active = timezone(tzname)
                #     time_now = datetime.now(timezone_active)
                #     time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
                #     time_now = datetime.strptime(time_now,"%Y-%m-%d %H:%M:%S")
                #     time_now = time_now.date()
                time_zone_time = HelperData.getTimezoneNow(request)
                time_now = time_zone_time.date()
                session_expire = False
                reg_between_end = session.reg_between_end
                if reg_between_end < time_now:
                    session_expire = True
                session = SessionSeatAvailability.get_seats_availability(request, session, session_option,
                                                                         request.session['event_id'], all_langs)
                session = SessionSeatAvailability.get_vat_lang(request, session, session_option,
                                                               request.session['event_id'], economy_lang, all_langs)
                all_session_status = []
                all_session_status.append(status)
                if full:
                    all_session_status.append("full")
                    if full_queue_open:
                        all_session_status.append("queue-open")
                if has_conflict:
                    all_session_status.append("time-conflict")
                if session_expire:
                    all_session_status.append("rsvp-ended")

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
                    'seat_availability': session.availability,
                    'lang_vat_included': session.lang_vat_included,
                    'lang_vat_excluded': session.lang_vat_excluded,
                    'cost': session.cost,
                    'cost_included_vat': session.cost_included_vat(),
                    'all_session_status': all_session_status
                }
                response_data.append(session_obj)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_sessions_details(request, sessions, session_option, economy_currency_txt):
        is_login = False
        if 'is_user_login' in request.session and request.session['is_user_login']:
            is_login = True
            attendee_id = request.session['event_user']['id']
        lang_keys = ['sessiondetails_txt_session_cost_excl_vat', 'sessiondetails_txt_session_cost_incl_vat',
                     'sessiondetails_txt_seat_availability_x_of_y', 'sessiondetails_txt_no_seats_available',
                     'sessiondetails_txt_seats_available_queue_is_open', 'sessiondetails_txt_no_seats_available',
                     'sessiondetails_txt_seats_available', 'sessiondetails_txt_few_seats_available']
        # all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
        all_langs = LanguageKey.catch_lang_key_multiple(request, 'session-details', lang_keys)
        # economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
        economy_cost = LanguageKey.catch_lang_key_multiple(request, 'economy',
                                                           ['economy_txt_cost_excl_vat', 'economy_txt_cost_incl_vat'])
        economy_lang = {
            "economy_currency_txt": economy_currency_txt,
            "economy_cost": economy_cost
        }
        # session_option = element_settings_info['session_agenda_session_available']
        # setting_timezone = Setting.objects.filter(name='timezone', event_id=request.session['event_id'])
        # all_sessions = []
        for session in sessions:
            session = LanguageKey.get_session_data_by_language(request, session)
            id = session.id
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
            # status = "not-attending"
            status = "not-answered"
            has_conflict = False
            tags = SessionTags.objects.filter(session_id=id)
            taglist = []
            for tag in tags:
                taglist.append(tag.tag.name)
            speakers = SeminarSpeakers.objects.filter(session_id=id)
            speakersData = []
            if speakers.count() > 0:
                for speaker in speakers:
                    if is_login:
                        if speaker.speaker_id == attendee_id:
                            status = "attending"
                    badge_firstname = Answers.objects.filter(question__actual_definition='firstname',
                                                             user_id=speaker.speaker_id)
                    if badge_firstname.exists():
                        firstname = badge_firstname[0].value
                    else:
                        firstname = speaker.speaker.firstname

                    badge_lastname = Answers.objects.filter(question__actual_definition='lastname',
                                                            user_id=speaker.speaker_id)
                    if badge_lastname.exists():
                        lastname = badge_lastname[0].value
                    else:
                        lastname = speaker.speaker.lastname

                    speaker_obj = {
                        'id': speaker.speaker_id,
                        'firstname': firstname,
                        'lastname': lastname
                    }
                    speakersData.append(speaker_obj)
            if is_login:
                session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=id)
                if session_attendee.count() > 0:
                    if session_attendee[0].status == 'attending':
                        status = "attending"
                    elif session_attendee[0].status == 'in-queue':
                        status = "in-queue"
                    elif session_attendee[0].status == 'deciding':
                        status = "deciding"
                    elif session_attendee[0].status == 'not-attending':
                        is_clash = Plugins.check_session_clash(attendee_id, session)
                        # session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                        #                                                    status="attending",
                        #                                                    session__allow_overlapping=0) & (
                        #                                                      Q(session__start__lte=session.start,
                        #                                                        session__end__gt=session.start) | Q(
                        #                                                          session__start__lt=session.end,
                        #                                                          session__end__gte=session.end)))

                        if is_clash:
                            has_conflict = True
                            # status = 'time-conflict'
                        # else:
                        if status != "attending":
                            status = 'not-attending'
                else:
                    is_clash = Plugins.check_session_clash(attendee_id, session)
                    # session_attending = SeminarsUsers.objects.filter(Q(attendee_id=attendee_id,
                    #                                                    status="attending",
                    #                                                    session__allow_overlapping=0) & (
                    #                                                      Q(session__start__lte=session.start,
                    #                                                        session__end__gt=session.start) | Q(
                    #                                                          session__start__lt=session.end,
                    #                                                          session__end__gte=session.end)))
                    if is_clash:
                        has_conflict = True
                        # status = 'time-conflict'
                    # else:
                    if status != "attending":
                        status = 'not-answered'
            # time_now = datetime.now().date()
            # if setting_timezone:
            #     tzname = setting_timezone[0].value
            #     timezone_active = timezone(tzname)
            #     time_now = datetime.now(timezone_active)
            #     time_now = time_now.strftime("%Y-%m-%d %H:%M:%S")
            #     time_now = datetime.strptime(time_now,"%Y-%m-%d %H:%M:%S")
            #     time_now = time_now.date()
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            session = SessionSeatAvailability.get_seats_availability(request, session, session_option,
                                                                     request.session['event_id'], all_langs)
            session = SessionSeatAvailability.get_vat_lang(request, session, session_option,
                                                           request.session['event_id'], economy_lang, all_langs)
            session.full = full
            session.session_expire = session_expire
            session.full_queue_open = full_queue_open
            session.status = status
            all_session_status = []
            all_session_status.append(status)
            if full:
                all_session_status.append("full")
                if full_queue_open:
                    all_session_status.append("queue-open")
            if has_conflict:
                all_session_status.append("time-conflict")
            if session_expire:
                all_session_status.append("rsvp-ended")
            session.all_status = all_session_status
            session.speakers = speakersData
            session.taglist = taglist
            session.cost_detail = session.get_cost_detail()
            session.cost_included_vat = session.cost_included_vat()
            current_status = None
            if status != 'not-attending' and status != 'not-answered':
                current_status = status
            elif status == "not-attending" or status == 'not-answered':
                if session_expire:
                    current_status = "rsvp-ended"
                elif has_conflict:
                    current_status = "time-conflict"
                elif full:
                    current_status = "full"
                else:
                    current_status = status
            session.is_disable = False
            # if remove_conflict_sessions:
            #     has_conflict = False
            if session_expire or has_conflict:
                session.is_disable = True
            elif full:
                if not full_queue_open:
                    session.is_disable = True
            session.current_status = current_status
            session.custom_classes = SessionClasses.objects.filter(session_id=id)
            # ErrorR.okblue(session.__dict__)
        #     session_obj = {
        #         'id': id,
        #         'name': session.name,
        #         'group_id': session.group_id,
        #         'group_name': session.group.name,
        #         'start': session.start,
        #         'end': session.end,
        #         'rsvp_date': session.reg_between_end,
        #         'allday': session.all_day,
        #         'full': full,
        #         'current_status': current_status,
        #         'full_queue_open': full_queue_open,
        #         'status': status,
        #         'custom_classes': SessionClasses.objects.filter(session_id=id),
        #         'speakers': speakersData,
        #         'taglist': taglist,
        #         'location_id': session.location_id,
        #         'location_name': session.location.name,
        #         'availability': session.availability,
        #         'cost': session.cost,
        #         'lang_vat_excluded': session.lang_vat_excluded,
        #         'lang_vat_included': session.lang_vat_included,
        #         'cost_included_vat': session.cost_included_vat
        #     }
        #     all_sessions.append(session_obj)
        # return all_sessions
        return sessions

    def get_filtered_session_agenda(request, *args, **kwargs):
        settings.USE_TZ = False
        response_data = {}
        box_id = request.POST.get('box_id')
        page_id = request.POST.get('page_id')
        element_id = request.POST.get('element_id')
        groups = []
        # groups = json.loads(request.POST.get('groups'))
        element_settings = request.POST.get('settings')
        # my_session = request.POST.get('my_session')
        # search_key = request.POST.get('search_key')
        date_range = request.POST.get('date_range')
        element_settings = json.loads(element_settings)
        session_agenda_day_starts_at = element_settings['session_agenda_day_starts_at']
        session_agenda_day_ends_at = element_settings['session_agenda_day_ends_at']

        start_time = datetime.strptime(session_agenda_day_starts_at, '%I:%M %p')
        start_time = datetime.strftime(start_time, '%H:%M:%S')

        end_time = datetime.strptime(session_agenda_day_ends_at, '%I:%M %p')
        end_time = datetime.strftime(end_time, '%H:%M:%S')

        start = date_range + ' ' + session_agenda_day_starts_at
        end = date_range + ' ' + session_agenda_day_ends_at
        sDate = datetime.strptime(start, "%m/%d/%Y %I:%M %p")
        eDate = datetime.strptime(end, "%m/%d/%Y %I:%M %p")
        lang = LanguageKey.get_lang_key(request, element_id)
        session_details_lang = LanguageKey.get_session_details_lang(request)
        search_group_name = False
        search_session_name = False
        search_tag_name = False
        search_speaker_name = False
        only_display_attendees_sessions = False

        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if request.session['event_user']['attending'] == "Yes":
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    session_agenda_session_start_time = element_settings['session_agenda_session_start_time']
                    session_agenda_session_start_date = element_settings['session_agenda_session_start_date']
                    session_agenda_session_end_time = element_settings['session_agenda_session_end_time']
                    session_agenda_session_end_date = element_settings['session_agenda_session_end_date']
                    session_agenda_session_rvsp_date = element_settings['session_agenda_session_rvsp_date']
                    session_agenda_session_speaker = element_settings['session_agenda_session_speaker']
                    session_agenda_session_link_speaker = element_settings['session_agenda_session_link_speaker']
                    session_agenda_session_tags = element_settings['session_agenda_session_tags']
                    session_agenda_session_session_groups = element_settings['session_agenda_session_session_groups']
                    session_agenda_session_location = element_settings['session_agenda_session_location']
                    session_agenda_session_limk_location = element_settings['session_agenda_session_limk_location']
                    session_agenda_column_session_group_available_in_agenda_view = element_settings[
                        'session_agenda_column_session_group_available_in_agenda_view']
                    session_agenda_column_date_available_in_agenda_view = element_settings[
                        'session_agenda_column_date_available_in_agenda_view']
                    session_agenda_column_time_available_in_agenda_view = element_settings[
                        'session_agenda_column_time_available_in_agenda_view']
                    session_agenda_session_cost = element_settings['session_agenda_session_cost']
                    session_agenda_session_incl_vat = element_settings['session_agenda_session_incl_vat']
                    session_agenda_show_session_group_toggle = element_settings[
                        'session_agenda_show_session_group_toggle']
                    session_agenda_view_sort_on = element_settings['session_agenda_view_sort_on']
                    if 'session_agenda_searchable_property' in element_settings:
                        session_agenda_searchable_property = element_settings['session_agenda_searchable_property']
                        if 'group_name' in session_agenda_searchable_property:
                            search_group_name = True
                        if 'name' in session_agenda_searchable_property:
                            search_session_name = True
                        if 'tag' in session_agenda_searchable_property:
                            search_tag_name = True
                        if 'speaker' in session_agenda_searchable_property:
                            search_speaker_name = True
                    if 'session_agenda_only_display_attendees_sessions' in element_settings:
                        if element_settings['session_agenda_only_display_attendees_sessions']:
                            only_display_attendees_sessions = True
                    visible_field = {}
                    visible_field['session_agenda_session_speaker'] = session_agenda_session_speaker
                    visible_field['session_agenda_session_tags'] = session_agenda_session_tags
                    visible_field['session_agenda_session_session_groups'] = session_agenda_session_session_groups

                    if len(groups) == 0:
                        default_groups = element_settings['session_agenda_session_groups']
                        for group in default_groups:
                            groups.append(group['value'])

                    # group_list = Group.objects.filter(id__in=groups)
                    # for group in group_list:
                    #     group = LanguageKey.get_group_data_by_language(request, group)
                    #
                    # grp_data = group_list
                    session_agenda_sort_on = ['time', 'group', 'name']
                    try:
                        if session_agenda_view_sort_on != '':
                            session_agenda_sort_on = session_agenda_view_sort_on
                    except Exception as e:
                        ErrorR.efail(e)
                    sort_by_array = []
                    for sort_key in session_agenda_sort_on:
                        if sort_key == 'time':
                            sort_by_array.append('start')
                            sort_by_array.append('end')
                        elif sort_key == 'group':
                            sort_by_array.append('group__name')
                        elif sort_key == 'name':
                            sort_by_array.append('name')

                    session_length = 0
                    # if my_session == 'false':
                    if only_display_attendees_sessions:
                        grp_data = Session.objects.filter((Q((Q(
                            seminarsusers__status='attending') | Q(seminarsusers__status='in-queue') | Q(
                            seminarsusers__status='deciding')), seminarsusers__attendee_id=user_id) | Q(
                            seminarspeakers__speaker_id=user_id))).filter(group__in=groups,start__range=(sDate,eDate)).order_by(*sort_by_array).distinct()
                    else:
                        grp_data = Session.objects.filter(group__in=groups, start__range=(sDate, eDate)).order_by(
                            *sort_by_array)
                    # if len(search_key) !=0:
                    #     grp_data = Plugins.get_searched_sessions(grp_data,session_agenda_searchable_property,search_key,visible_field)
                    economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                    grp_data = Plugins.get_sessions_details(request, grp_data,
                                                            element_settings['session_agenda_session_available'],
                                                            economy_currency_txt)
                    session_length += len(grp_data)
                    # else:
                    #     grp_data = Session.objects.filter(group__in=groups,start__range=(sDate,eDate)).order_by('name').order_by(*sort_by_array)
                    #     grp_data = grp_data.filter(Q(Q(seminarsusers__attendee_id=user_id) & Q(seminarsusers__status='attending'))| Q(seminarspeakers__speaker_id=user_id)).distinct()
                    #     if len(search_key) !=0:
                    #         grp_data = Plugins.get_searched_sessions(grp_data,session_agenda_searchable_property,search_key,visible_field)
                    #     grp_data = Plugins.get_sessions_details(request, grp_data, element_settings)
                    #     session_length += len(grp_data)
                    sessions_data = grp_data
                    economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
                    context = {
                        'sessions_data': sessions_data,
                        'session_agenda_session_start_time': session_agenda_session_start_time,
                        'session_agenda_session_start_date': session_agenda_session_start_date,
                        'session_agenda_session_end_time': session_agenda_session_end_time,
                        'session_agenda_session_end_date': session_agenda_session_end_date,
                        'session_agenda_session_rvsp_date': session_agenda_session_rvsp_date,
                        'session_agenda_session_speaker': session_agenda_session_speaker,
                        'session_agenda_session_link_speaker': session_agenda_session_link_speaker,
                        'session_agenda_session_tags': session_agenda_session_tags,
                        'session_agenda_session_session_groups': session_agenda_session_session_groups,
                        'session_agenda_session_location': session_agenda_session_location,
                        'session_agenda_session_limk_location': session_agenda_session_limk_location,
                        'session_agenda_session_cost': session_agenda_session_cost,
                        'session_agenda_session_incl_vat': session_agenda_session_incl_vat,
                        'economy_currency_txt': economy_currency_txt,
                        "language": lang,
                        "request": request,
                        "page_id": page_id,
                        "box_id": box_id,
                        "session_agenda_column_session_group_available_in_agenda_view": session_agenda_column_session_group_available_in_agenda_view,
                        "session_agenda_column_date_available_in_agenda_view": session_agenda_column_date_available_in_agenda_view,
                        "session_agenda_column_time_available_in_agenda_view": session_agenda_column_time_available_in_agenda_view,
                        "element_settings": element_settings,
                        "data_user_id": str(user_id),
                        "session_length": session_length,
                        "search_group_name": search_group_name,
                        "search_session_name": search_session_name,
                        "search_tag_name": search_tag_name,
                        "search_speaker_name": search_speaker_name,
                        "session_details_language": session_details_lang
                    }
                    session_agenda_list = render_to_string('public/element/session_agenda_list.html', context)
                    response_data['success'] = True
                    response_data['session_agenda_list'] = session_agenda_list
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data['success'] = False
            else:
                response_data['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_searched_sessions(sessions, searchable_property, key, visible_field):
        q = Q()
        if "group_name" in searchable_property and visible_field['session_agenda_session_session_groups']:
            q |= Q(group__name__icontains=key)
        if "name" in searchable_property:
            q |= Q(name__icontains=key)
        # if "description" in searchable_property:
        #     q |= Q(description__icontains=key)
        if "tag" in searchable_property and visible_field['session_agenda_session_tags']:
            q |= Q(sessiontags__tag__name__icontains=key)
        if "speaker" in searchable_property and visible_field['session_agenda_session_speaker']:
            q |= Q(seminarspeakers__speaker__firstname__icontains=key)
            q |= Q(seminarspeakers__speaker__lastname__icontains=key)
        data = sessions.filter(q).distinct()
        return data

    def get_scheduler_session_details(request, *args, **kwargs):
        try:
            is_logged_in = False
            attendee_id = 0
            if 'is_user_login' in request.session and request.session['is_user_login']:
                is_logged_in = True
                attendee_id = request.session['event_user']['id']
            session_id = request.POST.get('session_id')
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            plugin_name = request.POST.get('plugin_name')
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
            title = ''
            message = ''
            session_enable = 'False'
            session_choose_least = ''
            session_choose_heighest = ''
            description = 'True'
            start_time = 'False'
            start_date = 'False'
            end_time = 'False'
            end_date = 'False'
            rvsp_date = 'False'
            speaker = 'False'
            speaker_link = 'False'
            tags = 'False'
            group_appear = 'False'
            location = 'False'
            location_link = 'False'
            session_option = ''
            cost = 'False'
            including_vat = 'False'
            session = Session.objects.get(id=session_id)
            session = LanguageKey.get_session_data_by_language(request, session)

            speakers = SeminarSpeakers.objects.filter(session_id=session.id)
            spkFlag = False
            speakersData = []
            if speakers.count() > 0:
                for speaker_item in speakers:
                    if is_logged_in:
                        if speaker_item.speaker_id == attendee_id:
                            spkFlag = True
                    speaker_obj = {
                        'id': speaker_item.speaker_id,
                        'firstname': speaker_item.speaker.firstname,
                        'lastname': speaker_item.speaker.lastname
                    }
                    speakersData.append(speaker_obj)
            session.speakers = speakersData
            # attendee = Attendee.objects.filter(id=attendee_id)


            session.is_speaker = False
            tags_list = SessionTags.objects.filter(session_id=session.id)
            taglist = []
            for tag in tags_list:
                taglist.append(tag.tag.name)
            session.taglist = taglist
            session_full = True
            session_attendee_count = SeminarsUsers.objects.filter(session_id=session.id).exclude(
                status='not-attending').count()
            if session.max_attendees > session_attendee_count or session.max_attendees == 0:
                session_full = False
            full_queue_open = False
            if session_full:
                if session.allow_attendees_queue:
                    full_queue_open = True
            session.full = session_full
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            session.session_expire = session_expire

            has_conflict = False
            if is_logged_in:
                has_conflict = Plugins.check_session_clash(attendee_id, session)
            session.session_conflict = has_conflict
            session_details_lang = LanguageKey.get_session_details_lang(request)
            plugin_lang = 'scheduler'
            if plugin_name == 'session-agenda':
                plugin_lang = 'agenda'
            elif plugin_name == 'session-checkbox':
                plugin_lang = 'checkbox'
            elif plugin_name == 'session-radio':
                plugin_lang = 'radio'
            if plugin_name == 'evaluations' or plugin_name == 'next-up' or plugin_name == 'messages':
                try:
                    session_global_settings = Setting.objects.filter(name='session_global_settings',
                                                                     event_id=request.session['event_id']).first().value
                    session_settings = json.loads(session_global_settings)
                    for details in session_settings:
                        if details == 'description':
                            description = 'True'
                        elif details == 'start_time':
                            start_time = 'True'
                        elif details == 'start_date':
                            start_date = 'True'
                        elif details == 'end_time':
                            end_time = 'True'
                        elif details == 'end_date':
                            end_date = 'True'
                        elif details == 'rvsp_date':
                            rvsp_date = 'True'
                        elif details == 'cost':
                            cost = 'True'
                        elif details == 'cost_incl_vat':
                            including_vat = 'True'
                        elif details == 'speaker':
                            speaker = 'True'
                        elif details == 'link_to_speaker':
                            speaker_link = 'True'
                        elif details == 'tags':
                            tags = 'True'
                        elif details == 'session_group':
                            group_appear = 'True'
                        elif details == 'location':
                            location = 'True'
                        elif details == 'link_to_location':
                            location_link = 'True'
                        elif details == 'session_available_1':
                            session_option = 'x'
                        elif details == 'session_available_2':
                            session_option = 'x-of-y'
                        elif details == 'session_available_3':
                            session_option = 'estimate'
                        elif details == 'session_available_4':
                            session_option = 'do-not-show'
                except Exception as e:
                    ErrorR.efail(e)
            else:
                for setting in element_settings:
                    if setting.element_question.question_key == 'session_' + plugin_lang + '_session_enable':
                        session_enable = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_description':
                        description = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_start_time':
                        start_time = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_start_date':
                        start_date = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_end_time':
                        end_time = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_end_date':
                        end_date = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_rvsp_date':
                        rvsp_date = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_speaker':
                        speaker = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_link_speaker':
                        speaker_link = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_tags':
                        tags = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_session_groups':
                        group_appear = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_location':
                        location = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_limk_location':
                        location_link = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_available':
                        session_option = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_cost':
                        cost = setting.answer
                    elif setting.element_question.question_key == 'session_' + plugin_lang + '_session_details_incl_vat':
                        including_vat = setting.answer
            if plugin_name == "messages":
                session_enable = "True"
            all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
            status_text = all_langs['langkey']['sessiondetails_txt_status_not_attending']
            status = 'not-answered'
            if is_logged_in:
                session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=session.id)
                if session_attendee.count() > 0:
                    status = session_attendee[0].status
                    if session_attendee[0].status == 'attending':
                        status_text = all_langs['langkey']['sessiondetails_txt_status_attending']
                    elif session_attendee[0].status == 'in-queue':
                        status_text = all_langs['langkey']['sessiondetails_txt_status_in_queue']
                    elif session_attendee[0].status == 'not-attending':
                        status_text = all_langs['langkey']['sessiondetails_txt_status_not_attending']
                    elif session_attendee[0].status == 'deciding':
                        status_text = all_langs['langkey']['sessiondetails_txt_status_deciding']
                        # status = 'in-queue'
            if spkFlag:
                status = 'attending'
                status_text = all_langs['langkey']['sessiondetails_txt_status_attending']
                session.is_speaker = True
            session_details_lang['langkey']['status_full'] = all_langs['langkey']['sessiondetails_txt_status_full']
            session_details_lang['langkey']['status_queue_open'] = all_langs['langkey'][
                'sessiondetails_txt_status_queue_open']
            session_details_lang['langkey']['status_queue_close'] = all_langs['langkey'][
                'sessiondetails_txt_status_queue_close']
            session_details_lang['langkey']['status_rsvp_passed'] = all_langs['langkey'][
                'sessiondetails_txt_status_rsvp_passed']
            session_details_lang['langkey']['status_time_conflict'] = all_langs['langkey'][
                'sessiondetails_txt_status_time_conflict']
            session_details_lang['langkey']['status_in_queue'] = all_langs['langkey'][
                'sessiondetails_txt_status_in_queue']
            session_details_lang['langkey']['status_deciding'] = all_langs['langkey'][
                'sessiondetails_txt_status_deciding']
            session_details_lang['langkey']['status_attending'] = all_langs['langkey'][
                'sessiondetails_txt_status_attending']
            session_details_lang['langkey']['status_not_attending'] = all_langs['langkey'][
                'sessiondetails_txt_status_not_attending']

            economy_currency_txt = EconomyLibrary.get_event_currency(request.session['language_id'])
            if session.vat != None:
                lang_vat_included = session_details_lang["langkey"]['sessiondetails_txt_session_cost_incl_vat']
                amount = session.get_vat_amount()
                if not HelperData.isint(amount):
                    amount = '{:0,.2f}'.format(amount).replace(",", " ")
                else:
                    amount = '{0:,}'.format(int(amount)).replace(",", " ")
                lang_vat_included = lang_vat_included.replace("{X}", '%s %s' % (amount, economy_currency_txt))
                session.lang_vat_included = lang_vat_included

                lang_vat_excluded = session_details_lang["langkey"]['sessiondetails_txt_session_cost_excl_vat']
                lang_vat_excluded = lang_vat_excluded.replace("{X}", '%s %s' % (amount, economy_currency_txt))
                session.lang_vat_excluded = lang_vat_excluded
            else:
                lang_vat_included = session_details_lang["langkey"]['sessiondetails_txt_session_cost_incl_vat']
                lang_vat_included = lang_vat_included.replace("{X}", '%s %s' % (str(0), economy_currency_txt))
                session.lang_vat_included = lang_vat_included

                lang_vat_excluded = session_details_lang["langkey"]['sessiondetails_txt_session_cost_excl_vat']
                lang_vat_excluded = lang_vat_excluded.replace("{X}", '%s %s' % (str(0), economy_currency_txt))
                session.lang_vat_excluded = lang_vat_excluded

            session = SessionSeatAvailability.get_seats_availability(request, session, session_option,
                                                                     request.session['event_id'], all_langs)
            all_session_status = []
            all_session_status.append(status)
            if session_full:
                all_session_status.append("full")
                if full_queue_open:
                    all_session_status.append("queue-open")
            if has_conflict:
                all_session_status.append("time-conflict")
            if session_expire:
                all_session_status.append("rsvp-ended")
            session.all_status = all_session_status
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
                "session_details_language": session_details_lang,
                "box_id": box_id,
                "page_id": page_id,
                "cost": cost,
                "including_vat": including_vat,
                "economy_currency_txt": economy_currency_txt,
                "plugin_name": plugin_name,
                "request": request,
            }
            session_html = render_to_string('public/element/session_scheduler_session_details.html', context)
            return HttpResponse(json.dumps({'success': True, 'session_html': session_html}),
                                content_type='application/json')
        except Exception as e:
            ErrorR.efail(e)
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')

    def get_location_details(request, pk, *args, **kwargs):
        box_id = request.POST.get('box_id')
        page_id = request.POST.get('page_id')
        response = {}
        response['details'] = ''
        try:
            location = Locations.objects.get(id=pk)
            location = LanguageKey.get_location_data_by_language(request, location)
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question').order_by(
                'element_question_id')
            location_title = 'False'
            location_details = 'False'
            description = 'False'
            link_map = 'False'
            address_details = 'False'
            contact_details = 'False'
            custom_location = False
            custom_location_keys = ['session_scheduler_custom_location_settings',
                                    'session_radio_custom_location_settings',
                                    'session_checkbox_custom_location_settings', 'next_up_custom_location_settings',
                                    'session_agenda_custom_location_settings']
            for setting in element_settings:
                if setting.element_question.question_key in custom_location_keys:
                    if setting.answer == 'True':
                        custom_location = True
                if custom_location:
                    location_title_keys = ['session_scheduler_location_list_title', 'session_radio_location_list_title',
                                           'session_checkbox_location_list_title', 'next_up_location_list_title',
                                           'session_agenda_location_list_title']
                    location_link_keys = ['session_scheduler_location_link_location_details',
                                          'session_radio_location_link_location_details',
                                          'session_checkbox_location_link_location_details',
                                          'next_up_location_link_location_details',
                                          'session_agenda_location_link_location_details']
                    location_description_keys = ['ssession_scheduler_location_description',
                                                 'session_radio_location_description',
                                                 'session_checkbox_location_description',
                                                 'next_up_location_description', 'session_agenda_location_description']
                    location_map_keys = ['session_scheduler_location_link_map', 'session_radio_location_link_map',
                                         'session_checkbox_location_link_map', 'next_up_location_link_map',
                                         'session_agenda_location_link_map']
                    location_address_keys = ['session_scheduler_location_address_details',
                                             'session_radio_location_address_details',
                                             'session_checkbox_location_address_details',
                                             'next_up_location_address_details',
                                             'session_agenda_location_address_details']
                    location_contact_keys = ['session_scheduler_location_contact_details',
                                             'session_radio_location_contact_details',
                                             'session_checkbox_location_contact_details',
                                             'next_up_location_contact_details',
                                             'session_agenda_location_contact_details']
                    if setting.element_question.question_key in location_title_keys:
                        location_title = setting.answer
                    elif setting.element_question.question_key in location_link_keys:
                        location_details = setting.answer
                    elif setting.element_question.question_key in location_description_keys:
                        description = setting.answer
                    elif setting.element_question.question_key in location_map_keys:
                        link_map = setting.answer
                    elif setting.element_question.question_key in location_address_keys:
                        address_details = setting.answer
                    elif setting.element_question.question_key in location_contact_keys:
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
            response['lang_details'] = LanguageKey.catch_lang_key(request, 'location-list',
                                                                  'locationlist_txt_location_details')
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            ErrorR.efail(e)
            response['lang_details'] = LanguageKey.catch_lang_key(request, 'location-list',
                                                                  'locationlist_txt_location_details')
            return HttpResponse(json.dumps(response), content_type='application/json')

    def get_attendee_details(request, pk, *args, **kwargs):
        box_id = request.POST.get('box_id')
        page_id = request.POST.get('page_id')
        response = {}
        response['details'] = ''
        try:
            attendee = Attendee.objects.filter(id=pk)
            attendee_questions = []
            custom_keys = ['session_scheduler_custom_attendee_settings', 'session_radio_custom_attendee_settings',
                           'session_checkbox_custom_attendee_settings', 'next_up_custom_attendee_settings',
                           'session_agenda_custom_attendee_settings']
            question_keys = ['session_scheduler_attendee_selected_columns', 'session_radio_attendee_selected_columns',
                             'session_checkbox_attendee_selected_columns', 'next_up_attendee_selected_columns',
                             'session_agenda_attendee_selected_columns']
            temp_keys = custom_keys
            custom_keys.extend(question_keys)
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id,
                                                              element_question__question_key__in=custom_keys).select_related(
                'element_question').order_by(
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
                                                                             question_rules, attendee[0], True)
                response['details'] = attendee_details
            response['lang_details'] = LanguageKey.catch_lang_key(request, 'questions', 'th_question_attendee_details')
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            ErrorR.efail(e)
            response['lang_details'] = LanguageKey.catch_lang_key(request, 'questions', 'th_question_attendee_details')
            return HttpResponse(json.dumps(response), content_type='application/json')

    def check_session_clash(attendee_id, session):
        already_has_session = SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending',
                                                           session__allow_overlapping=0).exclude(session_id=session.id)
        already_has_session_as_speaker = SeminarSpeakers.objects.filter(speaker_id=attendee_id,
                                                                        session__allow_overlapping=0).exclude(
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
        # else:
        #     for sessionlist in already_has_session:
        #         if sessionlist.session.allow_overlapping == 0:
        #             if sessionlist.session.start <= session.start < sessionlist.session.end:
        #                 Inbetween = True
        #                 break
        #             elif sessionlist.session.start < session.end <= sessionlist.session.end:
        #                 Inbetween = True
        #                 break
        #             if session.start <= sessionlist.session.start < session.end:
        #                 Inbetween = True
        #                 break
        #             elif session.start < sessionlist.session.end <= session.end:
        #                 Inbetween = True
        #                 break
        #
        #     for sessionlist in already_has_session_as_speaker:
        #         if sessionlist.session.allow_overlapping == 0:
        #             if sessionlist.session.start <= session.start < sessionlist.session.end:
        #                 Inbetween = True
        #                 break
        #             elif sessionlist.session.start < session.end <= sessionlist.session.end:
        #                 Inbetween = True
        #                 break
        #             if session.start <= sessionlist.session.start < session.end:
        #                 Inbetween = True
        #                 break
        #             elif session.start < sessionlist.session.end <= session.end:
        #                 Inbetween = True
        #                 break
        # Inbetween = False
        return Inbetween

    # def get_session_details(request, sessionGroups, event_id, session_option,economy_currency_txt):
    #     response = {}
    #     session_details_lang = LanguageKey.get_session_details_lang(request)
    #     all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
    #
    #     for group in sessionGroups:
    #         group.sessions = Session.objects.filter(group_id=group.id).order_by('session_order')
    #         for session in group.sessions:
    #             session.cost_detail = session.get_cost_detail()
    #             if session.vat != None:
    #                 lang_vat_included = session_details_lang["langkey"]['sessiondetails_txt_session_cost_incl_vat']
    #                 amount = session.get_vat_amount()
    #                 if not HelperData.isint(amount):
    #                     amount = '{:0,.2f}'.format(amount).replace(",", " ")
    #                 else:
    #                     amount = '{0:,}'.format(int(amount)).replace(",", " ")
    #
    #                 lang_vat_included = lang_vat_included.replace("{X}", '%s %s'%(amount,economy_currency_txt))
    #                 session.lang_vat_included = lang_vat_included
    #
    #                 lang_vat_excluded = session_details_lang["langkey"]['sessiondetails_txt_session_cost_excl_vat']
    #                 lang_vat_excluded = lang_vat_excluded.replace("{X}", '%s %s'%(amount,economy_currency_txt))
    #                 session.lang_vat_excluded = lang_vat_excluded
    #             else:
    #                 lang_vat_included = session_details_lang["langkey"]['sessiondetails_txt_session_cost_incl_vat']
    #                 lang_vat_included = lang_vat_included.replace("{X}", '%s %s'%(str(0),economy_currency_txt))
    #                 session.lang_vat_included = lang_vat_included
    #
    #                 lang_vat_excluded = session_details_lang["langkey"]['sessiondetails_txt_session_cost_excl_vat']
    #                 lang_vat_excluded = lang_vat_excluded.replace("{X}", '%s %s'%(str(0),economy_currency_txt))
    #                 session.lang_vat_excluded = lang_vat_excluded
    #
    #             session.tags = SessionTags.objects.filter(session_id=session.id)
    #             session.speakers = SeminarSpeakers.objects.filter(session_id=session.id)
    #             session.custom_classes = SessionClasses.objects.filter(session_id=session.id)
    #             session = SessionSeatAvailability.get_seats_availability(request, session, session_option, event_id,
    #                                                                      all_langs)
    #             session = LanguageKey.get_session_data_by_language(request, session)
    #
    #
    #     response['sessionGroups'] = sessionGroups
    #     response['session_details_lang'] = session_details_lang
    #     return response

    def check_session_availability(request, *args, **kwargs):
        # rebates = json.loads(request.POST.get('rebates'))
        # rebate_type = request.POST.get('rebate_type')
        # else_rebate = rebates.pop()
        # user_id = request.session['event_user']['id']
        # if rebate_type == 'filter':
        #     for rebate_item in rebates:
        #         rule_set = RuleSet.objects.filter(id=rebate_item['filter_id']).first()
        #         if rule_set:
        #             filters = json.loads(rule_set.preset)
        #             q = Q()
        #             match_condition = filters[0][0]['matchFor']
        #             if match_condition == '2':
        #                 q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
        #             elif match_condition == '1':
        #                 q = Q(id=-11)
        #                 q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
        #
        #             filtered_attendee = Attendee.objects.filter(q).filter(id=user_id)
        #             if filtered_attendee:
        #                 print(rebate_item['rebate_id'])
        #
        # raise Exception()
        operation = request.POST.get('operation')
        response = {}
        event_id = request.session['event_id']
        tem_session = None
        all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')

        user_id = request.POST.get('temp_user_id')
        if 'is_user_login' in request.session and request.session['is_user_login'] and user_id == str(
                request.session['event_user']['id']):
            user_id = request.session['event_user']['id']
        else:
            if not user_id.isdigit():
                temp_attendee = Attendee(status='pending', event_id=event_id,
                                         language_id=request.session["language_id"])
                temp_attendee.save()
                user_id = temp_attendee.id
                # request.POST._mutable = True
                # request.POST['temp_user_id'] = user_id
                # request.POST._mutable = False
            # temporary login
            tem_session = DynamicPage.tem_login_make(request, user_id)

        session_id = request.POST.get('session_id')
        seats_option = request.POST.get('seats_option')
        if operation == 'checked':
            response = SessionDetail.status_type_attend(request, session_id)

            sessionAttendees = Session.objects.get(id=session_id)
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        seats_option,
                                                                                        event_id, all_langs)
            response['seats_availability'] = session_seats_availability.availability
            ## Economy Start
            if response['result'] and not response['exists'] and response['status'] == 'attending':
                order_number = request.POST.get('order_number')
                if not order_number or order_number == 'None':
                    order_number = None
                order_values = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='session',
                                                          item_id=session_id, admin_id=None, order_number=order_number)
                if order_values:
                    response['order_number'] = order_values['order_number']
                    rebate_type = request.POST.get('rebate_type')
                    rebates = request.POST.get('rebates')
                    if rebate_type and rebates:
                        Plugins.check_and_apply_rebate(request, rebate_type, rebates, user_id, order_values)
                else:
                    response['order_number'] = None
                    ## Economy End

        elif operation == 'unchecked':
            if SeminarsUsers.objects.filter(session_id=session_id, status='in-queue', attendee_id=user_id).exists():
                response = SessionDetail.status_type_queue(request, session_id, user_id, event_id)
            else:
                response = Plugins.remove_session(request, session_id, user_id, event_id, seats_option)
            ## Economy Start
            order_detail = EconomyLibrary.get_order_id(user_id, 'session', session_id)
            if order_detail:
                result = EconomyLibrary.remove_item_from_order(event_id, user_id, order_detail['order_id'], session_id)
                response['download_flag'] = result['download_applicable']
                response['order_number'] = order_detail['order_number']
                response['user_id'] = user_id
                ## Economy End
        elif operation == 'radio':
            previous_id = request.POST.get('previous_id')
            response = SessionDetail.status_type_attend(request, session_id, previous_id)
            sessionAttendees = Session.objects.get(id=session_id)
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        seats_option,
                                                                                        event_id, all_langs)
            response['seats_availability'] = session_seats_availability.availability
            if response['result'] and not response['exists']:
                if previous_id != session_id:
                    seats_response = Plugins.remove_session(request, previous_id, user_id, event_id, seats_option)
                    if 'seats_availability' in seats_response:
                        response['previous_session_seats_availability'] = seats_response['seats_availability']

                    ## Economy Start
                    if response['status'] == 'attending':
                        order_number = request.POST.get('order_number')
                        if not order_number or order_number == 'None':
                            order_number = None
                        order_values = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='session',
                                                                  item_id=session_id, admin_id=None,
                                                                  order_number=order_number)
                        if order_values:
                            response['order_number'] = order_values['order_number']
                            rebate_type = request.POST.get('rebate_type')
                            rebates = request.POST.get('rebates')
                            if rebate_type and rebates:
                                Plugins.check_and_apply_rebate(request, rebate_type, rebates, user_id, order_values)
                            # rebates = json.loads(request.POST.get('rebates'))
                            # for rebate in rebates:
                            #     EconomyLibrary.apply_rebate(user_id=user_id, order_id=order_values['order_id'],
                            #                                 rebate_id=rebate['rebate_id'],
                            #                                 rebate_item_type='session', rebate_item_id=rebate['rebate_for'])
                        else:
                            response['order_number'] = None
                        if previous_id not in [0, '0']:
                            tem_order_info = EconomyLibrary.get_order_id(user_id, 'session', previous_id)
                            if tem_order_info:
                                tem_order_id = tem_order_info['order_id']
                                EconomyLibrary.remove_item_from_order(event_id, user_id, tem_order_id, previous_id)
                            ## Economy End
            else:
                print('Session is full.')
        if user_id is not None:
            all_found_sessions = json.loads(request.POST.get('all_sessions'))
            ErrorR.ex_time_init()
            sessions_info = Plugins.getAllFoundSessionsInfo(request, all_found_sessions, user_id)
            response['sessions_info'] = sessions_info
            ErrorR.ex_time()
        if tem_session:
            response['temp_user_id'] = user_id
            DynamicPage.tem_login_clean(request, tem_session)

        return HttpResponse(json.dumps(response), content_type='application/json')

    def check_session_availability_act_radio(request, *args, **kwargs):

        operation = request.POST.get('operation')
        response = {}
        event_id = request.session['event_id']
        tem_session = None
        all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')

        user_id = request.POST.get('temp_user_id')
        if 'is_user_login' in request.session and request.session['is_user_login'] and user_id == str(
                request.session['event_user']['id']):
            user_id = request.session['event_user']['id']
        else:
            if not user_id.isdigit():
                temp_attendee = Attendee(status='pending', event_id=event_id,
                                         language_id=request.session["language_id"])
                temp_attendee.save()
                user_id = temp_attendee.id
                # request.POST._mutable = True
                # request.POST['temp_user_id'] = user_id
                # request.POST._mutable = False
            # temporary login
            tem_session = DynamicPage.tem_login_make(request, user_id)

        session_id = request.POST.get('session_id')
        seats_option = request.POST.get('seats_option')
        if operation == 'radio':
            previous_id = request.POST.getlist('previous_id[]')
            ErrorR.c_bicyan(request.POST.getlist('previous_id[]'))
            response = SessionDetail.status_type_attend_act_radio(request, session_id, previous_id)
            sessionAttendees = Session.objects.get(id=session_id)
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        seats_option,
                                                                                        event_id, all_langs)
            response['seats_availability'] = session_seats_availability.availability
            if response['result'] and not response['exists']:
                if session_id in previous_id:
                    previous_id.remove(session_id)
                ErrorR.c_bipurple(response)
                remove_session_act = False
                if request.POST.get('count_attending') == '0':
                    if response['status'] == "attending" or response['status'] == "in-queue":
                        remove_session_act = True
                else:
                    if response['status'] == "attending":
                        remove_session_act = True
                if len(previous_id) and remove_session_act:
                    seats_response = Plugins.remove_session_act_radio(request, previous_id, user_id, event_id,
                                                                      seats_option)
                    if 'previous_sessions_content_seats_availability' in seats_response:
                        response['previous_sessions_content_seats_availability'] = seats_response['previous_sessions_content_seats_availability']
                    if 'previous_sessions_content_status_msg' in seats_response:
                            response['previous_sessions_content_status_msg'] = seats_response['previous_sessions_content_status_msg']

                ## Economy Start
                if response['status'] == 'attending':
                    order_number = request.POST.get('order_number')
                    if not order_number or order_number == 'None':
                        order_number = None
                    order_values = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='session',
                                                              item_id=session_id, admin_id=None,
                                                              order_number=order_number)
                    if order_values:
                        response['order_number'] = order_values['order_number']
                        rebate_type = request.POST.get('rebate_type')
                        rebates = request.POST.get('rebates')
                        if rebate_type and rebates:
                            Plugins.check_and_apply_rebate(request, rebate_type, rebates, user_id, order_values)
                        # rebates = json.loads(request.POST.get('rebates'))
                        # for rebate in rebates:
                        #     EconomyLibrary.apply_rebate(user_id=user_id, order_id=order_values['order_id'],
                        #                                 rebate_id=rebate['rebate_id'],
                        #                                 rebate_item_type='session', rebate_item_id=rebate['rebate_for'])
                    else:
                        response['order_number'] = None

                for pre_id in previous_id:
                    if pre_id not in [0, '0'] and remove_session_act:
                        tem_order_info = EconomyLibrary.get_order_id(user_id, 'session', pre_id)
                        if tem_order_info:
                            tem_order_id = tem_order_info['order_id']
                            EconomyLibrary.remove_item_from_order(event_id, user_id, tem_order_id, pre_id)
                        ## Economy End
            else:
                print('Session is full.')
        elif operation == 'unchecked':
            if SeminarsUsers.objects.filter(session_id=session_id, status='in-queue', attendee_id=user_id).exists():
                response = SessionDetail.status_type_queue(request, session_id, user_id, event_id)
                if 'status_queue_open_msg' in response:
                    status_full = LanguageKey.catch_lang_key_multiple(request, "session-details",["sessiondetails_txt_status_full"])
                    response['status_queue_open_msg'] = status_full['langkey']['sessiondetails_txt_status_full'] +" "+ response['status_queue_open_msg']
            else:
                response = Plugins.remove_session(request, session_id, user_id, event_id, seats_option)
            ## Economy Start
            order_detail = EconomyLibrary.get_order_id(user_id, 'session', session_id)
            if order_detail:
                result = EconomyLibrary.remove_item_from_order(event_id, user_id, order_detail['order_id'], session_id)
                response['download_flag'] = result['download_applicable']
                response['order_number'] = order_detail['order_number']
                response['user_id'] = user_id
        if user_id is not None:
            all_found_sessions = json.loads(request.POST.get('all_sessions'))
            ErrorR.ex_time_init()
            sessions_info = Plugins.getAllFoundSessionsInfo(request, all_found_sessions, user_id)
            response['sessions_info'] = sessions_info
            ErrorR.ex_time()
        if tem_session:
            response['temp_user_id'] = user_id
            DynamicPage.tem_login_clean(request, tem_session)

        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_updated_session_info(request, *args, **kwargs):
        response = {}
        response['success'] = False
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                if 'all_sessions' in request.POST:
                    user_id = request.session['event_user']['id']
                    all_found_sessions = json.loads(request.POST.get('all_sessions'))
                    sessions_info = Plugins.getAllFoundSessionsInfo(request, all_found_sessions, user_id)
                    response['sessions_info'] = sessions_info
                    response['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return HttpResponse(json.dumps(response), content_type='application/json')


    def getAllFoundSessionsInfo(request, session_ids, attendee_id):
        all_sessions = []
        sessions = Session.objects.filter(id__in=session_ids)
        for session in sessions:
            id = session.id
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
            status = "not-answered"
            has_conflict = False
            speakers = SeminarSpeakers.objects.filter(session_id=id)
            if speakers.count() > 0:
                for speaker in speakers:
                    if speaker.speaker_id == attendee_id:
                        status = "attending"
            session_attendee = SeminarsUsers.objects.filter(attendee_id=attendee_id, session_id=id)
            if session_attendee.count() > 0:
                if session_attendee[0].status == 'attending':
                    status = "attending"
                elif session_attendee[0].status == 'in-queue':
                    status = "in-queue"
                elif session_attendee[0].status == 'deciding':
                    status = "deciding"
                elif session_attendee[0].status == 'not-attending':
                    is_clash = Plugins.check_session_clash(attendee_id, session)
                    if is_clash:
                        has_conflict = True
                    status = 'not-attending'
            else:
                is_clash = Plugins.check_session_clash(attendee_id, session)
                if is_clash:
                    has_conflict = True
                status = 'not-answered'
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            all_session_status = []
            if status != 'not-attending' and status != 'not-answered':
                all_session_status.append(status)
            if full:
                all_session_status.append("full")
                if full_queue_open:
                    all_session_status.append("queue-open")
            if has_conflict:
                all_session_status.append("time-conflict")
            if session_expire:
                all_session_status.append("rsvp-ended")
            if len(all_session_status) == 0:
                if status == 'not-attending' or status == 'not-answered':
                    all_session_status.append(status)
            current_status = None
            if status != 'not-attending' and status != 'not-answered':
                current_status = status
            elif status == "not-attending" or status == 'not-answered':
                if session_expire:
                    current_status = "rsvp-ended"
                elif has_conflict:
                    current_status = "time-conflict"
                elif full:
                    current_status = "full"
                else:
                    current_status = status
            status_msg = ''
            if current_status == 'attending':
                msg = LanguageKey.catch_lang_key_multiple(request, "session-details",["sessiondetails_txt_status_attending"])
                status_msg = msg['langkey']['sessiondetails_txt_status_attending']
            elif current_status == 'in-queue':
                msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                 ["sessiondetails_txt_status_in_queue"])
                status_msg = msg['langkey']['sessiondetails_txt_status_in_queue']
            elif current_status == 'deciding':
                msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                 ["sessiondetails_txt_status_deciding"])
                status_msg = msg['langkey']['sessiondetails_txt_status_deciding']
            elif current_status == 'rsvp-ended':
                msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                 ["sessiondetails_txt_status_rsvp_passed"])
                status_msg = msg['langkey']['sessiondetails_txt_status_rsvp_passed']
            elif current_status == 'time-conflict':
                msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                 ["sessiondetails_txt_status_time_conflict"])
                status_msg = msg['langkey']['sessiondetails_txt_status_time_conflict']
            elif current_status == 'full':
                if full_queue_open:
                    msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                 ["sessiondetails_txt_status_full","sessiondetails_txt_status_queue_open"])
                    status_msg = msg['langkey']['sessiondetails_txt_status_full'] + " - " + msg['langkey']['sessiondetails_txt_status_queue_open']
                else:
                    msg = LanguageKey.catch_lang_key_multiple(request, "session-details",
                                                                     ["sessiondetails_txt_status_full",
                                                                      "sessiondetails_txt_status_queue_close"])
                    status_msg = msg['langkey']['sessiondetails_txt_status_full'] + " - " + msg['langkey']['sessiondetails_txt_status_queue_close']

            session_obj = {
                'id': id,
                'current_status': current_status,
                'all_session_status': all_session_status,
                'status_msg': status_msg
            }
            all_sessions.append(session_obj)
        return all_sessions

    def check_and_apply_rebate(request, rebate_type, rebates, user_id, order_values):
        if rebate_type == 'filter':
            rebates = json.loads(rebates)
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
                    filtered_attendee = Attendee.objects.filter(q).filter(id=user_id)
                    if filtered_attendee:
                        rebate_found = rebate_item['rebate_id']
                        break
            if not rebate_found:
                rebate_found = else_rebate['rebate_id']
            for reb_item in rebate_found:
                EconomyLibrary.apply_rebate(user_id=user_id, order_id=order_values['order_id'], rebate_id=int(reb_item))

        elif rebate_type == 'date':
            for rebate in rebates:
                EconomyLibrary.apply_rebate(user_id=user_id, order_id=order_values['order_id'],
                                            rebate_id=rebate['rebate_id'],
                                            rebate_item_type='session', rebate_item_id=rebate['rebate_for'])

    def session_set_unset_availability(request, *args, **kwargs):
        all_response = {}
        event_id = request.session['event_id']
        unset_sessions = json.loads(request.POST.get('unset_sessions'))
        set_sessions = json.loads(request.POST.get('set_sessions'))
        all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
        unset_session_response = []
        for us_session in unset_sessions:
            response = {}
            response.update(us_session)
            tem_session = None
            user_id = us_session['attendee_id']
            if 'is_user_login' in request.session and request.session['is_user_login'] and user_id == str(
                    request.session['event_user']['id']):
                user_id = request.session['event_user']['id']
            else:
                if not user_id.isdigit():
                    temp_attendee = Attendee(status='pending', event_id=event_id,
                                             language_id=request.session["language_id"])
                    temp_attendee.save()
                    user_id = temp_attendee.id
                # temporary login
                tem_session = DynamicPage.tem_login_make(request, user_id)
            session_id = us_session['session_id']
            seats_option = us_session['seats_option']
            if SeminarsUsers.objects.filter(session_id=session_id, status='in-queue', attendee_id=user_id).exists():
                response_data = SessionDetail.status_type_queue(request, session_id, user_id, event_id)
            else:
                response_data = Plugins.remove_session(request, session_id, user_id, event_id, seats_option)
            ## Economy Start
            response.update(response_data)
            order_detail = EconomyLibrary.get_order_id(user_id, 'session', session_id)
            if order_detail:
                result = EconomyLibrary.remove_item_from_order(event_id, user_id, order_detail['order_id'], session_id)
                response['download_flag'] = result['download_applicable']
                response['order_number'] = order_detail['order_number']
                response['user_id'] = user_id
            if tem_session:
                response['temp_user_id'] = user_id
                DynamicPage.tem_login_clean(request, tem_session)
            unset_session_response.append(response)
        set_session_response = []
        group_order_number = None
        for se_session in set_sessions:
            response = {}
            response.update(se_session)
            tem_session = None
            user_id = se_session['attendee_id']
            if 'is_user_login' in request.session and request.session['is_user_login'] and user_id == str(
                    request.session['event_user']['id']):
                user_id = request.session['event_user']['id']
            else:
                if not user_id.isdigit():
                    temp_attendee = Attendee(status='pending', event_id=event_id,
                                             language_id=request.session["language_id"])
                    temp_attendee.save()
                    user_id = temp_attendee.id
                # temporary login
                tem_session = DynamicPage.tem_login_make(request, user_id)
            session_id = se_session['session_id']
            seats_option = se_session['seats_option']
            remove_conflict = False
            if 'conflict_session_setting' in se_session and se_session['conflict_session_setting'] == '1':
                remove_conflict = True
            session_response = SessionDetail.status_type_attend(request, session_id, None, remove_conflict)
            response.update(session_response)
            sessionAttendees = Session.objects.get(id=session_id)
            session_seats_availability = SessionSeatAvailability.get_seats_availability(request, sessionAttendees,
                                                                                        seats_option,
                                                                                        event_id, all_langs)
            response['seats_availability'] = session_seats_availability.availability
            ## Economy Start
            if response['result'] and not response['exists']:
                order_number = se_session['order_number']
                if group_order_number:
                    order_number = group_order_number
                elif not order_number or order_number == 'None':
                    order_number = None
                order_values = EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='session',
                                                          item_id=session_id, admin_id=None, order_number=order_number)
                if order_values:
                    response['order_number'] = order_values['order_number']
                    group_order_number = order_values['order_number']
                    # rebates = json.loads(se_session['rebates'])
                    # for rebate in rebates:
                    #     EconomyLibrary.apply_rebate(user_id=user_id, order_id=order_values['order_id'],
                    #                                 rebate_id=rebate['rebate_id'],
                    #                                 rebate_item_type='session', rebate_item_id=rebate['rebate_for'])
                    rebate_type = se_session.get('rebate_type')
                    rebates = se_session.get('rebates')
                    if rebate_type and rebates:
                        Plugins.check_and_apply_rebate(request, rebate_type, rebates, user_id, order_values)
                else:
                    print('ELSE BLOCK *********')
                    response['order_number'] = None
            if tem_session:
                response['temp_user_id'] = user_id
                DynamicPage.tem_login_clean(request, tem_session)
            set_session_response.append(response)
        all_response['unset_session_response'] = unset_session_response
        all_response['set_session_response'] = set_session_response
        return HttpResponse(json.dumps(all_response), content_type='application/json')

    def attend_session(request, session_id, user_id, event_id, session_option):
        response = {}
        session_exist = SeminarsUsers.objects.filter(attendee_id=user_id, session_id=session_id)
        notification_language = LanguageKey.catch_lang_key_obj(request, 'notification')
        all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
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
                                                                                        session_option, event_id,
                                                                                        all_langs)
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
                                                                                        session_option, event_id,
                                                                                        all_langs)
            response['seats_availability'] = session_seats_availability.availability
        return response

    def remove_session(request, previous_id, user_id, event_id, seats_option):
        response = {}
        response['result'] = False
        response['success'] = False
        session = SeminarsUsers.objects.filter(session_id=previous_id, attendee_id=user_id).select_related('session')
        all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
        if session.exists():
            time_zone_time = HelperData.getTimezoneNow(request)
            time_now = time_zone_time.date()
            session_expire = False
            reg_between_end = session[0].session.reg_between_end
            if reg_between_end < time_now:
                session_expire = True
            if not session_expire:
                session_data = session[0].session
                SeminarsUsers.objects.filter(id=session[0].id).update(status='not-attending')
                status = "Attending"
                if session[0].status == 'in-queue':
                    status = "In Queue"
                elif session[0].status == 'deciding':
                    status = "Deciding"
                activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                           session_id=previous_id, old_value=status, new_value="Not Attending",
                                           event_id=event_id)
                activity.save()
                session_seats_availability = SessionSeatAvailability.get_seats_availability(request, session_data,
                                                                                            seats_option, event_id,
                                                                                            all_langs)
                response['seats_availability'] = session_seats_availability.availability
                if previous_id not in [0, '0']:
                    SessionDetail.notify_queue_user(request, previous_id)
                response['result'] = False
                response['success'] = True
                response['status'] = 'not-attending'
                response['status_msg'] = LanguageKey.catch_lang_key(request, "session-details",
                                                                    "sessiondetails_txt_status_not_attending")
                ErrorR.okblue(response['status_msg'])
                response['message'] = NotifyView.get_notification_text(request, "notify_unregistered_session")
            else:
                response['rsvp_ended'] = True
        return response

    def remove_session_act_radio(request, previous_id, user_id, event_id, seats_option):
        response = {}
        response['result'] = False
        response['success'] = False
        session = SeminarsUsers.objects.filter(session_id__in=previous_id, attendee_id=user_id).select_related(
            'session')
        all_langs = LanguageKey.catch_lang_key_obj(request, 'session-details')
        time_zone_time = HelperData.getTimezoneNow(request)
        time_now = time_zone_time.date()
        if session.exists():
            for ses in session:
                session_expire = False
                reg_between_end = ses.session.reg_between_end
                if reg_between_end < time_now:
                    session_expire = True
                if not session_expire:
                    session_data = ses.session
                    SeminarsUsers.objects.filter(id=ses.id).update(status='not-attending')
                    status = "Attending"
                    if ses.status == 'in-queue':
                        status = "In Queue"
                    elif ses.status == 'deciding':
                        status = "Deciding"
                    ErrorR.c_biyellow(ses.session_id)
                    activity = ActivityHistory(activity_type="update", category="session", attendee_id=user_id,
                                               session_id=ses.session_id, old_value=status, new_value="Not Attending",
                                               event_id=event_id)
                    activity.save()
                    session_seats_availability = SessionSeatAvailability.get_seats_availability(request, session_data,
                                                                                                seats_option, event_id,
                                                                                                all_langs)
                    response['previous_sessions_content_seats_availability'] = {}
                    response['previous_sessions_content_status_msg'] = {}
                    response['previous_sessions_content_seats_availability'][str(ses.session_id)] = session_seats_availability.availability
                    for pre_id in previous_id:
                        if pre_id not in [0, '0']:
                            SessionDetail.notify_queue_user(request, pre_id)
                    response['result'] = False
                    response['success'] = True
                    response['status'] = 'not-attending'
                    response['previous_sessions_content_status_msg'][str(ses.session_id)] = all_langs['langkey']['sessiondetails_txt_status_not_attending']
                    # response['message'] = NotifyView.get_notification_text(request, "notify_unregistered_session")
                else:
                    response['rsvp_ended'] = True
        return response

    def get_economy_plugin(request, page_id, element):
        language = LanguageKey.get_lang_key(request, element['element_id'])
        box_id = element['box_id'].split('-')[1]
        plugin_div = """<div class="form-plugin element form-plugin-economy" box" id="box-""" + str(
            box_id) + """" data-id=""" + str(element['element_id']) + """ data-name="economy">"""
        try:
            context = {
                'language': language,
                'pay_by_card_button_status': True,
                'last_generated_pdf_button_status': True,
                'balance_table_pdf_button_status': True
            }
            order_table_visible_columns = {
                "show_item_name": "false",
                "show_cost_excl_vat": "false",
                "show_rebate_amount": "false",
                "show_vat_amount": "false",
                "show_vat_rate": "false",
                "show_cost_incl_vat": "false"
            }
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
            if element_settings:
                for setting in element_settings:
                    if setting.element_question.question_key == 'economy_message':
                        context['message'] = LanguageKey.get_plugin_description_by_language(request,
                                                                                            setting.description)
                    elif setting.element_question.question_key == 'economy_include_order_table':
                        context['order_table'] = eval(setting.answer)
                    elif setting.element_question.question_key == 'economy_order_table_item_name':
                        context['show_item_name'] = eval(setting.answer)
                        if context['show_item_name']:
                            order_table_visible_columns['show_item_name'] = "true"
                    elif setting.element_question.question_key == 'economy_order_table_cost_excl_vat':
                        context['show_cost_excl_vat'] = eval(setting.answer)
                        if context['show_cost_excl_vat']:
                            order_table_visible_columns['show_cost_excl_vat'] = "true"
                    elif setting.element_question.question_key == 'economy_order_table_rebate_amount':
                        context['show_rebate_amount'] = eval(setting.answer)
                        if context['show_rebate_amount']:
                            order_table_visible_columns['show_rebate_amount'] = "true"
                    elif setting.element_question.question_key == 'economy_order_table_vat_amount':
                        context['show_vat_amount'] = eval(setting.answer)
                        if context['show_vat_amount']:
                            order_table_visible_columns['show_vat_amount'] = "true"
                    elif setting.element_question.question_key == 'economy_order_table_vat_rate':
                        context['show_vat_rate'] = eval(setting.answer)
                        if context['show_vat_rate']:
                            order_table_visible_columns['show_vat_rate'] = "true"
                    elif setting.element_question.question_key == 'economy_order_table_cost_incl_vat':
                        context['show_cost_incl_vat'] = eval(setting.answer)
                        if context['show_cost_incl_vat']:
                            order_table_visible_columns['show_cost_incl_vat'] = "true"
                    elif setting.element_question.question_key == 'display_group_order_in_one_order_table':
                        context['group_order_combined'] = eval(setting.answer)
                    elif setting.element_question.question_key == 'economy_download_invoice_changing_status':
                        context['download_invoice_changing_status'] = eval(setting.answer)

                    # elif setting.element_question.question_key == 'economy_order_as':
                    #     context['order_table_type'] = setting.answer
                    elif setting.element_question.question_key == 'economy_include_balance_table':
                        context['balance_table'] = eval(setting.answer)
                    elif setting.element_question.question_key == 'economy_pay_by_card_button_status':
                        context['pay_by_card_button_status'] = eval(setting.answer)
                    elif setting.element_question.question_key == 'economy_generate_last_pdf_button_status':
                        context['last_generated_pdf_button_status'] = eval(setting.answer)
                    elif setting.element_question.question_key == 'economy_balance_table_pdf_button_status':
                        context['balance_table_pdf_button_status'] = eval(setting.answer)
                context['order_table_visible_columns'] = json.dumps(order_table_visible_columns)
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    context['data_user_id'] = user_id
                    no_orders = False
                    if context['order_table']:
                        economy_plugin_data = EconomyLibrary.get_order_tables(user_id, event_id, True)
                        context['order_table_type'] = economy_plugin_data['order_type']
                        if context['group_order_combined'] and context['order_table_type'] == 'group-order':
                            context['orders'] = EconomyLibrary.get_group_order_single_table(
                                economy_plugin_data['order_list'])
                        else:
                            context['orders'] = economy_plugin_data['order_list']
                        if not context['orders']:
                            no_orders = True
                    elif context['balance_table']:
                        # bcoz balance table will be included in order_table
                        context['balance_tables'] = EconomyLibrary.get_balance_tables(user_id, event_id)
                        if not context['balance_tables']:
                            no_orders = True
                    context['no_orders'] = no_orders
                    return render_to_string('public/element/economy.html', context)
                else:
                    context['no_orders'] = True
                    return render_to_string('public/element/economy.html', context)

            else:
                return plugin_div + """<div class="placeholder empty"> %s </div></div>""" % (
                    language['langkey']['economy_txt_empty'])

        except Exception as e:
            ErrorR.efail(e)
            return plugin_div + """<div class="placeholder misconfigured"> %s </div></div>""" % (
                language['langkey']['economy_txt_misconfigured'])

    def economy_change_order_status(request, *args, **kwargs):
        context = {'result': False}
        if 'is_user_login' in request.session and request.session['is_user_login']:
            user_id = request.session['event_user']['id']
            event_id = request.session['event_id']
            order_id = request.POST.get('order_id')
            order_number = request.POST.get('order_number')
            balance_table_pdf_button_status = request.POST.get('show_pdf_buttons')
            if order_number:
                result = EconomyLibrary.change_order_status(order_number=order_number, status='pending',
                                                            event_id=event_id, attendee_id=user_id)
                if result:
                    language = LanguageKey.get_lang_key(request, 41)
                    if result['status'] == 'open':
                        result['status_lang'] = language['langkey']['economy_txt_status_open']
                    elif result['status'] == 'pending':
                        result['status_lang'] = language['langkey']['economy_txt_status_pending']
                    elif result['status'] == 'paid':
                        result['status_lang'] = language['langkey']['economy_txt_status_paid']
                    elif result['status'] == 'cancelled':
                        result['status_lang'] = language['langkey']['economy_txt_status_cancelled']

                    if result['status'] in ['pending', 'paid']:
                        balance_table_data = EconomyLibrary.get_balance_tables(user_id, event_id, order_id)
                        context_for_balance_table = {
                            'language': language,
                            'order': {'balance_table': balance_table_data},
                            'balance_table_pdf_button_status': balance_table_pdf_button_status
                        }
                        result['balance_table_html'] = render_to_string('public/element/balance_table_partial.html',
                                                                        context_for_balance_table)

                    context['result'] = True
                    context['order_info'] = result
                    context['message'] = LanguageKey.catch_lang_key(request, 'economy',
                                                                    'economy_notify_order_status_change')
        return JsonResponse(context)

    def economy_pdf_request(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            event_id = request.session['event_id']
            data_action = request.GET.get('data')
            order_number = request.GET.get('order_number')
            if data_action == 'order-invoice':
                response = EconomyPDFGenerator.get_order_invoice(request, event_id, order_number, attendee_id)
            elif data_action == 'receipt':
                response = EconomyPDFGenerator.get_receipt(request, event_id, order_number, attendee_id)
            elif data_action == 'credit-invoice':
                """ In credit invoice, when group owner remove item in reg-page then user_id needed. """
                if request.GET.get('uid'):
                    attendee_id = request.GET.get('uid')
                response = EconomyPDFGenerator.get_credit_invoice(request, event_id, order_number, attendee_id)
            else:
                response = HttpResponse('Something went wrong.')
        else:
            response = HttpResponse('Something went wrong.')

        return response

    def convert_html_to_pdf(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            try:
                attendee_id = request.session['event_user']['id']
                page_id = request.GET.get('page_id')
                box_id = request.GET.get('box_id')
                element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id,
                                                                  element_question__question_key='pdf_button_template')
                template_id = element_settings[0].answer
                response = EconomyPDFGenerator.get_html_to_pdf(request, attendee_id, template_id)
            except Exception as e:
                ErrorR.efail(e)
                response = HttpResponse('Something went wrong.')
        else:
            response = HttpResponse('Something went wrong.')
        return response

    # def download_page_pdf(request, *args, **kwargs):
    #     try:
    #         if 'is_user_login' in request.session and request.session['is_user_login']:
    #             attendee_id = request.session['event_user']['id']
    #             page_id = request.GET.get('page_id')
    #             page = PageContent.objects.get(id=page_id)
    #             pdf_name = 'page_'+ str(attendee_id)
    #             session = boto3.Session(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    #             s3 = session.client('s3')
    #             key = 'public/' + page.template.event.url + '/files/'+pdf_name+'.txt'
    #             obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    #             html_content = obj['Body'].read().decode('utf-8')
    #             font_config = FontConfiguration()
    #             html = HTML(string=html_content)
    #             result = html.write_pdf(font_config=font_config)
    #             response = HttpResponse(content_type='application/pdf')
    #             response['Content-Disposition'] = 'attachment; filename="{}"'.format("page.pdf")
    #             response['Content-Transfer-Encoding'] = 'binary'
    #             response.write(result)
    #             s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    #             return response
    #     except Exception as e:
    #         ErrorR.efail(e)
    #         return HttpResponse('Something went wrong.')

    def get_logout_plugin(request, *args, **kwargs):
        response_data = {}
        try:
            if 'event_user' in request.session:
                del request.session['event_user']
            if 'is_user_login' in request.session:
                del request.session['is_user_login']
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class MultipleRegistration(generic.DetailView):
    def check_multiple_registration_attendee(request, *args, **kwargs):
        response_data = {}
        try:
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            click_event = request.POST.get('click_event')
            current_attendee = int(request.POST.get('current_attendee'))
            include_owner = request.POST.get('include_owner')
            event_id = request.session['event_id']
            element_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related(
                'element_question')
            min_attendees = 1
            max_attendees = 1
            for setting in element_settings:
                if setting.element_question.question_key == 'multiple_registration_min_attendees':
                    min_attendees = int(setting.answer)
                elif setting.element_question.question_key == 'multiple_registration_max_attendees':
                    max_attendees = int(setting.answer)
                    response_data['max_attendees'] = max_attendees

            response_data['success'] = True
            if current_attendee > max_attendees:
                response_data['success'] = False
                response_data['message'] = "Max Attendee exceeds"
            elif current_attendee < min_attendees:
                response_data['success'] = False
                response_data['message'] = "Min Attendee reduced"
            else:
                if click_event == "append":
                    tem_attendee_obj = Attendee.objects.create(status="pending", event_id=request.session['event_id'],
                                                               language_id=request.session['language_id'])
                    response_data["attendee_id"] = tem_attendee_obj.id
                    if "temp_attendee_id_array" in request.session:
                        request.session["temp_attendee_id_array"].append(tem_attendee_obj.id)
                        request.session.modified = True
                    if "temp_inline_page_url" in request.session:
                        [attendee_page_html, response_data["js"]] = DynamicPage.get_dynamic_attendee_page(
                            request, request.session["temp_inline_page_url"], tem_attendee_obj.id, False)
                        language = LanguageKey.get_lang_key(request,
                                                            Elements.objects.get(slug="multiple-registration").id)
                        total_attendee = current_attendee
                        if include_owner == '1':
                            total_attendee = total_attendee + 1
                        response_data["html"] = render_to_string(
                            'public/element/multiple_registration_append_inline.html',
                            {'user_id': tem_attendee_obj.id, 'html': attendee_page_html, 'language': language,
                             'total_attendees': total_attendee})

                else:
                    attendee_id = int(request.POST.get('attendee_id'))
                    response_data["attendee_id"] = attendee_id
                    attendee = Attendee.objects.get(id=attendee_id)
                    if attendee.status == "pending":
                        attendee.delete()
                        if "temp_attendee_id_array" in request.session:
                            request.session["temp_attendee_id_array"].remove(attendee_id)
                            request.session.modified = True
                    else:
                        activity_history = []
                        registration_group_id = int(attendee.registration_group_id)
                        attendee.registration_group_id = None
                        attendee.save()
                        activity_history.append(ActivityHistory(attendee_id=attendee.id,
                                                                activity_type='delete', category='registration_group',
                                                                registration_group_id=registration_group_id,
                                                                event_id=event_id))
                        attendee_reg_grp = Attendee.objects.filter(registration_group_id=registration_group_id)
                        ErrorR.warn(attendee_reg_grp)
                        if not attendee_reg_grp.exists():
                            ErrorR.c_white("DELETING GRP")
                            RegistrationGroups.objects.filter(id=registration_group_id).update(is_show=0)
                            owner = RegistrationGroupOwner.objects.filter(group_id=registration_group_id)
                            if owner.exists():
                                activity_history = ActivityHistory(attendee_id=owner[0].owner_id,
                                                                   activity_type='delete',
                                                                   category='registration_group',
                                                                   registration_group_id=registration_group_id,
                                                                   event_id=event_id)
                            RegistrationGroupOwner.objects.filter(group_id=registration_group_id).delete()
                        ActivityHistory.objects.bulk_create(activity_history)

        except Exception as e:
            response_data['success'] = False
            response_data['message'] = "Something went wrong"
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_multiple_registration_attendee_form(request, *args, **kwargs):
        response_data = {}
        try:
            page_id = request.POST.get('attendee_page_id')
            attendee_id = request.POST.get('attendee_id')
            page_data = MultipleRegistration.get_page_form(request, page_id, attendee_id)
            response_data['attendee_page'] = page_data['attendee_page']
            response_data['attendee_js'] = page_data['attendee_js']
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_page_form(request, page_id, attendee_id):
        attendee_page_data = PageContent.objects.get(id=int(page_id))
        [attendee_page, attendee_js] = DynamicPage.get_dynamic_attendee_page(request, attendee_page_data.url,
                                                                             attendee_id, False)
        context = {
            'attendee_page': attendee_page,
            'attendee_js': attendee_js
        }
        return context

    def get_attendee_next_page(request, *args, **kwargs):
        response_data = {}
        try:
            page_id = request.POST.get('page_id')
            attendee_id = request.POST.get('attendee_id')
            box_id = request.POST.get('box_id')
            attendee_data = json.loads(request.POST.get('attendee_data'))
            response_data_save_or_update = Registration.save_or_update_multiple_attendee(request, attendee_data)
            if not response_data_save_or_update["success"]:
                return HttpResponse(json.dumps(response_data_save_or_update), content_type="application/json")
            if response_data_save_or_update.get('order_number'):
                response_data['order_number'] = response_data_save_or_update.get('order_number')
            elemet_answer = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            finish_multiple_registration_loop = False
            page_id = 0
            result = False

            for answer in elemet_answer:
                if answer.element_question.question_key == 'submit_button_redirect_page':
                    btn_page_answer = json.loads(answer.answer)[0]
                    if btn_page_answer['state'] == 1:
                        result = False
                    elif btn_page_answer['state'] == 2:
                        result = True
                        page_id = int(btn_page_answer['data']['page_id'])
                        # elif btn_page_answer['state'] == 3:
                        #     response_data['result'] = True
                        #     p_counter = 0
                        #     p_length = len(btn_page_answer['data'])
                        #     for prerequisite in btn_page_answer['data']:
                        #         if p_counter < p_length - 1:
                        #             filters = json.loads(RuleSet.objects.get(id=prerequisite['filter_id']).preset)
                        #             q = Q()
                        #             match_condition = filters[0][0]['matchFor']
                        #             if match_condition == '2':
                        #                 q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                        #             elif match_condition == '1':
                        #                 q = Q(id=-11)
                        #                 q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
                        #
                        #             attendees = Attendee.objects.filter(q)
                        #             att_existence = '1' if attendees.filter(id=user_id).count() > 0 else '0'
                        #             if prerequisite['match'] == att_existence:
                        #                 if prerequisite['page_id'] != '':
                        #                     page_url = PageContent.objects.get(
                        #                         id=int(prerequisite['page_id'])).url
                        #                     response['page'] = Registration.get_redirect_page(request,page_url)
                        #                 break
                        #         else:
                        #             if prerequisite['page_id'] != '':
                        #                 page_url = PageContent.objects.get(id=int(prerequisite['page_id'])).url
                        #                 response['page'] = Registration.get_redirect_page(request,page_url)
                        #         p_counter += 1
                elif answer.element_question.question_key == 'submit_button_finish_multiple_registration_loop':
                    if answer.answer == 'True':
                        finish_multiple_registration_loop = True

            if not finish_multiple_registration_loop:
                if page_id != 0:
                    page_data = MultipleRegistration.get_page_form(request, page_id, attendee_id)
                    response_data['attendee_page'] = page_data['attendee_page']
                    response_data['attendee_js'] = page_data['attendee_js']
                    response_data['next_page'] = True
                else:
                    response_data['next_page'] = False
            else:
                response_data['next_page'] = False
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class PageWithLanguage(generic.DetailView):
    def change_language(request, *args, **kwargs):
        response = {}
        try:
            language_id = request.POST.get('language_id')
            page_url = request.POST.get('page_url')
            request.session['language_id'] = language_id
            request.session.modified = True
            notification_langs = LanguageKey.catch_lang_key_multiple(request, 'notification',
                                                                     ['notify_title_success', 'notify_title_warning',
                                                                      'notify_title_error', 'notify_title_notify'])
            request.growl_success = notification_langs['langkey']['notify_title_success']
            request.growl_warning = notification_langs['langkey']['notify_title_warning']
            request.growl_error = notification_langs['langkey']['notify_title_error']
            request.growl_notify = notification_langs['langkey']['notify_title_notify']
            request.session.modified = True
            if 'is_user_login' in request.session and request.session['is_user_login']:
                Attendee.objects.filter(id=request.session['event_user']['id']).update(language_id=language_id)
            if page_url == "" or page_url == None:
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    page_url = "logged-in"
                else:
                    page_url = "start"
            [page, js] = DynamicPage.get_dynamic_page_filtered_obj(request, page_url)
            request.menus = PageWithLanguage.get_menu_with_language(request)
            menus = render_to_string('public/content/menu.html', {'request': request})
            current_language = request.session['language_id']
            current_preset = Presets.objects.get(id=current_language)
            languages = PageReplace.get_all_language(request, current_preset)
            response['page'] = page
            response['menus'] = menus
            response['languages'] = languages
            response['js'] = js
            response['growl_success'] = request.growl_success
            response['growl_warning'] = request.growl_warning
            response['growl_error'] = request.growl_error
            response['growl_notify'] = request.growl_notify
            response['success'] = True
        except Exception as e:
            response['success'] = False
            ErrorR.efail(e)
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_menu_with_language(request):
        menus = UserRule.get_menu_permissions(request)
        all_menus = PageWithLanguage.get_all_menu(request, menus['menu_permissions'], menus['my_rule_set'],
                                                  request.session['event_id'])
        return all_menus

    def get_all_menu(request, mainMenu, rule_set, event_id):
        today_date = datetime.now()
        language_id = request.session['language_id']
        my_rule_set = rule_set
        for menu in mainMenu:
            if menu.menu.title_lang != '' and menu.menu.title_lang != None:
                try:
                    menu_title_lang = json.loads(menu.menu.title_lang, strict=False)
                    if menu_title_lang[str(language_id)]:
                        menu.menu.title = menu_title_lang[str(language_id)]
                except Exception as e:
                    pass
            menu_id = menu.menu.id
            # my_rule_set = []
            # attendee_id = 0
            # if 'is_user_login' in request.session and request.session['is_user_login']:
            #     attendee_id = request.session['event_user']['id']
            #     rule_sets = RuleSet.objects.filter(group__event_id=event_id)
            #     for rule in rule_sets:
            #         filters = json.loads(rule.preset)
            #         q = Q()
            #         match_condition = filters[0][0]['matchFor']
            #         if match_condition == '2':
            #             q &= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
            #         elif match_condition == '1':
            #             q = Q(id=-11)
            #             q |= Q(id__in=UserRule.get_filtered_attendee(request, filters, match_condition))
            #         attendees = Attendee.objects.filter(q)
            #
            #         if attendees.filter(id=attendee_id).count() > 0:
            #             my_rule_set.append(rule.id)

            if 'is_user_login' in request.session and request.session['is_user_login']:
                menu_items = MenuPermission.objects.filter(
                    (Q(rule_id__in=my_rule_set) | Q(menu__allow_unregistered=True) | Q(rule_id=None)),
                    menu__parent_id=menu_id,
                    menu__is_visible=1, menu__start_time__lt=today_date,
                    menu__end_time__gt=today_date,
                    menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')
            else:
                menu_items = MenuPermission.objects.filter(
                    (Q(rule_id__in=my_rule_set) | Q(menu__allow_unregistered=True)), menu__parent_id=menu_id,
                    menu__is_visible=1, menu__start_time__lt=today_date,
                    menu__end_time__gt=today_date,
                    menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')
            menu.items = []
            for m in menu_items:
                menu.items.extend(MenuPermission.objects.filter(id=m['id']))
            for item in menu.items:
                if item.menu.title_lang != '' and item.menu.title_lang != None:
                    try:
                        item_title_lang = json.loads(item.menu.title_lang, strict=False)
                        if item_title_lang[str(language_id)]:
                            item.menu.title = item_title_lang[str(language_id)]
                    except:
                        pass
                item_id = item.menu.id
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    menu_items = MenuPermission.objects.filter(
                        (Q(rule_id__in=my_rule_set) | Q(menu__allow_unregistered=True) | Q(rule_id=None)),
                        menu__parent_id=item_id,
                        menu__is_visible=1, menu__start_time__lt=today_date,
                        menu__end_time__gt=today_date,
                        menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')
                else:
                    menu_items = MenuPermission.objects.filter(
                        (Q(rule_id__in=my_rule_set) | Q(menu__allow_unregistered=True)), menu__parent_id=item_id,
                        menu__is_visible=1, menu__start_time__lt=today_date,
                        menu__end_time__gt=today_date,
                        menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')

                item.items = []
                for m in menu_items:
                    item.items.extend(MenuPermission.objects.filter(id=m['id']))
                if len(item.items) > 0:
                    PageWithLanguage.get_all_menu(request, item.items, rule_set, event_id)

        return mainMenu

    def get_date_with_language(request, *args, **kwargs):
        response = {}
        try:
            request_date = request.POST.get('request_date')
            language_id = request.session['language_id']
            current_language = Presets.objects.get(id=language_id)
            request_date = datetime.strptime(request_date, '%Y-%m-%d')
            context = {
                'current_language': current_language,
                'request_date': request_date
            }
            converted_date = render_to_string('public/content/language_date.html', context)
            response['converted_date'] = converted_date
            response['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return HttpResponse(json.dumps(response), content_type="application/json")


class QRResponse(generic.View):
    def get(self, request, *args, **kwargs):
        try:
            if "bid" in request.GET:
                bid = request.GET.get("bid")
                if bid != "":
                    import qrcode
                    import io
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
                    return HttpResponse(output_s, content_type="image/png")
        except Exception as e:
            ErrorR.efail(e)
        return HttpResponse("", content_type="image/png")
