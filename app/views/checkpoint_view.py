try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

from django.shortcuts import render, redirect
from django.core import serializers

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from app.models import Attendee, Checkpoint, Scan, SeminarsUsers, RuleSet, Group, Questions,ActivityHistory, Answers, Events, \
    ExportState, \
    AttendeeTag, Tag, AttendeeGroups, Option, EmailContents, MessageContents, CurrentFilter
import json, math
from django.db.models import Q
from django.db import transaction
from .filter import FilterView
from .common_views import GroupView, EventView, CommonContext, TimeDetailView
from django.views.decorators.http import require_http_methods
import boto3
from django.conf import settings
from boto3.session import Session as boto_session
from datetime import datetime, timedelta
import re
import io
from .export_lambda import ExcelView as ev
from .export_import_view import ExcelView
from . import aws_lambda
import boto
from boto.s3.key import Key
from app.views.gbhelper.error_report_helper import ErrorR, DateTimeHelper
from app.views.gbhelper.language_helper import LanguageH


class CheckpointView(generic.DetailView):
    def checkpoint_list(request):
        if EventView.check_read_permissions(request, 'checkpoints_permission'):
            event_id = request.session['event_auth_user']['event_id']
            checkpoints = Checkpoint.objects.filter(event_id=event_id)

            for checkpoint in checkpoints:
                checkpoint.max = 0
                checkpoint.checked = 0
                scans = Scan.objects.filter(checkpoint_id=checkpoint.id, status=True)
                checkpoint.checked = scans.count()
                if checkpoint.session_id:
                    max = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').count()
                    checkpoint.max = max
                    checkpoint.type = "session"
                elif checkpoint.filter_id:
                    # rule = RuleSet.objects.get(id=checkpoint.filter_id)
                    # filters = json.loads(rule.preset)
                    # q = Q()
                    # match_condition = filters[0][0]['matchFor']
                    # if match_condition == '2':
                    #     q &= FilterView.recur_filter(request, filters, match_condition)
                    # elif match_condition == '1':
                    #     q = Q(id=-11)
                    #     q |= FilterView.recur_filter(request, filters, match_condition)
                    # attendees = Attendee.objects.filter(q)

                    attendees = FilterView.get_filtered_attendees(request, checkpoint.filter_id)

                    checkpoint.max = attendees.count()
                    checkpoint.type = "admin"

                checkpoint.remaining = checkpoint.max - checkpoint.checked
                if checkpoint.max > 0:
                    checkpoint.percentage = (checkpoint.checked * 100) / checkpoint.max
                else:
                    checkpoint.percentage = 0
            quick_filter = RuleSet.objects.filter(name='quick-filter',
                                                  created_by_id=request.session['event_auth_user']['id'],
                                                  group__event_id=event_id)
            quick_filter_id = ''
            if quick_filter.exists():
                quick_filter_id = quick_filter[0].id


            common_context = CommonContext.get_all_common_context(request)

            context = {
                'checkpoints': checkpoints,
                'quick_filter_id': quick_filter_id,


            }
            context.update(common_context)
            filter_context= CommonContext.get_filter_context(request)
            context.update(filter_context)

            return render(request, 'checkpoint/checkpoint.html', context)

    def get_modal_html(request):
        event_id = request.session['event_auth_user']['event_id']
        updateFlag = False
        sessionFlag = False
        re_entry = ""
        checkpoint_gen_qustions = []
        general_questions = [
            {"id": "uid", "title": "UID(External)", "checked": ""},
            {"id": "bid", "title": "BID(Badge)", "checked": ""},
            {"id": "created", "title": "Registration Date", "checked": ""},
            {"id": "update", "title": "Update Date", "checked": ""},
            {"id": "group", "title": "Group", "checked": ""},
            {"id": "tag", "title": "Tags", "checked": ""},
        ]

        if 'id' in request.POST:
            updateFlag = True
            current_id = request.POST.get('id')
            current_checkpoint = Checkpoint.objects.filter(id=current_id).first()
            current_qlist = current_checkpoint.questions.split(',')
            current_rule_id = current_checkpoint.filter_id
            if current_checkpoint.session:
                sessionFlag = True

            if current_checkpoint.defaults:
                checkpoint_gen_qustions = current_checkpoint.defaults.split(',')

            for c_g_q in checkpoint_gen_qustions:
                if c_g_q == 'uid':
                    general_questions[0]['checked'] = 'checked'
                if c_g_q == 'bid':
                    general_questions[1]['checked'] = 'checked'
                elif c_g_q == 'created':
                    general_questions[2]['checked'] = 'checked'
                elif c_g_q == 'update':
                    general_questions[3]['checked'] = 'checked'
                elif c_g_q == 'group':
                    general_questions[4]['checked'] = 'checked'
                elif c_g_q == 'tag':
                    general_questions[5]['checked'] = 'checked'

        questions_group = GroupView.get_questionGroup(request)

        questions = []
        for group in questions_group:
            questions.extend(Questions.objects.filter(group=group))

        if updateFlag and current_checkpoint.allow_re_entry == 1:
            re_entry = "checked"

        filterGroup = ExcelView.get_filterGroup(request)
        for group in filterGroup:
            group.filters = RuleSet.objects.filter(group_id=group.id).exclude(name='quick-filter')

        for fff in filterGroup:
            for ff in fff.filters:
                if updateFlag == True and str(ff.id) == str(current_rule_id):
                    ff.selected = 'selected'

        crnt = -1
        for qqq in questions:
            if qqq.group_id != crnt:
                qqq.newGroup = True
                crnt = qqq.group_id
            else:
                qqq.newGroup = False

            if (updateFlag == True) and str(qqq.id) in current_qlist:
                qqq.checked = 'checked'


        quick_filter = RuleSet.objects.filter(name='quick-filter',created_by_id=request.session['event_auth_user']['id'],
                                              group__event_id=event_id)
        quick_filter_id = ''
        if quick_filter.exists():
            quick_filter_id = quick_filter[0].id

        context = {
            'questions': questions,
            'filterGroup': filterGroup,
            're_entry': re_entry,
            'isSession': sessionFlag,
            'general_questions': general_questions,
            'quick_filter_id': quick_filter_id,
        }

        if updateFlag:
            context.update({'name': current_checkpoint.name})

        from django.template.loader import render_to_string

        modal_html = render_to_string('checkpoint/add_checkpoint.html', context)
        response_data = {}
        response_data['modal_html'] = modal_html
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_checkpoint(request):
        if 'id' in request.POST:
            checkpoint = Checkpoint.objects.filter(id=request.POST.get('id')).first()

            if checkpoint:
                if request.POST.get('re_entry'):
                    checkpoint.allow_re_entry = request.POST.get('re_entry')
                else:
                    checkpoint.allow_re_entry = 0

                all_questions = request.POST.getlist('questions')
                general_questions = []
                for qus_item in all_questions:
                    if qus_item == 'uid':
                        general_questions.append(qus_item)
                    if qus_item == 'bid':
                        general_questions.append(qus_item)
                    elif qus_item == 'created':
                        general_questions.append(qus_item)
                    elif qus_item == 'update':
                        general_questions.append(qus_item)
                    elif qus_item == 'group':
                        general_questions.append(qus_item)
                    elif qus_item == 'tag':
                        general_questions.append(qus_item)

                all_questions = [qqq for qqq in all_questions if qqq not in general_questions]
                checkpoint.defaults = ','.join(map(str, general_questions))
                checkpoint.questions = ','.join(map(str, all_questions))

                if checkpoint.session == None:
                    checkpoint.name = request.POST.get('name')
                    checkpoint.filter_id = request.POST.get('rule_id')
                checkpoint.save()
                msg = "Checkpoint saved"

            else:
                msg = "Checkpoint not found"

        else:
            user_id = request.session['event_auth_user']['id']
            event_id = request.session['event_auth_user']['event_id']
            re_entry = 0
            if request.POST.get('re_entry'):
                re_entry = 1

            all_questions = request.POST.getlist('questions')
            general_questions = list(filter(lambda x: not x.isdigit(), all_questions))
            questions = list(filter(lambda x: x.isdigit(), all_questions))
            checkpoint_data = {
                'name': request.POST.get('name'),
                'allow_re_entry': re_entry,
                'filter_id': request.POST.get('rule_id'),
                'is_hide': 0,
                'defaults': ','.join(map(str, general_questions)),
                'questions': ','.join(map(str, questions)),
                'created_by_id': user_id,
                'event_id': event_id,
            }
            checkpoint = Checkpoint(**checkpoint_data)
            checkpoint.save()
        return redirect('checkpoint')

    def delete_checkpoint(request):
        Checkpoint.objects.filter(id=request.POST.get('id')).first().delete()
        return HttpResponse(json.dumps({'msg': "Checkpoint Deleted", 'error': False}))

    def perform_check(request, attendee_id, checkpoint_id):
        error = False
        checkpoint_stats = None
        if attendee_id and checkpoint_id:
            checkpoint = Checkpoint.objects.filter(id=checkpoint_id).first()
            scan_obj = Scan.objects.filter(attendee_id=attendee_id, checkpoint_id=checkpoint_id).last()
            if scan_obj and (checkpoint.allow_re_entry == 1 or (checkpoint.allow_re_entry == 0 and scan_obj.status == 0)):
                # if scan_obj.status == 1:
                #     scan_obj.status = 0
                # else:
                scan_obj.status = 1

                scan_obj.scan_time = datetime.now()
                scan_obj.save()
                activity = ActivityHistory(activity_type='check-in', category='checkpoint', attendee_id=attendee_id, checkpoint_id=checkpoint_id, admin_id=request.session['event_auth_user']['id'], event_id=checkpoint.event.id)
                activity.save()
                msg = "Check updated"

            elif scan_obj and checkpoint.allow_re_entry == 0:
                error = True
                msg = "Re entry not allowed"
            else:
                scan_data = {
                    'checkpoint_id': checkpoint_id,
                    'attendee_id': attendee_id,
                    'status': 1
                }
                scan_obj = Scan(**scan_data)
                scan_obj.save()
                activity = ActivityHistory(activity_type='check-in', category='checkpoint', attendee_id=attendee_id, checkpoint_id=checkpoint_id, admin_id=request.session['event_auth_user']['id'], event_id=checkpoint.event.id)
                activity.save()
                msg = "Check saved"
        else:
            error = True
            scan_obj = None
            msg = "Checkpoint or Attendee not found"

        if scan_obj:
            temp_datetime = TimeDetailView.utc_to_local(request, str(scan_obj.scan_time))
            scan_obj.scan_time = DateTimeHelper.get_formated_date_string(temp_datetime, scan_obj.attendee.language_id)
            checkpoint_stats = CheckpointView.checkpoint_stats(request, checkpoint)

        return HttpResponse(json.dumps({'msg': msg, 'error': error, 'scan': scan_obj.as_dict(), 'checkpoint': checkpoint_stats}))

    def change_status(request):
        attendee_id = request.POST.get('attendee_id')
        checkpoint_id = request.POST.get('checkpoint_id')
        error = False
        checkpoint_stats = None
        if attendee_id and checkpoint_id:
            checkpoint = Checkpoint.objects.filter(id=checkpoint_id).first()
            scan_obj = Scan.objects.filter(attendee_id=attendee_id, checkpoint_id=checkpoint_id).last()
            if scan_obj:
                if scan_obj.status == 1:
                    scan_obj.status = 0
                else:
                    scan_obj.status = 1

                scan_obj.scan_time = datetime.now()
                scan_obj.save()
                activity = ActivityHistory(activity_type='check-in', category='checkpoint', attendee_id=attendee_id, checkpoint_id=checkpoint_id, admin_id=request.session['event_auth_user']['id'], event_id=checkpoint.event.id)
                activity.save()
                msg = "Check updated"

            else:
                scan_data = {
                    'checkpoint_id': checkpoint_id,
                    'attendee_id': attendee_id,
                    'status': 1
                }
                scan_obj = Scan(**scan_data)
                scan_obj.save()
                activity = ActivityHistory(activity_type='check-in', category='checkpoint', attendee_id=attendee_id, checkpoint_id=checkpoint_id, admin_id=request.session['event_auth_user']['id'], event_id=checkpoint.event.id)
                activity.save()
                msg = "Check saved"
        else:
            error = True
            scan_obj = None
            msg = "Checkpoint or Attendee not found"

        if scan_obj:
            temp_datetime = TimeDetailView.utc_to_local(request, str(scan_obj.scan_time))
            scan_obj.scan_time = DateTimeHelper.get_formated_date_string(temp_datetime, scan_obj.attendee.language_id)
            checkpoint_stats = CheckpointView.checkpoint_stats(request, checkpoint)

        return HttpResponse(json.dumps({'msg': msg, 'error': error, 'scan': scan_obj.as_dict(), 'checkpoint': checkpoint_stats}))

    def checkpoint_stats(request, checkpoint):
        checkpoint.max = 0
        checkpoint.checked = Scan.objects.filter(checkpoint_id=checkpoint.id, status=1).count()
        if checkpoint.session_id:
            checkpoint.max = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').count()
            # checkpoint.max = seminar_users.count()
        elif checkpoint.filter_id:
            checkpoint.max = FilterView.get_filtered_attendees(request, checkpoint.filter_id).count()
            # checkpoint.max = attendees.count()

        checkpoint.remaining = checkpoint.max - checkpoint.checked
        if checkpoint.max > 0:
            checkpoint.percentage = round((checkpoint.checked * 100) / checkpoint.max, 2)
        else:
            checkpoint.percentage = 0
        stats = {'checked': checkpoint.checked, 'percentage': checkpoint.percentage, 'remaining': checkpoint.remaining, 'total': checkpoint.max}
        return stats

    def checkpoint_manual_update(request):
        response = {'success': False}
        try:
            checkpoint_id = request.POST.get('checkpoint_id')
            if checkpoint_id:
                checkpoint = Checkpoint.objects.filter(id=checkpoint_id).first()
                if checkpoint:
                    response['checkpoint'] = CheckpointView.checkpoint_stats(request, checkpoint)
                    response['success'] = True
        except Exception as exc:
            ErrorR.efail(exc)

        return HttpResponse(json.dumps(response), content_type='application/json')

    def change_checkpoint_status(request):
        attendee_id = request.POST.get('attendee_id')
        checkpoint_id = request.POST.get('checkpoint_id')
        return CheckpointView.perform_check(request, attendee_id, checkpoint_id)

    def auto_perform_check(request):
        attendee_bid = request.POST.get('attendee_secret', '').strip()
        checkpoint_id = request.POST.get('checkpoint_id')
        event_id = request.session['event_auth_user']['event_id']
        attendee = Attendee.objects.filter(bid=attendee_bid, event_id=event_id).first()
        if attendee:
            if CheckpointView.check_attendee_checkpoint(request, attendee.id, checkpoint_id):
                return CheckpointView.perform_check(request, attendee.id, checkpoint_id)

        return HttpResponse(json.dumps({'msg': "Attendee Not found....", 'error': True}))

    def check_attendee_checkpoint(request, attendee_id, checkpoint_id):
        if checkpoint_id:
            checkpoint = Checkpoint.objects.filter(id=checkpoint_id).first()
            if checkpoint.session:
                if SeminarsUsers.objects.filter(session_id=checkpoint.session_id, attendee_id=attendee_id, status='attending'):
                    return True
            else:
                attendees = FilterView.get_filtered_attendees(request, checkpoint.filter_id)
                if attendee_id in [a.id for a in attendees]:
                    return True
        return False

    def checkpoint_duplicate(request):
        response_data = {}
        id = request.POST.get('id')
        event_id = request.session['event_auth_user']['event_id']
        checkpoint = Checkpoint.objects.filter(id=id).first()

        duplicate_existance = Checkpoint.objects.filter(name=checkpoint.name + '[Copy]', event_id=event_id)
        if duplicate_existance.exists():
            response_data['error'] = 'This checkpoint is already make a duplicate.'
            return HttpResponse(json.dumps(response_data), content_type='application/json')

        if checkpoint:
            checkpoint.pk = None
            checkpoint.name += '[Copy]'
            checkpoint.created_by_id = request.session['event_auth_user']['id']
            checkpoint.save()

            # extra fields for view
            checkpoint.max = 0
            checkpoint.checked = 0
            scans = Scan.objects.filter(checkpoint_id=checkpoint.id)
            checkpoint.checked = scans.count()
            if checkpoint.session_id:
                max = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').count()
                checkpoint.max = max
                checkpoint.type = "session"
            elif checkpoint.filter_id:
                # rule = RuleSet.objects.get(id=checkpoint.filter_id)
                # filters = json.loads(rule.preset)
                # q = Q()
                # match_condition = filters[0][0]['matchFor']
                # if match_condition == '2':
                #     q &= FilterView.recur_filter(request, filters, match_condition)
                # elif match_condition == '1':
                #     q = Q(id=-11)
                #     q |= FilterView.recur_filter(request, filters, match_condition)
                # attendees = Attendee.objects.filter(q)

                attendees = FilterView.get_filtered_attendees(request, checkpoint.filter_id)

                checkpoint.max = attendees.count()
                checkpoint.type = "admin"

            checkpoint.remaining = checkpoint.max - checkpoint.checked
            if checkpoint.max > 0:
                checkpoint.percentage = (checkpoint.checked * 100) / checkpoint.max
            else:
                checkpoint.percentage = 0

            response_data['success'] = "Create duplicate filter Successfully"
            response_data['checkpoint'] = checkpoint.as_dict()
            response_data['percentage'] = checkpoint.percentage
            response_data['max'] = checkpoint.max
            response_data['remaining'] = checkpoint.remaining
            response_data['checked'] = checkpoint.checked
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def checkpoint_details(request, pk):
        if EventView.check_permissions(request, 'checkpoints_permission'):
            event_id = request.session['event_auth_user']['event_id']
            admin_id = request.session['event_auth_user']['id']
            checkpoint = Checkpoint.objects.filter(id=pk, event_id=event_id).first()
            if checkpoint:
                if checkpoint.questions:
                    checkpoint_questions = checkpoint.questions.split(',')
                else:
                    checkpoint_questions = []

                questions = Questions.objects.filter(id__in=checkpoint_questions)

                if checkpoint.defaults:
                    general_questions = checkpoint.defaults.split(',')
                else:
                    general_questions = []

                general_question_list = []
                for g_qus in general_questions:
                    if g_qus == 'uid':
                        general_question_list.append({"id": "444444", "title": "UID"})
                    if g_qus == 'bid':
                        general_question_list.append({"id": "777777", "title": "BID"})
                    elif g_qus == 'created':
                        general_question_list.append({"id": "222222", "title": "Registration Date"})
                    elif g_qus == 'update':
                        general_question_list.append({"id": "333333", "title": "Update Date"})
                    elif g_qus == 'group':
                        general_question_list.append({"id": "555555", "title": "Group"})
                    elif g_qus == 'tag':
                        general_question_list.append({"id": "666666", "title": "Tags"})

                # extra fields for view
                checkpoint.max = 0
                checkpoint.checked = 0
                scans = Scan.objects.filter(checkpoint_id=checkpoint.id, status=True)
                checkpoint.checked = scans.count()
                last_scan = None
                if checkpoint.session_id:
                    seminar_users = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').values('attendee_id')
                    checkpoint.max = seminar_users.count()
                    checkpoint.type = "session"
                    last_scan = Scan.objects.filter(attendee__in=seminar_users, checkpoint_id=checkpoint.id).order_by('-scan_time').first()
                elif checkpoint.filter_id:
                    attendees = FilterView.get_filtered_attendees(request, checkpoint.filter_id)
                    checkpoint.max = attendees.count()
                    checkpoint.type = "admin"
                    last_scan = Scan.objects.filter(attendee__in=attendees, checkpoint_id=checkpoint.id).order_by('-scan_time').first()

                checkpoint.remaining = checkpoint.max - checkpoint.checked
                if checkpoint.max > 0:
                    checkpoint.percentage = (checkpoint.checked * 100) / checkpoint.max
                else:
                    checkpoint.percentage = 0

                current_filter = CurrentFilter.objects.filter(admin_id=admin_id, event_id=event_id, table_type='checkpoint')
                if current_filter:
                    current_filter = current_filter[0]
                else:
                    current_filter = CurrentFilter(admin_id=admin_id, event_id=event_id, table_type='checkpoint', show_rows=10, sorted_column=1)
                    current_filter.save()

                show_entries = current_filter.show_rows
                sorting_order = current_filter.sorting_order
                sorted_column = current_filter.sorted_column
                column_counter = len(questions) + len(general_question_list) + 1
                if sorted_column > column_counter:
                    sorted_column = 1

                context = {
                    'questions': questions,
                    'questionGroup': questions,
                    'checkpoint': checkpoint,
                    'show_entries': show_entries,
                    'sorted_column': sorted_column,
                    'sorting_order': sorting_order,
                    'last_scan': last_scan,
                    'general_questions': general_question_list
                }
                return render(request, 'checkpoint/checkpoint_view.html', context)
            else:
                raise Http404
        else:
            raise Http404

    def get_answers_for_given_questions(attendee_id, question_ids):
        answers = []
        for q_id in question_ids:
            answer = Answers.objects.filter(user_id=attendee_id, question_id=q_id).first()
            if answer:
                answers.append({"q_id": q_id, "answer": answer.value})
            else:
                answers.append({"q_id": q_id, "answer": ""})

        return answers

    def export_checkpoint(request):
        checkpoint_id = request.POST.get('id')
        event_id = request.session['event_auth_user']['event_id']
        if checkpoint_id:
            checkpoint = Checkpoint.objects.filter(id=checkpoint_id).first()
            if checkpoint:
                if checkpoint.questions:
                    checkpoint_questions = checkpoint.questions.split(',')
                else:
                    checkpoint_questions = []
                questions = Questions.objects.filter(id__in=checkpoint_questions)

                time_with_timezone = ExcelView.getTimezoneNow(request)
                event = Events.objects.get(id=event_id)
                file_name = 'exported_files/' + event.name + '/' + checkpoint.name + '_' + str(
                    time_with_timezone.strftime("%Y_%m_%d_%H_%M_%S")) + '.xlsx'

                if checkpoint.session:
                    seminar_users = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending')
                    answers = Answers.objects.filter(question__id__in=checkpoint_questions,
                                                     user_id__in=seminar_users.values('attendee_id'))
                    checkpoint_type = "session"
                    scan = Scan.objects.filter(attendee_id__in=seminar_users.values('attendee_id'), checkpoint_id=checkpoint_id)
                    attendees = Attendee.objects.filter(id__in=seminar_users.values('attendee_id'))

                elif checkpoint.filter_id:
                    attendees = FilterView.get_filtered_attendees(request, checkpoint.filter_id)
                    answers = Answers.objects.filter(question_id__in=checkpoint_questions, user__in=attendees)
                    scan = Scan.objects.filter(attendee__in=attendees, checkpoint_id=checkpoint_id)
                    checkpoint_type = "admin"

                defaults = []
                if checkpoint.defaults:
                    defaults = checkpoint.defaults.split(',')
                attendee_tags = []
                all_tags = []
                attendee_groups = []
                all_group = []
                if 'tag' in defaults:
                    attendee_tags = AttendeeTag.objects.filter(attendee__in=attendees)
                    all_tags = Tag.objects.filter(event_id=event_id)

                if 'group' in defaults:
                    attendee_groups = AttendeeGroups.objects.filter(attendee__in=attendees)
                    all_group = Group.objects.all()
                headers = CheckpointView.prepare_export_header(questions, defaults)

                var_list = {
                    'checkpoint_export': True,
                    'headers': json.dumps(headers),
                    'defaults': json.dumps(defaults),
                    'file_name': file_name,
                    'checkpoint_questions': serializers.serialize('json', questions),
                    'attendees': serializers.serialize('json', attendees),
                    'attendee_tags': serializers.serialize('json', attendee_tags),
                    'all_tags': serializers.serialize('json', all_tags),
                    'attendee_groups': serializers.serialize('json', attendee_groups),
                    'all_groups': serializers.serialize('json', all_group),
                    'scan': serializers.serialize('json', scan),
                    'answers': serializers.serialize('json', answers),
                    'checkpoint_type': checkpoint_type
                }
                if checkpoint_type == 'session':
                    # print("sdfsdfdsf")
                    # print(seminar_users.count())
                    var_list['seminar_users'] = serializers.serialize('json', seminar_users)
                    # print(var_list)
                    # msg = "sdfsdf"
                    # return aws_lambda.export(json.dumps(var_list))

                    # S3
                message = json.dumps(var_list)

                conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                filename_with_path = 'export/data.txt'
                key_name = filename_with_path
                k = Key(bucket)
                k.key = key_name
                if not k.exists():
                    key = bucket.new_key(key_name)
                    key.set_contents_from_string(message)
                    key.set_metadata('Content-Type', 'text/plain')
                    key.set_acl('public-read')
                    key.make_public()
                else:
                    k.set_contents_from_string(message)
                    k.set_metadata('Content-Type', 'text/plain')
                    k.set_acl('public-read')
                    k.make_public()
                # END S3
                export_state = ExportState(file_name=file_name, status=0,
                                           event_id=request.session['event_auth_user']['event_id'],
                                           admin_id=request.session['event_auth_user']['id'])
                export_state.save()
                response = {
                    'error': False,
                    'message': 'Your file will be available momentarily.'
                }


            else:
                response = {
                    'error': False,
                    'message': 'Checkpoint not found'
                }
        else:
            response = {
                'error': False,
                'message': 'Checkpoint not found'
            }
        return HttpResponse(json.dumps(response), content_type="application/json")

    def prepare_export_header(questions, defaults):
        header_row = []
        for default in defaults:
            if default == 'uid':
                header_row.append("UID(External)")
            elif default == 'bid':
                header_row.append("BID(Badge)")
            elif default == 'created':
                header_row.append("Created")
            elif default == 'update':
                header_row.append("Updated")
            elif default == 'group':
                header_row.append("Groups")
            elif default == 'tag':
                header_row.append("Tags")

        for question in questions:
            header_row.extend([question.title])
        # if len(header_row) == 0:
        #     header_row = ['BID', 'First Name', 'Email']

        header_row.extend(["Check Status", "Last Check Time", "Last Check Date"])
        return header_row

    def prepare_attendee_row(attendee):
        att_row = [attendee.secret_key, attendee.firstname, attendee.lastname, attendee.email]
        for att in attendee.answers:
            att_row.append(att['answer'])
        att_row.append(attendee.scan_status)
        att_row.append(attendee.scan_time)
        att_row.append(attendee.scan_date)

        return att_row

    def search(request):
        search_key = request.POST.get('search_key')
        event_id = request.session['event_auth_user']['event_id']
        if search_key:
            checkpoints = Checkpoint.objects.filter(name__icontains=search_key,event_id=event_id)
        else:
            checkpoints = Checkpoint.objects.filter(name__icontains=search_key,event_id=event_id)
        for checkpoint in checkpoints:
            checkpoint.max = 0
            checkpoint.checked = 0
            scans = Scan.objects.filter(checkpoint_id=checkpoint.id)
            checkpoint.checked = scans.count()
            if checkpoint.session_id:
                max = SeminarsUsers.objects.filter(session_id=checkpoint.session_id, status='attending').count()
                checkpoint.max = max
                checkpoint.type = "session"
            elif checkpoint.filter_id:
                attendees = FilterView.get_filtered_attendees(request, checkpoint.filter_id)
                checkpoint.max = attendees.count()
                checkpoint.type = "admin"

            checkpoint.remaining = checkpoint.max - checkpoint.checked
            if checkpoint.max > 0:
                checkpoint.percentage = (checkpoint.checked * 100) / checkpoint.max
            else:
                checkpoint.percentage = 0
        data = {
            'checkpoints': checkpoints
        }
        return render(request, 'checkpoint/checkpoint_result.html', data)
