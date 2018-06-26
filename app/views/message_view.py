import threading
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import generic
from django.http import HttpResponse, Http404
from app.models import Notification, RuleSet, Answers, MessageHistory, ActivityHistory, Questions, Tag, Option, \
    MessageContents, MessageReceivers, MessageReceiversHistory, \
    Attendee, EmailContents, MessageLanguageContents, PresetEvent
from app.views.email_content_view import EmailContentDetailView
from app.views.gbhelper.details_helper import DetailsH
from app.views.gbhelper.language_helper import LanguageH
from .filter import GroupView
from .common_views import EventView, CommonContext, TimeDetailView
import json
from django.db.models import Q
import os
from app.snsHelper import SNSHelper
import re
from django.db.models.functions import Concat
from django.db.models import Value
from datetime import datetime
import io
from .filter import FilterView
import requests
import logging
from app.views.gbhelper.error_report_helper import ErrorR


class MessageView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'message_permission'):
            event_id = request.session['event_auth_user']['event_id']
            messages = MessageContents.objects.filter(event_id=event_id, is_show=1)
            for message in messages:
                message.total_receiver = message.messagereceivers_set.filter(is_show=1).count()
                message.sent_receiver = message.messagereceivers_set.filter(status='sent', is_show=1).count()
            context = {
                "messages": messages
            }
            return render(request, 'message_content/message_contents.html', context)

    def post(self, request):
        if EventView.check_permissions(request, 'message_permission'):
            try:
                event_id = request.session['event_auth_user']['event_id']
                admin_id = request.session['event_auth_user']['id']
                name = request.POST.get('name')
                sender_name = request.POST.get('sender_name')
                type = request.POST.get('message_type')
                message_form = {
                    "name": name,
                    "sender_name": sender_name,
                    "type": type,
                    "last_updated_by_id": admin_id
                }
                if 'id' in request.POST:
                    message_id = request.POST.get('id')
                    if not (MessageContents.objects.filter(name=message_form['name'], event_id=event_id).exclude(
                            id=message_id).exists()):
                        MessageContents.objects.filter(id=message_id).update(**message_form)
                        message = MessageContents.objects.get(id=message_id)
                        total_receiver = message.messagereceivers_set.all().count()
                        sent_receiver = message.messagereceivers_set.filter(status='sent').count()
                        response_data = {
                            'success': True,
                            'message_data': message.as_dict(),
                            'total_receiver': total_receiver,
                            'sent_receiver': sent_receiver,
                            'message': 'Message Updated Successfully',
                        }
                    else:
                        response_data = {
                            'success': False,
                            'message': 'Message Name Allready Exists ',
                        }
                else:
                    if not (MessageContents.objects.filter(name=message_form['name'], event_id=event_id).exists()):
                        message_form['event_id'] = event_id
                        message_form['created_by_id'] = admin_id
                        message = MessageContents(**message_form)
                        message.save()
                        message_data = message.as_dict()
                        total_receiver = message.messagereceivers_set.all().count()
                        sent_receiver = message.messagereceivers_set.filter(status='sent').count()
                        response_data = {
                            'success': True,
                            'message_data': message.as_dict(),
                            'total_receiver': total_receiver,
                            'sent_receiver': sent_receiver,
                            'message': 'Message created Successfully',
                        }
                    else:
                        response_data = {
                            'success': False,
                            'message': 'Message Name Allready Exists ',
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

    def message_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        message_id = request.POST.get('message_id')
        message = MessageContents.objects.get(id=message_id)

        duplicate_existance = MessageContents.objects.filter(name=message.name + '[Copy]', event_id=event_id)
        if duplicate_existance.exists():
            response_data['error'] = 'This message is already make a duplicate.'
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        message.pk = None
        message.name += '[Copy]'
        message.created_by_id = request.session['event_auth_user']['id']
        message.last_updated_by_id = request.session['event_auth_user']['id']
        message.save()
        message_contents = MessageLanguageContents.objects.filter(message_content_id=message_id)
        content_languages = []
        for message_lang in message_contents:
            content_languages.append(
                MessageLanguageContents(message_content_id=message.id, language_id=message_lang.language_id,
                                      content=message_lang.content))
            MessageLanguageContents.objects.bulk_create(content_languages)
        response_data['success'] = "Create duplicate Message Successfully"
        response_data['message'] = message.as_dict()
        response_data['total_receiver'] = message.messagereceivers_set.filter(id=message.id).count()
        response_data['sent_receiver'] = message.messagereceivers_set.filter(id=message.id, status='sent').count()
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def delete(request):
        response_data = {}
        message_content_id = request.POST.get('id')
        message = MessageContents.objects.get(id=message_content_id)
        MessageContents.objects.filter(id=message_content_id).update(is_show=0)
        response_data['success'] = "Message Deleted Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_content_with_lang(event_id,message_id,language_id):
        content = ""
        try:
            message_content = MessageLanguageContents.objects.filter(message_content_id=message_id,language_id=language_id)
            if message_content.exists():
                content = message_content[0].content
            else:
                defult_language = PresetEvent.objects.filter(event_id=event_id).first()
                default_content = MessageLanguageContents.objects.filter(message_content_id=message_id,
                                                                     language_id=defult_language.preset_id).first()
                content = default_content.content
        except Exception as e:
            ErrorR.efail(e)
        return content


class MessageDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            message = MessageContents.objects.filter(id=pk,
                                                     event_id=self.request.session['event_auth_user']['event_id']).first()
            if message:
                defult_language = PresetEvent.objects.filter(event_id=message.event_id).first()
                message_content = MessageLanguageContents.objects.filter(message_content_id=pk, language_id=defult_language.preset_id).first()
                if message_content:
                    message.content = message_content.content
                return message
            else:
                raise Http404
        except MessageContents.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        message = self.get_object(pk)
        context = {
            "message": message.as_dict()
        }
        return HttpResponse(json.dumps(context), content_type="application/json")


class MessageReceiversView(generic.DetailView):

    def get(self, request, pk):
        if EventView.check_read_permissions(request, 'message_permission'):
            message = MessageDetailView.get_object(self, pk)
            if message.type == 'push':
                message_receivers = MessageReceivers.objects.filter(message_content_id=pk, is_show=1,
                                                                    attendee__push_notification_status=1)
            else:
                message_receivers = MessageReceivers.objects.filter(message_content_id=pk, is_show=1)
            for receiver in message_receivers:
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
                "message": message,
                "message_receivers": message_receivers,
                'quick_filter_id': quick_filter_id,

            }
            context.update(common_context)
            filter_context = CommonContext.get_filter_context(request)
            context.update(filter_context)
            return render(request, 'message_content/message_receivers.html', context)

    def search_receivers(request):
        search_key = request.GET.get('search_key').strip()
        message_id = request.GET.get('message_id')
        message = MessageContents.objects.filter(id=message_id)
        if message.exists():
            if message[0].type == "push":
                if search_key == '':
                    message_receivers = MessageReceivers.objects.filter(message_content_id=message_id, is_show=1,
                                                                        attendee__push_notification_status=1)
                else:
                    message_receivers = MessageReceivers.objects.annotate(
                        full_name=Concat('firstname', Value(' '), 'lastname')).filter(Q(
                        Q(firstname__istartswith=search_key) | Q(lastname__istartswith=search_key) | Q(
                            mobile_phone__istartswith=search_key) | Q(full_name__istartswith=search_key)) & Q(
                        message_content_id=message_id, is_show=1, attendee__push_notification_status=1))
            else:
                if search_key == '':
                    message_receivers = MessageReceivers.objects.filter(message_content_id=message_id, is_show=1)
                else:
                    message_receivers = MessageReceivers.objects.annotate(
                        full_name=Concat('firstname', Value(' '), 'lastname')).filter(Q(
                        Q(firstname__istartswith=search_key) | Q(lastname__istartswith=search_key) | Q(
                            mobile_phone__istartswith=search_key) | Q(full_name__istartswith=search_key)) & Q(
                        message_content_id=message_id, is_show=1))
        for receiver in message_receivers:
            receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
        context = {
            "message_receivers": message_receivers
        }
        return render(request, 'message_content/receivers_list.html', context)

    def change_receiver_status(request):
        response_data = {}
        receivers = json.loads(request.POST.get('receivers'))
        status = request.POST.get('status')
        for receiver in receivers:
            MessageReceivers.objects.filter(id=int(receiver['id'])).update(status=status)
        response_data['success'] = True
        response_data['message'] = "Receivers Status Changed Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_receiver(request):
        response_data = {}
        receivers = json.loads(request.POST.get('receivers'))
        for receiver in receivers:
            MessageReceivers.objects.filter(id=int(receiver['id'])).update(is_show=0)
        response_data['success'] = True
        response_data['message'] = "Receivers Delete Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def receiver_preview(request, pk):
        receiver_data = MessageReceivers.objects.filter(id=pk)
        event_id = request.session['event_auth_user']['event_id']
        if receiver_data.exists():
            receiver = receiver_data[0]
            # content = receiver.message_content.content
            if receiver.attendee_id != None:
                content = MessageView.get_content_with_lang(event_id, receiver.message_content.id,
                                                            receiver.attendee.language_id)
            else:
                default_language = PresetEvent.objects.get(event_id=event_id)
                content = MessageView.get_content_with_lang(event_id, receiver.message_content.id,
                                                          default_language.preset_id)
            questions = []
            match = re.findall("qid:\d+", content)
            for q in match:
                data = {
                    'qid': q.split(':')[1]
                }
                questions.append(data)
            if receiver.attendee_id != None:
                content = EmailContentDetailView.replace_general_tags(request, content, receiver.attendee, receiver.attendee.language_id)
                for question in questions:
                    answer = Answers.objects.filter(question_id=question['qid'], user_id=receiver.attendee_id)
                    if answer.exists():
                        answer_data = DetailsH.get_answer_data_by_attendee(receiver.attendee.event_id,
                                                                           receiver.attendee.language_id, answer[0])
                        content = content.replace('{qid:' + question['qid'] + '}', answer_data.value)
                    else:
                        content = content.replace('{qid:' + question['qid'] + '}', '')
            else:
                content = MessageReceiversView.replace_empty_data(content, receiver)
                for question in questions:
                    content = content.replace('{qid:' + question['qid'] + '}', '')
            content = content.replace('\n', '<br/>')
            context = {
                'email_contents': content
            }
            return render(request, 'message/email_preview.html', context)
        else:
            return Http404

    def replace_empty_data(content, receiver):
        content = content.replace('{calendar}', '')
        content = content.replace('{uid_link}', '')
        content = content.replace('{uid}', '')
        content = content.replace('{bid}', '')
        content = content.replace('{registration_date}', '')
        content = content.replace('{updated_date}', '')
        content = content.replace('{attendee_groups}', '')
        content = content.replace('{tags}', '')
        content = content.replace('{first_name}', receiver.firstname)
        content = content.replace('{last_name}', receiver.lastname)
        content = content.replace('{email_address}', '')
        return content

    def download_message(request, pk):
        response_data = {}
        receiver_id = pk
        receiver = MessageReceivers.objects.filter(id=int(receiver_id))
        file_name = "message_content.txt"
        event_id = request.session['event_auth_user']['event_id']
        if receiver.exists():
            receiver = receiver[0]
            # content = receiver.message_content.content
            if receiver.attendee_id != None:
                content = MessageView.get_content_with_lang(event_id, receiver.message_content.id,
                                                            receiver.attendee.language_id)
            else:
                default_language = PresetEvent.objects.get(event_id=event_id)
                content = MessageView.get_content_with_lang(event_id, receiver.message_content.id,
                                                          default_language.preset_id)
            questions = []
            match = re.findall("qid:\d+", content)
            for q in match:
                data = {
                    'qid': q.split(':')[1]
                }
                questions.append(data)
            if receiver.attendee_id != None:
                content = EmailContentDetailView.replace_general_tags(request, content, receiver.attendee, receiver.attendee.language_id)
                for question in questions:
                    answer = Answers.objects.filter(question_id=question['qid'], user_id=receiver.attendee_id)
                    if answer.exists():
                        answer_data = DetailsH.get_answer_data_by_attendee(receiver.attendee.event_id,
                                                                           receiver.attendee.language_id, answer[0])
                        content = content.replace('{qid:' + question['qid'] + '}', answer_data.value)
                    else:
                        content = content.replace('{qid:' + question['qid'] + '}', '')
            else:
                content = MessageReceiversView.replace_empty_data(content, receiver)
                for question in questions:
                    content = content.replace('{qid:' + question['qid'] + '}', '')
            message_file = io.StringIO(content.strip())
            response = HttpResponse(message_file, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=' + file_name
            return response
        else:
            response_data['success'] = False
            response_data['message'] = "Receivers Not Found"
            return response_data

    def get_total_receiver(request):
        try:
            response_data = {}
            receivers = json.loads(request.POST.get('receivers'))
            total_receiver = 0
            push_receiver = 0
            sms_receiver = 0
            message_receiver = 0
            for receiver_id in receivers:
                receiver_info = MessageReceivers.objects.filter(id=int(receiver_id['id']))
                if receiver_info.exists():
                    receiver = receiver_info[0]
                    total_flag = False
                    if receiver.message_content.type == 'push_or_sms':
                        if receiver.push:
                            total_flag = True
                            push_receiver += 1
                        elif receiver.mobile_phone:
                            sms_receiver += 1
                            total_flag = True
                    elif receiver.message_content.type == 'sms_and_push':
                        if receiver.push:
                            total_flag = True
                            push_receiver += 1
                        if receiver.mobile_phone:
                            total_flag = True
                            sms_receiver += 1
                    elif receiver.message_content.type == 'sms':
                        if receiver.mobile_phone:
                            sms_receiver += 1
                            total_flag = True
                    elif receiver.message_content.type == 'push':
                        if receiver.push:
                            push_receiver += 1
                            total_flag = True
                    elif receiver.message_content.type == 'plugin_message':
                        message_receiver += 1
                        total_flag = True
                    if total_flag:
                        total_receiver += 1
            response_data['success'] = True
            message = ''
            if total_receiver > 0:
                message += 'You are about to send this message to ' + str(total_receiver) + ' receivers.'
                if sms_receiver > 0:
                    message += str(sms_receiver) + ' is sent by SMS.'
                if push_receiver > 0:
                    message += str(push_receiver) + ' is sent by Push.'
                if message_receiver > 0:
                    message += str(message_receiver) + ' will show in message plugin.'
                message += ' Are you sure you want to continue?'
            response_data['message'] = message
            response_data['total_receiver'] = total_receiver
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

    def send_message(request):
        try:
            receivers = json.loads(request.POST.get('receivers'))
            response_data = {}
            updated_receivers = []
            message_activities = []
            message_receivers_history = []
            message_history_flag = False
            message_histoty_id = 0
            push_attendees = []
            message = ''
            name = ''
            notifications = []
            status = True
            return_message = ''
            event_id = request.session['event_auth_user']['event_id']
            for receiver_id in receivers:
                receiver_info = MessageReceivers.objects.filter(id=int(receiver_id['id']))
                if receiver_info.exists():
                    receiver = receiver_info[0]
                    # content = receiver.message_content.content
                    if receiver.attendee_id != None:
                        content = MessageView.get_content_with_lang(event_id, receiver.message_content.id,
                                                                    receiver.attendee.language_id)
                    else:
                        default_language = PresetEvent.objects.get(event_id=event_id)
                        content = MessageView.get_content_with_lang(event_id, receiver.message_content.id,
                                                                    default_language.preset_id)
                    message = content
                    name = receiver.message_content.name
                    sender_name = receiver.message_content.sender_name
                    MessageReceivers.objects.filter(id=receiver.id).update(status='sent', last_received=datetime.now())
                    updated_receiver = MessageReceivers.objects.get(id=receiver.id)
                    updated_receiver_dict = updated_receiver.as_dict()
                    updated_receiver_dict['last_received'] = str(
                        TimeDetailView.utc_to_local(request, updated_receiver_dict['last_received']))
                    updated_receivers.append(updated_receiver_dict)
                    questions = []
                    match = re.findall("qid:\d+", content)
                    for q in match:
                        data = {
                            'qid': q.split(':')[1]
                        }
                        questions.append(data)
                    if receiver.attendee_id != None:
                        if not message_history_flag:
                            message_history = MessageHistory(subject=name, message=message,
                                                             admin_id=request.session['event_auth_user']['id'],
                                                             type='sms')
                            message_history.save()
                            message_histoty_id = message_history.id
                            message_history_flag = True
                        content = EmailContentDetailView.replace_general_message_tags(request, content,
                                                                                      receiver.attendee)
                        for question in questions:
                            answer = Answers.objects.filter(question_id=question['qid'], user_id=receiver.attendee_id)
                            if answer.exists():
                                answer_data = DetailsH.get_answer_data_by_attendee(receiver.attendee.event_id,
                                                                                   receiver.attendee.language_id,
                                                                                   answer[0])
                                content = content.replace('{qid:' + question['qid'] + '}', answer_data.value)
                            else:
                                content = content.replace('{qid:' + question['qid'] + '}', '')
                    else:
                        content = MessageReceiversView.replace_empty_data(content, receiver)
                        for question in questions:
                            content = content.replace('{qid:' + question['qid'] + '}', '')
                    send_message_data = MessageReceiversView.send_message_using_type(request, receiver, content.strip(),
                                                                                     message_activities,
                                                                                     message_receivers_history,
                                                                                     push_attendees, message_histoty_id,
                                                                                     notifications)
                    message_activities = send_message_data['message_activities']
                    message_receivers_history = send_message_data['message_receivers_history']
                    push_attendees = send_message_data['push_attendees']
                    notifications = send_message_data['notifications']
                    status = send_message_data['status']
                    return_message = send_message_data['return_message']
            if os.environ['ENVIRONMENT_TYPE'] == 'master':
                PushNotification(request, push_attendees, message, name, message_histoty_id).start()
            ActivityHistory.objects.bulk_create(message_activities)
            MessageReceiversHistory.objects.bulk_create(message_receivers_history)
            Notification.objects.bulk_create(notifications)
            response_data['success'] = True
            response_data['message_status'] = status
            response_data['return_message'] = return_message
            response_data['message'] = 'Message Sent Successfully'
            response_data['updated_receivers'] = updated_receivers
            print(response_data)
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception as e:
            print(e)
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            response_data = {
                'success': False,
                'message': 'Something went wrong. Please try again.'
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def send_message_using_type(request, receiver, content, message_activities, message_receivers_history,
                                push_attendees, message_histoty_id, notifications):
        status = True
        return_message = ''
        content = content.replace('”','"')
        try:
            message_flag = False
            searchChars = 'ÅÄåäÖö'
            replaceChars = 'AAaaOo'
            trans_table = str.maketrans(searchChars, replaceChars)
            data = {
                'username': 'springconf',
                'password': '96HVgu3W',
                'destination': '008801836457787',
                # 'destination': '+46732318023',
                'originatortype': 'alpha',
                'originator': receiver.message_content.sender_name.translate(trans_table),
                'type': 'text',
                'charset': 'UTF-8',
                'allowconcat': 1,
                'text': content
            }
            if len(data['text']) > 600:
                data['allowconcat'] = 6
            elif len(data['text']) > 480:
                data['allowconcat'] = 5
            elif len(data['text']) > 360:
                data['allowconcat'] = 4
            elif len(data['text']) > 240:
                data['allowconcat'] = 3
            elif len(data['text']) > 120:
                data['allowconcat'] = 2
            if receiver.message_content.type == 'push_or_sms':
                if receiver.attendee_id != None:
                    deveices = receiver.attendee.devicetoken_set.all()
                    if len(deveices) > 0 and receiver.attendee.push_notification_status:
                        message_flag = True
                        receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='push')
                        message_receivers_history.append(receiver_history)
                        push_attendees.append(receiver.attendee)
                        notification = Notification(type='filter_message', to_attendee_id=receiver.attendee.id,
                                                    message=content, message_content_id=receiver.message_content_id)
                        notifications.append(notification)
                    else:
                        if receiver.mobile_phone:
                            if os.environ['ENVIRONMENT_TYPE'] == 'master':
                                data['destination'] = receiver.mobile_phone
                                sms_send = requests.post('https://se-1.cellsynt.net/sms.php/', params=data)
                                if 'Error:' in str(sms_send.content):
                                    status = False
                                    return_message = sms_send.content
                            # print(sms_send.content)
                            # if 'Error:' in str(sms_send.content):
                            #     print('ok')
                            # print(sms_send.status_code)
                            message_flag = True
                            receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='sms')
                            message_receivers_history.append(receiver_history)
                            notification = Notification(type='filter_message', to_attendee_id=receiver.attendee.id,
                                                        message=content, message_content_id=receiver.message_content_id)
                            notifications.append(notification)
                else:
                    if receiver.mobile_phone:
                        if os.environ['ENVIRONMENT_TYPE'] == 'master':
                            data['destination'] = receiver.mobile_phone
                            sms_send = requests.post('https://se-1.cellsynt.net/sms.php/', params=data)
                            if 'Error:' in str(sms_send.content):
                                status = False
                                return_message = sms_send.content
                        # print(sms_send.content)
                        # if 'Error:' in str(sms_send.content):
                        #     print('ok')
                        # print(sms_send.status_code)
                        message_flag = True
                        receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='sms')
                        message_receivers_history.append(receiver_history)
            elif receiver.message_content.type == 'sms_and_push':
                if receiver.mobile_phone:
                    if os.environ['ENVIRONMENT_TYPE'] == 'master':
                        data['destination'] = receiver.mobile_phone
                        sms_send = requests.post('https://se-1.cellsynt.net/sms.php/', params=data)
                        if 'Error:' in str(sms_send.content):
                            status = False
                            return_message = sms_send.content
                    # print(sms_send.content)
                    # if 'Error:' in str(sms_send.content):
                    #     print('ok')
                    # print(sms_send.status_code)
                    message_flag = True
                    receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='sms')
                    message_receivers_history.append(receiver_history)
                if receiver.attendee_id != None:
                    deveices = receiver.attendee.devicetoken_set.all()
                    if len(deveices) > 0 and receiver.attendee.push_notification_status:
                        message_flag = True
                        push_history = MessageReceiversHistory(receiver_id=receiver.id, type='push')
                        message_receivers_history.append(push_history)
                        push_attendees.append(receiver.attendee)
                    if message_flag:
                        notification = Notification(type='filter_message', to_attendee_id=receiver.attendee.id,
                                                    message=content, message_content_id=receiver.message_content_id)
                        notifications.append(notification)
            elif receiver.message_content.type == 'sms':
                if receiver.mobile_phone:
                    if os.environ['ENVIRONMENT_TYPE'] == 'master':
                        data['destination'] = receiver.mobile_phone
                        sms_send = requests.post('https://se-1.cellsynt.net/sms.php/', params=data)
                        # print(sms_send.content)
                        if 'Error:' in str(sms_send.content):
                            status = False
                            return_message = sms_send.content
                            # print(sms_send.status_code)
                    message_flag = True
                    receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='sms')
                    message_receivers_history.append(receiver_history)
                    if receiver.attendee_id != None:
                        notification = Notification(type='filter_message', to_attendee_id=receiver.attendee.id,
                                                    message=content, message_content_id=receiver.message_content_id)
                        notifications.append(notification)
            elif receiver.message_content.type == 'push':
                if receiver.attendee_id != None:
                    deveices = receiver.attendee.devicetoken_set.all()
                    if len(deveices) > 0 and receiver.attendee.push_notification_status:
                        message_flag = True
                        receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='push')
                        message_receivers_history.append(receiver_history)
                        push_attendees.append(receiver.attendee)
                        notification = Notification(type='filter_message', to_attendee_id=receiver.attendee.id,
                                                    message=content, message_content_id=receiver.message_content_id)
                        notifications.append(notification)
            elif receiver.message_content.type == 'plugin_message':
                message_flag = True
                receiver_history = MessageReceiversHistory(receiver_id=receiver.id, type='plugin_message')
                message_receivers_history.append(receiver_history)
                if receiver.attendee_id != None:
                    notification = Notification(type='filter_message', to_attendee_id=receiver.attendee.id,
                                                message=content, message_content_id=receiver.message_content_id)
                    notifications.append(notification)
            if receiver.attendee_id != None and message_flag:
                activity_history = ActivityHistory(attendee_id=receiver.attendee.id,
                                                   admin_id=request.session['event_auth_user']['id'],
                                                   activity_type='message', category='message',
                                                   message_id=message_histoty_id,
                                                   event_id=request.session['event_auth_user']['event_id'])
                message_activities.append(activity_history)
            context = {
                'message_receivers_history': message_receivers_history,
                'push_attendees': push_attendees,
                'message_activities': message_activities,
                'notifications': notifications,
                'status': status,
                'return_message': return_message
            }
            return context
        except Exception as e:
            print(e)
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            context = {
                'message_receivers_history': message_receivers_history,
                'push_attendees': push_attendees,
                'message_activities': message_activities,
                'notifications': notifications,
                'status': status,
                'return_message': return_message
            }
            return context

    def send_message_to_single_receiver(request, receiver, message):
        try:
            response_data = {}
            message_activities = []
            message_receivers_history = []
            push_attendees = []
            notifications = []
            event_id = request.session['event_auth_user']['event_id']
            default_language = PresetEvent.objects.get(event_id=event_id)
            content = MessageView.get_content_with_lang(event_id, message.id,
                                                        default_language.preset_id)
            name = message.name
            message_history = MessageHistory(subject=name, message=content,
                                             admin_id=request.session['event_auth_user']['id'],
                                             type='sms')
            message_history.save()
            message_history_id = message_history.id
            questions = []
            match = re.findall("qid:\d+", content)
            for q in match:
                data = {
                    'qid': q.split(':')[1]
                }
                questions.append(data)
            for question in questions:
                answer = Answers.objects.filter(question_id=question['qid'], user_id=receiver.attendee_id)
                if answer.exists():
                    answer_data = DetailsH.get_answer_data_by_attendee(receiver.attendee.event_id,
                                                                       receiver.attendee.language_id, answer[0])
                    content = content.replace('{qid:' + question['qid'] + '}', answer_data.value)
                else:
                    content = content.replace('{qid:' + question['qid'] + '}', '')
            ErrorR.okgreen(content)
            send_message_data = MessageReceiversView.send_message_using_type(request, receiver, content.strip(),
                                                                             message_activities,
                                                                             message_receivers_history,
                                                                             push_attendees, message_history_id,
                                                                             notifications)
            ErrorR.okblue(send_message_data)
            message_activities = send_message_data['message_activities']
            message_receivers_history = send_message_data['message_receivers_history']
            push_attendees = send_message_data['push_attendees']
            notifications = send_message_data['notifications']
            if os.environ['ENVIRONMENT_TYPE'] == 'master':
                PushNotification(request, push_attendees, message, name, message_history_id).start()
            ActivityHistory.objects.bulk_create(message_activities)
            MessageReceiversHistory.objects.bulk_create(message_receivers_history)
            Notification.objects.bulk_create(notifications)
        except Exception as e:
            ErrorR.efail(e)

    def import_filter_receiver(request):
        response_data = {}
        filter_id = request.POST.get('filter_id')
        message_id = request.POST.get('message_id')
        message_obj = MessageContents.objects.get(id=message_id)
        attendees = FilterView.get_filtered_attendees(request, filter_id)
        receivers = []
        wrong_data = 0
        for attendee in attendees:
            token = attendee.devicetoken_set.all().count()
            if attendee.phonenumber or token > 0 or message_obj.type == 'plugin_message':
                receiver_data = {}
                receiver_data['attendee_id'] = attendee.id
                receiver_data['firstname'] = attendee.firstname
                receiver_data['lastname'] = attendee.lastname
                receiver_data['mobile_phone'] = attendee.phonenumber
                if token > 0:
                    receiver_data['attendee'] = attendee
                elif message_obj.type == 'plugin_message':
                    receiver_data['plugin_message'] = True
                receivers.append(receiver_data)
            else:
                wrong_data = wrong_data + 1
        receiver_message = MessageReceiversView.add_receivers(request, message_id, receivers)
        message_receivers = MessageReceivers.objects.filter(message_content_id=message_id, is_show=1)
        receiver_list = []
        for receiver in message_receivers:
            receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
            context = {
                'id': receiver.id,
                'firstname': receiver.firstname,
                'lastname': receiver.lastname,
                'mobile_phone': receiver.mobile_phone,
                'push': receiver.push,
                'status': receiver.status,
                'last_received': str(receiver.last_received),
            }
            receiver_list.append(context)
        if wrong_data:
            receiver_message['message'] += str(
                wrong_data) + " rows did not contain neither a correct phone number or device tokens."
        # response_data['message_receivers'] = render_to_string('message_content/receivers_list.html',
        #                                                       {'message_receivers': message_receivers,'request': request})
        response_data['success'] = True
        response_data['message_receivers'] = receiver_list
        response_data['admin_permission'] = False
        if 'message_permission' in request.session['admin_permission']['content_permission'] and request.session['admin_permission']['content_permission']['message_permission']['access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            response_data['admin_permission'] = True
        response_data['message'] = receiver_message['message']
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def import_excel_reciever(request):
        data = request.FILES.get('upload_file')
        message_id = request.POST.get('message_id')
        response_data = {}
        if data:
            from openpyxl import load_workbook
            MessageReceiversView.handle_uploaded_file(data, 'sample_import.xlsx')
            wb = load_workbook(filename='attendeeList/sample_import.xlsx', read_only=True)
            ws = wb.worksheets[0]
            receivers = []
            regex = r"[\+\-\(\)?0-9 ]{3,}"
            wrong_data = 0
            for row in ws.rows:
                if not row[0].value:
                    continue
                receiver_data = {}
                matches = re.match(regex, str(row[0].value).strip())
                if matches:
                    receiver_data['firstname'] = ""
                    receiver_data['lastname'] = ""
                    receiver_data['mobile_phone'] = str(row[0].value).strip()
                    receivers.append(receiver_data)
                else:
                    try:
                        receiver_data['firstname'] = str(row[0].value).strip()
                        receiver_data['lastname'] = str(row[1].value).strip()
                        matches = re.match(regex, str(row[2].value).strip())
                        if matches:
                            receiver_data['mobile_phone'] = str(row[2].value).strip()
                            receivers.append(receiver_data)
                        else:
                            wrong_data += 1
                    except:
                        wrong_data += 1
            receiver_message = MessageReceiversView.add_receivers(request, message_id, receivers)
            message_receivers = MessageReceivers.objects.filter(message_content_id=message_id, is_show=1)
            receiver_list = []
            for receiver in message_receivers:
                receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
                context = {
                    'id': receiver.id,
                    'firstname': receiver.firstname,
                    'lastname': receiver.lastname,
                    'mobile_phone': receiver.mobile_phone,
                    'push': receiver.push,
                    'status': receiver.status,
                    'last_received': str(receiver.last_received),
                }
                receiver_list.append(context)
            if wrong_data:
                receiver_message['message'] += str(
                    wrong_data) + " rows did not contain neither a correct phone number or device tokens."
            # response_data['message_receivers'] = render_to_string('message_content/receivers_list.html',
            #                                                       {'message_receivers': message_receivers,'request': request})
            response_data['message_receivers'] = receiver_list
            response_data['admin_permission'] = False
            if 'message_permission' in request.session['admin_permission']['content_permission'] and request.session['admin_permission']['content_permission']['message_permission']['access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
                response_data['admin_permission'] = True
            response_data['success'] = True
            response_data['message'] = receiver_message['message']
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
        message_id = request.POST.get('message_id')
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
                    regex = r"[\+\-\(\)?0-9 ]{3,}"
                    matches = re.match(regex, separator[2])
                    if matches:
                        receiver_data['mobile_phone'] = matches.group().strip()
                        receivers.append(receiver_data)
                    else:
                        wrong_data += 1
                elif len(separator) == 1:
                    receiver_data['firstname'] = ""
                    receiver_data['lastname'] = ""
                    regex = r"[\+\-\(\)?0-9 ]{3,}"
                    matches = re.match(regex, separator[0])
                    if matches:
                        receiver_data['mobile_phone'] = matches.group().strip()
                        receivers.append(receiver_data)
                    else:
                        wrong_data += 1
                else:
                    wrong_data += 1
        receiver_message = MessageReceiversView.add_receivers(request, message_id, receivers)
        message_receivers = MessageReceivers.objects.filter(message_content_id=message_id, is_show=1)
        receiver_list = []
        for receiver in message_receivers:
            receiver.last_received = TimeDetailView.utc_to_local(request, str(receiver.last_received))
            context = {
                'id': receiver.id,
                'firstname': receiver.firstname,
                'lastname': receiver.lastname,
                'mobile_phone': receiver.mobile_phone,
                'push': receiver.push,
                'status': receiver.status,
                'last_received': str(receiver.last_received),
            }
            receiver_list.append(context)
        if wrong_data:
            receiver_message['message'] += str(
                wrong_data) + " rows did not contain neither a correct phone number or device tokens."
        # response_data['message_receivers'] = render_to_string('message_content/receivers_list.html',
        #                                                       {'message_receivers': message_receivers,'request': request})
        response_data['message_receivers'] = receiver_list
        response_data['admin_permission'] = False
        if 'message_permission' in request.session['admin_permission']['content_permission'] and request.session['admin_permission']['content_permission']['message_permission']['access_level'] == 'write' or request.session['event_auth_user']['type'] == 'super_admin':
            response_data['admin_permission'] = True
        response_data['success'] = True
        response_data['message'] = receiver_message['message']
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def add_receivers(request, message_id, receivers):
        duplicate_receiver = 0
        added_receiver = 0
        sms_receiver = 0
        push_receiver = 0
        both_receiver = 0
        message_receiver = 0
        wrong_data = 0
        messages = "Added a total of X receivers successfully. Y can receive only SMS. Z can receive only Push. XX can receive both. There were YY duplicates. ZZ rows did not contain neither a correct phone number or device tokens."
        message = ''
        all_recievers = []
        ErrorR.ex_time_init()
        for receiver in receivers:
            if MessageReceivers.objects.filter(mobile_phone=receiver['mobile_phone'], is_show=1,
                                               message_content_id=message_id).exclude(mobile_phone='').exists():
                duplicate_receiver = duplicate_receiver + 1
            else:
                duplicate_flag = False
                receiver_form = {
                    'firstname': receiver['firstname'],
                    'lastname': receiver['lastname'],
                    'mobile_phone': receiver['mobile_phone'],
                    'status': 'not_sent',
                    'added_by_id': request.session['event_auth_user']['id'],
                    'message_content_id': message_id
                }
                attendee = None
                try:
                    attendee = Attendee.objects.filter(phonenumber=receiver['mobile_phone'],
                                                       event_id=request.session['event_auth_user']['event_id'],status="registered").values('id','firstname','lastname','phonenumber').exclude(phonenumber='').first()
                except:
                    pass
                if 'plugin_message' in receiver:
                    if 'attendee_id' in receiver:
                        receiver_form['attendee_id'] = receiver['attendee_id']
                        if MessageReceivers.objects.filter(attendee_id=receiver['attendee_id'], is_show=1,
                                                           message_content_id=message_id).exists():
                            duplicate_flag = True
                            duplicate_receiver = duplicate_receiver + 1
                        else:
                            attendee_tokens = Attendee.objects.get(id=receiver['attendee_id']).devicetoken_set.all().count()
                            if attendee_tokens > 0:
                                receiver_form['push'] = True
                            message_receiver = message_receiver + 1
                elif attendee:
                    if 'attendee_id' in receiver:
                        receiver_form['attendee_id'] = receiver['attendee_id']
                    else:
                        receiver_form['attendee_id'] = attendee['id']
                    if 'firstname' in receiver and receiver['firstname'] != '':
                        receiver_form['firstname'] = receiver['firstname']
                    else:
                        receiver_form['firstname'] = attendee['firstname']
                    if 'lastname' in receiver and receiver['lastname'] != '':
                        receiver_form['lastname'] = receiver['lastname']
                    else:
                        receiver_form['lastname'] = attendee['lastname']
                    receiver_form['mobile_phone'] = attendee['phonenumber']
                    if MessageReceivers.objects.filter(attendee_id=attendee['id'], is_show=1,
                                                       message_content_id=message_id).exists():
                        duplicate_flag = True
                        duplicate_receiver = duplicate_receiver + 1
                    else:
                        attendee_tokens = Attendee.objects.get(id=attendee['id']).devicetoken_set.all().count()
                        if not attendee['phonenumber'] and attendee_tokens == 0:
                            wrong_data = wrong_data + 1
                        if attendee['phonenumber'] and attendee_tokens > 0:
                            both_receiver = both_receiver + 1
                        elif attendee_tokens > 0:
                            push_receiver = push_receiver + 1
                        elif attendee['phonenumber']:
                            sms_receiver = sms_receiver + 1
                        if attendee_tokens > 0:
                            receiver_form['push'] = True
                elif 'attendee' in receiver:
                    if MessageReceivers.objects.filter(attendee_id=receiver['attendee'].id, is_show=1,
                                                       message_content_id=message_id).exists():
                        duplicate_flag = True
                        duplicate_receiver = duplicate_receiver + 1
                    elif receiver['attendee'].devicetoken_set.all().count() > 0:
                        receiver_form['push'] = True
                        if 'attendee_id' in receiver:
                            receiver_form['attendee_id'] = receiver['attendee_id']
                        else:
                            receiver_form['attendee_id'] = attendee['id']
                        if 'firstname' in receiver and receiver['firstname'] != '':
                            receiver_form['firstname'] = receiver['firstname']
                        else:
                            receiver_form['firstname'] = attendee['firstname']
                        if 'lastname' in receiver and receiver['lastname'] != '':
                            receiver_form['lastname'] = receiver['lastname']
                        else:
                            receiver_form['lastname'] = attendee['lastname']
                        receiver_form['mobile_phone'] = receiver['attendee'].phonenumber
                        push_receiver = push_receiver + 1
                else:
                    if receiver['mobile_phone'] == '':
                        wrong_data = wrong_data + 1
                    else:
                        sms_receiver = sms_receiver + 1
                if not duplicate_flag:
                    new_receiver = MessageReceivers(**receiver_form)
                    all_recievers.append(new_receiver)
                    # new_receiver.save()
                    added_receiver = added_receiver + 1
        MessageReceivers.objects.bulk_create(all_recievers)
        ErrorR.ex_time()
        if added_receiver > 0:
            message += 'Added a total of ' + str(added_receiver) + ' receivers successfully.'
        if sms_receiver > 0:
            message += str(sms_receiver) + ' can receive only SMS.'
        if push_receiver > 0:
            message += str(push_receiver) + ' can receive only Push.'
        if message_receiver > 0:
            message += str(message_receiver) + ' will show in message plugin.'
        if both_receiver > 0:
            message += str(both_receiver) + ' can receive both.'
        if duplicate_receiver > 0:
            message += ' There were ' + str(duplicate_receiver) + ' duplicates.'
        context = {
            "message": message,
            "wrong_data": wrong_data
        }
        return context


class MessageContentView(generic.DetailView):

    def get(self, request, pk):
        if EventView.check_permissions(request, 'message_permission'):
            message = MessageDetailView.get_object(self, pk)
            questionGroup = GroupView.get_questionGroup(request)
            for group in questionGroup:
                group.questions = Questions.objects.filter(group_id=group.id).order_by('question_order')
            [presets, presetsEvent] = LanguageH.get_preset_list(request.session['event_auth_user']['event_id'],
                                                                request.session['event_auth_user']['type'])
            context = {
                "message": message,
                "questionGroup": questionGroup,
                "presets": presets,
                "presetsEvent": presetsEvent,
            }
            return render(request, 'message_content/contents.html', context)
        else:
            raise Http404

    def post(self, request, pk):
        if EventView.check_permissions(request, 'message_permission'):
            message_id = pk
            content = request.POST.get('content')
            language_id = request.POST.get('language_id')
            try:
                message, message_created = MessageLanguageContents.objects.update_or_create(language_id=language_id,
                                                                                            message_content_id=message_id,
                                                                                            defaults={
                                                                                                "content": content
                                                                                            })
                if message_created:
                    response_data = {
                        'success': True,
                        'message': 'Message Content Created Successfully',
                    }
                else:
                    response_data = {
                        'success': True,
                        'message': 'Message Content Updated Successfully',
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

    def show_preview(request):
        content = request.POST.get('content')
        content = EmailContentDetailView.replace_general_tags(request, content, None, None, True)
        content = content.replace('\n','<br/>')
        context = {
            'email_contents': content
        }
        return render(request, 'message/email_preview.html', context)

    def get_lang_message(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        try:
            content_id = request.POST.get('content_id')
            language_id = request.POST.get('language_id')
            message = MessageLanguageContents.objects.filter(message_content=content_id, language_id=language_id,
                                                             message_content__event_id=event_id).first()
            if not message:
                defult_language = PresetEvent.objects.filter(event_id=event_id).first()
                message = MessageLanguageContents.objects.filter(message_content=content_id, language_id=defult_language.preset_id,
                                                                 message_content__event_id=event_id).first()

            response_data = {
                "success": True,
                "message_content": message.content
            }
        except Exception as e:
            ErrorR.efail(e)
            response_data = {
                "success": False,
                "message_content": ""
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class PushNotification(threading.Thread):
    """docstring for PushNotification"""

    def __init__(self, request, attendees, msg, subject, msg_id):
        self.request = request
        self.attendees = attendees
        self.msg = msg
        self.subject = subject
        self.msg_id = msg_id
        threading.Thread.__init__(self)

    def run(self):
        session = SNSHelper()
        push_activities = []
        for attendee in self.attendees:
            if attendee.push_notification_status:
                my_msg = self.msg
                questions = []
                match = re.findall("qid:\d+", my_msg)
                for q in match:
                    data = {
                        'qid': q.split(':')[1]
                    }
                    questions.append(data)
                for question in questions:
                    answer = Answers.objects.filter(question_id=question['qid'], user_id=attendee.id)
                    if answer.exists():
                        my_msg = my_msg.replace('{qid:' + question['qid'] + '}', answer[0].value)
                    else:
                        my_msg = my_msg.replace('{qid:' + question['qid'] + '}', '')
                my_msg = EmailContentDetailView.replace_general_tags(self.request, my_msg, attendee, attendee.language_id)
                for device in attendee.devicetoken_set.all():
                    endpoint = device.arn_enpoint
                    endpointAttr = session.getEndpointAttr(endpoint)
                    logger = logging.getLogger(__name__)
                    logger.debug('-----------Push notification-----------------------')
                    logger.debug(endpoint)
                    if 'attributes' in endpointAttr:
                        if endpointAttr['attributes']['Enabled']:
                            if device.os_type == '1' or device.os_type == 1:
                                session.androidMessageJSON(endpoint, my_msg, self.subject)
                                activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                   admin_id=self.request.session['event_auth_user'][
                                                                       'id'],
                                                                   activity_type='message',
                                                                   category='push_notification',
                                                                   message_id=self.msg_id,
                                                                   event_id=self.request.session['event_auth_user'][
                                                                       'event_id'])
                                push_activities.append(activity_history)
                            elif device.os_type == '2' or device.os_type == 2:
                                if 'ENVIRONMENT_TYPE' in os.environ:
                                    if os.environ['ENVIRONMENT_TYPE'] == 'master':
                                        session.iosMessageJSON(endpoint, my_msg)
                                        activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                           admin_id=
                                                                           self.request.session['event_auth_user'][
                                                                               'id'], activity_type='message',
                                                                           category='push_notification',
                                                                           message_id=self.msg_id,
                                                                           event_id=
                                                                           self.request.session['event_auth_user'][
                                                                               'event_id'])
                                        push_activities.append(activity_history)
                                    else:
                                        session.iosDevMessageJSON(endpoint, my_msg)
                                        activity_history = ActivityHistory(attendee_id=attendee.id,
                                                                           admin_id=
                                                                           self.request.session['event_auth_user'][
                                                                               'id'], activity_type='message',
                                                                           category='push_notification',
                                                                           message_id=self.msg_id,
                                                                           event_id=
                                                                           self.request.session['event_auth_user'][
                                                                               'event_id'])
                                        push_activities.append(activity_history)
                        else:
                            device.is_enable = False
                            device.save()

        ActivityHistory.objects.bulk_create(push_activities)
