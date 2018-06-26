from django.shortcuts import render, redirect
from django.views import generic
from app.models import PageContent, EmailTemplates, Questions, Elements, Option, ElementsAnswers, SessionRating, SeminarsUsers, Setting
import datetime
import re
import json
from django.template.loader import render_to_string
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from django.http import Http404
from slugify import slugify
from pytz import timezone

class StaticPage(generic.DeleteView):
    def get(self, request):
        return render(request, '')

    def get_object(request, pk):
        try:
            page_list = PageContent.objects.filter(url=pk, event_id=request.session['event_id'])
            if page_list.exists():
                return page_list[0]
            else:
                raise Http404
        except PageContent.DoesNotExist:
            raise Http404

    def get_static_page(request, staticPage=None):
        page = StaticPage.get_object(request, staticPage)
        if page.is_show:
            if page.login_required:
                if 'is_user_login' not in request.session:
                    return redirect('gt-welcome')
                elif 'is_user_login' in request.session and request.session['is_user_login'] == False:
                    return redirect('gt-welcome')
            pageContent = page.content
            pageContent = StaticPage.replace_questions(request, pageContent)
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                pageContent = pageContent.replace('{secret_key}', str(request.session['event_user']['secret_key']))

            # element_filters = json.loads(page.element_filter)
            # for element in element_filters:
            #     get_element = Elements.objects.filter(id=int(element['element_id']))
            #     if get_element.exists():
            #         element_name = get_element[0].name.lower() + '-' + element['box_id'].split('-')[1]
            #         get_element_content = StaticPage.get_evaluation(request,page.id,element)
            #         print('element:'+element_name)
            #         pageContent = pageContent.replace('{element:'+element_name+'}', get_element_content)
            if page.template_id == 1:
                content = pageContent.replace('[[static_alt]]', settings.STATIC_URL_ALT)
                context = {
                    "content": content,
                    "static_page": page
                }
                return render(request, 'gt/static_pages/page.html', context)
            else:
                template = EmailTemplates.objects.get(id=page.template_id)
                template_content = template.content.replace('[[static]]', settings.STATIC_URL_ALT)
                template_content = template_content.replace('public/js/jquery.min.js',
                                                            static('public/js/jquery.min.js'))
                content = pageContent.replace('[[static]]', settings.STATIC_URL_ALT)
                page_content = template_content.replace('{content}', content)
                menu_find = re.findall(r'{(menu)}', page_content)
                if len(menu_find) > 0:
                    menu = StaticPage.get_menu(request)
                    page_content = page_content.replace('{menu}', menu)
                context = {
                    "page_content": page_content
                }
                return render(request, 'gt/static_pages/page_test.html', context)
        else:
            return redirect('gt-welcome')

    def replace_questions(request, pageContent):
        questions = []
        match = re.findall("qid:\d+", pageContent)
        for q in match:
            print(q.split(':')[1])
            data = {
                'qid': q.split(':')[1]
            }
            questions.append(data)
        for qid in questions:
            question = Questions.objects.get(id=qid['qid'])
            options = Option.objects.filter(question_id=qid['qid'])
            slug_title = slugify(question.title);
            if question.type == 'select':
                option = """<option value="">- Select -</option>"""
                for opt in options:
                    option += """<option value='""" + opt.option + """'>""" + opt.option + """</option>"""
                print(option)
                content = """<label for="attendee-question-""" + str(
                        question.id) + """">""" + question.title + """<span>""" + question.description + """</span></label>
                        <div class="validationBorder">
                        <select id="attendee-question-""" + str(question.id) + """" class="given-answer">
                        """ + option + """
                        </select>
                        </div>"""
            elif question.type == 'radio_button':
                option = ""
                for key, opt in enumerate(options):
                    counter = key + 1
                    option += """<input type="radio" name="attendee-question-""" + str(
                            question.id) + """" value='""" + opt.option + """' id="attendee-question-""" + str(
                            question.id) + """-""" + str(
                            counter) + """" class="given-answer"><label for="attendee-question-""" + str(
                            question.id) + """-""" + str(counter) + """">""" + opt.option + """</label>"""
                content = """<label class="fontLarge">""" + question.title + """<span>""" + question.description + """</span></label><br/>
                        """ + option
            elif question.type == 'text':
                content = """<label for="attendee-question-""" + str(question.id) + """">""" + question.title + """<span>""" + question.description + """</span></label>
                          <input type="text" id="attendee-question-""" + str(question.id) + """" class="given-answer">"""
            elif question.type == 'checkbox':
                option = "";
                for key, opt in enumerate(options):
                    counter = key + 1;
                    option += """<input class="given-answer" type="checkbox" name="attendee-question-""" + str(question.id) + """" value=""" + opt.option + """ id="attendee-question-""" + str(question.id) + """-""" + str(counter) + """"><label for="attendee-question-""" + str(question.id) + """-""" + str(counter) + """">""" + opt.option + """</label>"""
                    content = """<label for="attendee-""" + slug_title + """">""" + question.title + """<span>""" + question.description + """</span></label><br/>
                        """ + option
            elif question.type == 'textarea':
                content = """<label for="attendee-question-""" + str(question.id) + """">""" + question.title + """<span>""" + question.description + """</span></label>
                          <textarea id="attendee-question-""" + str(question.id) + """" class="given-answer"></textarea>"""
            else:
                content = """<label for="attendee-question-""" + str(question.id) + """">""" + question.title + """<span>""" + question.description + """</span></label>
                          <input type="text" id="attendee-question-""" + str(question.id) + """" class="given-answer">"""

            element = content + """
                    <div class="errorValidating noMargin">Please select your '""" + question.title + """'</div>"""

            pageContent = pageContent.replace('{qid:' + qid['qid'] + '}', element)

        return pageContent


    def get_menu(request):
        context = {
            'request': request
        }
        return render_to_string('gt/content/menu_head.html', context)


    # def get_evaluation(request, page_id, element):
    #     if 'is_user_login' in request.session and request.session['is_user_login']:
    #         if request.session['event_user']['attending'] == "Yes":
    #             box_id = element['box_id'].split('-')[1]
    #             user_id = request.session['event_user']['id']
    #             element_settings = ElementsAnswers.objects.filter(page_id=page_id,box_id=box_id)
    #             time_now = StaticPage.getTimezoneNow(request)
    #             f = '%Y-%m-%d %H:%M:%S'
    #             today = datetime.datetime.strptime(str(time_now).split(".")[0], f)
    #             appear_time = 11
    #             message = ''
    #             for setting in element_settings:
    #                 if setting.element_question_id == 2:
    #                     appear_time = setting.answer
    #                 else:
    #                     message = setting.description
    #             print('appear_time')
    #             print(appear_time)
    #             rated_sessions = SessionRating.objects.values('session_id').filter(attendee_id=user_id)
    #
    #             print(today)
    #             current_time = today + datetime.timedelta(minutes=-int(appear_time))
    #             print(current_time)
    #
    #             sql = "SELECT `seminars_has_users`.`id`, `seminars_has_users`.`attendee_id`, `seminars_has_users`.`session_id`, `seminars_has_users`.`status`, `seminars_has_users`.`created`, `seminars_has_users`.`queue_order` FROM `seminars_has_users` INNER JOIN `sessions` ON ( `seminars_has_users`.`session_id` = `sessions`.`id` ) WHERE (`sessions`.`end` < '" + str(
    #                     current_time) + "' AND `seminars_has_users`.`attendee_id` =" + str(
    #                     user_id) + " AND `sessions`.`show_on_evaluation` = True AND `seminars_has_users`.`status` = 'attending' AND NOT ((`seminars_has_users`.`session_id`) IN (SELECT U0.`session_id` FROM `session_ratings` U0 WHERE U0.`attendee_id` = " + str(
    #                     user_id) + ")))"
    #             sessions = SeminarsUsers.objects.raw(
    #                     sql
    #             )
    #             for session in sessions:
    #                 print(session.id)
    #             print(list(sessions))
    #             context = {
    #                 "sessions": list(sessions),
    #                 'message': message
    #             }
    #             return render_to_string('public/element/session_evaluation.html', context)
    #         else:
    #             return ''
    #     else:
    #         return ''
    #
    # def getTimezoneNow(request, *args, **kwargs):
    #     setting_timezone = Setting.objects.filter(name='timezone',event_id=request.session['event_id'])
    #     if setting_timezone:
    #         tzname = setting_timezone[0].value
    #         timezone_active = timezone(tzname)
    #         now = datetime.datetime.now(timezone_active)
    #         # print(now.strftime('%Y-%m-%d_%H-%M-%S'))
    #         return now