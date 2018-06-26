from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
from app.models import SeminarsUsers, Notification, Elements, EmailTemplates, StyleSheet
import json
from django.db.models import Q

from publicfront.views.lang_key import LanguageKey
from publicfront.views.mail import MailHelper
from .page2 import DynamicPage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
import django
import re

class SessionMessageView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        response_data = {}

    def post(self, request, *args, **kwargs):
        response_data = {}
        type = request.POST.get('type')
        message = request.POST.get('message')
        subject = request.POST.get('subject')
        session_id = request.POST.get('session_id')
        session_attendee = SeminarsUsers.objects.filter(session_id=session_id, status='attending')
        for attendee in session_attendee:
            if type == 'message':
                # notification = Notification(type='session_message', to_attendee_id=attendee.attendee.id, message=message)
                # notification.save()
                # message_history = MessageHistory(subject=subject, attendee_id=attendee.id, message=message,
                #                                  admin_id=request.session['event_auth_user']['id'], type='message')
                # message_history.save()
                response_data['success'] = 'Message Sent Successfully'
            elif type == 'email':
                # context = {
                #     'message': message
                # }
                # # subject = "MESSAGE - KINGFOMARKET"
                # to = attendee.attendee.email
                # MailHelper.mail_send('email_template/email_message.html', context, subject, to)
                # message_history = MessageHistory(subject=subject, attendee_id=attendee.id, message=message,
                #                                  admin_id=request.session['event_auth_user']['id'], type='mail')
                # message_history.save()
                response_data['success'] = 'Email Sent Successfully'
            elif type == 'sms':
                print(message)
                # message_history = MessageHistory(subject=subject, attendee_id=attendee.id, message=message,
                #                                  admin_id=request.session['event_auth_user']['id'], type='sms')
                # message_history.save()
                response_data['success'] = 'SMS Sent Successfully'

            # activity_history = ActivityHistory(attendee_id=attendee.id,
            #                                    admin_id=request.session['event_auth_user']['id'],
            #                                    activity_type='message', category='message',
            #                                    message_id=message_history.id, event_id=1)
            # activity_history.save()

    def get_archived_message(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                user_id = request.session['event_user']['id']
                archived_messages = Notification.objects.filter(to_attendee_id=user_id, status=1).exclude(type='session')
                element = Elements.objects.filter(slug="archive-messages")
                language = LanguageKey.get_lang_key(request, element[0].id)
                context = {
                    'archived_messages': archived_messages,
                    "language": language,
                }
                archived_message = render_to_string('public/attendee/archived_messages.html', context)
                message_page = SessionMessageView.get_default_template(request,archived_message)
                return HttpResponse(message_page)
                # return render(request, 'public/attendee/archived_messages.html', context)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def get_default_template(request,pageContents):
        try:

            template_data = EmailTemplates.objects.filter(name="default-web-template", event_id=request.session['event_id'])
            if template_data.exists():
                # get css version
                css_version_obj = StyleSheet.objects.get(event_id=request.session['event_id'])
                css_version = css_version_obj.version

                template = template_data[0]
                page_content = template.content.replace('{content}', pageContents)
                position_head = page_content.index('</head>')
                head_content = render_to_string('public/static_pages/cms_header.html', {'csrf_token': django.middleware.csrf.get_token(request)})
                page_content = page_content[:position_head]+head_content+page_content[position_head:]
                page_content = page_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                page_content = page_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                page_content = page_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))
                page_content = page_content.replace('[[static]]', settings.STATIC_URL_ALT)
                page_content = page_content.replace('public/js/jquery.min.js',
                                                    static('public/js/jquery.min.js'))
                page_content = page_content.replace('[[event_url]]', request.session['event_url'])

                menu_find = re.findall(r'{(menu)}', page_content)
                if len(menu_find) > 0:
                    menu = DynamicPage.get_menu(request)
                    page_content = page_content.replace('{menu}', menu)

                page_content = page_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
                position_footer = page_content.index('</body>')
                foot_content = render_to_string('public/static_pages/cms_footer.html')
                page_content = page_content[:position_footer]+foot_content+page_content[position_footer:]
                context = {
                    "page_content": page_content,
                }
                str_test=page_content.replace('\n\n', '')
                str_test=str_test.replace('\r', '')
                str_test=str_test.replace('\t\t', '')
                return str_test
        except Exception as e:
            print(e)
            return ""

    def archive_all_messages(request, *args, **kwargs):
        response_data = {}
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                user_id = request.session['event_user']['id']
                unreadMessages = Notification.objects.filter(to_attendee_id=user_id, status=0).exclude(type='session')
                for message in unreadMessages:
                    Notification.objects.filter(id=message.id).update(status=1)
                notification_language = LanguageKey.catch_lang_key(request, 'messages', 'messages_notify_read_success')
                response_data['success'] = True
                response_data['message'] = notification_language
            else:
                response_data['error'] = True
                response_data['message'] = 'You are not attending in this event'
        else:
            response_data['error'] = True
            response_data['message'] = 'Pls Login First'
        empty_txt_language = LanguageKey.catch_lang_key(request, 'messages', 'messages_txt_empty')
        response_data['empty_txt_language'] = empty_txt_language

        return HttpResponse(json.dumps(response_data), content_type="application/json")

