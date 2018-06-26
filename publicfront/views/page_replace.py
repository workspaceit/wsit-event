from django.views import generic
from app.models import Questions, Option, Answers, Session, Attendee, AttendeeGroups, AttendeeTag, TravelAttendee, \
    Booking, Travel, Photo, Presets, EmailTemplates, RuleSet, StyleSheet, Setting, MenuPermission
import json
import re
import django
from django.template.loader import render_to_string
from django.conf import settings
from slugify import slugify
import html
import qrcode
import base64
import io
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Count, Max
# from publicfront.views.economy_page_replace import EconomyPageReplace
from app.views.gbhelper.common_helper import CommonHelper
from publicfront.views.lang_key import LanguageKey
from publicfront.views.details import DetailsData
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.rule import UserRule
from django.db.models import Q
# from django.contrib.staticfiles.templatetags.staticfiles import static


class PageReplace(generic.View):
    def replace_template(request, motive, page, pageContents):
        template_id = page.template_id
        body_id = '<body id="'+page.url+'"'
        if motive:
            template = EmailTemplates.objects.get(id=template_id)
            page_content = template.content.replace('<body', body_id)
            # page_content = page_content.replace('{content}',
            #                                         '<div id="content" class="loading-page">' + pageContents + '</div>')
            page_content = page_content.replace('{content}',
                                                '<div id="content" class="loading-page"></div>')
            position_head = page_content.index('</head>')
            head_content = render_to_string('public/static_pages/cms_header.html',
                                            {'csrf_token': django.middleware.csrf.get_token(request)})
            page_content = page_content[:position_head] + head_content + page_content[position_head:]
        else:
            page_content = pageContents
        return page_content

    def replace_menu(request, motive, page_content):
        menu_find = re.findall(r'{(menu)}', page_content)
        if len(menu_find) > 0:
            if motive:
                request.menus = PageReplace.get_menu_with_permission(request)
                menu = render_to_string('public/content/menu_head.html', {'request': request})
            else:
                menu = ""
            page_content = page_content.replace('{menu}', menu)
        return page_content

    def replace_language(request, motive, page_content, current_language):
        language_find = re.findall(r'{(language)}', page_content)
        if len(language_find) > 0:
            if motive:
                current_preset = Presets.objects.get(id=current_language)
                all_languages = PageReplace.get_all_language(request, current_preset)
            else:
                all_languages = ""
            page_content = page_content.replace('{language}', all_languages)
        return page_content

    def replace_footer_content(request, motive, class_list, page, page_content, kendo, updated_variable):
        footer_content_js = {}
        try:
            footer_content_js = PageReplace.get_filter_content_js(request, page)
            footer_content_js.class_list = class_list
            footer_content_js.kendo_content_js = kendo["kendo_content_js"]
            footer_content_js.kendo_content = kendo["kendo_content"]
            footer_content_js += updated_variable
            if motive:
                footer_content = {
                    "class_list": json.dumps(class_list),
                    "static_page": page,
                    "footer_ajax_page_id": page.id,
                    "disallow_page": 0,
                    "request": request
                }
                if page.disallow_logged_in:
                    footer_content['disallow_page'] = 1
                footer_content.update(footer_content_js.format_object())
                footer_content['page_id'] = page.id
                position_footer = page_content.index('</body>')
                footer_content['static_url'] = settings.STATIC_URL_ALT
                footer_content['datepicker_global_setting_json'] = None
                footer_content['timepicker_global_setting_json'] = None

                language = LanguageKey.catch_lang_key_multiple(request, 'notification', ['notify_session_expire', 'notify_attendee_registration_time_expire'])
                footer_content['notify_session_expire'] = language['langkey']['notify_session_expire']
                footer_content['notify_attendee_registration_time_expire'] = language['langkey']['notify_attendee_registration_time_expire']

                setting_temporary_attendee_expire_time = Setting.objects.filter(name='temporary_attendee_expire_time', event_id=request.session['event_id'])
                if setting_temporary_attendee_expire_time.exists():
                    temporary_attendee_expire_time = setting_temporary_attendee_expire_time[0].value
                else:
                    # setting default 5 min
                    temporary_attendee_expire_time = '300000'
                footer_content['temporary_attendee_expire_time'] = temporary_attendee_expire_time

                datepicker_global_setting_json=PageReplace.get_global_datepicker_settings(request, request.session['language_id'])
                if datepicker_global_setting_json:
                    footer_content['datepicker_global_setting_json']=datepicker_global_setting_json

                timepicker_global_setting_json = PageReplace.get_global_timepicker_settings(request, request.session['language_id'])
                if timepicker_global_setting_json:
                    footer_content['timepicker_global_setting_json'] = timepicker_global_setting_json

                foot_content = render_to_string('public/static_pages/cms_footer.html', footer_content)
                page_content = page_content[:position_footer] + foot_content + page_content[position_footer:]
        except Exception as e:
            ErrorR.efail(e)
        return [page_content, footer_content_js]

    def get_filter_content_js(request, page):
        footer_content = UpdatableObj()
        try:
            footer_content.static_page_filter = []
            footer_content.kendo_content_js = ""
            footer_content.kendo_content = ""
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
            multiple_reg_filter_javascript = ""
            order_filter_javascript = ""
            rebate_filter_javascript = ""
            checkpoint_filter_javascript = ""
            first_empty_filter_javascript = ""
            if page.filter:
                footer_content.static_page_filter = json.loads(page.filter)
                remove_content = []
                user_id = ""
                duid = ""
                dboxuid = ""
                datauid = ""
                if 'is_user_login' in request.session and request.session['is_user_login']:
                    user_id = request.session["event_user"]["id"]
                    duid = "_u" + str(user_id)
                    dboxuid = "-u-" + str(user_id)
                    datauid = '[data-uid="' + str(user_id) + '"]'
                ErrorR.c_purple(user_id)
                ErrorR.c_purple(duid)
                ErrorR.c_purple(dboxuid)
                ErrorR.c_purple(datauid)
                for filterId in footer_content.static_page_filter:
                    if 'filter_id' in filterId:
                        # ErrorR.okblue("--------------RULE-----------")
                        filter_action = True
                        if 'action' in filterId:
                            if filterId['action'] == '0':
                                filter_action = False
                        filter_ids.append(filterId['filter_id'])
                        rule_list = RuleSet.objects.filter(id=filterId['filter_id'])
                        if not rule_list.exists():
                            remove_content.append(filterId)
                            continue
                            # footer_content['static_page_filter'].remove(filterId)
                        for rule in rule_list:
                            filter_store_data = {}
                            filter_store_data['rule'] = json.loads(rule.preset)
                            filter_store_data['rule_id'] = rule.id
                            filter_store_data['box'] = filterId['box_id']
                            filter_store.append(filter_store_data)
                            field_condition = '0'
                            if 'field' in filter_store_data['rule'][0][0]:
                                field_condition = filter_store_data['rule'][0][0]['field']
                            match_condition = '0'
                            if 'matchFor' in filter_store_data['rule'][0][0]:
                                match_condition = filter_store_data['rule'][0][0]['matchFor']
                            elif rule.matchfor:
                                match_condition = rule.matchfor
                            # match_condition = filter_store_data['rule'][0][0]['matchFor']
                            filter_permission = PageReplace.get_filter_permissions(request, rule_list)
                            div_id = "page-" + str(page.id) + "-" + filterId['box_id'] + dboxuid
                            if match_condition == '2':
                                # AND
                                if filter_action:
                                    # True
                                    filter_javascript = PageReplace.get_filter_js(request, user_id, duid, datauid,
                                                                                  filter_store_data['rule'],
                                                                                  match_condition,
                                                                                  div_id)
                                    filter_javascript = filter_javascript.replace('if()', 'if(' + str(
                                        filter_permission).lower() + ')')
                                    filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
                                                                                  str(filter_permission).lower())
                                else:
                                    # False
                                    filter_javascript = PageReplace.get_filter_js_not(request, user_id, duid, datauid,
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
                                elif field_condition == "15":
                                    multiple_reg_filter_javascript += filter_javascript
                                elif field_condition == "16":
                                    order_filter_javascript += filter_javascript
                                elif field_condition == "17":
                                    rebate_filter_javascript += filter_javascript
                                elif field_condition == "18":
                                    checkpoint_filter_javascript += filter_javascript
                                # else:
                                #     print(filter_javascript)
                                #     first_empty_filter_javascript += filter_javascript


                            elif match_condition == '1':
                                # OR
                                if filter_action:
                                    # TURE
                                    filter_javascript = PageReplace.get_filter_js(request, user_id, duid, datauid,
                                                                                  filter_store_data['rule'],
                                                                                  match_condition,
                                                                                  div_id)
                                    filter_javascript = filter_javascript.replace('if()', 'if(' + str(
                                        filter_permission).lower() + ')')
                                    filter_javascript = filter_javascript.replace('logic_dynamicaly_fill',
                                                                                  str(filter_permission).lower())
                                else:
                                    # FLASE
                                    filter_javascript = PageReplace.get_filter_js_not(request, user_id, duid, datauid,
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
                                elif field_condition == "15":
                                    multiple_reg_filter_javascript += filter_javascript
                                elif field_condition == "16":
                                    order_filter_javascript += filter_javascript
                                elif field_condition == "17":
                                    rebate_filter_javascript += filter_javascript
                                elif field_condition == "18":
                                    checkpoint_filter_javascript += filter_javascript
                                # else:
                                #     first_empty_filter_javascript += filter_javascript
                                    # ErrorR.okblue(filter_javascript)
                for filterId in remove_content:
                    footer_content.static_page_filter.remove(filterId)
                footer_content.registration_date_filter_javascript = registration_date_filter_javascript
                footer_content.updated_date_filter_javascript = updated_date_filter_javascript
                footer_content.attendee_group_filter_javascript = attendee_group_filter_javascript
                footer_content.attendee_tag_filter_javascript = attendee_tag_filter_javascript
                footer_content.session_filter_javascript = session_filter_javascript
                footer_content.question_filter_javascript = question_filter_javascript
                footer_content.app_filter_javascript = app_filter_javascript
                footer_content.hotel_filter_javascript = hotel_filter_javascript
                footer_content.speaker_filter_javascript = speaker_filter_javascript
                footer_content.email_filter_javascript = email_filter_javascript
                footer_content.message_filter_javascript = message_filter_javascript
                footer_content.page_filter_javascript = page_filter_javascript
                footer_content.language_filter_javascript = language_filter_javascript
                footer_content.multiple_reg_filter_javascript = multiple_reg_filter_javascript
                footer_content.order_filter_javascript = order_filter_javascript
                footer_content.rebate_filter_javascript = rebate_filter_javascript
                footer_content.checkpoint_filter_javascript = checkpoint_filter_javascript
                footer_content.first_empty_filter_javascript = first_empty_filter_javascript
        except Exception as e:
            ErrorR.efail(e)
        return footer_content

    def replace_kendo_plugin(request, motive, kendo_plugin_flag, page_content):
        if motive:
            if kendo_plugin_flag:
                position_head = page_content.index('</head>')
                head_content = render_to_string('public/static_pages/cms_header_optional.html', {})
                page_content = page_content[:position_head] + head_content + page_content[position_head:]

                # position_footer = page_content.index('</body>')
                # foot_content = render_to_string('public/static_pages/cms_footer_optional.html', {})
                # page_content = page_content[:position_footer] + foot_content + page_content[position_footer:]
            position_head = page_content.index('</body>')
            head_content = render_to_string('public/static_pages/cms_csrf_token.html',
                                            {'csrf_token': django.middleware.csrf.get_token(request)})
            page_content = page_content[:position_head] + head_content + page_content[position_head:]
        else:
            if kendo_plugin_flag:
                head_content = render_to_string('public/static_pages/cms_header_optional.html', {})
                page_content += head_content
                foot_content = render_to_string('public/static_pages/cms_footer_optional_filter.html',
                                                {"filter": "css"})
                page_content += foot_content
        return page_content

    def replace_questions(request, pageContents, page_id):
        try:
            questions = []
            match = re.findall("questionid:\d+,box:\d+", pageContents)
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
                        question_name = "attendee-question-" + str(question.id)
                        question_input_id = "attendee-question-" + str(question.id)
                        question_input_q_id = "attendee-question-" + str(question.id)
                        question_filter_id = str(question.id)
                        if not question.time_interval:
                            question.time_interval = '30'
                        # if question.description != '' and question.description != None:
                        if question.show_description:
                            description = """<span class="form-question-label-description">""" + question.description + """</span>"""
                        if question.type == 'select':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            # option = """<option value="">- {} -</option>""".format(select_text)
                            empty_option = """<option value="">- {} -</option>""".format(select_text)
                            option_list = ""
                            opt_flag = False
                            for opt in options:
                                option_value = opt.option
                                option_value = option_value.replace('"',"&quot;").replace("'","&apos;")
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if opt.default_value:
                                    opt_flag = True
                                    option_list += """<option value='""" + option_value + """' selected>""" + opt.option + """</option>"""
                                else:
                                    option_list += """<option value='""" + option_value + """'>""" + opt.option + """</option>"""

                            if question.required or opt_flag:
                                option = option_list
                            else:
                                option = empty_option + option_list
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                        <div class="form-plugin-select">
                                        <select data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">
                                        """ + option + """
                                        </select>
                                        </div>"""
                        elif question.type == 'country':
                            default_value = ''
                            # description = ''
                            # question_name = "attendee-question-" + str(question.id)
                            # question_input_id = "attendee-question-" + str(question.id)
                            # question_input_q_id = "attendee-question-" + str(question.id)
                            # question_filter_id = str(question.id)
                            if question.show_description:
                                description = """<span class="form-question-label-description">""" + question.description + """</span>"""
                            if question.default_answer:
                                default_value = question.default_answer
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                        <div class="form-plugin-select">
                                        <select class='form-question-country given-answer' data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-default='""" + default_value + """'>
                                        </select>
                                        </div>"""
                        elif question.type == 'radio_button':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if opt.default_value:
                                    option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + question_filter_id + """ name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                        counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                        counter) + """ class="given-answer" checked><label for=""" + question_input_id + """-""" + str(
                                        counter) + """ class="radio-label">""" + opt.option + """</label></div>"""
                                else:
                                    option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + question_filter_id + """ name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                        counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                        counter) + """ class="given-answer"><label for=""" + question_input_id + """-""" + str(
                                        counter) + """ class="radio-label">""" + opt.option + """</label></div>"""

                            content = """<label class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                        """ + """<div class="form-question-radio">""" + option + """</div>"""
                        elif question.type == 'text':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <input type="text" id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer" data-filter-id=""" + question_filter_id + """>"""
                        elif question.type == 'checkbox':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if opt.default_value:
                                    option += """<div class="checkbox-wrapper"><input class="given-answer" type="checkbox" data-filter-id=""" + question_filter_id + """ name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                        counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                        counter) + """ checked><label class="checkbox-label" for=""" + question_input_id + """-""" + str(
                                        counter) + """>""" + opt.option + """</label></div>"""
                                else:
                                    option += """<div class="checkbox-wrapper"><input class="given-answer" type="checkbox" data-filter-id=""" + question_filter_id + """ name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                        counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                        counter) + """><label class="checkbox-label" for=""" + question_input_id + """-""" + str(
                                        counter) + """>""" + opt.option + """</label></div>"""

                                content = """<label  class="form-question-label" for="attendee-""" + slug_title + """">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><br/>
                                            """ + """<div class="form-question-checkbox">""" + option + """</div>"""
                        elif question.type == 'textarea':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <textarea  data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer"></textarea>"""

                        elif question.type == 'date':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                                                      <input type="text" name="date" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date="""+str(question.from_date)+""" data-to-date="""+str(question.to_date)+""" class="given-answer question-date">"""
                        elif question.type == 'time':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                                                                                  <input type="text" time-intervel="""+question.time_interval+"""  name="time"  data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(
                                question.from_time) + """ data-to-time=""" + str(
                                question.to_time) + """ class="given-answer question-time">"""
                        elif question.type =='date_range':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><div style="overflow:hidden">
                                <input name="date_range_from" style="width:49%; display:inline; float:left; margin-right:2%;" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date=""" + str(question.from_date) + """ data-to-date=""" + str(question.to_date) + """ data-range-type="from" class="given-answer question-date-range question-date-range-from">
                                <input name="date_range_to" style="width:49%; display:inline; float:left" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date=""" + str(question.from_date) + """ data-to-date=""" + str(question.to_date) + """ data-range-type="to" class="given-answer question-date-range question-date-range-to"></div>"""
                        elif question.type == 'time_range':
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><div style="overflow:hidden">
                                <input name="time_range_from" time-intervel="""+question.time_interval+"""  style="width:49%; display:inline; float:left; margin-right:2%;" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(question.from_time) + """ data-to-time=""" + str(question.to_time) + """ data-range-type="from" class="given-answer question-time-range question-time-range-from">
                                <input name="time_range_to" time-intervel="""+question.time_interval+""" style="width:49%; display:inline; float:left" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(question.from_time) + """ data-to-time=""" + str(question.to_time) + """ data-range-type="to" class="given-answer question-time-range question-time-range-to"></div>"""
                        else:
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                          <input type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">"""

                        lang = LanguageKey.catch_lang_key(request, "questions",
                                                          "th_question_select_ur_ques")
                        box_data = "page-" + str(page_id) + "-box-" + qid["box_id"]
                        required = ""
                        question_required = 0
                        actual_def = "null"
                        if question.required:
                            question_required = 1
                            required = " required"
                        if question.actual_definition:
                            actual_def = str(question.actual_definition)
                        error_text = lang.replace("{question}", question.title)
                        element = """<div class="form-question element box""" + required + """" data-id=""" + str(
                            question.id) + """ data-req=""" + str(
                            question_required) + """ data-def=""" + actual_def + """ id=""" + box_data + """ type=""" + question.type + """>""" + \
                                  content + """
                                    <div class="error-validating">""" + error_text + """</div></div>"""
                    else:
                        element = ""
                    pageContents = pageContents.replace('{questionid:' + qid['qid'] + ',box:' + qid['box_id'] + '}', element)
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
                        question_name = "usr-" + str(attendee_id) + "-attendee-question-" + str(
                            question.id)
                        question_input_id = "usr-" + str(
                            attendee_id) + "-attendee-question-" + str(question.id)
                        question_input_q_id = "attendee-question-" + str(question.id)
                        question_filter_id = str(question.id) + "_u" + str(attendee_id)
                        if not question.time_interval:
                            question.time_interval = '30'
                        # if question.description != '' and question.description != None:
                        if question.show_description:
                            description = """<span class="form-question-label-description">""" + question.description + """</span>"""
                        if question.type == 'select':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            empty_option = """<option value="">- {} -</option>""".format(select_text)
                            option_list = ""
                            opt_flag = False
                            if not answer.exists():
                                for opt in options:
                                    option_value = opt.option
                                    option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                    opt = LanguageKey.get_option_data_by_language(request, opt)
                                    if opt.default_value:
                                        option_list += """<option value='""" + option_value + """' selected>""" + opt.option + """</option>"""
                                    else:
                                        option_list += """<option value='""" + option_value + """'>""" + opt.option + """</option>"""
                            else:
                                value = answer[0].value
                                for opt in options:
                                    option_value = opt.option
                                    opt = LanguageKey.get_option_data_by_language(request, opt)
                                    if option_value == value:
                                        option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                        option_list += """<option value='""" + option_value + """' selected>""" + opt.option + """</option>"""
                                    else:
                                        option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                        option_list += """<option value='""" + option_value + """'>""" + opt.option + """</option>"""
                            if question.required or opt_flag:
                                option = option_list
                            else:
                                option = empty_option + option_list
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                        <div class="form-plugin-select">
                                        <select data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">
                                        """ + option + """
                                        </select>
                                        </div>"""
                        elif question.type == 'country':
                            default_value = ''
                            # description = ''
                            # question_name = "attendee-question-" + str(question.id)
                            # question_input_id = "attendee-question-" + str(question.id)
                            # question_input_q_id = "attendee-question-" + str(question.id)
                            # question_filter_id = str(question.id)
                            if question.show_description:
                                description = """<span class="form-question-label-description">""" + question.description + """</span>"""
                            if not answer.exists():
                                if question.default_answer:
                                    default_value = question.default_answer
                            else:
                                default_value = answer[0].value
                            content = """<label for="attendee-question-""" + str(
                                question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                        <div class="form-plugin-select">
                                        <select class='form-question-country given-answer' data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id +""" data-default='""" + default_value + """'>
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
                                    option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                    if opt.default_value:
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + question_filter_id + """  name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """ class="given-answer" checked><label for=""" + question_input_id + """-""" + str(
                                            counter) + """ class="radio-label">""" + opt.option + """</label></div>"""
                                    else:
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + question_filter_id + """  name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """ class="given-answer"><label for=""" + question_input_id + """-""" + str(
                                            counter) + """ class="radio-label">""" + opt.option + """</label></div>"""
                                else:
                                    value = answer[0].value
                                    if option_value == value:
                                        option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + question_filter_id + """  name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """ class="given-answer" checked><label for=""" + question_input_id + """-""" + str(
                                            counter) + """ class="radio-label">""" + opt.option + """</label></div>"""
                                    else:
                                        option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                        option += """<div class="radio-wrapper"><input type="radio" data-filter-id=""" + question_filter_id + """  name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """ class="given-answer"><label for=""" + question_input_id + """-""" + str(
                                            counter) + """ class="radio-label">""" + opt.option + """</label></div>"""

                            content = """<label class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><br/>
                                        """ + """<div class="form-question-radio">""" + option + """</div>"""
                        elif question.type == 'text':
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" data-filter-id=""" + question_filter_id + """  value='""" + value + """' id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">"""
                        elif question.type == 'checkbox':
                            options = Option.objects.filter(question_id=qid['qid']).order_by('option_order')
                            option = ""
                            for key, opt in enumerate(options):
                                counter = key + 1
                                option_value = opt.option
                                opt = LanguageKey.get_option_data_by_language(request, opt)
                                if not answer.exists():
                                    option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                    if opt.default_value:
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + question_filter_id + """  type="checkbox" name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """ checked><label class="checkbox-label" for=""" + question_input_id + """-""" + str(
                                            counter) + """>""" + opt.option + """</label></div>"""
                                    else:
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + question_filter_id + """  type="checkbox" name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """><label class="checkbox-label" for=""" + question_input_id + """-""" + str(
                                            counter) + """>""" + opt.option + """</label></div>"""
                                else:
                                    value = answer[0].value
                                    values = value.split("<br>")
                                    if option_value in values:
                                        option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + question_filter_id + """  type="checkbox" name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """ checked><label class="checkbox-label" for=""" + question_input_id + """-""" + str(
                                            counter) + """>""" + opt.option + """</label></div>"""
                                    else:
                                        option_value = option_value.replace('"', "&quot;").replace("'", "&apos;")
                                        option += """<div class="checkbox-wrapper"><input class="given-answer" data-filter-id=""" + question_filter_id + """  type="checkbox" name=""" + question_name + """ value='""" + option_value + """' id=""" + question_input_id + """-""" + str(
                                            counter) + """ data-q-id=""" + question_input_q_id + """-""" + str(
                                            counter) + """><label class="checkbox-label" for=""" + question_input_id + """-""" + str(
                                            counter) + """>""" + opt.option + """</label></div>"""

                                content = """<label class="form-question-label" for="attendee-""" + slug_title + """">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><br/>
                                        """ + """<div class="form-question-checkbox">""" + option + """</div>"""
                        elif question.type == 'textarea':
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <textarea  data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer"></textarea>"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <textarea data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">""" + value + """</textarea>"""
                        elif question.type == 'date':
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" name="date" data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """  data-from-date="""+str(question.from_date)+""" data-to-date="""+str(question.to_date)+""" class="given-answer question-date">"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" name="date" data-filter-id=""" + question_filter_id + """  data-value='""" + value + """' id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date="""+str(question.from_date)+""" data-to-date="""+str(question.to_date)+""" class="given-answer question-date">"""
                        elif question.type == 'time':
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" name="time" time-intervel="""+question.time_interval+""" data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """  data-from-time="""+str(question.from_time)+""" data-to-time="""+str(question.to_time)+""" class="given-answer question-time">"""
                            else:
                                value = answer[0].value
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" name="time" time-intervel="""+question.time_interval+""" data-filter-id=""" + question_filter_id + """  data-value='""" + value + """' id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time="""+str(question.from_time)+""" data-to-time="""+str(question.to_time)+""" class="given-answer question-time">"""
                        elif question.type == 'date_range':
                            if not answer.exists() or (answer and answer[0].value == ''):
                                content = """<label for="attendee-question-""" + str(question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><div style="overflow:hidden">
                                <input name="date_range_from" style="width:49%; display:inline; float:left; margin-right:2%;" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date=""" + str(question.from_date) + """ data-to-date=""" + str(question.to_date) + """ data-range-type="from" class="given-answer question-date-range question-date-range-from">
                                <input name="date_range_to" style="width:49%; display:inline; float:left" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date=""" + str(question.from_date) + """ data-to-date=""" + str(question.to_date) + """ data-range-type="to" class="given-answer question-date-range question-date-range-to"></div>"""
                            else:
                                value = json.loads(answer[0].value)
                                content = """<label for="attendee-question-""" + str(question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><div style="overflow:hidden">
                                    <input name="date_range_from" style="width:49%; display:inline; float:left; margin-right:2%;" type="text" data-value='""" + value[0] + """' data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date=""" + str(question.from_date) + """ data-to-date=""" + str(question.to_date) + """ data-range-type="from" class="given-answer question-date-range question-date-range-from">
                                    <input name="date_range_to" style="width:49%; display:inline; float:left" type="text" data-value='""" + value[1] + """' data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-date=""" + str(question.from_date) + """ data-to-date=""" + str(question.to_date) + """ data-range-type="to" class="given-answer question-date-range question-date-range-to"></div>"""
                        elif question.type == 'time_range':
                            if not answer.exists() or (answer and answer[0].value == ''):
                                content = """<label for="attendee-question-""" + str(question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><div style="overflow:hidden">
                                <input name="time_range_from" time-intervel="""+question.time_interval+""" style="width:49%; display:inline; float:left; margin-right:2%;" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(question.from_time) + """ data-to-time=""" + str(question.to_time) + """ data-range-type="from" class="given-answer question-time-range question-time-range-from">
                                <input name="time_range_to" time-intervel="""+question.time_interval+""" style="width:49%; display:inline; float:left" type="text" data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(question.from_time) + """ data-to-time=""" + str(question.to_time) + """ data-range-type="to" class="given-answer question-time-range question-time-range-to"></div>"""
                            else:
                                value = json.loads(answer[0].value)
                                content = """<label for="attendee-question-""" + str(question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label><div style="overflow:hidden">
                                <input name="time_range_from" time-intervel="""+question.time_interval+""" style="width:49%; display:inline; float:left; margin-right:2%;" type="text" value='""" + value[0] + """' data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(question.from_time) + """ data-to-time=""" + str(question.to_time) + """ data-range-type="from" class="given-answer question-time-range question-time-range-from">
                                <input name="time_range_to" time-intervel="""+question.time_interval+""" style="width:49%; display:inline; float:left" type="text" value='""" + value[1] + """' data-filter-id=""" + question_filter_id + """ id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ data-from-time=""" + str(question.from_time) + """ data-to-time=""" + str(question.to_time) + """ data-range-type="to" class="given-answer question-time-range question-time-range-to"></div>"""

                        else:
                            if not answer.exists():
                                content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">"""
                            else:
                                value = answer[0].value
                                if value == '' or value == None:
                                    content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" data-filter-id=""" + question_filter_id + """  id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">"""
                                else:
                                    content = """<label for="attendee-question-""" + str(
                                    question.id) + """" class="form-question-label">""" + """<span class="form-question-label-title">""" + question.title + """</span>""" + description + """</label>
                                              <input type="text" data-filter-id=""" + question_filter_id + """  value='""" + value + """' id=""" + question_input_id + """ data-q-id=""" + question_input_q_id + """ class="given-answer">"""

                        lang = LanguageKey.catch_lang_key(request, "questions",
                                                          "th_question_select_ur_ques")
                        error_text = lang.replace("{question}", question.title)
                        box_data = "page-" + str(page_id) + "-box-" + qid["box_id"] + "-u-" + str(attendee_id)
                        required = ""
                        question_required = 0
                        actual_def = "null"
                        if question.required:
                            question_required = 1
                            required = " required"
                        if question.actual_definition:
                            actual_def = str(question.actual_definition)
                        element = """<div class="form-question element box""" + required + """" data-id=""" + str(
                            question.id) + """ data-uid=""" + str(
                            attendee_id) + """ data-req=""" + str(
                            question_required) + """ data-def=""" + actual_def + """ id=""" + box_data + """ type=""" + question.type + """>""" + \
                                  content + """
                                    <div class="error-validating">""" + error_text + """</div></div>"""
                    else:
                        element = ""
                    pageContents = pageContents.replace('{questionid:' + qid['qid'] + ',box:' + qid['box_id'] + '}', element)
            return pageContents
        except Exception as e:
            ErrorR.efail(e)
            return pageContents

    def replace_questions_variable(request, pageContents):
        question_regex = r"({\"questions\":)(.|\s|\n)*?(]})"
        message = pageContents
        try:
            event_id = request.session['event_id']
            default_date_time_format = PageReplace.get_default_date_format(request.session['language_id'])
            default_date_format = default_date_time_format['default_datetime']
            question_default = '{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"' + default_date_format + '"}]}'
            if '{"questions"}' in message:
                message = message.replace('{"questions"}', question_default)
            question_matches = re.finditer(question_regex, message)
            for question_match in question_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    try:
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
                                                                 question__group_id__in=question_group_id).select_related('question')
                            else:
                                answers = Answers.objects.filter(question_id__in=question_id, user_id=attendee[0].id).select_related('question')
                        else:
                            if (len(question_group_id)):
                                answers = Answers.objects.filter(user_id=attendee[0].id,
                                                                 question__group_id__in=question_group_id).select_related('question')
                            else:
                                answers = Answers.objects.filter(user_id=attendee[0].id).select_related('question')
                        if answers:
                            questionAnswer["answers"] = answers
                            attendee_questions = DetailsData.get_question_data_by_attendee(request,
                                                                                           questionAnswer,
                                                                                           question_rules, attendee[0])
                        message = message.replace(question_match.group(),
                                                  '<span class="variable-tag">' + attendee_questions + '</span>')
                            # ****QUESTION END****
                    except Exception as e:
                        ErrorR.efail(e)
                        message = message.replace(question_match.group(), "")
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
            match = re.findall("qid:\d+", pageContents)
            for q in match:
                data = {
                    'qid': q.split(':')[1]
                }
                questions.append(data)
            if 'event_user' not in request.session:
                for qid in questions:
                    pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', "")
            else:
                attendee_id = request.session['event_user']['id']
                for qid in questions:
                    answer = Answers.objects.filter(question_id=qid['qid'], user_id=attendee_id)
                    if answer.exists():
                        answer_data = DetailsData.get_answer_data_by_attendee(request, answer[0])
                        pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', answer_data.value)
                    else:
                        pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', '')
                    # question = Questions.objects.filter(id=qid['qid'])
                    # if question.exists():
                    #     answer = Answers.objects.filter(question_id=qid['qid'], user_id=attendee_id)
                    #     if answer.exists():
                    #         if answer[0].question.type == 'date_range' or answer[0].question.type == 'time_range':
                    #             value_list = json.loads(answer[0].value)
                    #             value = ' - '.join(value_list)
                    #             pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', value)
                    #         elif answer[0].question.type == 'country':
                    #             country_list = CommonHelper.get_country_list(request)
                    #             pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', country_list[answer[0].value])
                    #         else:
                    #             print(answer[0].value)
                    #             pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', answer[0].value)
                    #     else:
                    #         pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', '')
                    # else:
                    #     pageContents = pageContents.replace('{qid:' + qid['qid'] + '}', '')
            return pageContents
        except Exception as e:
            ErrorR.efail(e)
            return pageContents

    def replace_sessions(request, pageContents):
        session_regex = r"({\"sessions\":)(.|\s|\n)*?(]})"
        message = pageContents
        try:
            event_id = request.session['event_id']
            default_date_time_format = PageReplace.get_default_date_format(request.session['language_id'])
            default_date_format = default_date_time_format['default_datetime']
            session_default = '{"sessions":[{"columns":"name,start,end","sort-column":"start","status":"attending","time-date":"' + default_date_format + '"}]}'
            if '{"sessions"}' in message:
                message = message.replace('{"sessions"}', session_default)
            session_matches = re.finditer(session_regex, message)
            for session_match in session_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    try:
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
                        if "status" in session_rules and "always" not in session_rules["status"]:
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
                    except Exception as e:
                        ErrorR.efail(e)
                        message = message.replace(session_match.group(), "")
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
            default_date_time_format = PageReplace.get_default_date_format(request.session['language_id'])
            default_date_format = default_date_time_format['default_datetime']
            travel_default = '{"travels":[{"columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"' + default_date_format + '"}]}'
            if '{"travels"}' in message:
                message = message.replace('{"travels"}', travel_default)
            travel_matches = re.finditer(travel_regex, message)
            for travel_match in travel_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    try:
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
                    except Exception as e:
                        ErrorR.efail(e)
                        message = message.replace(travel_match.group(), "")
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
            default_date_time_format = PageReplace.get_default_date_format(request.session['language_id'])
            default_date_format = default_date_time_format['default_date']
            hotel_default = '{"hotels":[{"columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"' + default_date_format + '"}]}'
            if '{"hotels"}' in message:
                message = message.replace('{"hotels"}', hotel_default)
            hotel_matches = re.finditer(hotel_regex, message)
            for hotel_match in hotel_matches:
                if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                    try:
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
                                                                                      hotel_rules,attendee[0].id)

                        message = message.replace(hotel_match.group(),
                                                  '<span class="variable-tag">' + attendee_hotels + '</span>')
                        # ****BOOKING END****
                    except Exception as e:
                        ErrorR.efail(e)
                        message = message.replace(hotel_match.group(), "")
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
        registration_date = ""
        updated_date = ""
        password = ""
        attendee_groups = ""
        tags = ""
        uid = ''
        bid = ''
        bidqr = ''
        first_name = ''
        last_name = ''
        email_address = ''
        try:
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                attendee = Attendee.objects.get(id=request.session['event_user']['id'])
                if '{first_name}' in pageContents:
                    first_name = str(attendee.firstname)
                if '{last_name}' in pageContents:
                    last_name = str(attendee.lastname)
                if '{email_address}' in pageContents:
                    email_address = str(attendee.email)
                if '{registration_date}' in pageContents:
                    registration_date = str(attendee.created)
                if '{updated_date}' in pageContents:
                    updated_date = str(attendee.updated)
                if '{attendee_groups}' in pageContents:
                    attendee_groups_data = AttendeeGroups.objects.filter(attendee_id=attendee.id)
                    attendee_groups_list = []
                    for attendee_group in attendee_groups_data:
                        attendee_group.group = LanguageKey.get_group_data_by_language(request, attendee_group.group)
                        attendee_groups_list.append(attendee_group.group.name)
                    attendee_groups = ','.join(attendee_groups_list)
                if '{tags}' in pageContents:
                    tags_data = AttendeeTag.objects.filter(attendee_id=attendee.id)
                    tags = ', '.join(tag.tag.name for tag in tags_data)
                # uid = request.session['event_user']['secret_key']
                if attendee.status == 'registered':
                    bid = attendee.bid
                    uid = attendee.secret_key
                # else:
                #     bid = ''
                #     uid = ''
                if '{bidqr}' in pageContents:
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
                # else:
                #     bidqr = ''
            # else:
            #     registration_date = ""
            #     updated_date = ""
            #     password = ""
            #     attendee_groups = ""
            #     tags = ""
            #     uid = ''
            #     bid = ''
            #     bidqr = ''
            #     first_name = ''
            #     last_name = ''
            #     email_address = ''
        except Exception as e:
            ErrorR.efail(e)
            # registration_date = ""
            # updated_date = ""
            # password = ""
            # attendee_groups = ""
            # tags = ""
            # uid = ''
            # bid = ''
            # bidqr = ''
            # first_name = ''
            # last_name = ''
            # email_address = ''

        # uid_link = """<a href=""" + base_url + """/?uid={uid}>""" + base_url + """/?uid={uid}</a>"""
        # calender_content = """<a href=""" + base_url + """/webcal/?uid={uid}>""" + base_url + """/webcal/?uid={uid}</a>"""
        uid_link = base_url + "/?uid={uid}"
        webcal_url = request.session['webcal_url']
        calender_content = webcal_url + "/webcal/?uid={uid}"
        pageContents = pageContents.replace('{registration_date}',
                                            '<span class="variable-tag">' + registration_date + '</span>')
        pageContents = pageContents.replace('{updated_date}', '<span class="variable-tag">' + updated_date + '</span>')
        pageContents = pageContents.replace('{attendee_groups}',
                                            '<span class="variable-tag">' + attendee_groups + '</span>')
        pageContents = pageContents.replace('{tags}', '<span class="variable-tag">' + tags + '</span>')
        pageContents = pageContents.replace('{uid_link}', uid_link)
        pageContents = pageContents.replace('{calendar}', calender_content)

        pageContents = pageContents.replace('{first_name}', '<span class="variable-tag">' + first_name + '</span>')
        pageContents = pageContents.replace('{last_name}', '<span class="variable-tag">' + last_name + '</span>')
        pageContents = pageContents.replace('{email_address}',
                                            '<span class="variable-tag">' + email_address + '</span>')
        pageContents = pageContents.replace('{uid}', uid)
        pageContents = pageContents.replace('{bid}', bid)
        pageContents = pageContents.replace('{base_url}', base_url)
        pageContents = pageContents.replace('{bidqr}', '<img src="data:image/png;base64,{0}"/ class="qr-code">'.format(bidqr))
        return pageContents


    def get_default_date_format(language_id):
        response = {}
        try:
            user_language = Presets.objects.get(id=language_id)
            response['default_date'] = user_language.date_format
            response['default_time'] = user_language.time_format
            response['default_datetime'] = user_language.datetime_format
            # default_date_format = Setting.objects.filter(name='default_date_format', event_id=event_id)
            # if default_date_format:
            #     default_date_format = json.loads(default_date_format[0].value)['python']
            # else:
            #     default_date_format = 'm-d-Y'
        except:
            response['default_date'] = 'Y-m-d'
            response['default_time'] = 'H:i'
            response['default_datetime'] = 'Y-m-d H:i'
        return response

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

    def get_menu_with_permission(request):
        menus = UserRule.get_menu_permissions(request)
        all_menus = PageReplace.get_all_menu_with_permission(request, menus['menu_permissions'], menus['my_rule_set'],
                                                  request.session['event_id'])
        return all_menus

    def get_all_menu_with_permission(request, mainMenu, rule_set, event_id):
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
                    PageReplace.get_all_menu_with_permission(request, item.items, rule_set, event_id)

        return mainMenu

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

    def get_filter_js(request, user_id, duid, datauid, filters, match_condition, box_id, addif=0):
        filter_js = ""
        try:

            for i, filter1 in enumerate(filters):
                # if addif != 0:
                #     print(str(i) + " " + str(addif))
                if i == 0 and addif == 0:
                    context_filter_javascript = {'type': 'if', 'user_id': user_id, 'duid': duid, 'datauid': datauid}
                    filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                  context_filter_javascript)
                if isinstance(filter1[0], dict):
                    single_filter = filter1[0]
                    try:
                        if len(single_filter['values']) > 1:
                            single_filter['values'][1] = html.unescape(single_filter['values'][1])
                    except Exception as e:
                        ErrorR.efail(e)
                        pass
                    # ErrorR.okgreen(single_filter)
                    js = render_to_string('public/static_pages/filter_javascript.html',
                                          {'single_filter': single_filter, 'user_id': user_id, 'duid': duid,
                                           'datauid': datauid})
                    context_filter_javascript = {
                        'type': 'condition',
                        'condition': js.strip(' \n\r\t'),
                        'user_id': user_id, 'duid': duid, 'datauid': datauid
                    }
                    if match_condition == '2':
                        # AND
                        filter_js += PageReplace.get_bracket(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += PageReplace.get_bracket(addif, len(filters), i, ")")

                        if i < len(filters) - 1:
                            filter_js += " && "
                    elif match_condition == '1':
                        # OR
                        filter_js += PageReplace.get_bracket(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += PageReplace.get_bracket(addif, len(filters), i, ")")
                        if i < len(filters) - 1:
                            filter_js += " || "

                    if i == len(filters) - 1 and addif == 0:
                        context_filter_javascript = {'type': 'pre-logic', 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id, 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id, 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)

                else:
                    match_condition_inner = filter1[0][0]['matchFor']
                    filter_js += "("
                    if match_condition == '2':
                        # And
                        filter_js += PageReplace.get_filter_js(request, user_id, duid, datauid, filter1,
                                                               match_condition_inner,
                                                               box_id,
                                                               addif + 1)
                    elif match_condition == '1':
                        # Or
                        filter_js += PageReplace.get_filter_js(request, user_id, duid, datauid, filter1,
                                                               match_condition_inner,
                                                               box_id,
                                                               addif + 1)
                    filter_js += ")"
                    ErrorR.okblue(i)
                    ErrorR.okblue(len(filters))
                    ErrorR.okblue(addif)
                    if i == len(filters) - 1 and addif == 0:
                        filter_js += ")"
                    if addif != 0 and i != len(filters) - 1:
                        filter_js += " && "
                    if addif == 0:
                        context_filter_javascript = {'type': 'pre-logic', 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id, 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id, 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/filter_javascript.html',
                                                      context_filter_javascript)

        except Exception as e:
            ErrorR.efail(e)
        return filter_js

    def get_filter_js_not(request, user_id, duid, datauid, filters, match_condition, box_id, addif=0):
        filter_js = ""
        try:

            for i, filter1 in enumerate(filters):
                # if addif != 0:
                #     print(str(i) + " " + str(addif))
                if i == 0 and addif == 0:
                    context_filter_javascript = {'type': 'if', 'user_id': user_id, 'duid': duid, 'datauid': datauid}
                    filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                  context_filter_javascript)
                if isinstance(filter1[0], dict):
                    single_filter = filter1[0]
                    single_filter['values'][1] = html.unescape(single_filter['values'][1])
                    js = render_to_string('public/static_pages/not_filter_javascript.html',
                                          {'single_filter': single_filter, 'user_id': user_id, 'duid': duid,
                                           'datauid': datauid})
                    context_filter_javascript = {
                        'type': 'condition',
                        'condition': js.strip(' \n\r\t'),
                        'user_id': user_id, 'duid': duid, 'datauid': datauid
                    }
                    if match_condition == '2':
                        # AND
                        filter_js += PageReplace.get_bracket_with_not(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += PageReplace.get_bracket_with_not(addif, len(filters), i, ")")

                        if i < len(filters) - 1:
                            filter_js += " && "
                    elif match_condition == '1':
                        # OR
                        filter_js += PageReplace.get_bracket_with_not(addif, len(filters), i, "(")
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        filter_js += PageReplace.get_bracket_with_not(addif, len(filters), i, ")")
                        if i < len(filters) - 1:
                            filter_js += " || "

                    if i == len(filters) - 1 and addif == 0:
                        context_filter_javascript = {'type': 'pre-logic', 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
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
                        filter_js += PageReplace.get_filter_js_not(request, user_id, duid, datauid, filter1,
                                                                   match_condition_inner, box_id,
                                                                   addif + 1)
                    elif match_condition == '1':
                        # Or
                        filter_js += PageReplace.get_filter_js_not(request, user_id, duid, datauid, filter1,
                                                                   match_condition_inner, box_id,
                                                                   addif + 1)
                    filter_js += ")"
                    if i == len(filters) - 1 and addif == 0:
                        filter_js += "))"
                    if addif != 0 and i != len(filters) - 1:
                        filter_js += " && "
                    if addif == 0:
                        context_filter_javascript = {'type': 'pre-logic', 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'logic', 'logic': box_id, 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)
                        context_filter_javascript = {'type': 'endif', 'logic': box_id, 'user_id': user_id, 'duid': duid,
                                                     'datauid': datauid}
                        filter_js += render_to_string('public/static_pages/not_filter_javascript.html',
                                                      context_filter_javascript)

        except Exception as e:
            ErrorR.efail(e)
        return filter_js

    def get_filter_permissions(request, rule_list):
        try:
            if 'is_user_login' in request.session and request.session['is_user_login']:
                attendee_id = request.session['event_user']['id']
                for rule in rule_list:
                    filters = json.loads(rule.preset)
                    q = Q()
                    match_condition = '0'
                    if 'matchFor' in filters[0][0]:
                        match_condition = filters[0][0]['matchFor']
                    elif rule.matchfor:
                        match_condition = rule.matchfor
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
    def get_global_datepicker_settings(request,language_id):
        preset = Presets.objects.filter(id=language_id)
        if preset.exists():
            preset = preset[0]
            date_lanaguage_json = '{"monthsFull":["January","February","March","April","May","June","July","August","September","October","November","December"],"monthsShort":["Jan","Feb","Mar","Apr","May","Jun","July","Aug","Sept","Oct","Nov","Dec"],"weekdaysShort":["Sun","Mon","Tues","Wed","Thurs","Fri","Sat"],"weekdaysFull":["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"today":"Today","tomorrow":"Tomorrow","yesterday":"Yesterday","clear":"Clear","close":"Close","firstDay":"0"}'
            if preset.datetime_language:
                date_lanaguage_json = preset.datetime_language
            date_lanaguage_json = json.loads(date_lanaguage_json)
            date_format = PageReplace.get_regerated_date_time_format(preset.date_format)
            # time_format = PageReplace.get_regerated_date_time_format(preset.time_format)
            # date_lanaguage_json['hiddenName']='true'

            date_lanaguage_json['firstDay'] = int(date_lanaguage_json['firstDay'])
            date_lanaguage_json['clear'] = ''
            date_lanaguage_json['format'] = date_format
            date_lanaguage_json['formatSubmit'] = 'yyyy-mm-dd'
            return date_lanaguage_json
        else:
            return None

    def get_global_timepicker_settings(request,language_id):
        preset = Presets.objects.filter(id=language_id)
        if preset.exists():
            preset = preset[0]
            if preset:
                time_language_json = {}
                time_format = PageReplace.get_regerated_date_time_format(preset.time_format)
                time_language_json['format'] = time_format
                time_language_json['formatSubmit'] = 'HH:i'
                if preset.datetime_language:
                    date_lanaguage_json = json.loads(preset.datetime_language)
                    time_language_json['clear']=date_lanaguage_json['clear']
                return time_language_json
            else:
                return None
        else:
            return None


    def get_regerated_date_time_format(date_format_str):
        date_format_str = date_format_str.replace("j","d")
        date_format_str = date_format_str.replace("d","dd")
        date_format_str = date_format_str.replace("D","ddd")
        date_format_str = date_format_str.replace("l","dddd")
        date_format_str = date_format_str.replace("n","m")
        date_format_str = date_format_str.replace("m","mm")
        date_format_str = date_format_str.replace("M","mmm")
        date_format_str = date_format_str.replace("F","mmmm")
        date_format_str = date_format_str.replace("g","h")
        date_format_str = date_format_str.replace("h","hh")
        date_format_str = date_format_str.replace("Y","yyyy")
        date_format_str = date_format_str.replace("G","H")
        date_format_str = date_format_str.replace("H","HH")
        return date_format_str

    def get_session_expire_lang(request, *args, **kwargs):
        language = LanguageKey.catch_lang_key_multiple(request, 'notification', ['notify_session_expire'])
        print(language)
        return HttpResponse(language['langkey']['notify_session_expire'])
#     def replace_economy_templates(request, html_content, order_number, template):
#         html_content = html_content.replace('{order-number}', order_number)
# #
#         html_content = PageReplace.replace_questions_variable(request, html_content)
#         html_content = PageReplace.replace_answers(request, html_content)
#         html_content = PageReplace.replace_sessions(request, html_content)
#         html_content = PageReplace.replace_travels(request, html_content)
#         html_content = PageReplace.replace_hotels(request, html_content)
#         html_content = PageReplace.replace_photos(request, html_content)
#         html_content = PageReplace.replace_general_tags(request, html_content)
#
#         # economy tags
#         html_content = EconomyPageReplace.replace_order_table(request, html_content)
#         html_content = EconomyPageReplace.replace_multiple_order_table(request, html_content)
#         html_content = EconomyPageReplace.replace_balance_table(request, html_content)
#         html_content = EconomyPageReplace.replace_order_value_paid_order(request, html_content)
#         html_content = EconomyPageReplace.replace_multiple_order_value_paid_order(request, html_content)
#         html_content = EconomyPageReplace.replace_order_value_pending_order(request, html_content)
#         html_content = EconomyPageReplace.replace_multiple_order_value_pending_order(request, html_content)
#         html_content = EconomyPageReplace.replace_order_value_open_order(request, html_content)
#         html_content = EconomyPageReplace.replace_multiple_order_value_open_order(request, html_content)
#         html_content = EconomyPageReplace.replace_order_value_all_order(request, html_content)
#         html_content = EconomyPageReplace.replace_multiple_order_value_all_order(request, html_content)
#         html_content = EconomyPageReplace.replace_order_value_credit_order(request, html_content)
#         html_content = EconomyPageReplace.replace_multiple_order_value_credit_order(request, html_content)
#         html_content = EconomyPageReplace.replace_reciept(request, html_content)
#         # get css version
#         css_version_obj = StyleSheet.objects.get(event_id=request.session['event_id'])
#         css_version = css_version_obj.version
#
#         html_content = html_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
#         html_content = html_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
#         html_content = html_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))
#         html_content = html_content.replace('[[static]]', settings.STATIC_URL_ALT)
#         html_content = html_content.replace('public/js/jquery.min.js',
#                                             static('public/js/jquery.min.js'))
#         html_content = html_content.replace('[[event_url]]', template.event.url)
#         html_content = html_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
#         return html_content



class UpdatableObj(object):
    def __init__(self):
        self.static_page_filter = []
        self.registration_date_filter_javascript = ""
        self.updated_date_filter_javascript = ""
        self.attendee_group_filter_javascript = ""
        self.attendee_tag_filter_javascript = ""
        self.session_filter_javascript = ""
        self.question_filter_javascript = ""
        self.app_filter_javascript = ""
        self.hotel_filter_javascript = ""
        self.speaker_filter_javascript = ""
        self.email_filter_javascript = ""
        self.message_filter_javascript = ""
        self.page_filter_javascript = ""
        self.language_filter_javascript = ""
        self.multiple_reg_filter_javascript = ""
        self.order_filter_javascript = ""
        self.rebate_filter_javascript = ""
        self.checkpoint_filter_javascript = ""
        self.first_empty_filter_javascript = ""
        self.kendo_content = ""
        self.kendo_content_js = ""
        self.class_list = []
        self.plugin_js_need = {
            'get_evaluation': False,
            'get_messages': False,
            'get_session_next_up': False,
            'get_location_list': False,
            'get_session_radio': False,
            'get_session_checkbox': False,
            'get_login_form': False,
            'get_request_login': False,
            'get_submit_button': False,
            'get_reset_password': False,
            'get_new_password': False,
            'get_attendee_plugin': False,
            'get_plugin_hotel_reservation': False,
            'get_session_scheduler': False,
            'get_archive_messages': False,
            'get_photo_upload': False,
            'get_photo_gallery': False,
            'get_logout': False,
            'get_multiple_registration': {
                'loop_registration': False,
                'inline_registration': False,
            },
        }

    def __add__(self, existing_variable):
        try:
            self.static_page_filter += existing_variable.static_page_filter
            self.registration_date_filter_javascript += existing_variable.registration_date_filter_javascript
            self.updated_date_filter_javascript += existing_variable.updated_date_filter_javascript
            self.attendee_group_filter_javascript += existing_variable.attendee_group_filter_javascript
            self.attendee_tag_filter_javascript += existing_variable.attendee_tag_filter_javascript
            self.session_filter_javascript += existing_variable.session_filter_javascript
            self.question_filter_javascript += existing_variable.question_filter_javascript
            self.app_filter_javascript += existing_variable.app_filter_javascript
            self.hotel_filter_javascript += existing_variable.hotel_filter_javascript
            self.speaker_filter_javascript += existing_variable.speaker_filter_javascript
            self.email_filter_javascript += existing_variable.email_filter_javascript
            self.message_filter_javascript += existing_variable.message_filter_javascript
            self.page_filter_javascript += existing_variable.page_filter_javascript
            self.language_filter_javascript += existing_variable.language_filter_javascript
            self.multiple_reg_filter_javascript += existing_variable.multiple_reg_filter_javascript
            self.order_filter_javascript += existing_variable.order_filter_javascript
            self.rebate_filter_javascript += existing_variable.rebate_filter_javascript
            self.checkpoint_filter_javascript += existing_variable.checkpoint_filter_javascript
            self.first_empty_filter_javascript += existing_variable.first_empty_filter_javascript
            self.kendo_content += existing_variable.kendo_content
            self.kendo_content_js += existing_variable.kendo_content_js
            self.class_list += existing_variable.class_list
            self.plugin_js_need.update(existing_variable.plugin_js_need)
        except Exception as e:
            ErrorR.efail(e)
        return self

    def format_object(self):
        content = {}
        try:
            content["static_page_filter"] = self.static_page_filter
            content[
                "registration_date_filter_javascript"] = self.registration_date_filter_javascript
            content["updated_date_filter_javascript"] = self.updated_date_filter_javascript
            content["attendee_group_filter_javascript"] = self.attendee_group_filter_javascript
            content["attendee_tag_filter_javascript"] = self.attendee_tag_filter_javascript
            content["session_filter_javascript"] = self.session_filter_javascript
            content["question_filter_javascript"] = self.question_filter_javascript
            content["app_filter_javascript"] = self.app_filter_javascript
            content["hotel_filter_javascript"] = self.hotel_filter_javascript
            content["speaker_filter_javascript"] = self.speaker_filter_javascript
            content["email_filter_javascript"] = self.email_filter_javascript
            content["message_filter_javascript"] = self.message_filter_javascript
            content["page_filter_javascript"] = self.page_filter_javascript
            content["language_filter_javascript"] = self.language_filter_javascript
            content["multiple_reg_filter_javascript"] = self.multiple_reg_filter_javascript
            content["order_filter_javascript"] = self.order_filter_javascript
            content["rebate_filter_javascript"] = self.rebate_filter_javascript
            content["checkpoint_filter_javascript"] = self.checkpoint_filter_javascript
            content["first_empty_filter_javascript"] = self.first_empty_filter_javascript
            content["kendo_content"] = self.kendo_content
            content["kendo_content_js"] = self.kendo_content_js
            content["class_list"] = json.dumps(self.class_list)
            content["plugin_js_need"] = self.plugin_js_need
        except Exception as e:
            ErrorR.efail(e)
        return content

