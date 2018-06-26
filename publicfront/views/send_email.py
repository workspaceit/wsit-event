from datetime import datetime
from django.views import generic
from app.models import Attendee, EmailContents, AttendeePasswordResetRequest, \
    EmailLanguageContents, PresetEvent, ActivityHistory, EmailReceivers, EmailReceiversHistory, MessageHistory
from app.views.email_view import EmailReceiversView

from app.views.gbhelper.error_report_helper import ErrorR
# from django.conf import settings
import json
import boto.sqs
# from boto.sqs.message import Message
from django.conf import settings
# import os
from app.views.email_content_view import EmailContentDetailView
import logging


class UserEmail(generic.DeleteView):

    def email_connection(request):
        conn = boto.sqs.connect_to_region(settings.SES_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        queue = conn.get_queue('test_email_queue')
        return queue

    def send_email_to_user(request, send_email_id, attendee, attendee_owner_id=None):
        try:
            ErrorR.okblue('send Single')
            ErrorR.okblue(send_email_id)
            email_data = EmailContents.objects.filter(id=int(send_email_id))
            if email_data.exists():
                email_queue = []
                email_data = email_data[0]
                # m = Message()
                # content = email_data[0].content
                content = UserEmail.get_content_with_lang(attendee.event_id, email_data.id, attendee.language_id)
                mail_template_content = email_data.template.content.replace('{content}', content)
                mail_template_content = UserEmail.replace_email_content(request, attendee, mail_template_content,
                                                                        attendee.language_id)
                admin_id=1
                if attendee_owner_id:
                    attendee_owner = Attendee.objects.get(id=attendee_owner_id)
                    to = attendee_owner.email
                    subject = UserEmail.get_email_subject_by_language(attendee_owner.language_id, email_data)
                    email_receiver = attendee_owner
                else:
                    to = attendee.email
                    subject = UserEmail.get_email_subject_by_language(attendee.language_id, email_data)
                    email_receiver = attendee
                sender_mail = email_data.sender_email
                # data = json.dumps({
                #     'to': to,
                #     'sender': sender_mail,
                #     'subject': subject,
                #     'template': mail_template_content,
                #     'environment': os.environ['ENVIRONMENT_TYPE'],
                #     'local_env': settings.LOCAL_ENV
                # })
                data = {
                    "from_address": sender_mail.strip(),
                    "to_address": to.strip(),
                    "subject": subject.strip(),
                    "mime_message_html": mail_template_content.strip()
                }
                # m.set_body(data)
                # queue.write(m)
                email_queue.append(data)
                # queue.write_batch(email_queue)
                EmailReceiversView.process_mail_and_send(request, email_queue)
                # Add Email Activities for attendee
                ErrorR.ex_time_init()
                UserEmail.add_or_update_email_receivers(email_receiver, email_data.id, admin_id)
                email_activities = UserEmail.add_email_activities(subject, admin_id, email_receiver.id,
                                                                  email_receiver.event_id, [])
                if len(email_activities) > 0:
                    ActivityHistory.objects.bulk_create(email_activities)
                ErrorR.ex_time()
                logger = logging.getLogger(__name__)
                logger.debug("-------send single email to------" + str(sender_mail))
        except Exception as e:
            ErrorR.efail(e)
        return

    # send email to multiple registered attendee

    def send_email_to_multiple_user(request, send_email_id, attendee_ids, attendee_owner_id=None,
                                    email_id_for_attendee=None):
        try:
            if send_email_id != 0:
                email_data = EmailContents.objects.filter(id=int(send_email_id))
                if email_data.exists():
                    email_queue = []
                    email_data = email_data[0]
                    # m = Message()
                    attendees = Attendee.objects.filter(id__in=attendee_ids)
                    main_content = ''
                    admin_id = 1
                    if attendee_owner_id:
                        ErrorR.okblue("-------------send all to Owner------------")
                        attendee_owner = Attendee.objects.get(id=attendee_owner_id)
                        content = UserEmail.get_content_with_lang(attendee_owner.event_id, email_data.id,
                                                                  attendee_owner.language_id)
                        content_for_attendee = content
                        if email_id_for_attendee:
                            email_data_for_att = EmailContents.objects.filter(id=int(email_id_for_attendee))
                            if email_data_for_att:
                                email_data_for_att = email_data_for_att[0]
                                content_for_attendee = UserEmail.get_content_with_lang(attendee_owner.event_id,
                                                                                       email_data_for_att.id,
                                                                                       attendee_owner.language_id)
                        main_content = UserEmail.replace_email_content(request, attendee_owner, content,
                                                                       attendee_owner.language_id)
                        for attendee in attendees:
                            mail_content = UserEmail.replace_email_content(request, attendee, content_for_attendee,
                                                                           attendee_owner.language_id)
                            main_content = main_content + mail_content
                        mail_template = UserEmail.replace_email_content(request, attendee_owner,
                                                                        email_data.template.content,
                                                                        attendee_owner.language_id)
                        mail_template_content = mail_template.replace('{content}', main_content)
                        # to = attendee_owner.email
                        i = 1
                        email_queue = UserEmail.add_email_to_queue(email_data, attendee_owner, mail_template_content,
                                                                   email_queue, i)
                        # queue.write_batch(email_queue)
                        # Add Email Activities for attendee
                        ErrorR.ex_time_init()
                        UserEmail.add_or_update_email_receivers(attendee_owner, email_data.id, admin_id)
                        email_activities = UserEmail.add_email_activities(email_data.subject, admin_id, attendee_owner.id,
                                                                          attendee_owner.event_id, [])
                        if len(email_activities) > 0:
                            ActivityHistory.objects.bulk_create(email_activities)
                        ErrorR.ex_time()
                        logger = logging.getLogger(__name__)
                        logger.debug("-------send multiple email to------" + str(attendee_owner_id))
                    else:
                        i = 1
                        email_activities = []
                        ErrorR.okblue("-------------send to all attendee------------")
                        for attendee in attendees:
                            # to = attendee.email
                            content = UserEmail.get_content_with_lang(attendee.event_id, email_data.id,
                                                                      attendee.language_id)
                            mail_template_content = email_data.template.content.replace('{content}', content)
                            mail_template_content = UserEmail.replace_email_content(request, attendee,
                                                                                    mail_template_content,
                                                                                    attendee.language_id)
                            email_queue = UserEmail.add_email_to_queue(email_data, attendee, mail_template_content,
                                                                       email_queue, i)

                            # Add Email Activities for attendee
                            ErrorR.ex_time_init()
                            UserEmail.add_or_update_email_receivers(attendee, email_data.id, admin_id)
                            email_activities = UserEmail.add_email_activities(email_data.subject, admin_id,attendee.id,attendee.event_id, email_activities)
                            ErrorR.ex_time()
                        #     if i == 10:
                        #         queue.write_batch(email_queue)
                        #         email_queue = []
                        #         i = 1
                        #     else:
                        #         i = i + 1
                        # if i > 1:
                        #     print('hi')
                        #     queue.write_batch(email_queue)
                        ErrorR.ex_time_init()
                        if len(email_activities) > 0:
                            ActivityHistory.objects.bulk_create(email_activities)
                        ErrorR.ex_time()
                        logger = logging.getLogger(__name__)
                        logger.debug("-------send multiple email to------" + str(attendee_ids) + " email_queue " + str(
                            len(email_queue)))
                    import threading
                    task = threading.Thread(target=EmailReceiversView.process_mail_and_send,
                                            args=(request, email_queue))
                    task.start()
        except Exception as e:
            ErrorR.efail(e)
        return

    def replace_email_content(request, attendee, mail_template_content, language_id):
        mail_template_content = EmailContentDetailView.replace_questions_variable(request, mail_template_content,
                                                                                  attendee, language_id)
        mail_template_content = EmailContentDetailView.replace_sessions(request, mail_template_content, attendee,
                                                                        language_id)
        mail_template_content = EmailContentDetailView.replace_travels(request, mail_template_content, attendee,
                                                                       language_id)
        mail_template_content = EmailContentDetailView.replace_hotels(request, mail_template_content, attendee,
                                                                      language_id)
        mail_template_content = EmailContentDetailView.replace_general_tags(request, mail_template_content, attendee,
                                                                            language_id)
        mail_template_content = EmailContentDetailView.replace_economy_tags(request, mail_template_content, attendee,
                                                                            language_id)
        mail_template_content = EmailContentDetailView.replace_general_questions(request, mail_template_content,
                                                                                 attendee, language_id)
        mail_template_content = EmailContentDetailView.replace_photos(request, mail_template_content, attendee,
                                                                      language_id)
        return mail_template_content

    def add_email_to_queue(email_data, attendee, main_content, email_queue, i):
        subject = UserEmail.get_email_subject_by_language(attendee.language_id, email_data)
        sender_mail = email_data.sender_email
        # data = json.dumps({
        #     'to': attendee.email,
        #     'sender': sender_mail,
        #     'subject': subject,
        #     'template': main_content,
        #     'environment': os.environ['ENVIRONMENT_TYPE'],
        #     'local_env': settings.LOCAL_ENV
        # })
        data = {
            "from_address": sender_mail.strip(),
            "to_address": attendee.email.strip(),
            "subject": subject.strip(),
            "mime_message_html": main_content.strip()
        }
        # m.set_body(data)
        # queue.write(m)
        # email_queue.append((i, data, 0))
        email_queue.append(data)
        return email_queue

    # recovery account use only
    def send_email_reset_password(request, send_email_id, userData):
        # import json
        # import boto.sqs
        # from boto.sqs.message import Message
        from django.conf import settings
        # import os
        from app.views.email_content_view import EmailContentDetailView
        try:
            admin_id = 1
            email_data = EmailContents.objects.filter(id=int(send_email_id))
            if email_data.exists():
                # conn = boto.sqs.connect_to_region(settings.SES_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                #                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                # queue = conn.get_queue('test_email_queue')
                # m = Message()
                email_queue = []
                # content = email_data[0].content
                content = UserEmail.get_content_with_lang(userData[0].event_id, send_email_id, userData[0].language_id)
                to = userData[0].email
                subject = UserEmail.get_email_subject_by_language(userData[0].language_id, email_data[0])
                sender_mail = email_data[0].sender_email
                mail_template_content = email_data[0].template.content.replace('{content}', content)
                mail_template_content = EmailContentDetailView.replace_general_tags(request, mail_template_content,
                                                                                    userData[0],
                                                                                    userData[0].language_id)
                userPasswordResetData = AttendeePasswordResetRequest.objects.filter(attendee_id=userData[0].id,
                                                                                    already_used=0,
                                                                                    expired_at__gt=datetime.now())

                if '[start_hash:]' in mail_template_content:
                    start_hash_msg = mail_template_content.index('[start_hash:]')
                    hash_msg = mail_template_content[start_hash_msg:]
                    end_hash_msg = mail_template_content.index('[:end_hash]')
                    end_hash_msg2 = hash_msg.index('[:end_hash]')
                    hash_msg = mail_template_content[start_hash_msg:][:end_hash_msg2]
                    hash_msg = hash_msg.replace('[start_hash:]', '')
                    hash_msg = hash_msg.replace('[:end_hash]', '')

                    if userPasswordResetData.exists():
                        resetpass_hash_key = userPasswordResetData[0].hash_code

                    hash_new_msg = ''
                    for attendee in userData:
                        reset_password_hash_link = settings.SITE_URL + "/" + attendee.event.url + "/resetpass/?key={resetpass_hash_key}"
                        reset_password_hash_link = reset_password_hash_link.replace('{resetpass_hash_key}',
                                                                                    resetpass_hash_key)
                        hash_new_msg += hash_msg.replace('{reset_password_hash_link}',
                                                         reset_password_hash_link).replace('{event_name}',
                                                                                           attendee.event.name)
                    mail_template_content = mail_template_content[
                                            :start_hash_msg] + hash_new_msg + mail_template_content[
                                                                              end_hash_msg:]
                    mail_template_content = mail_template_content.replace('[:end_hash]', '')

                # data = json.dumps({
                #     'to': to,
                #     'sender': sender_mail,
                #     'subject': subject,
                #     'template': mail_template_content,
                #     'environment': os.environ['ENVIRONMENT_TYPE'],
                #     'local_env': settings.LOCAL_ENV
                # })
                data = {
                    "from_address": sender_mail.strip(),
                    "to_address": to.strip(),
                    "subject": subject.strip(),
                    "mime_message_html": mail_template_content.strip()
                }
                # m.set_body(data)
                # queue.write(m)
                email_queue.append(data)
                EmailReceiversView.process_mail_and_send(request, email_queue)
                UserEmail.add_or_update_email_receivers(userData[0], email_data[0].id, admin_id)
                email_activities = UserEmail.add_email_activities(subject, admin_id, userData[0].id,
                                                                  userData[0].event_id, [])
                if len(email_activities) > 0:
                    ActivityHistory.objects.bulk_create(email_activities)
                # queue.write_batch(email_queue)
            return
        except Exception as e:
            ErrorR.efail(e)
            return

    # send session conflict/not_conflict conirmations

    def send_session_email_to_user(request, send_email_id, attendee, session_name=None):
        try:
            ErrorR.okblue(send_email_id)
            email_data = EmailContents.objects.filter(id=int(send_email_id))
            if email_data.exists():
                admin_id = 1
                email_queue = []
                email_data = email_data[0]
                content = UserEmail.get_content_with_lang(attendee.event_id, email_data.id, attendee.language_id)
                mail_template_content = email_data.template.content.replace('{content}', content)
                mail_template_content = UserEmail.replace_email_content(request, attendee, mail_template_content,
                                                                        attendee.language_id)
                if session_name:
                    mail_template_content = mail_template_content.replace('{session_name}', session_name)
                to = attendee.email
                subject = UserEmail.get_email_subject_by_language(attendee.language_id, email_data)
                sender_mail = email_data.sender_email
                # data = json.dumps({
                #     'to': to,
                #     'sender': sender_mail,
                #     'subject': subject,
                #     'template': mail_template_content,
                #     'environment': os.environ['ENVIRONMENT_TYPE'],
                #     'local_env': settings.LOCAL_ENV
                # })
                data = {
                    "from_address": sender_mail.strip(),
                    "to_address": to.strip(),
                    "subject": subject.strip(),
                    "mime_message_html": mail_template_content.strip()
                }
                email_queue.append(data)
                EmailReceiversView.process_mail_and_send(request, email_queue)
                UserEmail.add_or_update_email_receivers(attendee, email_data.id, admin_id)
                email_activities = UserEmail.add_email_activities(subject, admin_id, attendee.id,
                                                                  attendee.event_id, [])
                if len(email_activities) > 0:
                    ActivityHistory.objects.bulk_create(email_activities)
                # queue.write_batch(email_queue)
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

    def get_email_subject_by_language(language_id, email):
        subject_lang = email.subject
        if email.subject_lang != '' and email.subject_lang != None:
            try:
                email_subject_lang = json.loads(email.subject_lang, strict=False)
                if email_subject_lang[str(language_id)]:
                    subject_lang = email_subject_lang[str(language_id)]
            except:
                pass
        return subject_lang

    def add_or_update_email_receivers(attendee,email_id,admin_id):
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

    def add_email_activities(subject,admin_id,attendee_id,event_id,email_activity):
        try:
            message_history = MessageHistory(subject=subject, message='N/A',
                                             admin_id=admin_id,
                                             type='mail')

            message_history.save()
            activity_history = ActivityHistory(attendee_id=attendee_id,
                                               admin_id=admin_id,
                                               activity_type='message', category='message',
                                               message_id=message_history.id,
                                               event_id=event_id)
            email_activity.append(activity_history)
        except Exception as e:
            ErrorR.efail(e)
        return email_activity
