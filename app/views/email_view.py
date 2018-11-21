from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views import generic
from django.db import transaction
from app.models import EmailContents, EmailTemplates, Questions, Travel, Session, Hotel, Room, RuleSet, Attendee, \
    Answers, SeminarsUsers, TravelAttendee, Booking, RequestedBuddy, MessageHistory, \
    AttendeeGroups, AttendeeTag, SeminarSpeakers, SessionTags, TravelTag, Setting, EmailReceivers, Option, Tag, \
    EmailReceiversHistory, \
    ActivityHistory, MessageContents, EmailLanguageContents, PresetEvent, Presets
from app.views.email_content_view import EmailContentDetailView
from app.views.gbhelper.language_helper import LanguageH
from app.views.mail import Mailer
from .filter import FilterView
from django.http import Http404
# from .message_view import MessageView
from .common_views import GroupView, CommonContext, EventView
from django.db.models import Q
from .mail import MailHelper
from .page_view import PageDetailView
import re
import json
import os
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from .common_views import TimeDetailView
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.gbhelper.editor_helper import EditorHelper
from bs4 import BeautifulSoup


class EmailView(generic.TemplateView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'message_permission'):
            event_id = request.session['event_auth_user']['event_id']
            emails = EmailContents.objects.filter(template__event_id=event_id, is_show=1)
            for email in emails:
                email.total_receiver = email.emailreceivers_set.filter(is_show=1).count()
                email.sent_receiver = email.emailreceivers_set.filter(status='sent', is_show=1).count()
            emailTemplates = EmailTemplates.objects.filter(event_id=event_id, category='email_templates', is_show=1)
            email_setting = Setting.objects.filter(name='sender_email', event_id=event_id)
            if email_setting.exists():
                sender_email = email_setting[0].value
            else:
                sender_email = 'mahedi@workspaceit.com'
            context = {
                "emails": emails,
                "emailTemplates": emailTemplates,
                "sender_email": sender_email
            }
            return render(request, 'email_content/email_contents.html', context)

    def post(self, request):
        if EventView.check_permissions(request, 'message_permission'):
            try:
                response_data = {}
                event_id = request.session['event_auth_user']['event_id']
                admin_id = request.session['event_auth_user']['id']
                subject = request.POST.get('subject')
                name = request.POST.get('name')
                template_id = request.POST.get('template_id')
                sender_email = request.POST.get('email_sender')
                email_form = {
                    "subject": subject,
                    "name": name,
                    "template_id": template_id,
                    "sender_email": sender_email,
                    "last_updated_by_id": admin_id
                }
                if 'id' in request.POST:
                    email_id = request.POST.get('id')
                    old_email_content = EmailContents.objects.get(id=email_id)
                    if old_email_content.name == 'default-email-confirmation':
                        email_form['name'] = 'default-email-confirmation'
                    if not (
                            EmailContents.objects.filter(name=email_form['name'], is_show=1,
                                                         template__event_id=event_id).exclude(
                                id=email_id).exists()):
                        EmailContents.objects.filter(id=email_id).update(**email_form)
                        email = EmailContents.objects.get(id=email_id)
                        total_receiver = email.emailreceivers_set.all().count()
                        sent_receiver = email.emailreceivers_set.filter(status='sent').count()
                        response_data = {
                            'success': True,
                            'email': email.as_dict(),
                            'total_receiver': total_receiver,
                            'sent_receiver': sent_receiver,
                            'message': 'Email Updated Successfully',
                        }
                    else:
                        response_data = {
                            'success': False,
                            'message': 'Email Name Allready Exists ',
                        }
                else:
                    if not (
                            EmailContents.objects.filter(name=email_form['name'], is_show=1,
                                                         template__event_id=event_id).exists()):
                        email_form['created_by_id'] = admin_id
                        email = EmailContents(**email_form)
                        email.save()
                        email_data = email.as_dict()
                        total_receiver = email.emailreceivers_set.all().count()
                        sent_receiver = email.emailreceivers_set.filter(status='sent').count()
                        response_data = {
                            'success': True,
                            'email': email.as_dict(),
                            'total_receiver': total_receiver,
                            'sent_receiver': sent_receiver,
                            'message': 'Email created Successfully',
                        }
                    else:
                        response_data = {
                            'success': False,
                            'message': 'Email Name Allready Exists ',
                        }

                return HttpResponse(json.dumps(response_data), content_type="application/json")

            except Exception as e:
                print(e)
                response_data = {
                    'success': False,
                    'message': 'Something went wrong. Please try again.'
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data = {
                'success': False,
                'message': 'You do not have Permission to do this'
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def email_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        email_id = request.POST.get('email_id')
        email = EmailContents.objects.get(id=email_id)

        duplicate_existance = EmailContents.objects.filter(name=email.name + '[Copy]', template__event_id=event_id)
        if duplicate_existance.exists():
            response_data['error'] = 'This email is already make a duplicate.'
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        email.pk = None
        email.name += '[Copy]'
        email.created_by_id = request.session['event_auth_user']['id']
        email.last_updated_by_id = request.session['event_auth_user']['id']
        email.save()
        email_contents = EmailLanguageContents.objects.filter(email_content_id=email_id)
        content_languages = []
        for email_lang in email_contents:
            content_languages.append(
                EmailLanguageContents(email_content_id=email.id, language_id=email_lang.language_id,
                                      content=email_lang.content))
        EmailLanguageContents.objects.bulk_create(content_languages)
        response_data['success'] = "Create duplicate email Successfully"
        response_data['email'] = email.as_dict()
        response_data['total_receiver'] = email.emailreceivers_set.filter(id=email.id).count()
        response_data['sent_receiver'] = email.emailreceivers_set.filter(id=email.id, status='sent').count()
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def delete(request):
        response_data = {}
        email_content_id = request.POST.get('id')
        email = EmailContents.objects.get(id=email_content_id)
        default_emails = ['default-email-confirmation', 'request-login-confirmation', 'reset-password-confirmation',
                          'session-no-conflict-email-confirmation', 'session-conflict-email-confirmation']
        if email.name in default_emails:
            response_data['warning'] = "You can't delete the This Email"
        else:
            EmailContents.objects.filter(id=email_content_id).update(is_show=0)
            response_data['success'] = "Email Deleted Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def send_email(request, attendee, email_content):
        try:
            # content = email_content.content
            content = EmailView.get_content_with_lang(attendee.event_id, email_content.id,
                                                      attendee.language_id)
            content = email_content.template.content.replace('{content}', content)
            content = EmailContentDetailView.replace_questions_variable(request, content, attendee,
                                                                        attendee.language_id)
            content = EmailContentDetailView.replace_sessions(request, content, attendee, attendee.language_id)
            content = EmailContentDetailView.replace_travels(request, content, attendee, attendee.language_id)
            content = EmailContentDetailView.replace_hotels(request, content, attendee, attendee.language_id)
            content = EmailContentDetailView.replace_general_tags(request, content, attendee, attendee.language_id)
            content = EmailContentDetailView.replace_economy_tags(request, content, attendee, attendee.language_id)
            content = EmailContentDetailView.replace_general_questions(request, content, attendee, attendee.language_id)
            content = EmailContentDetailView.replace_photos(request, content, attendee, attendee.language_id)
            # mail_template_content = email_content.template.content.replace('{content}', content)
            mail_template_content = content
            subject = LanguageH.get_email_subject_by_language(attendee.language_id, email_content)
            to = attendee.email
            if email_content.sender_email:
                sender_mail = email_content.sender_email
            else:
                sender_mail = "mahedi@workspaceit.com"
            MailHelper.mail_template_send(mail_template_content, subject, to, sender_mail)
        except Exception as e:
            ErrorR.efail(e)
        return

    def get_content_with_lang(event_id, email_id, language_id):
        content = ""
        try:
            email_content = EmailLanguageContents.objects.filter(email_content_id=email_id, language_id=language_id)
            if email_content.exists():
                content = email_content[0].content
            else:
                defult_language = PresetEvent.objects.filter(event_id=event_id).first()
                default_content = EmailLanguageContents.objects.filter(email_content_id=email_id,
                                                                       language_id=defult_language.preset_id).first()
                content = default_content.content
        except Exception as e:
            ErrorR.efail(e)
        return content

    def add_or_update_email_receivers(attendee, email_id, admin_id):
        try:
            receiver = EmailReceivers.objects.filter(attendee_id=attendee.id, email_content_id=email_id,
                                                     is_show=1).first()
            if receiver:
                EmailReceivers.objects.filter(id=receiver.id).update(status='sent', last_received=datetime.now())
            else:
                receiver_form = {
                    'firstname': attendee.firstname,
                    'lastname': attendee.lastname,
                    'email': attendee.email,
                    'status': 'sent',
                    'added_by_id': admin_id,
                    'email_content_id': email_id,
                    'attendee_id': attendee.id,
                    'is_show': 1,
                }
                receiver = EmailReceivers(**receiver_form)
                receiver.save()
            receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
            receiver_history.save()
        except Exception as e:
            ErrorR.efail(e)
        return ''


class EmailDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            email = EmailContents.objects.filter(id=pk,
                                                 template__event_id=self.request.session['event_auth_user'][
                                                     'event_id']).first()
            if email:
                defult_language = PresetEvent.objects.filter(event_id=email.template.event_id).first()
                email_content = EmailLanguageContents.objects.filter(email_content_id=pk,
                                                                     language_id=defult_language.preset_id).first()
                if email_content:
                    email.content = email_content.content
                return email
            else:
                raise Http404
        except EmailContents.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        email = self.get_object(pk)
        context = {
            "email": email.as_dict()
        }
        return HttpResponse(json.dumps(context), content_type="application/json")


class EmailReceiversView(generic.TemplateView):

    def get(self, request, pk):
        if EventView.check_read_permissions(request, 'message_permission'):
            email = EmailDetailView.get_object(self, pk)
            email_receivers = EmailReceivers.objects.filter(email_content_id=pk, is_show=1)
            for receiver in email_receivers:
                receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))

            event_id = request.session['event_auth_user']['event_id']
            quick_filter = RuleSet.objects.filter(name='quick-filter',
                                                  created_by_id=request.session['event_auth_user']['id'],
                                                  group__event_id=event_id)
            quick_filter_id = ''
            if quick_filter.exists():
                quick_filter_id = quick_filter[0].id
            common_context = CommonContext.get_all_common_context(request)
            context = {
                "email": email,
                "email_receivers": email_receivers,
                'quick_filter_id': quick_filter_id,

            }
            context.update(common_context)
            filter_context = CommonContext.get_filter_context(request)
            context.update(filter_context)
            return render(request, 'email_content/email_receivers.html', context)

    def search_receivers(request):
        from django.db.models.functions import Concat
        from django.db.models import Value
        search_key = request.GET.get('search_key').strip()
        email_id = request.GET.get('email_id')
        if search_key == '':
            email_receivers = EmailReceivers.objects.filter(email_content_id=email_id, is_show=1)
        else:
            email_receivers = EmailReceivers.objects.annotate(
                full_name=Concat('firstname', Value(' '), 'lastname')).filter(Q(
                Q(firstname__istartswith=search_key) | Q(lastname__istartswith=search_key) | Q(
                    email__istartswith=search_key) | Q(full_name__istartswith=search_key)) & Q(
                email_content_id=email_id, is_show=1))
        for receiver in email_receivers:
            receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
        context = {
            "email_receivers": email_receivers
        }
        return render(request, 'email_content/receivers_list.html', context)

    def change_receiver_status(request):
        response_data = {}
        receivers = json.loads(request.POST.get('receivers'))
        status = request.POST.get('status')
        ErrorR.ex_time_init()
        # for receiver in receivers:
        #     EmailReceivers.objects.filter(id=int(receiver)).update(status=status)
        EmailReceivers.objects.filter(id__in=receivers).update(status=status)
        ErrorR.ex_time()
        response_data['success'] = True
        response_data['message'] = "Receivers Status Changed Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_receiver(request):
        response_data = {}
        receivers = json.loads(request.POST.get('receivers'))
        # for receiver in receivers:
        #     EmailReceivers.objects.filter(id=int(receiver['id'])).update(is_show=0)
        EmailReceivers.objects.filter(id__in=receivers).update(is_show=0)
        response_data['success'] = True
        response_data['message'] = "Receivers Delete Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def download_email(request, pk):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        receiver_id = pk
        receiver = EmailReceivers.objects.filter(id=int(receiver_id))
        cwd = os.getcwd()
        file_name = "email_content.eml"
        outfile_name = os.path.join(cwd, file_name)
        if receiver.exists():
            receiver = receiver[0]
            previewContent = ''
            # content = receiver.email_content.content
            msg = MIMEMultipart('alternative')
            if receiver.attendee_id != None:
                content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                                                          receiver.attendee.language_id)
                previewContent = receiver.email_content.template.content.replace('{content}', content)
                previewContent = EmailContentDetailView.replace_questions_variable(request, previewContent,
                                                                                   receiver.attendee,
                                                                                   receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_sessions(request, previewContent, receiver.attendee,
                                                                         receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_travels(request, previewContent, receiver.attendee,
                                                                        receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_hotels(request, previewContent, receiver.attendee,
                                                                       receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_general_tags(request, previewContent, receiver.attendee,
                                                                             receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_economy_tags(request, previewContent, receiver.attendee,
                                                                             receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_general_questions(request, previewContent,
                                                                                  receiver.attendee,
                                                                                  receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_photos(request, previewContent, receiver.attendee,
                                                                       receiver.attendee.language_id)
                msg['Subject'] = LanguageH.get_email_subject_by_language(receiver.attendee.language_id,
                                                                         receiver.email_content)
            else:
                default_language = PresetEvent.objects.get(event_id=event_id)
                content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                                                          default_language.preset_id)
                previewContent = receiver.email_content.template.content.replace('{content}', content)
                previewContent = EmailReceiversView.replace_empty_data(previewContent, receiver)
                previewContent = EmailContentDetailView.replace_general_questions(request, previewContent, None, None)
                previewContent = EmailContentDetailView.replace_photos(request, previewContent, None, None)
                msg['Subject'] = LanguageH.get_email_subject_by_language(default_language.preset_id,
                                                                         receiver.email_content)
            html_data = previewContent

            msg['From'] = receiver.email_content.sender_email
            msg['To'] = receiver.email
            part = MIMEText(html_data, 'html')
            msg.attach(part)
            with open(outfile_name, 'w') as outfile:
                gen = generator.Generator(outfile)
                gen.flatten(msg)
            file_data = open(outfile_name, "rb")
            response = HttpResponse(file_data, content_type='message/rfc822')
            response['Content-Disposition'] = 'attachment; filename=' + file_name
            os.remove(outfile_name)
            return response
        else:
            response_data['success'] = False
            response_data['message'] = "Receivers Not Found"
            return response_data

    def receiver_preview(request, pk):
        event_id = request.session['event_auth_user']['event_id']
        receiver_data = EmailReceivers.objects.filter(id=pk)
        if receiver_data.exists():
            receiver = receiver_data[0]
            previewContent = ''

            # content = receiver.email_content.content
            if receiver.attendee_id != None:
                content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                                                          receiver.attendee.language_id)
                previewContent = receiver.email_content.template.content.replace('{content}', content)
                previewContent = EmailContentDetailView.replace_questions_variable(request, previewContent,
                                                                                   receiver.attendee,
                                                                                   receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_sessions(request, previewContent, receiver.attendee,
                                                                         receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_travels(request, previewContent, receiver.attendee,
                                                                        receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_hotels(request, previewContent, receiver.attendee,
                                                                       receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_general_tags(request, previewContent, receiver.attendee,
                                                                             receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_economy_tags(request, previewContent, receiver.attendee,
                                                                             receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_general_questions(request, previewContent,
                                                                                  receiver.attendee,
                                                                                  receiver.attendee.language_id)
                previewContent = EmailContentDetailView.replace_photos(request, previewContent, receiver.attendee,
                                                                       receiver.attendee.language_id)
            else:
                default_language = PresetEvent.objects.get(event_id=event_id)
                content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                                                          default_language.preset_id)
                previewContent = receiver.email_content.template.content.replace('{content}', content)
                previewContent = EmailReceiversView.replace_empty_data(previewContent, receiver)
                previewContent = EmailContentDetailView.replace_general_questions(request, previewContent, None, None)
                previewContent = EmailContentDetailView.replace_photos(request, previewContent, None, None)

            context = {
                'email_contents': previewContent
            }
            import sys
            print(sys.getsizeof(previewContent))
            return render(request, 'message/email_preview.html', context)
        else:
            return Http404

    def replace_empty_data(content, receiver):
        session_regex = r"({\"sessions\":)(.|\s|\n)*?(]})"
        session_default = '{"sessions":[{"columns":"name,start,end","sort-column":"start","status":"attending","time-date":"Y.M.d H:i"}]}'
        if '{"sessions"}' in content:
            content = content.replace('{"sessions"}', session_default)
        session_matches = re.finditer(session_regex, content)
        for session_match in session_matches:
            content = content.replace(session_match.group(), '')

        travel_default = '{"travels":[{"columns":"name, departure-city, departure-time-date, arrival-city, arrival-time-date","sort-column":"departure-date-time","date-time":"Y.M.d H:i"}]}'
        if '{"travels"}' in content:
            content = content.replace('{"travels"}', travel_default)
        travel_regex = r"({\"travels\":)(.|\s|\n)*?(]})"
        travel_matches = re.finditer(travel_regex, content)
        for travel_match in travel_matches:
            content = content.replace(travel_match.group(), '')

        hotel_default = '{"hotels":[{"columns":"name, room-description, check-in, check-out","sort-column":"check-in","date":"Y.M.d"}]}'
        if '{"hotels"}' in content:
            content = content.replace('{"hotels"}', hotel_default)
        booking_regex = r"({\"hotels\":)(.|\s|\n)*?(]})"
        booking_matches = re.finditer(booking_regex, content)
        for booking_match in booking_matches:
            content = content.replace(booking_match.group(), '')

        question_default = '{"questions":[{"id":"registration-date,last-update-date,attendee-group,tags,","group-id":"","columns":"questions,answer","sort-column":"order","date-time":"Y.M.d H:i"}]}'
        if '{"questions"}' in content:
            content = content.replace('{"questions"}', question_default)
        question_regex = r"({\"questions\":)(.|\s|\n)*?(]})"
        question_matches = re.finditer(question_regex, content)
        for question_match in question_matches:
            content = content.replace(question_match.group(), '')

        content = content.replace('{calendar}', '')
        content = content.replace('{uid_link}', '')
        content = content.replace('{uid}', '')
        content = content.replace('{bid}', '')
        content = content.replace('{registration_date}', '')
        content = content.replace('{updated_date}', '')
        content = content.replace('{attendee_groups}', '')
        content = content.replace('{tags}', '')
        content = content.replace('{messages_link}', '')
        content = content.replace('{base_url}', '')
        content = content.replace('{order_table}', '')
        content = content.replace('{multiple_order_table}', '')
        content = content.replace('{balance_table}', '')
        content = content.replace('{order_value_paid_order}', '')
        content = content.replace('{multiple_order_value_paid_order}', '')
        content = content.replace('{order_value_pending_order}', '')
        content = content.replace('{multiple_order_value_pending_order}', '')
        content = content.replace('{order_value_open_order}', '')
        content = content.replace('{multiple_order_value_open_order}', '')
        content = content.replace('{order_value_all_order}', '')
        content = content.replace('{multiple_order_value_all_order}', '')
        content = content.replace('{order_value_credit_order}', '')
        content = content.replace('{multiple_order_value_credit_order}', '')
        content = content.replace('{receipt}', '')
        content = content.replace('{first_name}', receiver.firstname)
        content = content.replace('{last_name}', receiver.lastname)
        content = content.replace('{email_address}', receiver.email)
        return content

    def send_email(request):
        # from wsitEvent.tasks import mail_task
        import boto.sqs
        from boto.sqs.message import Message
        from django.conf import settings
        import os
        import time
        from django.db.models.aggregates import Count
        try:
            ErrorR.ex_time_init()
            event_id = request.session['event_auth_user']['event_id']
            receivers = json.loads(request.POST.get('receivers'))
            response_data = {}
            updated_receivers = []
            email_activities = []
            email_receivers_history = []
            message_history_flag = False
            message_histoty_id = 0
            conn = boto.sqs.connect_to_region(settings.SES_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            queue = conn.get_queue('test_email_queue')
            start_time = time.time()
            email_queue = []
            i = 1
            all_receivers = EmailReceivers.objects.filter(id__in=receivers)
            email_content_id = request.POST.get('email_id')
            email_content = EmailContents.objects.get(id=email_content_id)
            content_languages = {}
            attendee_languages = Attendee.objects.filter(emailreceivers__in=receivers).values('language_id').annotate(
                lcount=Count('language_id'))
            for attendee_lang in attendee_languages:
                # email_content_language = email_content.emaillanguagecontents_set.all()
                # content_languages = {}
                # for content_lang in email_content_language:
                language_id = str(attendee_lang['language_id'])
                content_languages["subject_" + language_id] = LanguageH.get_email_subject_by_language(language_id,
                                                                                                      email_content)
                content_languages["content_" + language_id] = EmailView.get_content_with_lang(event_id,
                                                                                              email_content.id,
                                                                                              language_id)
                content_languages["economy_language_" + language_id] = LanguageH.catch_lang_key_obj(event_id,
                                                                                                    language_id,
                                                                                                    'economy')
                content_languages["session_language_" + language_id] = LanguageH.catch_lang_key_obj(event_id,
                                                                                                    language_id,
                                                                                                    'sessions')
                content_languages["hotel_language_" + language_id] = LanguageH.catch_lang_key_obj(event_id, language_id,
                                                                                                  'hotels')
                content_languages["session_language_" + language_id]['langkey'].update(
                    content_languages["economy_language_" + language_id]['langkey'])
                content_languages["hotel_language_" + language_id]['langkey'].update(
                    content_languages["economy_language_" + language_id]['langkey'])
                content_languages["language_" + language_id] = LanguageH.catch_lang_key_obj(event_id, language_id,
                                                                                            'economy')
            default_date_time_format = EmailContentDetailView.get_language_date_format(event_id)
            ErrorR.ex_time()
            for receiver in all_receivers:
                # ErrorR.ex_time_init()
                # if len(email_queue) == 0:
                #     ErrorR.ex_time_init()
                # receiver_info = EmailReceivers.objects.filter(id=int(receiver_id['id']))
                # if receiver_info.exists():
                #     receiver = receiver_info[0]
                # content = receiver.email_content.content
                to = receiver.email
                sender_mail = receiver.email_content.sender_email
                EmailReceivers.objects.filter(id=receiver.id).update(status='sent', last_received=datetime.now())
                updated_receiver = EmailReceivers.objects.get(id=receiver.id)
                updated_receiver_dict = updated_receiver.as_dict()
                updated_receiver_dict['last_received'] = str(
                    TimeDetailView.utc_to_local(request, updated_receiver_dict['last_received']))
                updated_receivers.append(updated_receiver_dict)
                if receiver.attendee_id != None:
                    # subject = LanguageH.get_email_subject_by_language(receiver.attendee.language_id,receiver.email_content)
                    # ErrorR.ex_time()
                    # ErrorR.ex_time_init()
                    # content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                    #                                           receiver.attendee.language_id)
                    subject = content_languages["subject_" + str(receiver.attendee.language_id)]
                    content = content_languages["content_" + str(receiver.attendee.language_id)]

                    mail_template_content = receiver.email_content.template.content.replace('{content}', content)

                    mail_template_content = EmailContentDetailView.replace_questions_variable(request,
                                                                                              mail_template_content,
                                                                                              receiver.attendee,
                                                                                              receiver.attendee.language_id,
                                                                                              default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_sessions(request, mail_template_content,
                                                                                    receiver.attendee,
                                                                                    receiver.attendee.language_id,
                                                                                    content_languages[
                                                                                        "session_language_" + str(
                                                                                            receiver.attendee.language_id)],
                                                                                    default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_travels(request, mail_template_content,
                                                                                   receiver.attendee,
                                                                                   receiver.attendee.language_id,
                                                                                   default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_hotels(request, mail_template_content,
                                                                                  receiver.attendee,
                                                                                  receiver.attendee.language_id,
                                                                                  content_languages[
                                                                                      "hotel_language_" + str(
                                                                                          receiver.attendee.language_id)],
                                                                                  default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_general_tags(request, mail_template_content,
                                                                                        receiver.attendee,
                                                                                        receiver.attendee.language_id)

                    mail_template_content = EmailContentDetailView.replace_economy_tags(request, mail_template_content,
                                                                                        receiver.attendee,
                                                                                        content_languages[
                                                                                            "economy_language_" + str(
                                                                                                receiver.attendee.language_id)])

                    mail_template_content = EmailContentDetailView.replace_general_questions(request,
                                                                                             mail_template_content,
                                                                                             receiver.attendee,
                                                                                             receiver.attendee.language_id)

                    mail_template_content = EmailContentDetailView.replace_photos(request, mail_template_content,
                                                                                  receiver.attendee,
                                                                                  receiver.attendee.language_id)

                    if not message_history_flag:
                        message_history = MessageHistory(subject=subject, message='N/A',
                                                         admin_id=request.session['event_auth_user']['id'],
                                                         type='mail')
                        message_history.save()
                        message_histoty_id = message_history.id
                        message_history_flag = True
                    receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
                    email_receivers_history.append(receiver_history)
                    activity_history = ActivityHistory(attendee_id=receiver.attendee.id,
                                                       admin_id=request.session['event_auth_user']['id'],
                                                       activity_type='message', category='message',
                                                       message_id=message_histoty_id,
                                                       event_id=request.session['event_auth_user']['event_id'])
                    email_activities.append(activity_history)
                    # MailHelper.mail_template_send(mail_template_content, subject, to, sender_mail)
                    # mail_task.apply_async([
                    #     {
                    #         'template':mail_template_content,
                    #         'subject': subject,
                    #         'to': to,
                    #         'sender': sender_mail
                    #     }
                    # ])
                    # m = Message()
                    data = json.dumps({
                        'to': to,
                        'sender': sender_mail,
                        'subject': subject,
                        'template': mail_template_content,
                        'environment': os.environ['ENVIRONMENT_TYPE'],
                        'local_env': settings.LOCAL_ENV
                    })
                    # m.set_body(data)
                    email_queue.append((i, data, 0))
                    # queue.write(m)
                else:
                    default_language = PresetEvent.objects.get(event_id=event_id)
                    subject = LanguageH.get_email_subject_by_language(default_language.preset_id,
                                                                      receiver.email_content)
                    content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                                                              default_language.preset_id)
                    mail_template_content = receiver.email_content.template.content.replace('{content}', content)
                    mail_template_content = EmailReceiversView.replace_empty_data(mail_template_content, receiver)
                    receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
                    email_receivers_history.append(receiver_history)
                    # MailHelper.mail_template_send(mail_template_content, subject, to, sender_mail)
                    # mail_task.apply_async([
                    #     {
                    #         'template':mail_template_content,
                    #         'subject': subject,
                    #         'to': to,
                    #         'sender': sender_mail
                    #     }
                    # ])
                    # m = Message()
                    data = json.dumps({
                        'to': to,
                        'sender': sender_mail,
                        'subject': subject,
                        'template': mail_template_content,
                        'environment': os.environ['ENVIRONMENT_TYPE'],
                        'local_env': settings.LOCAL_ENV
                    })
                    email_queue.append((i, data, 0))
                    # m.set_body(data)
                    # queue.write(m)
                # ErrorR.ex_time()
                if i == 10:
                    # ErrorR.ex_time_init()
                    queue.write_batch(email_queue)
                    # ErrorR.ex_time()
                    # ErrorR.ex_time()
                    email_queue = []
                    i = 1
                else:
                    i = i + 1
            # ErrorR.ex_time_init()
            if i > 1:
                queue.write_batch(email_queue)
            # ErrorR.ex_time()
            ErrorR.ex_time_init()
            ActivityHistory.objects.bulk_create(email_activities)
            EmailReceiversHistory.objects.bulk_create(email_receivers_history)
            ErrorR.ex_time()
            response_data['success'] = True
            response_data['message'] = 'Email Sent Successfully'
            response_data['updated_receivers'] = updated_receivers

            ErrorR.ilog("-----------Email-Total-time--------------")
            ErrorR.ilog(time.time() - start_time)
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            print(e)
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            response_data = {
                'success': False,
                'message': 'Something went wrong. Please try again.'
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def send_email_by_lambda(request):
        # from wsitEvent.tasks import mail_task

        import time

        from django.db.models.aggregates import Count
        try:
            ErrorR.ex_time_init("Processing of DEF")
            event_id = request.session['event_auth_user']['event_id']
            receivers = json.loads(request.POST.get('receivers'))
            response_data = {}
            updated_receivers = []
            email_activities = []
            email_receivers_history = []
            start_time = time.time()
            all_receivers = EmailReceivers.objects.filter(id__in=receivers)
            email_content_id = request.POST.get('email_id')
            email_content = EmailContents.objects.get(id=email_content_id)
            content_languages = {}
            attendee_languages = Attendee.objects.filter(emailreceivers__in=receivers).values('language_id').annotate(
                lcount=Count('language_id'))
            for attendee_lang in attendee_languages:
                # email_content_language = email_content.emaillanguagecontents_set.all()
                # content_languages = {}
                # for content_lang in email_content_language:
                language_id = str(attendee_lang['language_id'])
                content_languages["subject_" + language_id] = LanguageH.get_email_subject_by_language(language_id,
                                                                                                      email_content)
                content_languages["content_" + language_id] = EmailView.get_content_with_lang(event_id,
                                                                                              email_content.id,
                                                                                              language_id)
                content_languages["economy_language_" + language_id] = LanguageH.catch_lang_key_obj(event_id,
                                                                                                    language_id,
                                                                                                    'economy')
                content_languages["session_language_" + language_id] = LanguageH.catch_lang_key_obj(event_id,
                                                                                                    language_id,
                                                                                                    'sessions')
                content_languages["hotel_language_" + language_id] = LanguageH.catch_lang_key_obj(event_id, language_id,
                                                                                                  'hotels')
                content_languages["session_language_" + language_id]['langkey'].update(
                    content_languages["economy_language_" + language_id]['langkey'])
                content_languages["hotel_language_" + language_id]['langkey'].update(
                    content_languages["economy_language_" + language_id]['langkey'])
                content_languages["language_" + language_id] = LanguageH.catch_lang_key_obj(event_id, language_id,
                                                                                            'economy')
            default_date_time_format = EmailContentDetailView.get_language_date_format(event_id)
            ErrorR.ex_time()
            ErrorR.ex_time_init("Preparing message")
            i = 1
            message_history_flag = False
            message_histoty_id = 0

            email_container = []
            response_data['last_received'] = str(TimeDetailView.utc_to_local(request, str(datetime.now())))
            response_data['status'] = 'sent'
            for receiver in all_receivers:
                ErrorR.c_bblue("Message:" + str(i))
                i += 1
                to = receiver.email
                sender_mail = receiver.email_content.sender_email
                # EmailReceivers.objects.filter(id=receiver.id).update(status='sent', last_received=datetime.now())
                # updated_receiver = EmailReceivers.objects.get(id=receiver.id)
                # updated_receiver_dict = updated_receiver.as_dict()
                # updated_receiver_dict['last_received'] = str(
                #     TimeDetailView.utc_to_local(request, updated_receiver_dict['last_received']))
                updated_receiver_dict = {
                    'id': receiver.id,
                    # 'status': 'sent',
                    # 'last_received': last_received
                }
                updated_receivers.append(updated_receiver_dict)
                if receiver.attendee_id != None:
                    # subject = LanguageH.get_email_subject_by_language(receiver.attendee.language_id,receiver.email_content)
                    # ErrorR.ex_time()
                    # ErrorR.ex_time_init()
                    # content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                    #                                           receiver.attendee.language_id)
                    subject = content_languages["subject_" + str(receiver.attendee.language_id)]
                    content = content_languages["content_" + str(receiver.attendee.language_id)]

                    mail_template_content = receiver.email_content.template.content.replace('{content}', content)

                    mail_template_content = EmailContentDetailView.replace_questions_variable(request,
                                                                                              mail_template_content,
                                                                                              receiver.attendee,
                                                                                              receiver.attendee.language_id,
                                                                                              default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_sessions(request, mail_template_content,
                                                                                    receiver.attendee,
                                                                                    receiver.attendee.language_id,
                                                                                    content_languages[
                                                                                        "session_language_" + str(
                                                                                            receiver.attendee.language_id)],
                                                                                    default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_travels(request, mail_template_content,
                                                                                   receiver.attendee,
                                                                                   receiver.attendee.language_id,
                                                                                   default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_hotels(request, mail_template_content,
                                                                                  receiver.attendee,
                                                                                  receiver.attendee.language_id,
                                                                                  content_languages[
                                                                                      "hotel_language_" + str(
                                                                                          receiver.attendee.language_id)],
                                                                                  default_date_time_format)

                    mail_template_content = EmailContentDetailView.replace_general_tags(request,
                                                                                        mail_template_content,
                                                                                        receiver.attendee,
                                                                                        receiver.attendee.language_id)

                    mail_template_content = EmailContentDetailView.replace_economy_tags(request,
                                                                                        mail_template_content,
                                                                                        receiver.attendee,
                                                                                        content_languages[
                                                                                            "economy_language_" + str(
                                                                                                receiver.attendee.language_id)])

                    mail_template_content = EmailContentDetailView.replace_general_questions(request,
                                                                                             mail_template_content,
                                                                                             receiver.attendee,
                                                                                             receiver.attendee.language_id)

                    mail_template_content = EmailContentDetailView.replace_photos(request, mail_template_content,
                                                                                  receiver.attendee,
                                                                                  receiver.attendee.language_id)

                    if not message_history_flag:
                        message_history = MessageHistory(subject=subject, message='N/A',
                                                         admin_id=request.session['event_auth_user']['id'],
                                                         type='mail')
                        message_history.save()
                        message_histoty_id = message_history.id
                        message_history_flag = True
                    receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
                    email_receivers_history.append(receiver_history)
                    activity_history = ActivityHistory(attendee_id=receiver.attendee.id,
                                                       admin_id=request.session['event_auth_user']['id'],
                                                       activity_type='message', category='message',
                                                       message_id=message_histoty_id,
                                                       event_id=request.session['event_auth_user']['event_id'])
                    email_activities.append(activity_history)
                    # Send in parallel using several threads
                    from_address = sender_mail.strip()
                    to_address = to.strip()
                    subject = subject.strip()
                    data = {
                        "from_address": from_address,
                        "to_address": to_address,
                        "subject": subject.strip(),
                        "mime_message_html": mail_template_content.strip()
                    }
                    email_container.append(data)
                else:
                    default_language = PresetEvent.objects.get(event_id=event_id)
                    subject = LanguageH.get_email_subject_by_language(default_language.preset_id,
                                                                      receiver.email_content)
                    content = EmailView.get_content_with_lang(event_id, receiver.email_content.id,
                                                              default_language.preset_id)
                    mail_template_content = receiver.email_content.template.content.replace('{content}', content)
                    mail_template_content = EmailReceiversView.replace_empty_data(mail_template_content, receiver)
                    receiver_history = EmailReceiversHistory(receiver_id=receiver.id)
                    email_receivers_history.append(receiver_history)
                    # Send in parallel using several threads
                    from_address = sender_mail.strip()
                    to_address = to.strip()
                    subject = subject.strip()

                    data = {
                        "from_address": from_address,
                        "to_address": to_address,
                        "subject": subject.strip(),
                        "mime_message_html": mail_template_content.strip()
                    }
                    email_container.append(data)

            EmailReceivers.objects.filter(id__in=receivers).update(status='sent', last_received=datetime.now())
            ErrorR.ex_time()
            import threading
            task = threading.Thread(target=EmailReceiversView.process_mail_and_send, args=(request, email_container))
            task.start()
            ErrorR.ex_time_init("Activity History")
            ActivityHistory.objects.bulk_create(email_activities)
            EmailReceiversHistory.objects.bulk_create(email_receivers_history)
            ErrorR.ex_time()
            response_data['success'] = True
            response_data['message'] = 'Email Sent Successfully'
            response_data['updated_receivers'] = updated_receivers

            ErrorR.ilog("-----------Email-Total-time--------------")
            ErrorR.ilog(time.time() - start_time)
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            print(e)
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            response_data = {
                'success': False,
                'message': 'Something went wrong. Please try again.'
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def process_mail_and_send(request,email_container):
        import concurrent.futures
        max_threads = 2
        ErrorR.warn("Sending message data")
        ErrorR.ex_time_init()
        e = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
        for email in email_container:
            e.submit(MailHelper.mail_template_send, email['mime_message_html'], email['subject'], email['to_address'],
                     email['from_address'])
        e.shutdown()
        ErrorR.ex_time()

    def import_filter_receiver(request):
        response_data = {}
        filter_id = request.POST.get('filter_id')
        email_id = request.POST.get('email_id')
        attendees = FilterView.get_filtered_attendees(request, filter_id)
        receivers = []
        for attendee in attendees:
            receiver_data = {}
            receiver_data['id'] = attendee.id
            receiver_data['firstname'] = attendee.firstname
            receiver_data['lastname'] = attendee.lastname
            receiver_data['email'] = attendee.email
            receiver_data['attendee'] = True
            receivers.append(receiver_data)
        receiver_message = EmailReceiversView.add_receivers(request, email_id, receivers)
        email_receivers = EmailReceivers.objects.filter(email_content_id=email_id, is_show=1)
        receiver_list = []
        for receiver in email_receivers:
            receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
            context = {
                'id': receiver.id,
                'firstname': receiver.firstname,
                'lastname': receiver.lastname,
                'email': receiver.email,
                'status': receiver.status,
                'last_received': str(receiver.last_received),
            }
            receiver_list.append(context)
        # response_data['email_receivers'] = render_to_string('email_content/receivers_list.html',
        #                                                     {'email_receivers': email_receivers,'request': request})
        response_data['email_receivers'] = receiver_list
        response_data['success'] = True
        response_data['admin_permission'] = False
        if 'message_permission' in request.session['admin_permission']['content_permission'] and \
                request.session['admin_permission']['content_permission']['message_permission'][
                    'access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            response_data['admin_permission'] = True
        ErrorR.ex_time()
        response_data['message'] = receiver_message
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def import_excel_reciever(request):
        data = request.FILES.get('upload_file')
        email_id = request.POST.get('email_id')
        response_data = {}
        if data:
            from openpyxl import load_workbook
            EmailReceiversView.handle_uploaded_file(data, 'sample_import.xlsx')
            wb = load_workbook(filename='attendeeList/sample_import.xlsx', read_only=True)
            ws = wb.worksheets[0]
            receivers = []
            regex = r"([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)"
            wrong_data = 0
            for row in ws.rows:
                if not row[0].value:
                    continue
                receiver_data = {}
                matches = re.match(regex, row[0].value.strip())
                if matches:
                    receiver_data['firstname'] = ""
                    receiver_data['lastname'] = ""
                    receiver_data['email'] = row[0].value.strip()
                    receivers.append(receiver_data)
                else:
                    try:
                        receiver_data['firstname'] = row[0].value.strip()
                        receiver_data['lastname'] = row[1].value.strip()
                        matches = re.match(regex, row[2].value.strip())
                        if matches:
                            receiver_data['email'] = row[2].value.strip()
                            receivers.append(receiver_data)
                        else:
                            wrong_data += 1
                    except:
                        wrong_data += 1
            receiver_message = EmailReceiversView.add_receivers(request, email_id, receivers)
            if wrong_data:
                receiver_message += str(wrong_data) + " rows did not contain a correct email address."
            email_receivers = EmailReceivers.objects.filter(email_content_id=email_id, is_show=1)
            receiver_list = []
            for receiver in email_receivers:
                receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
                context = {
                    'id': receiver.id,
                    'firstname': receiver.firstname,
                    'lastname': receiver.lastname,
                    'email': receiver.email,
                    'status': receiver.status,
                    'last_received': str(receiver.last_received),
                }
                receiver_list.append(context)
            # response_data['email_receivers'] = render_to_string('email_content/receivers_list.html',
            #                                                     {'email_receivers': email_receivers,'request': request})
            response_data['email_receivers'] = receiver_list
            response_data['success'] = True
            response_data['admin_permission'] = False
            if 'message_permission' in request.session['admin_permission']['content_permission'] and \
                    request.session['admin_permission']['content_permission']['message_permission'][
                        'access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
                response_data['admin_permission'] = True
            response_data['message'] = receiver_message
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def handle_uploaded_file(f, filename):
        import os

        if not os.path.exists("attendeeList/"):
            os.makedirs("attendeeList/")
        filepath = 'attendeeList/'
        with open(filepath + filename, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def import_clipboard_receiver(request):
        response_data = {}
        email_id = request.POST.get('email_id')
        receivers = []
        wrong_data = 0
        clipboard_data = request.POST.get('clipboard_data').split("\n")
        for clipboard in clipboard_data:
            receiver_data = {}
            if clipboard.strip() != "":
                separator = clipboard.split(",")
                if len(separator) == 3:
                    receiver_data['firstname'] = separator[0].strip()
                    receiver_data['lastname'] = separator[1].strip()
                    regex = r"([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)"
                    matches = re.match(regex, separator[2].strip())
                    if matches:
                        receiver_data['email'] = separator[2].strip()
                        receivers.append(receiver_data)
                    else:
                        wrong_data += 1
                elif len(separator) == 1:
                    receiver_data['firstname'] = ""
                    receiver_data['lastname'] = ""
                    regex = r"([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)"
                    matches = re.match(regex, separator[0].strip())
                    if matches:
                        receiver_data['email'] = separator[0].strip()
                        receivers.append(receiver_data)
                    else:
                        wrong_data += 1
                else:
                    wrong_data += 1
        receiver_message = EmailReceiversView.add_receivers(request, email_id, receivers)
        if wrong_data:
            receiver_message += str(wrong_data) + " rows did not contain a correct email address."
        email_receivers = EmailReceivers.objects.filter(email_content_id=email_id, is_show=1)
        receiver_list = []
        ErrorR.ex_time_init()
        for receiver in email_receivers:
            receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
            context = {
                'id': receiver.id,
                'firstname': receiver.firstname,
                'lastname': receiver.lastname,
                'email': receiver.email,
                'status': receiver.status,
                'last_received': str(receiver.last_received),
            }
            receiver_list.append(context)
            # receiver_list.append(receiver.as_dict())
        # response_data['email_receivers'] = render_to_string('email_content/receivers_list.html',
        #                                                     {'email_receivers': email_receivers,'request': request})
        ErrorR.ex_time()
        response_data['email_receivers'] = receiver_list
        response_data['success'] = True
        response_data['admin_permission'] = False
        if 'message_permission' in request.session['admin_permission']['content_permission'] and \
                request.session['admin_permission']['content_permission']['message_permission'][
                    'access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            response_data['admin_permission'] = True
        response_data['message'] = receiver_message
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add_receivers(request, email_id, receivers):
        duplicate_receiver = 0
        added_receiver = 0
        messages = 'Added X receivers successfully. There were Y duplicates. Z rows did not contain a correct email address'
        message = ''
        all_recievers = []
        duplicate_attendees = []
        for receiver in receivers:
            receiver_form = {
                'firstname': receiver['firstname'],
                'lastname': receiver['lastname'],
                'email': receiver['email'],
                'status': 'not_sent',
                'added_by_id': request.session['event_auth_user']['id'],
                'email_content_id': email_id
            }
            if 'id' in receiver and EmailReceivers.objects.filter(attendee_id=receiver['id'], is_show=1, email_content_id=email_id).exists():
                duplicate_receiver = duplicate_receiver + 1
            elif 'attendee' in receiver:
                receiver_form['attendee_id'] = receiver['id']
                new_receiver = EmailReceivers(**receiver_form)
                all_recievers.append(new_receiver)
                added_receiver = added_receiver + 1
            else:
                attendees = Attendee.objects.filter(email=receiver['email'],
                                                   event_id=request.session['event_auth_user']['event_id']).exclude(id__in=duplicate_attendees).values(
                    'id', 'firstname', 'lastname')
                if attendees.exists():
                    for attendee in attendees:
                        if not EmailReceivers.objects.filter(attendee_id=attendee['id'], is_show=1, email_content_id=email_id).exists():
                            receiver_form['attendee_id'] = attendee['id']
                            receiver_form['firstname'] = attendee['firstname']
                            receiver_form['lastname'] = attendee['lastname']
                            duplicate_attendees.append(attendee['id'])
                            new_receiver = EmailReceivers(**receiver_form)
                            all_recievers.append(new_receiver)
                            added_receiver = added_receiver + 1
                        else:
                            duplicate_receiver = duplicate_receiver + 1
                elif not Attendee.objects.filter(email=receiver['email'],event_id=request.session['event_auth_user']['event_id']).exists() and not EmailReceivers.objects.filter(email=receiver['email'], is_show=1, email_content_id=email_id).exists():
                    new_receiver = EmailReceivers(**receiver_form)
                    all_recievers.append(new_receiver)
                    added_receiver = added_receiver + 1
        EmailReceivers.objects.bulk_create(all_recievers)
        if added_receiver > 0:
            message += 'Added ' + str(added_receiver) + ' receivers successfully.'
        if duplicate_receiver > 0:
            message += ' There were ' + str(duplicate_receiver) + ' duplicates.'
        return message


class EmailContentView(generic.DetailView):
    def get(self, request, pk):
        if EventView.check_permissions(request, 'message_permission'):
            language_id = None
            try:
                email = EmailContents.objects.filter(id=pk,
                                                     template__event_id=request.session['event_auth_user'][
                                                         'event_id']).first()
                if email:
                    defult_language = PresetEvent.objects.filter(event_id=email.template.event_id).first()
                    language_id = defult_language.preset_id
                    email_content = EmailLanguageContents.objects.filter(email_content_id=pk,
                                                                         language_id=defult_language.preset_id).first()
                    if email_content:
                        email.content = email_content.content
                else:
                    raise Http404
            except EmailContents.DoesNotExist:
                raise Http404
            editor_common_context = EditorHelper.get_editor_context(request, language_id=language_id, styles=False)
            [presets, presetsEvent] = LanguageH.get_preset_list(request.session['event_auth_user']['event_id'],
                                                                request.session['event_auth_user']['type'])
            content = BeautifulSoup(email.content, 'html5lib')

            context = {
                "email": email,
                # "editor_content": content.prettify(),
                "editor_content": email.content,
                "presets": presets,
                "presetsEvent": presetsEvent
            }
            context.update(editor_common_context)
            # return render(request, 'email_content/contents.html', context)
            return render(request, 'email_content/contents_froala.html', context)
        else:
            raise Http404

    def post(self, request, pk):
        if EventView.check_permissions(request, 'message_permission'):
            response_data = {}
            email_id = pk
            content = request.POST.get('content')
            ErrorR.okblue(content)
            language_id = request.POST.get('language_id')
            try:
                email, email_created = EmailLanguageContents.objects.update_or_create(language_id=language_id,
                                                                                      email_content_id=email_id,
                                                                                      defaults={
                                                                                          "content": content
                                                                                      })
                if email_created:
                    response_data = {
                        'success': True,
                        'message': 'Email Content Created Successfully',
                    }
                else:
                    response_data = {
                        'success': True,
                        'message': 'Email Content Updated Successfully',
                    }
            except Exception as e:
                ErrorR.efail(e)
                response_data = {
                    'success': False,
                    'message': 'Something went wrong',
                }
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data = {
                'success': False,
                'message': 'You do not have Permission to do this',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def get_floara_editor(request,pk,*args, **kwargs):
    #     if EventView.check_permissions(request, 'message_permission'):
    #         language_id = None
    #         try:
    #             email = EmailContents.objects.filter(id=pk,
    #                                                  template__event_id=request.session['event_auth_user'][
    #                                                      'event_id']).first()
    #             if email:
    #                 defult_language = PresetEvent.objects.filter(event_id=email.template.event_id).first()
    #                 language_id = defult_language.preset_id
    #                 email_content = EmailLanguageContents.objects.filter(email_content_id=pk,
    #                                                                      language_id=defult_language.preset_id).first()
    #                 if email_content:
    #                     email.content = email_content.content
    #             else:
    #                 raise Http404
    #         except EmailContents.DoesNotExist:
    #             raise Http404
    #         editor_common_context = EditorHelper.get_editor_context(request,language_id)
    #         [presets, presetsEvent] = LanguageH.get_preset_list(request.session['event_auth_user']['event_id'],
    #                                                             request.session['event_auth_user']['type'])
    #         context = {
    #             "email": email,
    #             # "questionGroup": questionGroup,
    #             "presets": presets,
    #             "presetsEvent": presetsEvent
    #         }
    #         context.update(editor_common_context)
    #         return render(request, 'email_content/contents_froala.html', context)
    #     else:
    #         raise Http404

    def show_preview(request):
        content = request.POST.get('content')
        email_id = request.POST.get('email_id')
        email = EmailContents.objects.get(id=email_id)
        previewContent = ''
        if email.template:
            previewContent = email.template.content.replace('{content}', content)
            previewContent = EmailContentDetailView.replace_questions_variable(request, previewContent, None, None,
                                                                               None, True)
            previewContent = EmailContentDetailView.replace_sessions(request, previewContent, None, None, None, None,
                                                                     True)
            previewContent = EmailContentDetailView.replace_travels(request, previewContent, None, None, None, True)
            previewContent = EmailContentDetailView.replace_hotels(request, previewContent, None, None, None, None,
                                                                   True)
            previewContent = EmailContentDetailView.replace_general_tags(request, previewContent, None, None, True)
            previewContent = EmailContentDetailView.replace_economy_tags(request, previewContent, None, None, True)
            previewContent = EmailContentDetailView.replace_general_questions(request, previewContent, None, None, True)
            previewContent = EmailContentDetailView.replace_photos(request, previewContent, None, None, True)
        context = {
            'email_contents': previewContent
        }
        return render(request, 'message/email_preview.html', context)

    def get_lang_email(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        try:
            content_id = request.POST.get('content_id')
            language_id = request.POST.get('language_id')
            language_data = Presets.objects.get(id=language_id)
            email = EmailLanguageContents.objects.filter(email_content=content_id, language_id=language_id,
                                                         email_content__template__event_id=event_id
                                                         ).first()
            if not email:
                defult_language = PresetEvent.objects.filter(event_id=event_id).first()
                email = EmailLanguageContents.objects.filter(email_content=content_id,
                                                             language_id=defult_language.preset_id,
                                                             email_content__template__event_id=event_id
                                                             ).first()
            ErrorR.okblue(email)
            response_data = {
                "success": True,
                "email_content": email.content,
                "language_data": language_data.as_dict()
            }
        except Exception as e:
            ErrorR.efail(e)
            response_data = {
                "success": False,
                "email_content": ""
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")
