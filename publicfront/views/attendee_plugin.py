import json, os
from django.http import HttpResponse
from django.db.models import Q
from app.models import Attendee, RuleSet, Answers, Questions, Option, AttendeeTag, AttendeeGroups, SeminarsUsers, \
    Booking, MatchLine, RequestedBuddy, ExportRule, Events
from .rule import UserRule
import boto
from boto.s3.key import Key
from boto3.session import Session as boto_session
from django.conf import settings
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey
from publicfront.views.helper import HelperData
from datetime import datetime


class AttendeePluginList:
    def attendee_datatable(request, *args, **kwargs):
        filter_id = request.GET.get('$filter_id')
        total_attendees = AttendeePluginList.get_all_attendee(request, filter_id)
        search_key = request.GET.get('$filter')
        column_ids = request.GET.get('$columns')
        if search_key:
            total_attendees = AttendeePluginList.get_matched_attendee(search_key, total_attendees, column_ids)
        skip = request.GET.get('$skip')
        top = request.GET.get('$top')
        orderby = request.GET.get('$orderby')
        attendees = []

        if skip:
            attendees = AttendeePluginList.get_selected_attendee(int(skip), int(top), total_attendees)
        else:
            attendees = total_attendees[:int(top)]

        if orderby:
            attendees = AttendeePluginList.get_ordered_attendees(orderby, attendees, total_attendees)

        column_ids = json.loads(column_ids)
        attendee_data = AttendeePluginList.get_attendee_data(attendees, column_ids)
        data = {
            'd': {
                'results': attendee_data,
                '__count': len(total_attendees)
            }
        }
        callback_id = request.GET.get('$callback')
        data = json.dumps(data)
        attendee_data = callback_id + '(' + data + ')'

        return HttpResponse(attendee_data, content_type='application/json')

    def get_all_attendee(request, filter_id):
        attendee_filter = RuleSet.objects.filter(id=filter_id)
        filter_preset = json.loads(attendee_filter[0].preset)
        q = Q()
        match_condition = '0'
        if 'matchFor' in filter_preset[0][0]:
            match_condition = filter_preset[0][0]['matchFor']
        elif attendee_filter[0].matchfor:
            match_condition = attendee_filter[0].matchfor
        if match_condition == '2':
            q &= Q(id__in=UserRule.get_filtered_attendee(request, filter_preset, match_condition))
        elif match_condition == '1':
            q = Q(id=-11)
            q |= Q(id__in=UserRule.get_filtered_attendee(request, filter_preset, match_condition))
        else:
            q = Q(id=-11)
        attendees = Attendee.objects.filter(q)
        return attendees

    def get_matched_attendee(search_key, total_attendees, column_ids):
        column_ids = json.loads(column_ids)
        search = search_key.split("search-key eq '")[1][:-1]
        att_ids = [att.id for att in total_attendees]
        matched_attendees = []
        for q_id in column_ids:
            matched_item = Answers.objects.filter(value__icontains=search, question_id=q_id,
                                                  user_id__in=att_ids).values('user_id')
            matched_item_att = [att['user_id'] for att in matched_item]
            matched_attendees.extend(matched_item_att)
        matched_attendees = set(matched_attendees)
        matched_attendees = Attendee.objects.filter(id__in=matched_attendees)
        return matched_attendees

    def get_selected_attendee(skip, top, total_attendees):
        attendees = total_attendees[int(skip): int(skip) + int(top):]
        return attendees

    def get_ordered_attendees(orderby, attendees, total_attendees):
        attendee_ids = [att.id for att in attendees]
        final_ordered_atts = []
        if ' ' in orderby:
            orderby = orderby.split(' ')[0]
            column_check = Questions.objects.filter(Q(title=orderby) | Q(actual_definition=orderby))
            if len(column_check) == 0:
                print('printed column check here')
                orderby = orderby.replace('_', ' ')
            if orderby in ['firstname', 'lastname', 'email', 'phone']:
                got_atts = Answers.objects.filter(user_id__in=attendee_ids,
                                                  question__actual_definition=orderby).order_by('-value')
            else:
                got_atts = Answers.objects.filter(user_id__in=attendee_ids, question__title=orderby).order_by('-value')
            got_atts = [att.user_id for att in got_atts]
            ordered_attendees = got_atts + [id for id in attendee_ids if id not in got_atts]
            for att_id in ordered_attendees:
                final_ordered_atts.append(Attendee.objects.get(id=att_id))
        else:
            column_check = Questions.objects.filter(Q(title=orderby) | Q(actual_definition=orderby))
            if len(column_check) == 0:
                print('printed column check here')
                orderby = orderby.replace('_', ' ')
            if orderby in ['firstname', 'lastname', 'email', 'phone']:
                got_atts = Answers.objects.filter(user_id__in=attendee_ids,
                                                  question__actual_definition=orderby).order_by('value')
            else:
                got_atts = Answers.objects.filter(user_id__in=attendee_ids, question__title=orderby).order_by('value')
            got_atts = [att.user_id for att in got_atts]
            ordered_attendees = got_atts + [id for id in attendee_ids if id not in got_atts]
            for att_id in ordered_attendees:
                final_ordered_atts.append(Attendee.objects.get(id=att_id))

        return final_ordered_atts

    def get_attendee_data(attendees, column_ids):
        attendee_data = []
        for att in attendees:
            answers = Answers.objects.filter(user_id=att.id, question_id__in=column_ids)
            att_ans = {}
            match_question_ids = []
            for ans in answers:
                match_question_ids.append(ans.question_id)
                att_ans[
                    ans.question.actual_definition.replace(' ',
                                                           '_') if ans.question.actual_definition else ans.question.title.replace(
                        ' ', '_')] = ans.value

            unmatch_questions = Questions.objects.filter(id__in=column_ids).exclude(id__in=match_question_ids)
            for unmatch_question in unmatch_questions:
                att_ans[unmatch_question.actual_definition.replace(' ','_') if unmatch_question.actual_definition else unmatch_question.title.replace(' ', '_')] = ""
            attendee_data.append(att_ans)
        return attendee_data

    def get_attendee(request, attendees, generel_ques, question_ids, sessions, hotels, max_booking_number, max_actual_room_buddy):
        attendee_data = []
        try:
            for att in attendees:
                attendee_data.append(AttendeePluginList.get_all_attendee_information(request, att, generel_ques, question_ids, sessions, hotels, max_booking_number, max_actual_room_buddy))
        except Exception as e:
            ErrorR.efail(e)
        # print(attendee_data)
        return attendee_data

    def get_single_attendee(request, attendees, column_ids):
        try:
            attendee_data = []
            for att in attendees:
                attendee_data.append(AttendeePluginList.get_single_attendee_data(request, att, column_ids))
            return attendee_data
        except Exception as e:
            attendee_data = []
            ErrorR.efail(e)
            return attendee_data

    def get_single_attendee_data(request, attendee, column_ids):
        attr = []
        try:
            for column_id in column_ids:
                answer = Answers.objects.filter(user_id=attendee.id, question_id=column_id).select_related('question')
                question_definition = ""
                if answer.exists():
                    answer_value = answer[0].value
                    try:
                        if answer[0].question.type == 'checkbox':
                            checkbox_answers = answer[0].value.split('<br>')
                            checkbox_answer_list = []
                            for checkbox_answer in checkbox_answers:
                                answer_lang = Option.objects.filter(option=checkbox_answer.strip(),
                                                                    question_id=answer[0].question_id).first()
                                answer_data = LanguageKey.get_option_data_by_language(request, answer_lang)
                                checkbox_answer_list.append(answer_data.option)
                            answer_value = '<br>'.join(checkbox_answer_list)
                        elif answer[0].question.type == 'select' or answer[0].question.type == 'radio_button':
                            answer_lang = Option.objects.filter(option=answer[0].value,
                                                                question_id=answer[0].question_id).first()
                            answer_data = LanguageKey.get_option_data_by_language(request, answer_lang)
                            answer_value = answer_data.option
                        elif answer[0].question.type == 'date_range' or answer[0].question.type == 'time_range':
                            answer_values = json.loads(answer_value)
                            if answer_values[0] != '' and answer_values[1] != '':
                                answer_value = answer_values[0]+' to '+answer_values[1]
                            else:
                                answer_value = ''

                    except Exception as e:
                        ErrorR.efail(e)
                        pass
                    if answer[0].question.actual_definition != '' and answer[0].question.actual_definition != None:
                        question_definition = answer[0].question.actual_definition
                    attr.append({'answer': answer_value, 'question': question_definition, 'question_id': column_id})
                else:
                    attr.append({'answer': "", 'question': "", 'question_id': column_id})
        except Exception as e:
            ErrorR.efail(e)
        return {'attr': attr, 'id': attendee.id, 'status': attendee.status}

    def get_all_attendee_information(request, attendee, generel_ques, question_ids, sessions, hotels, max_booking_number, max_actual_room_buddy):
        attr = []
        for key in enumerate(question_ids):
            attr.append('')

        answer_question_ids = []
        try:
            # for question in question_ids:
            answers = Answers.objects.filter(user_id=attendee.id, question_id__in=question_ids)
            for answer in answers:
                question_definition = ""
                index = question_ids.index(answer.question_id)
                if answer:
                    answer_value = answer.value
                    answer_question_ids.append(answer.question_id)
                    try:
                        if answer.question.type == 'checkbox':
                            checkbox_answers = answer.value.split('<br>')
                            checkbox_answer_list = []
                            for checkbox_answer in checkbox_answers:
                                answer_lang = Option.objects.filter(option=checkbox_answer.strip(),
                                                                    question_id=answer.question_id).first()
                                answer_data = LanguageKey.get_option_data_by_language(request, answer_lang)
                                checkbox_answer_list.append(answer_data.option)
                            answer_value = '<br>'.join(checkbox_answer_list)
                        elif answer.question.type == 'select' or answer.question.type == 'radio_button':
                            answer_lang = Option.objects.filter(option=answer.value,
                                                                question_id=answer.question_id).first()
                            answer_data = LanguageKey.get_option_data_by_language(request, answer_lang)
                            answer_value = answer_data.option
                    except Exception as e:
                        ErrorR.efail(e)
                    if answer.question.actual_definition != '' and answer.question.actual_definition != None:
                        question_definition = answer.question.actual_definition
                    # attr.append({'answer': answer_value, 'question': question_definition})
                    dict ={'answer': answer_value, 'question': question_definition}
                    print(index)
                    # attr.insert(index, dict)
                    attr[index] = dict
                else:
                    dict = {'answer': '', 'question': ''}
                    attr[index] = dict
        except Exception as e:
            ErrorR.efail(e)
        unmatched_items = [d for d in question_ids if d not in answer_question_ids]
        for unmatched_item in unmatched_items:
            index = question_ids.index(unmatched_item)
            dict = {'answer': '', 'question': ''}
            attr[index] = dict
        # generel_ques part
        generel_que_ans = []
        
        if 'uid' in generel_ques:
            generel_que_ans.append({'question': '', 'answer': attendee.id})
        if 'att-reg-date' in generel_ques:
            reg_date = HelperData.utc_to_local(request, str(attendee.created))
            reg_date = HelperData.get_formated_date_string(reg_date, request.session['language_id'])
            generel_que_ans.append({'question': '', 'answer': reg_date})
        if 'att-update' in generel_ques:
            u_date = HelperData.utc_to_local(request, str(attendee.updated))
            u_date = HelperData.get_formated_date_string(u_date, request.session['language_id'])
            generel_que_ans.append({'question': '', 'answer': u_date})
        if 'uid-secret' in generel_ques:
            generel_que_ans.append({'question': '', 'answer': attendee.secret_key})
        if 'bid' in generel_ques:
            generel_que_ans.append({'question': '', 'answer': attendee.bid})
        if 'att-grp' in generel_ques:
            att_groups = AttendeeGroups.objects.filter(attendee_id=attendee.id).values('group__name')
            att_group_text = ''
            if att_groups:
                for att_grp in att_groups:
                    att_group_text += att_grp['group__name'] + ', '
                    att_group_text = att_group_text[:-2]
            generel_que_ans.append({'question': '', 'answer': att_group_text})
        if 'att-tag' in generel_ques:
            att_tags = AttendeeTag.objects.filter(attendee_id=attendee.id).values('tag__name')
            att_tag_text = ''
            if att_tags:
                for att_tag in att_tags:
                    att_tag_text += att_tag['tag__name'] + ', '
                att_tag_text = att_tag_text[:-2]
            generel_que_ans.append({'question': '', 'answer': att_tag_text})

        # Session part
        session_ans = []
        for session in sessions:
            sn_answer = {'question': '', 'answer': 'not-attending'}
            session_object = SeminarsUsers.objects.filter(attendee_id=attendee.id, session_id=session).first()
            if session_object:
                sn_answer['answer'] = session_object.status
            session_ans.append(sn_answer)

        # Hotel part
        hotel_ans = []
        if hotels not in [None, '']:
            att_booking_counter = 0
            att_bookings = Booking.objects.filter(attendee_id=attendee.id)
            for att_booking in att_bookings:
                att_booking_counter += 1
                hotel_ans.extend(AttendeePluginList.get_single_booking_data(request, hotels, max_actual_room_buddy, att_booking))
            if max_booking_number > att_booking_counter:
                max_booking_number -= att_booking_counter
                for i in range(0, max_booking_number):
                    hotel_ans.extend(AttendeePluginList.get_single_booking_data(request, hotels, max_actual_room_buddy))


        return {'id': attendee.id, 'attr': attr, 'general_ques': generel_que_ans, 'session_ans': session_ans, 'hotel_ans': hotel_ans}

    def get_single_booking_data(request, hotels, max_actual_room_buddy, booking=None):
        hotel_ans = []
        if 'booking-id-col' in hotels:
            hotel_ans.append({'question': '', 'answer': booking.id if booking else ''})
        if 'match-id-col' in hotels:
            match_id_str = ''
            if booking:
                match_lines = MatchLine.objects.filter(booking_id=booking.id)
                for match_line in match_lines:
                    match_id_str += str(match_line.match_id) + ', '
                if len(match_id_str) > 0:
                    match_id_str = match_id_str[:-2]
            hotel_ans.append({'question': '', 'answer': match_id_str})
        if 'hotel-name-col' in hotels:
            hotel_ans.append({'question': '', 'answer': booking.room.hotel.name if booking else ''})
        if 'description-col' in hotels:
            hotel_ans.append({'question': '', 'answer': booking.room.description if booking else ''})
        if 'room-id-col' in hotels:
            hotel_ans.append({'question': '', 'answer': booking.room_id if booking else ''})
        if 'check-in-col' in hotels:
            check_in = ''
            if booking:
                # ValueError: time data '2017-09-06' does not match format '%Y-%m-%d %H:%M:%S'
                check_in = HelperData.utc_to_local(request, str(datetime.strftime(booking.check_in, "%Y-%m-%d %H:%M:%S")))
                check_in = HelperData.get_formated_date_string(check_in, request.session['language_id'])
            hotel_ans.append({'question': '', 'answer': check_in})
        if 'check-out-col' in hotels:
            check_out = ''
            if booking:
                check_out = HelperData.utc_to_local(request, str(datetime.strftime(booking.check_out, "%Y-%m-%d %H:%M:%S")))
                check_out = HelperData.get_formated_date_string(check_out, request.session['language_id'])
            hotel_ans.append({'question': '', 'answer': check_out})
        if 'beds-col' in hotels:
            hotel_ans.append({'question': '', 'answer': booking.room.beds if booking else ''})
        if 'location-col' in hotels:
            hotel_ans.append({'question': '', 'answer': booking.room.hotel.location.name if booking else ''})
        if 'rbr-col' in hotels:
            rbr_text = ''
            if booking:
                rbr_objs = RequestedBuddy.objects.filter(booking_id=booking.id)
                for rbr_obj in rbr_objs:
                    rbr_text += rbr_obj.email if rbr_obj.email else rbr_obj.buddy.get_full_name() + ', '
                if len(rbr_text) > 0:
                    rbr_text = rbr_text[:-2]
            hotel_ans.append({'question': '', 'answer': rbr_text})

        if booking:
            if 'rba-col' in hotels or 'rba-checkin-col' in hotels or 'rba-checkout-col' in hotels:
                match_ids = MatchLine.objects.filter(booking_id=booking.id).values('match_id')
                other_bookings = MatchLine.objects.filter(match_id__in=match_ids).exclude(booking_id=booking.id)
                actual_bud_counter = 0
                for other_booking in other_bookings:
                    actual_bud_counter += 1
                    if 'rba-col' in hotels:
                        hotel_ans.append({'question': '', 'answer': other_booking.booking.attendee.get_full_name()})
                    if 'rba-checkin-col' in hotels:
                        check_in = HelperData.utc_to_local(request, str(datetime.strftime(other_booking.booking.check_in, "%Y-%m-%d %H:%M:%S")))
                        check_in = HelperData.get_formated_date_string(check_in, request.session['language_id'])
                        hotel_ans.append({'question': '', 'answer': check_in})
                    if 'rba-checkout-col' in hotels:
                        check_out = HelperData.utc_to_local(request, str(datetime.strftime(other_booking.booking.check_out, "%Y-%m-%d %H:%M:%S")))
                        check_out = HelperData.get_formated_date_string(check_out, request.session['language_id'])
                        hotel_ans.append({'question': '', 'answer': check_out})
                if max_actual_room_buddy > actual_bud_counter:
                    max_actual_room_buddy -= actual_bud_counter
                    for i in range(0, max_actual_room_buddy):
                        if 'rba-col' in hotels:
                            hotel_ans.append({'question': '', 'answer': ''})
                        if 'rba-checkin-col' in hotels:
                            hotel_ans.append({'question': '', 'answer': ''})
                        if 'rba-checkout-col' in hotels:
                            hotel_ans.append({'question': '', 'answer': ''})
        else:
            for i in range(0, max_actual_room_buddy):
                if 'rba-col' in hotels:
                    hotel_ans.append({'question': '', 'answer': ''})
                if 'rba-checkin-col' in hotels:
                    hotel_ans.append({'question': '', 'answer': ''})
                if 'rba-checkout-col' in hotels:
                    hotel_ans.append({'question': '', 'answer': ''})
        return hotel_ans

    def get_attendee_answer(attendees, order_owner_id):
        attendee_data = {}
        try:
            atd = []
            atd.append(order_owner_id)
            attendee_data[str(order_owner_id)] = {}
            attendee_data[str(order_owner_id)]["answers"] = {}
            for attendee in attendees:
                atd.append(attendee["id"])
                attendee_data[str(attendee["id"])] = {}
                attendee_data[str(attendee["id"])]["answers"] = {}
            answers = Answers.objects.filter(user_id__in=atd)
            for answer in answers:
                ans = {}
                ans["answer"] = answer.value
                ans["id"] = answer.question_id
                if answer.user_id == order_owner_id:
                    attendee_data[str(answer.user_id)]["answers"][answer.question_id] = ans
                else:
                    attendee_data[str(answer.user_id)]["answers"][answer.question_id] = ans
        except Exception as e:
            ErrorR.efail(e)
        return attendee_data

    def export_attendee_old(request, *args, **kwargs):
        if request.method == "GET":
            session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                   region_name='eu-west-1')
            client = session.client('s3')
            key = 'exported_files/plugin_attendees/attendee.xlsx'
            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
            f = response['Body'].read()
            response = HttpResponse(f, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=attendee.xlsx'
            return response

        elif request.method == "POST":
            filter_id = request.POST.get('filter_id')
            columns = request.POST.get('columns')
            columns = json.loads(columns)
            if len(columns) < 1:
                response = {'result': False, 'message': 'no column'}
                return HttpResponse(json.dumps(response), content_type='application/json')

            attendees = AttendeePluginList.get_all_attendee(request, filter_id)
            attendee_data = AttendeePluginList.get_attendee_data(attendees, columns)

            export_data = []
            questions = [Questions.objects.get(id=qus_id) for qus_id in columns]
            header_column = [qus.actual_definition.replace(' ','_') if qus.actual_definition else qus.title.replace(' ','_') for qus in questions]
            header_title = [qus.title for qus in questions]
            export_data.append(header_title)
            for data in attendee_data:
                row = []
                for head in header_column:
                    try:
                        row.append(data[head])
                    except:
                        row.append('')
                export_data.append(row)

            # print(export_data)
            export_data = {
                'data': export_data,
                'file_name': 'exported_files/plugin_attendees/attendee.xlsx'
            }
            # S3 Strat
            AttendeePluginList.upload_data_to_s3(export_data)
            # END S3
            message = LanguageKey.catch_lang_key(request, 'attendee-list', 'attendee_list_notify_download_processing')
            response = {
                'result': True,
                'message': message
            }
            return HttpResponse(json.dumps(response), content_type='application/json')

    def export_attendee(request, *args, **kwargs):
        if request.method == "GET":
            event_id = request.session['event_id']
            event = Events.objects.get(id=event_id)
            session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                   region_name='eu-west-1')
            client = session.client('s3')
            # key = 'exported_files/plugin_attendees/attendee.xlsx'
            key = 'exported_files/' + event.name + '/attendee.xlsx'
            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
            f = response['Body'].read()
            response = HttpResponse(f, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=attendee.xlsx'
            return response

        elif request.method == "POST":
            from app.views.gbhelper.export_library import ExportLibrary
            response = {
                'result': False,
                'message': 'something went wrong!'
            }
            attendee_export_id = request.POST.get('attendee_export_id')
            if attendee_export_id:
                rule = ExportRule.objects.get(id=attendee_export_id)
                event_id = request.session['event_id']
                data = json.loads(rule.preset)
                export_filter_name = rule.name
                qlist = data['questions'].split(',')
                slist = data['sessions'].split(',')
                hotel_columns = None
                economy_columns = None
                include_import_header = data.get('include_import_header')
                if 'hotel_columns' in data:
                    hotel_columns = data.get('hotel_columns')
                if 'economy_columns' in data:
                    economy_columns = data.get('economy_columns')
                if len(data['questions']) < 1:
                    qlist = []
                if len(data['sessions']) < 1:
                    slist = []

                attendees = AttendeePluginList.get_all_attendee(request, data['rule_id'])
                export_result = ExportLibrary.prepare_export_data_s3_upload('attendee', qlist, slist, data['uid'], data['rdate'],
                                                                            data['udate'], data['secret'], data.get('bid'), data['attGroup'],
                                                                            data['attTag'], data['flight'], hotel_columns, attendees, economy_columns,
                                                                            include_import_header, event_id)
                if export_result['success']:
                    response['result'] = True
                    response['message'] = LanguageKey.catch_lang_key(request, 'attendee-list', 'attendee_list_notify_download_processing')
                    response['public_checker'] = export_result['public_checker']

            return HttpResponse(json.dumps(response), content_type='application/json')

    def attendee_plugin_export_state(request, *args, **kwargs):
        public_checker = request.POST.get('public_checker')
        event_id = request.session['event_id']
        event = Events.objects.get(id=event_id)
        file_name = 'exported_files/' + event.name + '/attendee_' + public_checker + '.xlsx'
        response_data = {}
        # response_data['msg'] = []
        response_data['next_ajax_req'] = False
        session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                   region_name='eu-west-1')
        client = session.client('s3')
        # for each_file in export_state:
        # exported_files/GT - Revision/attendee_1514288345.7731862.xlsx
        key = file_name
        try:
            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
            # print(response)
            if response:
                conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
                bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                newKey = 'exported_files/' + event.name + '/attendee.xlsx'
                bucket.copy_key(newKey, settings.AWS_STORAGE_BUCKET_NAME, key)
                newKey_bucket_file = Key(bucket)
                newKey_bucket_file.key = newKey
                newKey_bucket_file.make_public()
                bucket.delete_key(key)
                # filename_arr = key.split('/')
                # if len(filename_arr) > 2:
                #     filename_key = filename_arr[2]
                # else:
                #     filename_key = filename_arr[1]
                # msg = [{'filename': key,
                #         'message': " Your exported list " + filename_key + " is ready, check in Download Exported list Menu. <a href='" + reverse(
                #             'downloadExportedFile') + "?export=" + key + "'>Click </a> to download."}]
                # response_data['msg'].extend(msg)
                # each_file.status = 1
                # each_file.save()
            else:
                response_data['next_ajax_req'] = True
        except:
            # msg = [{'filename' : key, 'message': " Your exported list "+key.split('/')[2]+" is ready, check in Download Exported list Menu. "}]
            # response_data['msg'].extend(msg)
            response_data['next_ajax_req'] = True

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def upload_data_to_s3(export_data):
        data_json = json.dumps(export_data)
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        filename_with_path = 'export_attendee_plugin/data.txt'
        key_name = filename_with_path
        k = Key(bucket)
        k.key = key_name
        if not k.exists():
            key = bucket.new_key(key_name)
            key.set_contents_from_string(data_json)
            key.set_metadata('Content-Type', 'text/plain')
            key.set_acl('public-read')
            key.make_public()
        else:
            k.set_contents_from_string(data_json)
            k.set_metadata('Content-Type', 'text/plain')
            k.set_acl('public-read')
            k.make_public()
        return
