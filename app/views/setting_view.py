from django.shortcuts import render
from django.views import generic
from app.models import Group, Setting, Room, Tag, Events, Presets, PresetEvent, \
    EmailContents, ContentPermission, GroupPermission
from .common_views import GroupView, EventView
from django.http import HttpResponse, JsonResponse
import json, pytz, time
from datetime import datetime
from app.views.page_view import PageDetailView
from django.db.models import Q
from django.db import connection
from app.views.gbhelper.language_helper import LanguageH


class SettingView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'setting_permission'):
            attendeeGroup = GroupView.get_attendeeGroup(request)
            sessionGroup = GroupView.get_sessionGroup(request)
            hotelGroup = GroupView.get_hotelGroup(request)
            filterGroup = GroupView.get_filterGroup(request)
            exportFilterGroup = GroupView.get_exportfilterGroup(request)
            paymentGroup = GroupView.get_paymentGroup(request)
            questionGroup = GroupView.get_questionGroup(request)
            locationGroup = GroupView.get_locationGroup(request)
            travelGroup = GroupView.get_travelGroup(request)
            menuGroup = GroupView.get_menuGroup(request)
            allowedEmail = GroupView.get_allowedEmail(request)
            event_id = request.session['event_auth_user']['event_id']
            slider_duration = Setting.objects.filter(name='photo_slider_duration', event_id=event_id)
            projects = Events.objects.filter(is_show=1)
            default_project = Setting.objects.filter(name='default_project')
            presets = Presets.objects.filter(Q(event_id=event_id) | Q(event_id=None))
            presetsEvent = PresetEvent.objects.filter(event_id=event_id)
            if presetsEvent.exists():
                presetsEvent = presetsEvent[0]
            else:
                presetsEvent = None
            if default_project.exists():
                defailt_project_url = default_project[0].value
            else:
                defailt_project_url = ''
            setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
            if setting:
                timeout = setting[0].value
            else:
                timeout = 0
            appear_next_up = 0
            appear_next_up_setting = Setting.objects.filter(name='appear_next_up_setting', event_id=event_id)
            if appear_next_up_setting.exists():
                appear_next_up = appear_next_up_setting[0].value
            disappear_next_up = 0
            disappear_next_up_setting = Setting.objects.filter(name='disappear_next_up_setting', event_id=event_id)
            if disappear_next_up_setting.exists():
                disappear_next_up = disappear_next_up_setting[0].value
            appear_evaluation = 0
            appear_evaluation_setting = Setting.objects.filter(name='appear_evaluation_setting', event_id=event_id)
            if appear_evaluation_setting.exists():
                appear_evaluation = appear_evaluation_setting[0].value

            setting_timezone = Setting.objects.filter(name='timezone', event_id=event_id)
            if setting_timezone:
                timezone_now = setting_timezone[0].value
            else:
                timezone_now = ""

            timezones = []
            for tz in pytz.common_timezones:
                now = datetime.now(pytz.timezone(tz))
                ofs = now.strftime("%z")
                timezone = {
                    "timezone": tz,
                    "offset": ofs[:3] + ":" + ofs[3:]
                }
                timezones.append(timezone)

            setting_week_start_day = Setting.objects.filter(name='week_start_day', event_id=event_id)
            if setting_week_start_day:
                week_start_day = setting_week_start_day[0].value
            else:
                week_start_day = "mon"

            setting_plugin_language = Setting.objects.filter(name='plugin_language', event_id=event_id)
            if setting_plugin_language:
                plugin_language = setting_plugin_language[0].value
            else:
                plugin_language = "en"

            setting_default_date_format = Setting.objects.filter(name='default_date_format', event_id=event_id)
            if setting_default_date_format:
                default_date_format = setting_default_date_format[0].value
            else:
                default_date_format = '{"kendo":"MM-dd-yyyy","python":"m-d-Y"}'

            setting_temp_attendee_expire_time = Setting.objects.filter(name='temporary_attendee_expire_time', event_id=event_id)
            if setting_temp_attendee_expire_time:
                temporary_attendee_expire_time = int(int(setting_temp_attendee_expire_time[0].value) / 60000)
            else:
                temporary_attendee_expire_time = "5"

            setting_uid_length = Setting.objects.filter(name='uid_length', event_id=event_id)
            if setting_uid_length:
                uid_length = setting_uid_length[0].value
            else:
                uid_length = "16"

            setting_start_order_number = Setting.objects.filter(name='start_order_number', event_id=event_id)
            if setting_start_order_number:
                start_order_number = setting_start_order_number[0].value
            else:
                start_order_number = "{}-0000001".format(event_id)

            setting_due_date = Setting.objects.filter(name='due_date', event_id=event_id)
            if setting_due_date:
                due_date = setting_due_date[0].value
            else:
                due_date = "0"

            setting_allow_same_email = Setting.objects.filter(name='allow_same_email_multiple_registration', event_id=event_id)
            allow_same_email_multiple_registration = True if setting_allow_same_email and setting_allow_same_email[0].value == 'true' else False

            all_rooms = Room.objects.filter(hotel__group__event_id=event_id)
            setting_email = Setting.objects.filter(name='sender_email', event_id=event_id)
            if setting_email:
                sender_email = setting_email[0].value
            else:
                sender_email = "mahedi@workspaceit.com"
            email_confirmations = EmailContents.objects.filter(template__event_id=event_id, is_show=1)
            attendee_add_confirmation = 0
            attendee_edit_confirmation = 0
            session_no_conflict_confirmation = 0
            session_conflict_confirmation = 0
            attendeeAddConfirmation = Setting.objects.filter(name="attendee_add_confirmation", event_id=event_id)
            if attendeeAddConfirmation.exists():
                attendee_add_confirmation = attendeeAddConfirmation[0].value
            attendeeEditConfirmation = Setting.objects.filter(name="attendee_edit_confirmation", event_id=event_id)
            if attendeeEditConfirmation.exists():
                attendee_edit_confirmation = attendeeEditConfirmation[0].value
            sessionNoConflictConfirmation = Setting.objects.filter(name="session_no_conflict_confirmation", event_id=event_id)
            if sessionNoConflictConfirmation.exists():
                session_no_conflict_confirmation = sessionNoConflictConfirmation[0].value
            sessionConflictConfirmation = Setting.objects.filter(name="session_conflict_confirmation", event_id=event_id)
            if sessionConflictConfirmation.exists():
                session_conflict_confirmation = sessionConflictConfirmation[0].value
            setting_cookie_expire = Setting.objects.filter(name='cookie_expire', event_id=event_id)
            cookie_expire_year = False
            if setting_cookie_expire:
                cookie_expire = setting_cookie_expire[0].value
                if cookie_expire == "31536000":
                    cookie_expire_year = True
                if len(cookie_expire.split(':')) > 1:
                    cookie_expire = cookie_expire
                else:
                    cookie_expire = int(int(cookie_expire) / 60)
            else:
                cookie_expire = ""
            global_session_settings = {}
            global_session_details_settings = Setting.objects.filter(name="session_global_settings", event_id=event_id)
            if global_session_details_settings.exists():
                session_settings = json.loads(global_session_details_settings[0].value)
                for details in session_settings:
                    global_session_settings[details] = True

            global_location_settings = {}
            global_location_details_settings = Setting.objects.filter(name="location_global_settings", event_id=event_id)
            if global_location_details_settings.exists():
                location_settings = json.loads(global_location_details_settings[0].value)
                for details in location_settings:
                    global_location_settings[details] = True

            global_order_table_settings = {}
            global_order_table_columns_settings = Setting.objects.filter(name="economy_order_table_global_settings", event_id=event_id)
            if global_order_table_columns_settings.exists():
                order_table_settings = json.loads(global_order_table_columns_settings[0].value)
                for columns in order_table_settings:
                    global_order_table_settings[columns] = True



            context = {
                'attendeeGroup': attendeeGroup,
                'sessionGroup': sessionGroup,
                'hotelGroup': hotelGroup,
                'filterGroup': filterGroup,
                'paymentGroup': paymentGroup,
                'questionGroup': questionGroup,
                'locationGroup': locationGroup,
                'travelGroup': travelGroup,
                'allowedEmail': allowedEmail,
                'notification_timeout': timeout,
                'slider_duration': slider_duration,
                'exportFilterGroup': exportFilterGroup,
                'menuGroup': menuGroup,
                'timezone_now': timezone_now,
                'timezones': timezones,
                'week_start_day': week_start_day,
                'plugin_language': plugin_language,
                'default_date_format': default_date_format,
                'temporary_attendee_expire_time': temporary_attendee_expire_time,
                'uid_length': uid_length,
                'rooms': all_rooms,
                'projects': projects,
                'defailt_project_url': defailt_project_url,
                'presets': presets,
                'presetsEvent': presetsEvent,
                'sender_email': sender_email,
                'email_confirmations': email_confirmations,
                'attendee_add_confirmation': attendee_add_confirmation,
                'attendee_edit_confirmation': attendee_edit_confirmation,
                'session_no_conflict_confirmation': session_no_conflict_confirmation,
                'session_conflict_confirmation': session_conflict_confirmation,
                'appear_next_up': appear_next_up,
                'disappear_next_up': disappear_next_up,
                'appear_evaluation': appear_evaluation,
                'cookie_expire': cookie_expire,
                'cookie_expire_year': cookie_expire_year,
                'global_session_settings': global_session_settings,
                'global_location_settings': global_location_settings,
                'global_order_table_settings': global_order_table_settings,
                'start_order_number': start_order_number,
                'due_date': due_date,
                'allow_same_email_multiple_registration': allow_same_email_multiple_registration
            }
            context.update(LanguageH.get_current_and_all_presets(request))
            return render(request, 'setting/settings.html', context)

    def post(self, request):
        start_time = time.time()
        response_data = {}
        response_data['warnings'] = []
        if EventView.check_permissions(request, 'setting_permission'):
            event = request.POST.get('event')
            groups = json.loads(request.POST.get('groups'))
            current_language_id = request.POST.get('current_language_id')
            event_id = request.session['event_auth_user']['event_id']
            default_language_id = LanguageH.get_current_language_id(request.session['event_auth_user']['event_id'])
            new_settings = []
            updated_settings = ""
            updated_setting_ids = []
            cursor = connection.cursor()
            group_response = SettingView.addGroup(request, groups, event)
            searchable_list = json.loads(request.POST.get('group_searchable_List'))
            sql_case_array = []
            group_ids = []
            new_time = time.time()
            sql_name_case = ""
            sql_name_lang_case = ""
            for searchable_group in searchable_list:
                if not (Group.objects.filter(name=searchable_group['group_name'], type=searchable_group['group_type'], event_id=request.session['event_auth_user']['event_id'], is_show=1).exclude(id=searchable_group['id']).exists()):
                    if searchable_group['group_type'] == 'email' or searchable_group['group_type'] == 'payment':
                        sql_name_case +="WHEN id = "+searchable_group['id']+" THEN '"+searchable_group['group_name']+"' "
                    else:
                        if current_language_id == default_language_id:
                            sql_name_case += "WHEN id = " + searchable_group['id'] + " THEN '" + searchable_group['group_name'] + "' "
                        else:
                            sql_name_case += "WHEN id = " + searchable_group['id'] + " THEN '" + searchable_group['group_prev_name'] + "' "
                    if "group_name_lang" in searchable_group:
                        if searchable_group['group_name_lang'] != '' and searchable_group['group_name_lang'] != None:
                            name_lang = json.loads(searchable_group['group_name_lang'], strict=False)
                            name_lang[str(current_language_id)] = searchable_group['group_name']
                        else:
                            name_lang = {str(current_language_id): searchable_group['group_name']}
                        name_lang = str(name_lang).replace("'", '"')
                        sql_name_lang_case += "WHEN id = " + searchable_group['id'] + " THEN '" + str(name_lang) + "' "
                    group_ids.append(int(searchable_group['id']))
            if sql_name_case != '':
                sql_case_array.append('name = CASE '+sql_name_case+'END')
            if sql_name_lang_case != '':
                sql_case_array.append('name_lang = CASE ' + sql_name_lang_case + 'END')
            sql_group_query = ','.join(sql_case_array)
            if sql_group_query != '':
                group_update_sql = 'update groups set '+sql_group_query+' WHERE id IN ('+str(group_ids).replace("[","").replace("]","")+')'
                cursor.execute(group_update_sql)
            color_list = json.loads(request.POST.get('session_color_List'))
            for color_group in color_list:
                Group.objects.filter(id=color_group['id']).update(color=color_group['color'])

            timeout = request.POST.get('timeout')
            setting = SettingView.save_or_update_settings(request,'notification_timeout',timeout,new_settings,updated_settings,updated_setting_ids)

            sender_email = request.POST.get('sender_email')
            setting = SettingView.save_or_update_settings(request,'sender_email',sender_email,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            email_contents = EmailContents.objects.filter(template__event_id=event_id)
            for email in email_contents:
                EmailContents.objects.filter(id=email.id).update(sender_email=sender_email)

            appear_next_up_setting = request.POST.get('appear_next_up_setting')
            setting = SettingView.save_or_update_settings(request,'appear_next_up_setting',appear_next_up_setting,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            disappear_next_up_setting = request.POST.get('disappear_next_up_setting')
            setting = SettingView.save_or_update_settings(request,'disappear_next_up_setting',disappear_next_up_setting,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            appear_evaluation_setting = request.POST.get('appear_evaluation_setting')
            setting = SettingView.save_or_update_settings(request,'appear_evaluation_setting',appear_evaluation_setting,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            timezone = request.POST.get('timezone')
            setting = SettingView.save_or_update_settings(request,'timezone',timezone,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            uid_length = request.POST.get('uid_length')
            setting = SettingView.save_or_update_settings(request, 'uid_length', uid_length,setting['new_settings'], setting['updated_settings'],setting['updated_setting_ids'])

            week_start_day = request.POST.get('week_start_day')
            setting = SettingView.save_or_update_settings(request,'week_start_day',week_start_day,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            plugin_language = request.POST.get('plugin_language')
            setting = SettingView.save_or_update_settings(request,'plugin_language',plugin_language,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            default_date_format = request.POST.get('default_date_format')
            setting = SettingView.save_or_update_settings(request,'default_date_format',default_date_format,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            # converting minute to milliseconds
            temporary_attendee_expire_time = str(int(request.POST.get('temporary_attendee_expire_time')) * 60000)
            setting = SettingView.save_or_update_settings(request,'temporary_attendee_expire_time',temporary_attendee_expire_time,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            duration = request.POST.get('duration')
            setting = SettingView.save_or_update_settings(request,'photo_slider_duration',duration,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            default_project = request.POST.get('default_project')
            setting = SettingView.save_or_update_settings(request,'default_project',default_project,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            start_order_number = request.POST.get('start_order_number')
            if start_order_number and start_order_number != '0':
                order_number_availabile = SettingView.get_order_number_availability(start_order_number, event_id)
                if order_number_availabile:
                    setting = SettingView.save_or_update_settings(request, 'start_order_number', start_order_number, setting['new_settings'],
                                                                  setting['updated_settings'], setting['updated_setting_ids'])

            due_date = request.POST.get('due_date')
            setting = SettingView.save_or_update_settings(request, 'due_date', due_date, setting['new_settings'],
                                                          setting['updated_settings'], setting['updated_setting_ids'])

            allow_same_email_multiple_registration = request.POST.get('allow_same_email_multiple_registration')
            setting = SettingView.save_or_update_settings(request, 'allow_same_email_multiple_registration', allow_same_email_multiple_registration,
                                                          setting['new_settings'], setting['updated_settings'], setting['updated_setting_ids'])

            defaults_answers = json.loads(request.POST.get('defaults_answers'))
            answer_sql = SettingView.set_default_answers(defaults_answers,'questions')
            if answer_sql != '':
                cursor.execute(answer_sql)

            defaults_sessions = json.loads(request.POST.get('default_sessions'))
            session_sql = SettingView.set_default_answers(defaults_sessions,'sessions')
            if session_sql != '':
                cursor.execute(session_sql)

            defaults_travels = json.loads(request.POST.get('default_travels'))
            travel_sql = SettingView.set_default_answers(defaults_travels,'travels')
            if travel_sql != '':
                cursor.execute(travel_sql)

            rooms = json.loads(request.POST.get('rooms'))
            sql_room_case = ''
            room_ids = []
            for room in rooms:
                sql_room_case +='WHEN id = '+str(room['id'])+' THEN "'+room['value']+'" '
                room_ids.append(str(room['id']))
            room_case = ''
            if sql_room_case != '':
                room_case = 'keep_hotel = CASE '+sql_room_case+'END'
            if room_case != '':
                room_sql = 'update rooms set '+room_case+' WHERE id IN ('+str(room_ids).replace("[","").replace("]","")+')'
                cursor.execute(room_sql)

            event_id = request.session['event_auth_user']['event_id']
            default_group = Setting.objects.filter(name='default_group', event_id=event_id)
            if request.POST.get('default_group'):
                new_default_group = int(request.POST.get('default_group'))
                if default_group.exists() and new_default_group > 0:
                    setting['updated_settings'] +="WHEN id = "+str(default_group[0].id)+" THEN '"+str(new_default_group)+"' "
                    setting['updated_setting_ids'].append(default_group[0].id)
                elif new_default_group > 0:
                    new_default_tag = Setting(name='default_group', event_id=event_id, value=str(new_default_group))
                    setting['new_settings'].append(new_default_tag)

            tags = request.POST.getlist('default_tags[]')
            all_tags = []
            for tag in tags:
                if tag.isdigit():
                    all_tags.append(int(tag))

                else:
                    if tag != "" and tag != None:
                        new_tag = Tag(name=tag,event_id=event_id)
                        new_tag.save()
                        all_tags.append(new_tag.id)
            setting = SettingView.save_or_update_settings(request,'default_tag',json.dumps(all_tags),setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            if request.POST.get('default_language'):
                preset_id = request.POST.get('default_language')
                default_language = PresetEvent.objects.filter(event_id=event_id)
                if default_language.exists():
                    default_language.update(preset_id=preset_id)
                else:
                    new_default_language = PresetEvent(preset_id=preset_id, event_id=event_id)
                    new_default_language.save()

            if request.POST.get('attendee_add_confirmation'):
                email_content_id = request.POST.get('attendee_add_confirmation')
                setting = SettingView.save_or_update_settings(request,'attendee_add_confirmation',email_content_id,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            if request.POST.get('attendee_edit_confirmation'):
                email_content_id = request.POST.get('attendee_edit_confirmation')
                setting = SettingView.save_or_update_settings(request,'attendee_edit_confirmation',email_content_id,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            if request.POST.get('session_conflict_confirmation'):
                email_content_id = request.POST.get('session_conflict_confirmation')
                setting = SettingView.save_or_update_settings(request,'session_conflict_confirmation',email_content_id,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            if request.POST.get('session_no_conflict_confirmation'):
                email_content_id = request.POST.get('session_no_conflict_confirmation')
                setting = SettingView.save_or_update_settings(request,'session_no_conflict_confirmation',email_content_id,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            cookie_expire = request.POST.get('cookie_expire')
            setting = SettingView.save_or_update_settings(request,'cookie_expire',cookie_expire,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            session_global_settings = request.POST.get('session_global_settings')
            setting = SettingView.save_or_update_settings(request,'session_global_settings',session_global_settings,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            location_global_settings = request.POST.get('location_global_settings')
            setting = SettingView.save_or_update_settings(request,'location_global_settings',location_global_settings,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            economy_order_table_global_settings = request.POST.get('economy_order_table_global_settings')
            setting = SettingView.save_or_update_settings(request,'economy_order_table_global_settings',economy_order_table_global_settings,setting['new_settings'],setting['updated_settings'],setting['updated_setting_ids'])

            attendee_global_settings = request.POST.get('attendee_global_settings')
            setting_attendee_global_settings = Setting.objects.filter(name='attendee_global_settings', event_id=event_id)
            if setting_attendee_global_settings.exists():
                Setting.objects.filter(name='attendee_global_settings', event_id=event_id).update(
                    value=attendee_global_settings)
            else:
                setting_attendee = Setting(name='attendee_global_settings', value=attendee_global_settings, event_id=event_id)
                setting['new_settings'].append(setting_attendee)
            if setting['updated_settings'] != '':
                setting_sql = 'update settings set value = CASE '+setting['updated_settings']+'END'+' WHERE id IN ('+str(setting['updated_setting_ids']).replace("[","").replace("]","")+')'
                cursor.execute(setting_sql)
            Setting.objects.bulk_create(setting['new_settings'])
            updated_group_list = []
            updated_groups = Group.objects.filter(id__in=group_ids)
            for updated_group in updated_groups:
                updated_group_list.append({'group_id':updated_group.id, 'group_name_lang':updated_group.name_lang, 'type': updated_group.type, 'group_name': updated_group.name})
            response_data['success'] = 'Group and Settings Update Successfully'
            response_data['updated_group_list'] = updated_group_list
            response_data['group_response'] = group_response
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_or_update_settings(request,name,value,new_settings, updated_settings,updated_setting_ids):
        event_id = request.session['event_auth_user']['event_id']
        if value != "" and value != "Empty":
            setting = Setting.objects.filter(name=name, event_id=event_id)
            if setting.exists():
                updated_settings +="WHEN id = "+str(setting[0].id)+" THEN '"+value+"' "
                updated_setting_ids.append(setting[0].id)
            else:
                setting = Setting(name=name, value=value, event_id=event_id)
                new_settings.append(setting)
        response = {
            'new_settings': new_settings,
            'updated_settings': updated_settings,
            'updated_setting_ids': updated_setting_ids
        }
        return response

    # This function use for create new groups
    def addGroup(request, groups, event):
        # new_groups = []
        event_id = request.session['event_auth_user']['event_id']
        group_response = []
        questions_groups = []
        current_language_id = LanguageH.get_current_language_id(event_id)
        for group in groups:
            if group != None and len(group) != 0:
                response_data = {}
                form_data = {
                    "name": group['name'],
                    "type": group['type']
                    # "is_searchable": group['is_searchable'],
                }
                if 'id' in group:
                    group_id = group['id']
                    old_group = Group.objects.get(id=group['id'])
                    if old_group.name == 'temporary-filter':
                        form_data['name'] = 'temporary-filter'
                    if not (Group.objects.filter(name=form_data['name'], event_id=event_id, is_show=1).exclude(id=group_id).exists()):
                        Group.objects.filter(id=group_id).update(**form_data)
                        response_data['success'] = 'Group Update Successfully'
                    else:
                        response_data['warning'] = 'Group Name Already Exist'
                    response_data['group_id'] = group_id
                else:
                    if not (Group.objects.filter(name=form_data['name'], type=group['type'], event_id=event_id, is_show=1).exists()):
                        form_data['event_id'] = event_id
                        form_data = LanguageH.insert_lang(current_language_id, form_data, "name_lang", group['name'])
                        all_group = Group.objects.filter(type=group['type'],
                                                         event_id=event_id).order_by(
                            'group_order')
                        if all_group.exists():
                            form_data['group_order'] = all_group[all_group.count() - 1].group_order + 1
                            new_group = Group(**form_data)
                            # new_groups.append(new_group)
                            new_group.save()
                        else:
                            new_group = Group(**form_data)
                            new_group.save()
                        response_data['group_id'] = new_group.id
                        response_data['group_name_lang'] = new_group.name_lang
                        response_data['group_name'] = new_group.name
                        response_data['success'] = 'Group Create Successfully'
                        if group['type'] == "question":
                            questions_groups.append(new_group.id)
                    else:
                        response_data['warning'] = 'Group Name Already Exist'
                response_data['type'] = group['type']
                response_data['serial_id'] = group['serial_id']
                group_response.append(response_data)

        if len(questions_groups) > 0:
            contentPermission_list = ContentPermission.objects.filter(event_id=event_id, content='question',
                                                                      access_level="write")
            group_permissions = []
            for contentPermission in contentPermission_list:
                for group_id in questions_groups:
                    insert_group = {
                        "admin_id": contentPermission.admin_id,
                        "group_id": group_id,
                        "access_level": "write"
                    }
                    addGroupPermission = GroupPermission(**insert_group)
                    group_permissions.append(addGroupPermission)
            GroupPermission.objects.bulk_create(group_permissions)
        return group_response

    def set_default_answers(defaults_answers,table):
        sql_answer_case_array = []
        answer_ids = []
        sql_answer_case = ''
        sql_answer_status_case = ''
        for defaults_answer in defaults_answers:
            if defaults_answer['status'] == "set" and defaults_answer['value'] != "Empty":
                sql_answer_status_case +='WHEN id = '+str(defaults_answer['id'])+' THEN "'+defaults_answer['status']+'" '
                sql_answer_case +='WHEN id = '+str(defaults_answer['id'])+' THEN "'+defaults_answer['value']+'" '
                answer_ids.append(str(defaults_answer['id']))
            elif defaults_answer['status'] == 'empty' or defaults_answer['status'] == 'leave':
                sql_answer_status_case += 'WHEN id = ' + str(defaults_answer['id']) + ' THEN "' + defaults_answer['status'] + '" '
                answer_ids.append(str(defaults_answer['id']))
        if sql_answer_status_case != '':
            sql_answer_case_array.append('default_answer_status = CASE '+sql_answer_status_case+'END')
        if sql_answer_case:
            sql_answer_case_array.append('default_answer = CASE '+sql_answer_case+'END')
        sql_answer = ','.join(sql_answer_case_array)
        if sql_answer != '':
            answer_sql = 'update '+table+' set '+sql_answer+' WHERE id IN ('+str(answer_ids).replace("[","").replace("]","")+')'
            return answer_sql
        else:
            return ''

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'setting_permission'):
            groupList = json.loads(request.POST.get('groupList'))
            for group in groupList:
                id = group['id']
                old_group = Group.objects.get(id=id)
                if old_group.name != 'temporary-filter':
                    Group.objects.filter(id=id).update(is_show=0)
                    Group.objects.filter(id=id, type='session').delete()
            response_data['success'] = 'Group Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def set_groups_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'setting_permission'):
            groups_order = json.loads(request.POST.get('groups_order'))
            for group in groups_order:
                Group.objects.filter(id=group['group_id']).update(group_order=group['order'])
            response_data['success'] = 'Group Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def notificationTimeout(request):
        timeout = request.POST.get('timeout')
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        setting = Setting.objects.filter(name='notification_timeout', event_id=event_id)
        if setting.exists():
            Setting.objects.filter(name='notification_timeout', event_id=event_id).update(value=timeout)
            response_data['success'] = 'Notification Timeout Setting Update Successfully'
        else:
            setting = Setting(name='notification_timeout', value=timeout, event_id=event_id)
            setting.save()
            response_data['success'] = 'Notification Timeout Saved'

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_settings_attendee_global_details(request):
        context = {}
        event_id = request.session['event_auth_user']['event_id']
        question_groups = PageDetailView.get_fancyTreeView_question_group(request)
        return JsonResponse(question_groups, safe=False)

    def get_order_number_availability(order_number, event_id):
        if not order_number.isdigit():
            return True
        order_numbers = Setting.objects.filter(name='start_order_number').exclude(event_id=event_id).values('value')
        if order_numbers:
            order_numbers = [int(item['value']) for item in order_numbers if item['value'].isdigit()]
            max_order_number = max(order_numbers)
            order_number = int(order_number)
            if (order_number - max_order_number) < 1000:
                return False
        return True