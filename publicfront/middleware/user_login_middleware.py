from django.views import generic
from app.models import Attendee, Answers, SeminarSpeakers, Notification, MenuPermission, MenuItem, Events, RuleSet, Setting, PresetEvent, \
    Presets
import os.path
from django.core.urlresolvers import resolve
from django.db.models import Q
import boto
from boto.s3.key import Key
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404
from publicfront.views.rule import UserRule
from publicfront.views.lang_key import LanguageKey
import json
import time
import logging
from publicfront.views.helper import HelperData
from django.contrib import messages
from app.views.gbhelper.error_report_helper import ErrorR
from django.db.models import Count,Avg,Max


class UserLoginMiddleware(generic.DetailView):
    def process_request(self, request):
        start_time = time.time()
        path = request.path.split('/')[1]
        # browser_current_url = resolve(request.path_info).url_name
        if path != '' and path != 'device' and path != 'health':
            url_info = resolve(request.path_info)
            browser_current_url = url_info.url_name
            if path == 'admin':
                settings.USE_TZ = False
                if request.is_ajax() == False:
                    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
                    cookie_seconds = 86400
                    # settings.SESSION_COOKIE_AGE =100
                    # settings.SESSION_SAVE_EVERY_REQUEST = True
                    if 'event_auth_user' in request.session and 'event_id' in request.session['event_auth_user'] and 'is_login' in request.session and request.session['is_login']:
                        admin_events = Events.objects.filter(id=request.session['event_auth_user']['event_id'])
                        if admin_events.exists():
                            request.session['event_auth_user']['event_url'] = admin_events[0].url
                        request.session.modified = True
                        cookie_expire = Setting.objects.filter(name='cookie_expire', event_id=request.session['event_auth_user']['event_id'])
                        if cookie_expire.exists():
                            cookie_expire_time = cookie_expire[0].value
                            if len(cookie_expire_time.split(':')) > 1:
                                time_format = [3600, 60, 1]
                                cookie_seconds = sum(
                                    [a * b for a, b in zip(time_format, map(int, cookie_expire_time.split(':')))])
                            else:
                                cookie_seconds = cookie_expire_time
                        else:
                            cookie_seconds = 864000
                    settings.SESSION_COOKIE_AGE = int(cookie_seconds)
                    request.session['cookie_expire'] = cookie_seconds
                    if browser_current_url != 'login' and browser_current_url != 'reset-password' and browser_current_url != 'reset-your-password':
                        if 'is_login' not in request.session or not request.session['is_login']:
                            return redirect('login')
            elif path == 'retrieve-password':
                settings.USE_TZ = False
            else:
                settings.USE_TZ = False
                # today_date = datetime.now()
                if request.is_ajax() == False:
                    keyword_arguments = url_info.kwargs
                    if 'event_url' in keyword_arguments:
                        event_url = keyword_arguments['event_url']
                    else:
                        event_url = path

                    socket_url = 'ws://127.0.0.1'
                    base_url = settings.SITE_URL+'/'+str(event_url)
                    webcal_url= 'webcal://127.0.0.1'+'/'+str(event_url)

                    request.session['event_url'] = event_url
                    request.session['base_url'] = base_url
                    request.session['socket_url'] = socket_url
                    request.session['webcal_url'] = webcal_url
                    request.session.modified = True
                    event_data = Events.objects.filter(url=event_url)
                    if event_data.exists():
                        event_id = event_data[0].id
                    else:
                        raise Http404

                    if 'event_id' in request.session:
                        if str(request.session['event_id']) != str(event_id):
                            if 'is_user_login' in request.session:
                                del request.session['is_user_login']
                            if 'event_user' in request.session:
                                del request.session['event_user']
                            # request.session.modified = True
                            if 'language_id' in request.session:
                                del request.session['language_id']
                    if browser_current_url == 'static-pages':
                        current_url = url_info.kwargs['staticPage']
                    else:
                        current_url = browser_current_url
                    request.session['current_url'] = current_url
                    request.session.modified = True
                    request.current_path_name = current_url
                    page_accept_login = 0
                    browser_page_current_url = MenuItem.objects.filter(Q(url=current_url) | Q(content__url=current_url), event_id=event_id)
                    if browser_page_current_url.exists():
                        page_accept_login = browser_page_current_url[0].accept_login
                    logout_param = False
                    if 'logout' in request.GET and request.GET.get('logout') == 'true':
                        logout_param = True
                    if current_url == 'logout' or logout_param:
                        if 'event_user' in request.session:
                            del request.session['event_user']
                        if 'is_user_login' in request.session:
                            del request.session['is_user_login']
                    if page_accept_login == 1 or current_url == 'admin-attendee-logged-in' or current_url == 'activation' or current_url == 'session-help' or current_url == 'welcome' or current_url == 'notifications' or current_url == 'public-session-detail' or current_url == 'my-kingfomarket' or current_url == 'gt-welcome' or current_url == 'export-for-offline' or current_url == 'webcal' or current_url == 'gt-summering' or current_url == 'ff' or current_url == 'messages':
                        if 'is_user_login' in request.session and request.session['is_user_login']:
                            if 'uid' in request.GET:
                                user_key = request.GET.get('uid')
                                if user_key != request.session['event_user']['secret_key']:
                                    user = Attendee.objects.filter(secret_key=user_key, event_id=event_id)
                                    if user.exists():
                                        del request.session['event_user']
                                        del request.session['is_user_login']
                                        first_name = Answers.objects.filter(question__actual_definition='firstname',
                                                                            user_id=user[0].id)
                                        last_name = Answers.objects.filter(question__actual_definition='lastname',
                                                                           user_id=user[0].id)
                                        attending = 'Yes'
                                        if first_name.exists():
                                            fname = first_name[0].value
                                        else:
                                            fname = user[0].firstname
                                        if last_name.exists():
                                            lname = last_name[0].value
                                        else:
                                            lname = user[0].lastname
                                        if os.environ['ENVIRONMENT_TYPE'] != 'master' and os.environ[
                                            'ENVIRONMENT_TYPE'] != 'staging' and os.environ['ENVIRONMENT_TYPE'] != 'develop':
                                            avatar = ''
                                        else:
                                            if user[0].avatar != '':
                                                avatar = user[0].avatar
                                                conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                                                       settings.AWS_SECRET_ACCESS_KEY)
                                                bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                                                filename = 'public/images/attendee/attendee_' + str(user[0].id) + '.jpg'
                                                key_name = filename
                                                k = Key(bucket)
                                                k.key = key_name
                                                if not k.exists():
                                                    avatar = ''
                                            else:
                                                avatar = ''
                                        attendee_type = user[0].type
                                        speakers = SeminarSpeakers.objects.filter(speaker_id=user[0].id)
                                        notification = Notification.objects.filter(to_attendee_id=user[0].id, status=0)
                                        new_noty = 0
                                        if notification.count() > 0:
                                            new_noty = notification[notification.count() - 1].id
                                        if speakers.exists():
                                            attendee_type = "speaker"
                                        auth_user = {
                                            "id": user[0].id,
                                            "name": fname + ' ' + lname,
                                            "email": user[0].email,
                                            "type": attendee_type,
                                            "attending": attending,
                                            "avatar": avatar,
                                            "secret_key": user[0].secret_key,
                                            "event_id": user[0].event.id
                                        }
                                        request.session['event_user'] = auth_user
                                        request.session['event_user']['new_sessions_finished'] = []
                                        request.session['event_user']['new_sessions_next_up'] = []
                                        request.session['is_user_login'] = True

                        elif 'uid' in request.GET:
                            user_key = request.GET.get('uid')
                            user = Attendee.objects.filter(secret_key=user_key, event_id=event_id)
                            if user.exists():
                                first_name = Answers.objects.filter(question__actual_definition='firstname', user_id=user[0].id)
                                last_name = Answers.objects.filter(question__actual_definition='lastname', user_id=user[0].id)

                                attending = 'Yes'
                                if first_name.exists():
                                    fname = first_name[0].value
                                else:
                                    fname = user[0].firstname
                                if last_name.exists():
                                    lname = last_name[0].value
                                else:
                                    lname = user[0].lastname
                                if os.environ['ENVIRONMENT_TYPE'] != 'master' and os.environ[
                                    'ENVIRONMENT_TYPE'] != 'staging' and os.environ['ENVIRONMENT_TYPE'] != 'develop':
                                    avatar = ''
                                else:
                                    if user[0].avatar != '':
                                        avatar = user[0].avatar
                                        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                                        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                                        filename = 'public/images/attendee/attendee_' + str(user[0].id) + '.jpg'
                                        key_name = filename
                                        k = Key(bucket)
                                        k.key = key_name
                                        if not k.exists():
                                            avatar = ''
                                    else:
                                        avatar = ''
                                attendee_type = user[0].type
                                speakers = SeminarSpeakers.objects.filter(speaker_id=user[0].id)
                                notification = Notification.objects.filter(to_attendee_id=user[0].id, status=0)
                                new_noty = 0
                                if notification.count() > 0:
                                    new_noty = notification[notification.count() - 1].id
                                if speakers.exists():
                                    attendee_type = "speaker"
                                auth_user = {
                                    "id": user[0].id,
                                    "name": fname + ' ' + lname,
                                    "email": user[0].email,
                                    "type": attendee_type,
                                    "attending": attending,
                                    "avatar": avatar,
                                    "secret_key": user[0].secret_key,
                                    "event_id": user[0].event.id
                                }
                                request.session['event_user'] = auth_user
                                request.session['event_user']['new_sessions_finished'] = []
                                request.session['event_user']['new_sessions_next_up'] = []
                                request.session['is_user_login'] = True
                    request.session['event_id'] = event_id
                    request.session.modified = True
                    try:
                        if 'is_user_login' in request.session and request.session['is_user_login']:
                            attendee_id = request.session['event_user']['id']
                            current_attendee = Attendee.objects.get(id=attendee_id)
                            current_language = current_attendee.language_id
                            request.session['language_id'] = current_language
                        else:
                            presetsEvent = PresetEvent.objects.filter(event_id=event_id).first()
                            request.session['language_id'] = presetsEvent.preset_id
                    except Exception as e:
                        print(e)
                        request.session['language_id'] = 6
                    if 'languageid' in request.GET:
                        temp_language_id = request.GET.get('languageid')
                        try:
                            if Presets.objects.filter(id=int(temp_language_id),event_id=event_id).exists():
                                request.session['language_id'] = temp_language_id
                        except:
                            pass
                    request.session.modified = True
                    notification_langs = LanguageKey.catch_lang_key_multiple(request, 'notification', ['notify_title_success','notify_title_warning','notify_title_error','notify_title_notify'])
                    request.growl_success = notification_langs['langkey']['notify_title_success']
                    request.growl_warning = notification_langs['langkey']['notify_title_warning']
                    request.growl_error = notification_langs['langkey']['notify_title_error']
                    request.growl_notify = notification_langs['langkey']['notify_title_notify']
                    if 'is_user_login' in request.session and request.session['is_user_login']:
                        cookie_expire = Setting.objects.filter(name='cookie_expire', event_id=request.session['event_id'])
                        if cookie_expire.exists():
                            cookie_expire_time = cookie_expire[0].value
                            if len(cookie_expire_time.split(':')) > 1:
                                time_format = [3600, 60, 1]
                                cookie_seconds = sum(
                                    [a * b for a, b in zip(time_format, map(int, cookie_expire_time.split(':')))])
                            else:
                                cookie_seconds = cookie_expire_time
                        else:
                            cookie_seconds = 86400
                    else:
                        cookie_seconds = 86400
                    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
                    # settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
                    # settings.SESSION_SAVE_EVERY_REQUEST = False
                    # settings.SESSION_COOKIE_AGE = 100
                    settings.SESSION_COOKIE_AGE = int(cookie_seconds)
                    # menus= UserRule.get_menu_permissions(request)
                    request.session['cookie_expire'] = cookie_seconds
                    # request.menus = UserLoginMiddleware.get_menu(request, menus['menu_permissions'], menus['my_rule_set'], event_id)
                    if 'uid' in request.GET:
                        menu_url = MenuItem.objects.filter(url=current_url, menupermission__rule__group__event_id=event_id)
                        if menu_url.exists():
                            if menu_url[0].uid_include == 0:
                                if request.session['event_url'] == 'kingfomarket':
                                    if browser_current_url == 'static-page':
                                        return redirect(browser_current_url, staticPage=current_url, event_url=request.session['event_url'])
                                    else:
                                        return redirect("static-pages",staticPage=current_url, event_url=request.session['event_url'])
                                else:
                                    if browser_current_url == 'static-page' or browser_current_url == 'gt-static-page':
                                        return redirect(browser_current_url, staticPage=current_url, event_url=request.session['event_url'])
                                    else:
                                        return redirect("static-pages",staticPage=current_url,event_url=request.session['event_url'])
                        else:
                            page_url = MenuItem.objects.filter(content__url=current_url, menupermission__rule__group__event_id=event_id)
                            if page_url.exists():
                                if page_url[0].uid_include == 0:
                                    if request.session['event_url'] == 'kingfomarket':
                                        if browser_current_url == 'static-page':
                                            return redirect(browser_current_url, staticPage=current_url, event_url=request.session['event_url'])
                                        else:
                                            return redirect("static-pages",staticPage=current_url, event_url=request.session['event_url'])
                                    else:
                                        if browser_current_url == 'static-page' or browser_current_url == 'gt-static-page':
                                            return redirect(browser_current_url, staticPage=current_url)
                                        else:
                                            return redirect("static-pages",staticPage=current_url,event_url=request.session['event_url'])
        ErrorR.okblue("Middleware time")
        ErrorR.okblue(time.time()-start_time)

    def process_response(self, request, response):
        path = request.path.split('/')[1]
        response['Pragma'] = 'no-cache'
        if path == 'admin' or path == '' or path == 'device' or path == 'retrieve-password' or path == 'health':
            response['Cache-Control'] = 'no-cache must-revalidate proxy-revalidate'
        else:
            response['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
        return response

    def get_menu(request, mainMenu, rule_set, event_id):
        # today_date = datetime.now()
        today_date = HelperData.getTimezoneNow(request)
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
            #     attendee_id= request.session['event_user']['id']
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
            #         if attendees.filter(id=attendee_id).count()>0:
            #             my_rule_set.append(rule.id)
            if 'is_user_login' in request.session and request.session['is_user_login']:
                menu_items = MenuPermission.objects.filter((Q(rule_id__in=my_rule_set)|Q(menu__allow_unregistered=True)|Q(rule_id=None)),menu__parent_id=menu_id,
                                                           menu__is_visible=1, menu__start_time__lt=today_date,
                                                           menu__end_time__gt=today_date,
                                                           menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')
            else:
                menu_items = MenuPermission.objects.filter((Q(rule_id__in=my_rule_set)|Q(menu__allow_unregistered=True)),menu__parent_id=menu_id,
                                                           menu__is_visible=1, menu__start_time__lt=today_date,
                                                           menu__end_time__gt=today_date,
                                                           menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')
            menu.items=[]
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
                    menu_items = MenuPermission.objects.filter((Q(rule_id__in=my_rule_set)|Q(menu__allow_unregistered=True)|Q(rule_id=None)),menu__parent_id=item_id,
                                                               menu__is_visible=1, menu__start_time__lt=today_date,
                                                               menu__end_time__gt=today_date,
                                                               menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')
                else:
                    menu_items = MenuPermission.objects.filter((Q(rule_id__in=my_rule_set)|Q(menu__allow_unregistered=True)),menu__parent_id=item_id,
                                                           menu__is_visible=1, menu__start_time__lt=today_date,
                                                           menu__end_time__gt=today_date,
                                                           menu__event_id=event_id).values('menu_id').annotate(id=Max('id')).order_by('menu__rank')

                item.items=[]
                for m in menu_items:
                    item.items.extend(MenuPermission.objects.filter(id=m['id']))


                # item.items = MenuPermission.objects.all().values('id','menu_id').annotate(Count('id'))
                # duplicates = MenuPermission.objects.values('menu_id').annotate(id=Max('id'),).order_by()
                # item.items.exclude(duplicates)
                if len(item.items) > 0:
                    UserLoginMiddleware.get_menu(request, item.items, rule_set, event_id)

        return mainMenu
