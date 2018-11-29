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


from django.db import transaction
from app.views.gbhelper.error_report_helper import ErrorR
import json, re, os
from datetime import date, datetime, timedelta
import mysql.connector
from openpyxl import load_workbook


class LambdaUpload:
    new_attendee_email_list = dict(emails=[], attendee_id=[], attendees_detail=[])
    deciding_attendees = dict(ids=[], detail=[])

    def lambda_upload(request, filename):

        LambdaUpload.handle_uploaded_file(request.FILES.get('upload_file'), 'sample_import.xlsx')
        wb = load_workbook(filename='attendeeList/sample_import.xlsx', read_only=True)
        ws = wb.worksheets[0]  # ws is now an IterableWorksheet

        response_data2 = []
        global_new_att_flag = False
        header_row = []
        change_status_filename = filename

        from wsitEvent.local_settings import DATABASES as local_db
        config = {
            'user': local_db['default']['USER'],
            'password': local_db['default']['PASSWORD'],
            'host': local_db['default']['HOST'],
            'database': local_db['default']['NAME'],
            'raise_on_warnings': True,
            'use_pure': False,
        }

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        admin_id = request.session['event_auth_user']['id']
        event_id = request.session['event_auth_user']['event_id']
        new_attendee_counter = -1  # this counter will decrease to track as new attendee
        item_row = 0
        error_flag = False
        message = []

        header_errors = []
        ignored_header_list = ['att-rdate', 'att-udate', 'att-secret', 'att-bid', 'h-match_id', 'h-hotel_name', 'h-description', 'h-beds', 'h-location_id', 'h-rba_checkin', 'h-rba_checkout']
        for HEADer_ROW in ws.rows:
            for HEADer_ROW_item in HEADer_ROW:
                HEADer_ROW_item_value = HEADer_ROW_item.value.strip()
                if HEADer_ROW_item_value not in ignored_header_list:
                    splitted_header = HEADer_ROW_item_value.split('-')
                    if splitted_header[0] == 'att':
                        available_general_header = ['uid', 'group', 'tag']
                        if splitted_header[1] not in available_general_header:
                            actual_available_general_header = ["att-" + item for item in available_general_header]
                            header_errors.append(dict(incorrect_header=HEADer_ROW_item_value, available_headers=', '.join(actual_available_general_header), message=''))
                    elif splitted_header[0] == 'q':
                        if not splitted_header[1].isdigit():
                            header_errors.append(dict(incorrect_header=HEADer_ROW_item_value, available_headers="q-{question_id}", message="Question id must be integer"))
                    elif splitted_header[0] == 'session':
                        if not splitted_header[1].isdigit():
                            header_errors.append(dict(incorrect_header=HEADer_ROW_item_value, available_headers="session-{session_id}", message="Session id must be integer"))
                    elif splitted_header[0] == 'h':
                        available_hotel_header = ['booking_id', 'hotel_id', 'check_in', 'check_out', 'rbr', 'rba']
                        if splitted_header[1] not in available_hotel_header:
                            actual_available_hotel_header = ["h-" + item for item in available_hotel_header]
                            header_errors.append(dict(incorrect_header=HEADer_ROW_item_value, available_headers=', '.join(actual_available_hotel_header), message=''))
                    else:
                        header_errors.append(dict(incorrect_header=HEADer_ROW_item_value, available_headers="", message='wrong header name provided'))
            break

        if header_errors:
            insert_query = "INSERT INTO import_change_request(event_id, changed_data, imported_by_id, status, created_at) VALUES(%(event_id)s, %(changed_data)s, %(imported_by_id)s, %(status)s, %(created_at)s)"
            insert_data = {
                'event_id': event_id,
                'changed_data': json.dumps(response_data2),
                'imported_by_id': admin_id,
                'status': 1,
                'created_at': datetime.now(),
            }
            cursor.execute(insert_query, insert_data)
            cnx.commit()
            last_import_id = cursor.lastrowid  # it will return last inserted row id

            update_query = "UPDATE import_change_status SET status=6, import_change_id={0}, message=%(message)s WHERE filename=%(file_name)s".format(last_import_id)
            update_data = {
                'message': json.dumps(header_errors),
                'file_name': change_status_filename
            }
            cursor.execute(update_query, update_data)
            cnx.commit()
            return

        # no incorrect header found
        for row in ws.rows:
            generals = []
            answers = []
            travels = []
            sessions = []
            hotels = []
            previous_hotel_field_name = ''
            only_answers = []
            att_only_answers = []

            if item_row < 2:
                if row[0].value == "booking":
                    # from app.views.export_import_view import HotelImport
                    # return HotelImport.dynamic_hotel_import(request, ws.rows)
                    return HotelLamda.hotel_import(request, ws.rows, filename, cursor, cnx)
                if item_row == 0:
                    for item in row:
                        if item.value is not None:
                            item_val = item.value.split('-')
                            header_row.append(item_val)
                item_row += 1
                continue
            item_row += 1

            general_history = []
            question_history = []
            session_history = []
            travel_history = []
            hotel_history = []
            try:
                att = None
                attendee_full_name = ""
                exception_identifier = ""
                if header_row[0][1] == "uid":
                    attendee_id = row[0].value
                    exception_identifier = str(attendee_id)
                    select_query = ("SELECT secret_key,firstname,lastname,email,phonenumber,created,updated, id FROM attendees WHERE id = " + str(attendee_id))
                    cursor.execute(select_query)
                    for result in cursor:
                        att = result
                        attendee_full_name = "{} {}".format(result[1], result[2])
                else:
                    email_index = LambdaUpload.get_email_index(header_row, cursor)
                    if email_index != -1:
                        email_value = row[email_index].value.strip()
                        att = LambdaUpload.get_attendee_by_email(email_value, cursor, event_id)
                        if att:
                            attendee_id = int(att[7])
                            attendee_full_name = "{} {}".format(att[1], att[2])
                        else:
                            flag_for_new_att = True
                            new_attendee, attendee_full_name = LambdaUpload.add_new_attendee(header_row, row, event_id, cursor)
                            for validation in new_attendee["validation"]:
                                if validation["valid"] == False:
                                    message.append(
                                        [{'name': validation["question"], 'type': 'New Attendee',
                                          'attendee': row[email_index].value,
                                          'reason': validation["reason"]}])
                                    flag_for_new_att = False
                                    global_new_att_flag = True
                                    error_flag = True

                            if flag_for_new_att:
                                response_data2.append({"Attendee": new_attendee_counter, "name": attendee_full_name, "data": new_attendee["data"]})
                                if email_value in LambdaUpload.new_attendee_email_list['emails']:
                                    index_of_duplicate_email = LambdaUpload.new_attendee_email_list['emails'].index(email_value)
                                    first_email_attendee_id = LambdaUpload.new_attendee_email_list['attendee_id'][index_of_duplicate_email]
                                    if first_email_attendee_id not in LambdaUpload.deciding_attendees['ids']:
                                        LambdaUpload.deciding_attendees['ids'].append(first_email_attendee_id)
                                        LambdaUpload.deciding_attendees['detail'].append(LambdaUpload.new_attendee_email_list['attendees_detail'][index_of_duplicate_email])
                                    LambdaUpload.deciding_attendees['ids'].append(new_attendee_counter)
                                    LambdaUpload.deciding_attendees['detail'].append(dict(id=new_attendee_counter, name=attendee_full_name, email=email_value))

                                LambdaUpload.new_attendee_email_list['emails'].append(email_value)
                                LambdaUpload.new_attendee_email_list['attendee_id'].append(new_attendee_counter)
                                LambdaUpload.new_attendee_email_list['attendees_detail'].append(dict(id=new_attendee_counter, name=attendee_full_name, email=email_value))
                                new_attendee_counter -= 1
                            continue
                    exception_identifier = " row " + str(item_row)
                # print ("att")
                # print (att)
                if not att:
                    continue

                content_serial = 0
                for item in row:

                    if len(header_row) <= content_serial:
                        content_serial += 1
                        continue

                    # print(content_serial)

                    if header_row[content_serial][0] == "att" and header_row[content_serial][1] not in ["uid", "bid", "rdate", "udate"]:
                        generals.extend([{"question_id": header_row[content_serial][1], "answer": item.value, "a_type": 'text'}])

                    elif header_row[content_serial][0] == "q":
                        answers.extend(
                            [{"question_id": header_row[content_serial][1], "answer": item.value, "a_type": 'text'}])
                        if item.value:
                            only_answers.append(str(item.value))
                            # print (item.value)

                            # att_only_answer = Answers.objects.filter(user_id=attendee_id,
                            #                                          question_id=header_row[content_serial][1]).first()
                            att_only_answer = None
                            select_query = ("SELECT value FROM answers WHERE user_id = " + str(attendee_id) +
                                            " AND question_id = " + str(header_row[content_serial][1]) )
                            cursor.execute(select_query)
                            for result in cursor:
                                att_only_answer = result

                            if att_only_answer:
                                # att_only_answers.append(att_only_answer.value)

                                att_only_answers.append(att_only_answer[0])
                            else:
                                att_only_answers.append('')

                    elif header_row[content_serial][0] == "travel":
                        if str.lower(str(item.value)) == "attending" or str.lower(
                                str(item.value)) == "not-attending" or str.lower(
                                str(item.value)) == "in-queue" or str.lower(str(item.value)) == "deciding":
                            travels.extend(
                                [{"travel_id": header_row[content_serial][1], "status": str.lower(item.value)}])

                    elif header_row[content_serial][0].lower() == "session":
                        # print("session found")
                        if str.lower(str(item.value)) == "attending" or str.lower(
                                str(item.value)) == "not-attending" or str.lower(
                                str(item.value)) == "in-queue" or str.lower(str(item.value)) == "deciding":
                            sessions.extend(
                                [{"session_id": header_row[content_serial][1], "status": str.lower(item.value)}])
                    elif header_row[content_serial][0].lower() == 'h' and header_row[content_serial][1] in \
                            ['booking_id', 'match_id', 'hotel_id', 'check_in', 'check_out', 'rbr', 'rba']:
                        data_inserted = False
                        field_name = header_row[content_serial][1]
                        for hotel_booking in hotels:
                            # checking all bookings, where field_name(column) has no value
                            if not hotel_booking[field_name]:
                                hotel_booking[field_name] = item.value if item.value else ''
                                data_inserted = True
                                previous_hotel_field_name = field_name
                                break
                            elif previous_hotel_field_name == 'rba' and previous_hotel_field_name == field_name:
                                # this block for actual buddy column, where one booking can have multiple actual buddy columns
                                hotel_booking[field_name] += ',' + item.value if item.value else ''
                                data_inserted = True
                                previous_hotel_field_name = field_name
                                break

                        if not data_inserted:
                            att_single_booking_data = dict(att=attendee_id, booking_id=None, match_id=None, hotel_id=None, check_in=None, check_out=None, rbr=None, rba=None)
                            att_single_booking_data[field_name] = item.value
                            hotels.append(att_single_booking_data)

                    content_serial += 1

                if att:
                    for general in generals:
                        if general['answer'] or general['question_id'] == "tag" or general['question_id'] == "group":
                            test_general = LambdaUpload.testGeneral( att, str(general['answer']), str(general['question_id'].strip()), cursor)
                            if test_general['valid'] == False:
                                message.append([{'name': test_general['question'], 'type': 'General',
                                                 'attendee': attendee_id, 'reason': test_general['reason']}])
                                error_flag = True
                            else:
                                general_history = LambdaUpload.generalHistory(att, general_history, general, attendee_id, cursor)
                    for answer in answers:
                        # if answer['answer']:
                        # question = Questions.objects.filter(id=answer['question_id'])
                        question = None
                        select_query = ("SELECT * FROM questions WHERE id = " + str(answer['question_id']) )
                        cursor.execute(select_query)
                        for result in cursor:
                            question = result
                        # if (question.exists()): changed after raw query
                        if question:
                            test_question = LambdaUpload.testQuestion(answer['answer'],
                                                                   int(answer['question_id']), cursor)

                            if test_question['valid'] == False:
                                message.append([{'name': test_question['question'], 'type': 'Question',
                                                 'attendee': attendee_id, 'reason': test_question['reason']}])
                                error_flag = True
                            else:
                                question_history = LambdaUpload.question_history(question_history, answer, attendee_id, cursor)
                    for travel in travels:
                        if travel['travel_id']:
                            travel_existance = None
                            select_query = ("SELECT * FROM travels WHERE id = " + str(travel['travel_id']))
                            cursor.execute(select_query)
                            for result in cursor:
                                travel_existance = result
                            if travel_existance:
                                travel_history = LambdaUpload.travel_history(travel_history, travel, attendee_id, cursor)

                    # print(sessions)
                    for ssn in sessions:
                        if ssn['session_id']:
                            session_existance = None
                            select_query = ("SELECT name,max_attendees,allow_overlapping,start,end,allow_attendees_queue "
                                            " FROM sessions WHERE id = " + str(ssn['session_id']))
                            # session column index
                            # name -> 0, max_attendees -> 1, allow_overlapping -> 2, start -> 3, end -> 4, allow_attendees_queue -> 5,
                            cursor.execute(select_query)
                            for result in cursor:
                                session_existance = result
                            if session_existance:
                                test_session = LambdaUpload.testSession(attendee_id, int(ssn['session_id']), session_existance, cursor)
                                # print("test session result")
                                # print(test_session)
                                if test_session['valid'] == False:
                                    message.append([{'name': test_session['session'], 'type': 'Session',
                                                     'attendee': attendee_id, 'reason': test_session['reason']}])
                                    error_flag = True
                                else:
                                    session_history = LambdaUpload.session_history(session_history, ssn, attendee_id, cursor)

                    print('**********hotel data**********')
                    print(hotels)
                    for single_booking in hotels:
                        booking_result = LambdaUpload.handle_single_booking(single_booking, event_id, cursor)
                        if not booking_result['valid']:
                            message.extend(booking_result['err_messages'])
                            error_flag = True
                        else:
                            if len(booking_result['result']['new_data']['sqls']) > 0:
                                hotel_history.append(booking_result['result'])

                    changed_data = {}
                    if len(general_history) > 0:
                        changed_data['generals'] = general_history
                    if len(question_history) > 0:
                        changed_data['questions'] = question_history
                    if len(session_history) > 0:
                        changed_data['sessions'] = session_history
                    if len(travel_history) > 0:
                        changed_data['travels'] = travel_history
                    if len(hotel_history) > 0:
                        changed_data['hotels'] = hotel_history
                    if len(changed_data) > 0:
                        response_data2.append({"Attendee": attendee_id, "name": attendee_full_name, 'data': changed_data})

            except Exception as e:
                ErrorR.efail(e)
                response_data2.append({"Attendee": "Error!!! =" + str(e)})
                message.append([{'question': '', 'attendee': exception_identifier, 'reason': "Error!!! =" + str(e)}])
                error_flag = True

        context = {
            'errors': message
        }
        # print (response_data2)
        if len(response_data2) > 0 or global_new_att_flag:
            if not error_flag:
                # icr = ImportChangeRequest(event_id=event_id, changed_data=json.dumps(response_data2),
                #                           imported_by_id=admin_id, status=1, created_at=datetime.now())
                # icr.save()
                # print ('no exception')
                insert_query = ("INSERT INTO import_change_request "
                                "(event_id, changed_data, imported_by_id, status, created_at) "
                                "VALUES (%(event_id)s, %(changed_data)s, %(imported_by_id)s, %(status)s, %(created_at)s)")
                insert_data = {
                    'event_id': event_id,
                    'changed_data': json.dumps(response_data2),
                    'imported_by_id': admin_id,
                    'status': 1,
                    'created_at': datetime.now(),
                }
                cursor.execute(insert_query, insert_data)
                cnx.commit()

                last_import_id = cursor.lastrowid

                context = {
                    'success': "Success"
                }

                update_query = ("UPDATE import_change_status SET status = 1, import_change_id= " + str(
                    last_import_id) + " , duplicate_attendees= %(dup_atts)s WHERE filename = '" + change_status_filename + "'")
                update_data = dict(dup_atts=json.dumps(LambdaUpload.deciding_attendees['detail']))
                cursor.execute(update_query, update_data)
                cnx.commit()
            else:
                insert_query = ("INSERT INTO import_change_request "
                                "(event_id, changed_data, imported_by_id, status, created_at) "
                                "VALUES (%(event_id)s, %(changed_data)s, %(imported_by_id)s, %(status)s, %(created_at)s)")
                insert_data = {
                    'event_id': event_id,
                    'changed_data': json.dumps(response_data2),
                    'imported_by_id': admin_id,
                    'status': 1,
                    'created_at': datetime.now(),
                }

                cursor.execute(insert_query, insert_data)
                cnx.commit()

                last_import_id = cursor.lastrowid  # it will return last inserted row id

                update_query = ("UPDATE import_change_status SET status = 2, import_change_id= " + str(
                    last_import_id) + " , message = %(message)s, duplicate_attendees= %(dup_atts)s WHERE filename = '" + change_status_filename + "'")
                update_data = dict(message=json.dumps(message), dup_atts=json.dumps(LambdaUpload.deciding_attendees['detail']))
                cursor.execute(update_query, update_data)
                cnx.commit()
        else:
            update_query = ("UPDATE import_change_status SET status = 3 WHERE filename = '" + change_status_filename + "'")
            cursor.execute(update_query)
            cnx.commit()
            context['success'] = "Not found any importing changes"

        cursor.close()
        cnx.close()

        return

    def handle_uploaded_file(f, filename):
        import os

        if not os.path.exists("attendeeList/"):
            os.makedirs("attendeeList/")
        filepath = 'attendeeList/'
        with open(filepath + filename, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def get_email_index(rows, cursor):
        index = -1
        for row in rows:
            index += 1
            if row:
                if row[0] == "q":
                    actual_def = None
                    select_query = ("SELECT actual_definition FROM questions WHERE id = " + str(row[1]))
                    cursor.execute(select_query)
                    for result in cursor:
                        actual_def = result
                    if actual_def[0] == "email":
                        return index
        return -1

    def get_attendee_by_email(email, cursor, event_id):
        att = None
        select_query = ("SELECT secret_key,firstname,lastname,email,phonenumber,created,updated,id FROM attendees WHERE email = '{1}' and event_id={0}".format(event_id,email))
        cursor.execute(select_query)
        for result in cursor:
            att = result
        return att

    def testGeneral( att, value, question_id, cursor):
        response_data = {}
        if question_id == "rdate":
            if len(value) > 0:
                try:
                    datetime.strptime(value.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    response_data['valid'] = True
                except Exception:
                    response_data['question'] = "Registration"
                    response_data['valid'] = False
                    response_data['reason'] = "Registration date is't correct format, the format should be %Y-%m-%dT%H:%M:%S"
            else:
                response_data['valid'] = False
                response_data['question'] = "Registration"
                response_data['reason'] = "Registration date can't be empty"
        elif question_id == "udate":
            if len(value) > 0:
                try:
                    datetime.strptime(value.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                    response_data['valid'] = True
                except Exception:
                    response_data['question'] = "Updated"
                    response_data['valid'] = False
                    response_data[
                        'reason'] = "Updated date is't correct format, the format should be %Y-%m-%dT%H:%M:%S"
            else:
                response_data['question'] = "Updated"
                response_data['valid'] = False
                response_data['reason'] = "Updated date can't be empty"
        elif question_id == "tag":
            response_data['valid'] = True
        elif question_id == "group":
            response_data['valid'] = True
        elif question_id == "secret":
            if att[0] == value:
                response_data['valid'] = True
            else:
                response_data['question'] = "Secret"
                response_data['valid'] = False
                response_data['reason'] = "Secret Key can't be changed or empty"
        return response_data

    def testQuestion(value, question_id, cursor):
        # question = Questions.objects.get(id=question_id)
        question = None
        select_query = ("SELECT title, type, actual_definition, required FROM questions WHERE id = " + str(question_id))
        # question data index ---> title --> 0   type --> 1   actual_definition --> 2
        cursor.execute(select_query)
        for result in cursor:
            question = result

        response_data = {}
        response_data['question'] = question[0]
        if question:
            if question[1] == 'text':
                if int(question[3]) == 1:
                    if value == None or value == "":
                        response_data['valid'] = False
                        response_data['reason'] = str(question[0]) + " can't be empty"
                    else:
                        response_data['valid'] = True
                    if question[2] == 'email':
                        if LambdaUpload.validateEmail(value) == 0:
                            response_data['valid'] = False
                            response_data['reason'] = "Email is not in the Correct Format"
                else:
                    response_data['valid'] = True
            elif question[1] == 'radio_button' or question[1] == 'select' or question[1] == 'checkbox':
                if value and value != '':
                    # options = Option.objects.filter(question_id=question_id)
                    options = []
                    select_query = ("SELECT options.option FROM options WHERE question_id = " + str(question_id))
                    cursor.execute(select_query)
                    for result in cursor:
                        options.append(result)

                    found = True
                    option_list = [opt[0] for opt in options]
                    values = [val.strip() for val in value.split(',')]
                    option_str = ','.join(option_list)
                    for val in values:
                        if val not in option_list:
                            found = False

                    if found:
                        response_data['valid'] = True
                    else:
                        response_data['valid'] = False
                        response_data['reason'] = str(
                            question[0]) + "'s value is not valid. options are " + option_str
                        response_data['options'] = "options are " + option_str
                else:
                    response_data['valid'] = True

            else:
                response_data['valid'] = True

        return response_data

    def validateEmail(email):

        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{1,3}|[0-9]{1,3})(\\]?)$", email) != None:
                return 1
        return 0

    def generalHistory(att, general_history, general, userId, cursor):
        general_answer_info = {}
        question = str(general['question_id'].strip())
        answer = general['answer']
        if question == "tag":
            general_answer_info["old_data"] = ""
            general_answer_info["new_data"] = answer

            new_tags = []
            if answer and answer != 'None':
                new_tags = answer.split(',')

            select_query = ( "SELECT tags.name FROM tags left join attendee_tags "
                             "on tags.id = attendee_tags.tag_id "
                             "where attendee_tags.attendee_id = " + str(userId))
            cursor.execute(select_query)
            old_tags = []
            for result in cursor:
                old_tags.append(result[0])
                general_answer_info["old_data"] = general_answer_info["old_data"] + result[0] + ","
            general_answer_info["old_data"] = (general_answer_info["old_data"])[:-1]
            flag = False
            if len(old_tags) != len(new_tags):
                flag = True
            for tag in new_tags:
                if tag not in old_tags and tag != "None":
                    flag = True
                    break
            if flag:
                general_answer_info['id'] = question
                general_answer_info['name'] = "Tag"
                general_history.append(general_answer_info)

        elif question == "group":
            general_answer_info["old_data"] = ""
            general_answer_info["new_data"] = answer
            new_groups = []
            if answer:
                new_groups = answer.split(',')
            select_query = ("SELECT groups.name FROM groups left join attendee_groups "
                            "on groups.id = attendee_groups.group_id "
                            "where attendee_groups.attendee_id = " + str(userId))
            cursor.execute(select_query)
            old_groups = []
            for result in cursor:
                old_groups.append(result[0])
                general_answer_info["old_data"] = general_answer_info["old_data"] + result[0] + ","
            general_answer_info["old_data"] = (general_answer_info["old_data"])[:-1]
            flag = False
            if len(old_groups) != len(new_groups):
                flag = True
            for group in new_groups:
                if group not in old_groups and group != "None":
                    flag = True
                    break
            if flag:
                general_answer_info['id'] = question
                general_answer_info['name'] = "Group"
                general_history.append(general_answer_info)

        return general_history

    def question_history(question_history, new_question_answer, userId, cursor):
        question_answer_info = {}
        x_answer = None
        select_query = ( "SELECT answers.value, questions.title, questions.type FROM answers"
                         " JOIN questions ON answers.question_id = questions.id "
                         "WHERE answers.user_id = "+ str(userId) +" AND questions.id = " + str(new_question_answer['question_id']) )

        # data index ---->   answers.value --> 0, questions.title --> 1

        cursor.execute(select_query)
        for result in cursor:
            x_answer = result

        if x_answer:
            checkbox = True if x_answer[2] == 'checkbox' else False
            old_value = str(x_answer[0])
            new_value = str(new_question_answer['answer']).strip()
            if checkbox:
                old_value = str(x_answer[0]).strip().replace('<br>', ',')
                new_value = ','.join([val.strip() for val in new_question_answer['answer'].split(',')])

            question_answer_info['old_data'] = old_value
            if type(new_question_answer['answer']) is datetime.time:
                question_answer_info['new_data'] = new_value
            else:
                question_answer_info['new_data'] = new_value

            # if question_answer_info['old_data'] != question_answer_info['new_data']:
            if old_value != new_value:
                question_answer_info['id'] = new_question_answer['question_id']
                question_answer_info['name'] = x_answer[1].strip() # x_answer[1] is question title
                question_history.append(question_answer_info)

        else:
            if new_question_answer['answer']:
                if type(new_question_answer['answer']) is datetime.time:
                    question_answer_info['new_data'] = str(new_question_answer['answer'])
                else:
                    question_answer_info['new_data'] = str(new_question_answer['answer']).strip()
                question_answer_info['id'] = new_question_answer['question_id']
                question_answer_info['old_data'] = "Old Data Not Found"
                # question = Questions.objects.get(pk=new_question_answer['question_id'])
                question = None
                select_query = ("SELECT title FROM questions WHERE id = " + str(new_question_answer['question_id']))
                cursor.execute(select_query)
                for result in cursor:
                    question = result

                question_answer_info['name'] = question[0].strip()
                question_history.append(question_answer_info)
        return question_history

    def add_new_attendee(header, row, event_id, cursor):
        validation = []
        att_info = {}
        data = {}
        questions = []
        generals = []
        sessions = []
        travels = []
        hotels = []
        hotel_bookings = []
        previous_hotel_field_name = ''
        index = 0
        flag_for_firstname = False
        flag_for_lastname = False
        attendee_first_name = ""
        attendee_last_name = ""

        for item in header:
            validation_info = {}
            validation_info["valid"] = True
            if header[index][0] == "att":
                if header[index][1] == "tag" and row[index].value:
                    generals.append({"new_data":row[index].value, "old_data":"", "name": "Tag", "id" : "tag"})
                elif header[index][1] == "group" and row[index].value:
                    generals.append({"new_data":row[index].value, "old_data":"", "name": "Group", "id" : "group"})
            elif header[index][0] == "q":
                question = None
                select_query = ("SELECT title, required, actual_definition FROM questions WHERE id = " + str(header[index][1]))
                cursor.execute(select_query)
                for result in cursor:
                    question = result

                if question[2] == 'firstname':
                    flag_for_firstname = True
                    attendee_first_name = row[index].value
                if question[2] == 'lastname':
                    flag_for_lastname = True
                    attendee_last_name = row[index].value

                if (question[2] == 'email' or question[2] == 'firstname' or question[2] == 'lastname') and row[index].value == None:
                    validation_info["valid"] = False
                    validation_info["question"] = question[0]
                    validation_info["reason"] = "Can't be empty"
                validation.append(validation_info)
                if row[index].value:
                    questions.append({"new_data":row[index].value, "old_data":"", "name": question[0],
                                  "id" : header[index][1], "defination": question[2]})
            elif header[index][0] == "session" and row[index].value:
                session = None
                select_query = ("SELECT name FROM sessions WHERE id = " + str(header[index][1]))
                cursor.execute(select_query)
                for result in cursor:
                    session = result
                sessions.append({"new_data":row[index].value, "old_data":"", "name": session[0], "id" : header[index][1]})
            elif header[index][0] == "travel" and row[index].value:
                travel = None
                select_query = ("SELECT name FROM travels WHERE id = " + str(header[index][1]))
                cursor.execute(select_query)
                for result in cursor:
                    travel = result
                travels.append(
                    {"new_data": row[index].value, "old_data": "", "name": travel[0], "id": header[index][1]})
            elif header[index][0] == 'h' and header[index][1] in ['hotel_id', 'check_in', 'check_out', 'rbr', 'rba']:
                data_inserted = False
                field_name = header[index][1]
                for hotel_booking in hotels:
                    # checking all bookings, where field_name(column) has no value
                    if not hotel_booking[field_name]:
                        hotel_booking[field_name] = row[index].value if row[index].value else ''
                        data_inserted = True
                        previous_hotel_field_name = field_name
                        break
                    elif previous_hotel_field_name == 'rba' and previous_hotel_field_name == field_name:
                        # this block for actual buddy column, where one booking can have multiple actual buddy columns
                        hotel_booking[field_name] += ',' + row[index].value if row[index].value else ''
                        data_inserted = True
                        previous_hotel_field_name = field_name
                        break

                if not data_inserted:
                    att_single_booking_data = dict(hotel_id=None, check_in=None, check_out=None, rbr=None, rba=None)
                    att_single_booking_data[field_name] = row[index].value
                    hotels.append(att_single_booking_data)

            index += 1

        if not flag_for_firstname:
            validation_info = {}
            validation_info["valid"] = False
            validation_info["question"] = "Firstname"
            validation_info["reason"] = "firstname field is absent in imported file"
            validation.append(validation_info)
        if not flag_for_lastname:
            validation_info = {}
            validation_info["valid"] = False
            validation_info["question"] = "Lastname"
            validation_info["reason"] = "lastname field is absent in imported file"
            validation.append(validation_info)

        data["generals"] = generals
        data["questions"] = questions
        data["sessions"] = sessions
        data["travels"] = travels
        if hotels:
            hotel_sql = []
            hotel_view = []
            insert_data_flag = False
            for hotel_item in hotels:
                room_id = hotel_item['hotel_id']
                check_in = hotel_item['check_in']
                check_out = hotel_item['check_out']
                if check_in and check_out and room_id:
                    hotel_info_check = LambdaUpload.verify_hotel_information(room_id, check_in, check_out, cursor)
                    if not hotel_info_check['valid']:
                        validation_info["valid"] = False
                        validation_info["reason"] = hotel_info_check['message']
                    else:
                        if LambdaUpload.check_booking_availability(room_id, check_in, check_out, cursor):
                            hotel_sql.append(dict(action='insert', table='bookings', data=dict(room_id=room_id, check_in=check_in, check_out=check_out)))
                            hotel_view.append("<b>check-in:</b> {}, <b>check-out:</b> {}, <b>Hotel:</b> {}".format(check_in, check_out, room_id))
                            insert_data_flag = True

                booking_rbr = hotel_item['rbr']
                if booking_rbr and insert_data_flag:
                    booking_rbr = booking_rbr.split(',')
                    for rbr_item in booking_rbr:
                        cursor.execute("SELECT id FROM attendees WHERE email='{}' AND status='registered' AND event_id={}".format(rbr_item, event_id))
                        rbr_att_id = 0
                        for result in cursor:
                            rbr_att_id = result[0]
                        if rbr_att_id != 0:
                            hotel_sql.append(dict(action='insert', table='requested_buddies', data=dict(user_exists=True, attendee_id=rbr_att_id)))
                        else:
                            hotel_sql.append(dict(action='insert', table='requested_buddies', data=dict(user_exists=False, email=rbr_item)))
                    hotel_view.append("<b>Requested buddy:</b> {}".format(hotel_item['rbr']))
                if hotel_item['rba'] and hotel_item.get('rba') != '[REMOVE]' and insert_data_flag:
                    actual_buddy_list = hotel_item['rba'].split(',')
                    hotel_sql.append(dict(table='actual_buddy_block', data=actual_buddy_list))
                    hotel_view.append("<b>Actual buddy:</b> {}".format(hotel_item['rba']))
            if len(hotel_sql) > 0:
                hotel_bookings.append({'id': '', 'name': 'Booking', 'old_data': '', 'new_data': {'view': hotel_view, 'sqls': hotel_sql}})

        data["hotels"] = hotel_bookings
        att_info["data"] = data
        att_info["validation"] = validation
        attendee_full_name = "{} {}".format(attendee_first_name, attendee_last_name)
        return att_info, attendee_full_name

    def travel_history(travel_history, new_travel, userId, cursor):
        travel_info = {}
        x_travel = None
        # TravelAttendee.objects.filter(travel_id=new_travel['travel_id'], attendee_id=userId)
        select_query = ("SELECT travel_has_attendees.status, travels.name FROM travel_has_attendees "
                        " LEFT JOIN travels ON travel_has_attendees.travel_id=travels.id "
                        " WHERE travel_has_attendees.travel_id=" + str(new_travel['travel_id'])+
                        " AND travel_has_attendees.attendee_id=" + str(userId))
        cursor.execute(select_query)
        for result in cursor:
            x_travel = result
        if x_travel:
            travel_info['old_data'] = x_travel[0]
            travel_info['new_data'] = new_travel['status'].strip()
            if travel_info['old_data'] != travel_info['new_data']:
                travel_info['id'] = new_travel['travel_id']
                travel_info['name'] = x_travel[1]
                travel_history.append(travel_info)
        return travel_history

    def testSession(attendee_id, session_id, session, cursor):
        # session column index
        # name -> 0, max_attendees -> 1, allow_overlapping -> 2, start -> 3, end -> 4, allow_attendees_queue -> 5,
        response = {}
        response['valid'] = True
        # session = Session.objects.get(id=session_id)
        if session:
            response['session'] = session[0]
            capacity = session[1]
             # count = SeminarsUsers.objects.filter(session_id=session_id, status='attending').count()
            count = 0
            select_query = ("SELECT COUNT(*) FROM seminars_has_users WHERE status = 'attending' AND session_id = "+str(session_id))
            cursor.execute(select_query)
            for result in cursor:
                count = result[0]

            if capacity > count or capacity == 0:
                already_has_session = []
                # SeminarsUsers.objects.filter(attendee_id=attendee_id, status='attending', session__allow_overlapping=0)
                select_query = ( "SELECT sessions.start, sessions.end FROM seminars_has_users "
                                 " left join sessions on seminars_has_users.session_id=sessions.id "
                                 " where seminars_has_users.status ='attending' "
                                 " and seminars_has_users.attendee_id = " + str(attendee_id) +
                                 " and sessions.allow_overlapping=0 ")

                cursor.execute(select_query)
                for result in cursor:
                    already_has_session.append(result)

                Inbetween = 0
                if session[2] == 0:
                    for sessionlist in already_has_session:
                        if sessionlist[0] <= session[3] < sessionlist[1]:
                            Inbetween = 1
                            break
                        elif sessionlist[0] < session[4] <= sessionlist[1]:
                            Inbetween = 1
                            break
                        if session[3] <= sessionlist[0] < session[4]:
                            Inbetween = 1
                            break
                        elif session[3] < sessionlist[1] <= session[4]:
                            Inbetween = 1
                            break

                    already_has_session_as_speaker = []
                    #SeminarSpeakers.objects.filter(speaker_id=attendee_id)
                    select_query = ("SELECT sessions.start, sessions.end FROM seminars_has_speakers "
                                    " left join sessions on seminars_has_speakers.session_id=sessions.id "
                                    " WHERE seminars_has_speakers.speaker_id = " + str(attendee_id))

                cursor.execute(select_query)
                for result in cursor:
                    already_has_session_as_speaker.append(result)

                    for sessionlist in already_has_session_as_speaker:
                        if sessionlist[0] <= session[3] < sessionlist[1]:
                            Inbetween = 1
                            break
                        elif sessionlist[0] < session[4] <= sessionlist[1]:
                            Inbetween = 1
                            break
                        if session[3] <= sessionlist[0] < session[4]:
                            Inbetween = 1
                            break
                        elif session[3] < sessionlist[1] <= session[4]:
                            Inbetween = 1
                            break

                if Inbetween == 1:
                    response['valid'] = False
                    response['reason'] = "Attendee has Session Clash"
            else:
                response['valid'] = False
                response['reason'] = "Session limit exceed."
                if session[5]:
                    response['is_queue'] = True
        else:
            response['valid'] = False
            response['reason'] = "Session not found."

        return response

    def session_history(session_history, new_session, userId, cursor):
        session_info = {}
        x_session = None
        # SeminarsUsers.objects.filter(session_id=new_session['session_id'], attendee_id=userId)
        select_query = ("SELECT seminars_has_users.status, sessions.name FROM seminars_has_users "
                        " LEFT JOIN sessions ON seminars_has_users.session_id=sessions.id "
                        " WHERE seminars_has_users.session_id= " + str(new_session['session_id']) +
                        " AND attendee_id = " + str(userId))
        cursor.execute(select_query)
        for result in cursor:
            x_session = result
            break
        if x_session:
            session_info['old_data'] = x_session[0]
            session_info['new_data'] = new_session['status']
            if session_info['old_data'] != session_info['new_data']:
                session_info['id'] = new_session['session_id']
                session_info['name'] = x_session[1]
                session_history.append(session_info)
        else:
            session_info['id'] = new_session['session_id']
            ssn = None
            # Session.objects.get(pk=new_session['session_id'])
            select_query = ("SELECT name FROM sessions WHERE id = " + str(new_session['session_id']))
            cursor.execute(select_query)
            for result in cursor:
                ssn = result
            session_info['name'] = ssn[0]
            session_info['old_data'] = "Old Data Not found"
            session_info['new_data'] = new_session['status'].strip()
            session_history.append(session_info)
        return session_history

    def handle_single_booking(att_booking_import_data, event_id, cursor):
        response = {'valid': True, 'err_messages': [], 'result': ''}
        booking_result = {'id': '', 'name': '', 'old_data': '', 'new_data': {'view': '', 'sqls': []}}
        result_data_view = []
        result_data_sqls = []
        result_old_data_view = []
        erro_msg = []
        try:
            attendee_id = att_booking_import_data.get('att')
            booking_id = att_booking_import_data.get('booking_id')
            room_id = att_booking_import_data.get('hotel_id')
            check_in = att_booking_import_data.get('check_in')
            check_out = att_booking_import_data.get('check_out')
            booking_name = 'Booking: {}'.format(booking_id) if booking_id else 'Booking'
            booking_result['name'] = booking_name
            new_booking_created = False
            if check_in and check_out and room_id:
                hotel_info_check = LambdaUpload.verify_hotel_information(room_id, check_in, check_out, cursor)
                if not hotel_info_check['valid']:
                    response['valid'] = False
                    response['err_messages'].append([{'name': booking_name, 'type': 'Hotel', 'attendee': attendee_id, 'reason': hotel_info_check['message']}])
                    return response

            if not booking_id:
                # new booking
                insert_data_flag = False
                if check_in and check_out and room_id:
                    if LambdaUpload.check_booking_availability(room_id, check_in, check_out, cursor):
                        result_data_sqls.append(dict(action='insert', table='bookings', data=dict(room_id=room_id, check_in=check_in, check_out=check_out)))
                        result_data_view.append("<b>check-in:</b> {}, <b>check-out:</b> {}, <b>Hotel:</b> {}".format(check_in, check_out, room_id))
                        insert_data_flag = True

                booking_rbr = att_booking_import_data.get('rbr')
                if booking_rbr and insert_data_flag:
                    booking_rbr = booking_rbr.split(',')
                    for rbr_item in booking_rbr:
                        cursor.execute("SELECT id FROM attendees WHERE email='{}' AND status='registered' AND event_id={}".format(rbr_item, event_id))
                        rbr_att_id = 0
                        for result in cursor:
                            rbr_att_id = result[0]
                        if rbr_att_id != 0:
                            result_data_sqls.append(dict(action='insert', table='requested_buddies', data=dict(user_exists=True, attendee_id=rbr_att_id)))
                        else:
                            result_data_sqls.append(dict(action='insert', table='requested_buddies', data=dict(user_exists=False, email=rbr_item)))
                            result_data_view.append("<b>Requested buddy:</b> {}".format(att_booking_import_data['rbr']))
                if att_booking_import_data['rba'] and att_booking_import_data.get('rba') != '[REMOVE]' and insert_data_flag:
                    actual_buddy_list = att_booking_import_data['rba'].split(',')
                    result_data_sqls.append(dict(table='actual_buddy_block', data=actual_buddy_list))
                    result_data_view.append("<b>Actual buddy:</b> {}".format(att_booking_import_data['rba']))

            elif not isinstance(booking_id, int):
                erro_msg.append([{'name': booking_name, 'type': 'Hotel', 'attendee': attendee_id, 'reason': 'Error in booking id.'}])
                response['valid'] = False
            else:
                x_booking = None
                select_query = (
                    "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id = " + str(booking_id))
                # id -> 0,  attendee_id -> 1, check_in -> 2, check_out -> 3, room_id -> 4, broken_up -> 5
                cursor.execute(select_query)
                for result in cursor:
                    x_booking = result

                booking = x_booking
                if booking:
                    x_room = None
                    select_query = ("SELECT id, description, cost, beds, vat, hotel_id, room_order, keep_hotel "
                                    " FROM rooms WHERE id = " + str(booking[4]))
                    # id-> 0, description -> 1, cost -> 2, beds -> 3, vat -> 4, hotel_id -> 5, room_order -> 6, keep_hotel -> 7
                    cursor.execute(select_query)
                    for result in cursor:
                        x_room = result

                    if x_room[0] != room_id:
                        if room_id:
                            if room_id == "[REMOVE]":
                                result_old_data_view.append(booking_name)
                                booking_result['new_data']['view'] = ['Delete Booking']
                                select_query = "SELECT match_id FROM match_line WHERE booking_id={}".format(booking_id)
                                cursor.execute(select_query)
                                match_ids = []
                                for result in cursor:
                                    match_ids.append(str(result[0]))

                                if match_ids:
                                    result_data_sqls.append({'action': 'delete', 'table': 'match_line', 'data': {'match_ids': match_ids}, 'booking_id': booking_id})
                                    result_data_sqls.append({'action': 'delete', 'table': 'matches', 'data': {'match_ids': match_ids}, 'booking_id': booking_id})

                                result_data_sqls.append({'action': 'delete', 'table': 'requested_buddies', 'data': {}, 'booking_id': booking_id})
                                result_data_sqls.append({'action': 'delete', 'table': 'bookings', 'data': {'room_id': x_room[0]}, 'booking_id': booking_id})
                                booking_result['new_data']['sqls'] = result_data_sqls
                                response['result'] = booking_result
                                response['err_messages'] = erro_msg
                                return response
                            else:
                                if check_in and check_out:
                                    is_available = LambdaUpload.check_booking_availability(room_id, check_in, check_out, cursor)
                                    if is_available:
                                        select_query = "SELECT match_id FROM match_line WHERE booking_id={}".format(booking_id)
                                        cursor.execute(select_query)
                                        match_ids = []
                                        for result in cursor:
                                            match_ids.append(str(result[0]))

                                        if match_ids:
                                            result_data_sqls.append({'action': 'delete', 'table': 'match_line', 'data': {'match_ids': match_ids}, 'booking_id': booking_id})
                                            result_data_sqls.append({'action': 'delete', 'table': 'matches', 'data': {'match_ids': match_ids}, 'booking_id': booking_id})

                                        result_data_sqls.append({'action': 'delete', 'table': 'requested_buddies', 'data': {}, 'booking_id': booking_id})
                                        result_data_sqls.append({'action': 'delete', 'table': 'bookings', 'data': {}, 'booking_id': booking_id})
                                        result_old_data_view.append('<b>Room:</b> {}'.format(booking[4]))
                                        result_data_view.append('<b>Room:</b> {}'.format(room_id))

                                        result_data_sqls.append({'action': 'insert', 'table': 'bookings',
                                                                 'data': {'room_id': room_id, 'check_in': check_in, 'check_out': check_out}, 'booking_id': None})
                                        new_booking_created = True
                                    else:
                                        response['valid'] = False
                                        erro_msg.append([{'name': booking_name, 'type': 'Hotel', 'attendee': attendee_id, 'reason': 'Room not available.'}])
                                else:
                                    response['valid'] = False
                                    erro_msg.append([{'name': booking_name, 'type': 'Hotel', 'attendee': attendee_id, 'reason': 'Check-in or Check-out date missing.'}])
                        else:
                            # room_id might not be available in excel file
                            room_id = x_room[0]
                    else:
                        if not room_id:
                            room_id = x_room[0]
                        if check_in and check_out:
                            if str(booking[2]) != str(check_in) or str(booking[3]) != str(check_out):
                                # update_flag = False
                                new_checkin_date = datetime.strptime(str(check_in), "%Y-%m-%d").date()
                                new_checkout_date = datetime.strptime(str(check_out), "%Y-%m-%d").date()

                                if not new_checkout_date > new_checkin_date:
                                    erro_msg.append([{'name': booking_name, 'type': 'Hotel', 'attendee': attendee_id, 'reason': 'Wrong check-in Check-out data provided.'}])
                                else:
                                    old_checkin_date = booking[2]
                                    old_checkout_date = booking[3]

                                    old_dates = []
                                    new_dates = []

                                    for single_date in HotelLamda.daterange(new_checkin_date, new_checkout_date):
                                        new_dates.append(str(single_date))
                                    for single_date in HotelLamda.daterange(old_checkin_date, old_checkout_date):
                                        old_dates.append(str(single_date))

                                    for dd in old_dates:
                                        if dd in new_dates:
                                            new_dates.remove(dd)

                                    is_available = False
                                    if len(new_dates) > 0:
                                        for new_date in new_dates:
                                            # room_allotments = RoomAllotment.objects.filter(room_id=room_id, available_date=str(new_date))
                                            room_allotments = []
                                            select_query = "SELECT id, room_id, allotments, available_date FROM room_allotments WHERE room_id =" \
                                                           + str(room_id) + " AND available_date= %(p_new_date)s"
                                            cursor.execute(select_query, {'p_new_date': new_date})

                                            for result in cursor:
                                                room_allotments.append(result)

                                            for allotment in room_allotments:
                                                available = HotelLamda.get_available_allotment(allotment, room_id, cursor)
                                                if available > 0:
                                                    is_available = True
                                    else:
                                        is_available = True

                                    if is_available:
                                        result_data_sqls.append({'action': 'update', 'table': 'bookings', 'data': {'check_in': str(check_in), 'check_out': str(check_out)}, 'booking_id': booking_id})
                                        result_old_data_view.append('<b>check-in:</b> {}<br> <b>check-out:</b> {}'.format(old_checkin_date, old_checkout_date))
                                        result_data_view.append('<b>check-in:</b> {}<br> <b>check-out:</b> {}'.format(check_in, check_out))

                                        get_match = []
                                        select_query = "SELECT id, booking_id, match_id FROM match_line WHERE booking_id = (%(p_booking_id)s)"
                                        cursor.execute(select_query, {'p_booking_id': booking[0]})
                                        for result in cursor:
                                            get_match.append(result)

                                        booking_matches = []
                                        if get_match:
                                            matches = []
                                            select_query = "SELECT id, booking_id, match_id FROM match_line WHERE match_id=(%(p_match_id)s)"
                                            cursor.execute(select_query, {'p_match_id': get_match[0][2]})
                                            for result in cursor:
                                                matches.append(result)

                                            for match in matches:
                                                booking_matches.append(match[1])

                                        common_dates = LambdaUpload.get_booking_common_dates(booking_matches, cursor, new_checkin_date, new_checkout_date, booking_id)
                                        print('common date')
                                        print(str(common_dates))
                                        if len(common_dates) == 0:
                                            if len(booking_matches) > 1:
                                                if get_match:
                                                    match_ids = [str(r[2]) for r in get_match]
                                                    result_data_sqls.append({'action': 'delete', 'table': 'match_line', 'data': {'match_ids': match_ids}, 'booking_id': booking_id})
                                                    result_data_sqls.append({'action': 'delete', 'table': 'matches', 'data': {'match_ids': match_ids}, 'booking_id': booking_id})

                                        elif len(common_dates) > 0:
                                            all_dates = []
                                            for my_date in common_dates:
                                                all_dates.append(str(my_date))

                                            start_date = min(common_dates)
                                            end_date = max(common_dates) + timedelta(days=1)
                                            update_data = {'start_date': start_date, 'end_date': end_date, 'all_dates': json.dumps(all_dates), 'match_id': get_match[0][2]}
                                            result_data_sqls.append({'action': 'update', 'table': 'matches', 'data': update_data, 'booking_id': booking_id})
                                    else:
                                        erro_msg.append([{'name': booking_name, 'type': 'Hotel', 'attendee': attendee_id, 'reason': 'Room not available.'}])

                    req_room_buddies = att_booking_import_data.get('rbr')
                    if req_room_buddies:
                        if req_room_buddies == "[REMOVE]":
                            select_query = "SELECT a.email, b.exists, b.email FROM requested_buddies b left join " \
                                           " attendees a on b.buddy_id = a.id WHERE  b.booking_id = " + str(booking_id)
                            cursor.execute(select_query)
                            old_req_buddies = []
                            for result in cursor:
                                old_req_buddies.append(result[0] if result[1] else result[2])
                            if old_req_buddies:
                                result_old_data_view.append("<b>Requested-buddy:</b> {}".format(', '.join(old_req_buddies)))
                                result_data_sqls.append({'action': 'delete', 'table': 'requested_buddies', 'data': {}, 'booking_id': booking_id})
                                result_data_view.append('<b>Requested-buddy:</b> Delete')
                        else:
                            rbr_list = [x.strip() for x in req_room_buddies.strip().split(',')]
                            rbr_list = list(filter(lambda lam_item: lam_item != '', rbr_list))
                            rbr_count = 0
                            if not new_booking_created:
                                old_rbr_list = []
                                old_req_buddies_for_view = []
                                select_query = "SELECT b.id, b.buddy_id, a.email, b.exists, b.email FROM requested_buddies b left join " \
                                               " attendees a on b.buddy_id = a.id WHERE  b.booking_id = " + str(booking_id)
                                cursor.execute(select_query)
                                for result in cursor:
                                    email_checker = result[2] if result[3] else result[4]
                                    if email_checker in rbr_list:
                                        old_req_buddies_for_view.append(email_checker)
                                        rbr_count += 1
                                        rbr_list.remove(email_checker)
                                    else:
                                        old_req_buddies_for_view.append(email_checker)
                                        old_rbr_list.append(result)

                                if len(rbr_list) > 0:
                                    result_data_view.append("<b>Requested-buddy:</b> {}".format(req_room_buddies))
                                    if old_req_buddies_for_view:
                                        result_old_data_view.append(
                                            "<b>Requested-buddy:</b> {}".format(', '.join(old_req_buddies_for_view)))
                                    else:
                                        result_old_data_view.append('<b>Requested-buddy:</b> Empty')

                                    if len(old_rbr_list) > 0:
                                        req_bud_ids = ','.join(str(item[0]) for item in old_rbr_list)
                                        result_data_sqls.append({'action': 'delete', 'table': 'requested_buddies', 'data': {'ids': req_bud_ids}, 'booking_id': booking_id})

                            if rbr_count < 2:
                                for rbr_item in rbr_list:
                                    if rbr_count < 2:
                                        # need to check with event_id here along with email
                                        cursor.execute("SELECT id FROM attendees WHERE email='{}' AND status='registered' AND event_id={}".format(rbr_item, event_id))
                                        rbr_att_id = 0
                                        for result in cursor:
                                            rbr_att_id = result[0]
                                        if rbr_att_id != 0:
                                            result_data_sqls.append({'action': 'insert', 'table': 'requested_buddies', 'data': {'user_exists': True, 'attendee_id': rbr_att_id}, 'booking_id': booking_id})
                                            rbr_count += 1
                                        else:
                                            result_data_sqls.append({'action': 'insert', 'table': 'requested_buddies', 'data': {'user_exists': False, 'email': rbr_item}, 'booking_id': booking_id})

                    actual_buddies = att_booking_import_data.get('rba')
                    if actual_buddies:
                        actual_buddies = actual_buddies.strip()
                        if actual_buddies != '':
                            abl_result = LambdaUpload.handle_actual_buddy(booking, actual_buddies, check_in, check_out, room_id, cursor)
                            result_data_view.extend(abl_result['views'])
                            result_data_sqls.extend(abl_result['sqls'])
                            result_old_data_view.extend(abl_result['old_views'])
                else:
                    erro_msg.append([{'name': 'Booking: ' + str(booking_id), 'type': 'Hotel', 'attendee': attendee_id, 'reason': 'Booking not found.'}])
                    response['valid'] = False
        except Exception as exc:
            ErrorR.efail(exc)

        booking_result['old_data'] = result_old_data_view
        booking_result['new_data']['view'] = result_data_view
        booking_result['new_data']['sqls'] = result_data_sqls
        response['result'] = booking_result
        response['err_messages'] = erro_msg
        return response

    def check_booking_availability(room_id, check_in, check_out, cursor):
        is_available = False
        try:
            room_allotments = []
            select_query = "SELECT id, room_id, allotments, available_date FROM room_allotments " \
                           " WHERE (room_id = %(p_room_id)s AND available_date BETWEEN %(p_checkin_date)s AND %(p_checkout_date)s)"
            select_param = {
                'p_room_id': room_id,
                'p_checkin_date': check_in,
                'p_checkout_date': check_out
            }
            cursor.execute(select_query, select_param)
            for result in cursor:
                room_allotments.append(result)

            if room_allotments:
                for allotment in room_allotments:
                    available = HotelLamda.get_available_allotment(allotment, room_id, cursor)
                    if available > 0:
                        is_available = True
                    else:
                        is_available = False
                        break
        except Exception as exec:
            print(exec)
        print('Final Return: *** {} ***'.format(is_available))
        return is_available

    def verify_hotel_information(room_id, check_in, check_out, cursor):
        response = dict(valid=False, message='Wrong booking data provided.')
        try:
            if room_id == "[REMOVE]":
                response['valid'] = True
            else:
                check_in_date = datetime.strptime(str(check_in), "%Y-%m-%d").date()
                check_out_date = datetime.strptime(str(check_out), "%Y-%m-%d").date()
                if not check_out_date > check_in_date:
                    response['message'] = 'Wrong check_in and check_out date.'
                    return response

                select_query = "SELECT * FROM rooms WHERE id={}".format(room_id)
                cursor.execute(select_query)
                room_exists = False
                for res in cursor:
                    room_exists = True
                if not room_exists:
                    response['message'] = 'Wrong hotel id provided.'
                    return response
                booking_dates = ["'" + str(item) + "'" for item in HotelLamda.daterange(check_in_date, check_out_date)]
                select_query = "SELECT COUNT(*) FROM room_allotments WHERE available_date in ({}) AND room_id={}".format(','.join(booking_dates), room_id)
                cursor.execute(select_query)
                available_date_count = 0
                for res in cursor:
                    available_date_count = res[0]

                if len(booking_dates) != available_date_count:
                    response['message'] = 'Wrong check_in or check_out date.'
                    return response
                response['valid'] = True
        except Exception as exc:
            ErrorR.efail(exc)

        return response

    def get_booking_common_dates(bookings, cursor, new_checkin_date, new_checkout_date, booking_id):
        a_list = []
        all_dates = []
        if len(bookings) > 1:
            booking_list = []
            str_booking_id_list = ','.join(str(b) for b in bookings)
            select_query = "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id IN ({})".format(str_booking_id_list)
            cursor.execute(select_query)
            for result in cursor:
                booking_list.append(result)

            for booking in booking_list:
                if booking[0] == int(booking_id):
                    booking_check_in = new_checkin_date
                    booking_check_out = new_checkout_date
                else:
                    booking_check_in = booking[2]
                    booking_check_out = booking[3]

                day_count = (booking_check_out - booking_check_in).days + 1
                booking_date_list = []
                for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                    booking_date_list.append(single_date)
                    all_dates.append(single_date)
                a_list.append(booking_date_list)

            for i in range(0, len(a_list)):
                for j in range(1, len(a_list)):
                    all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
        return all_dates

    def handle_actual_buddy(attendee_booking, actual_buddy_list, check_in, check_out, room_id, cursor):
        result_old_data_view = []
        result_data_view = []
        result_data_sqls = []
        try:
            if actual_buddy_list == "[REMOVE]":
                select_query = "SELECT m.match_id, a.email FROM match_line m join bookings b on m.booking_id=b.id and m.booking_id={} join attendees a on b.attendee_id=a.id".format(attendee_booking[0])
                cursor.execute(select_query)
                match_ids = []
                old_actual_buddies = []
                for result in cursor:
                    match_ids.append(str(result[0]))
                    old_actual_buddies.append(result[1])

                if match_ids:
                    result_data_sqls.append({'action': 'delete', 'table': 'match_line', 'data': {'match_ids': match_ids}, 'booking_id': attendee_booking[0]})
                    result_data_sqls.append({'action': 'delete', 'table': 'matches', 'data': {'match_ids': match_ids}, 'booking_id': attendee_booking[0]})
                    result_old_data_view.append("<b>Actual-buddy:</b> {}".format(', '.join(old_actual_buddies)))
                result_data_view.append('<b>Actual-buddy:</b> Delete')
            else:
                actual_buddy_list_text = actual_buddy_list
                actual_buddy_list = [x.strip() for x in actual_buddy_list.split(',')]
                actual_buddy_list = list(filter(lambda abl: abl != '', actual_buddy_list))
                existing_rba_check = LambdaUpload.check_existing_rba(attendee_booking, actual_buddy_list, cursor)
                # here 'x_result' was 'result' [ to avoid same name with cursor result ]
                if existing_rba_check['result']:
                    # result_data_view += '<b>Updated actual buddy:</b> {}.<br>'.format(actual_buddy_list_text)
                    result_data_view.append('<b>Actual-buddy:</b> {}.'.format(actual_buddy_list_text))
                    result_data_sqls.append({'table': 'actual_buddy_block', 'booking_id': attendee_booking[0], 'data': actual_buddy_list})
                    result_old_data_view.append(existing_rba_check['existing_buddies'])
                    # if rba is need to update then we show them only
                    # CHECKING IS IGNORED [all code will be proceeded when actual buddy execute when admin approve it]
        except Exception as exc:
            ErrorR.efail(exc)
        return {'views': result_data_view, 'sqls': result_data_sqls, 'old_views': result_old_data_view}

    def check_existing_rba(attendee_booking, actual_buddy_list, cursor):
        response = dict(result=False, existing_buddies="<b>Actual-buddy:</b> Empty")
        old_actual_buddies = []
        if attendee_booking:
            try:
                select_query = "SELECT match_id FROM match_line WHERE booking_id = {}".format(attendee_booking[0])
                cursor.execute(select_query)
                match_ids = []
                for result in cursor:
                    match_ids.append(result[0])

                str_x_match_id = str(match_ids).replace('[', '').replace(']', '')
                str_x_match_id = str_x_match_id if len(str_x_match_id) > 0 else '0'
                select_query = "SELECT booking_id FROM match_line WHERE (match_id IN " \
                               "( " + str_x_match_id + " ) AND booking_id <> %(p_booking_id)s)"
                cursor.execute(select_query, {'p_booking_id': attendee_booking[0]})
                other_booking_ids = [result[0] for result in cursor]
                for item in other_booking_ids:
                    select_query = "SELECT a.email FROM attendees a LEFT JOIN bookings b ON a.id = b.attendee_id WHERE b.id=%(p_booking_id)s"
                    cursor.execute(select_query, {'p_booking_id': item})
                    for result in cursor:
                        old_actual_buddies.append(result[0])
                        if result[0] in actual_buddy_list:
                            actual_buddy_list.remove(result[0])
                if len(actual_buddy_list) > 0:
                    response['result'] = True
                    if old_actual_buddies:
                        response['existing_buddies'] = "<b>Actual-buddy:</b> {}".format(','.join(old_actual_buddies))
            except Exception as exc:
                print(exc)

        return response


class HotelLamda:
    def hotel_import(request, all_rows, filename, cursor, cnx):
        messages = []
        item_row = -1

        for rows in all_rows:
            with transaction.atomic():
                try:
                    update_msg = []
                    erro_msg = []
                    update_flag = False
                    item_row += 1
                    if item_row < 2:
                        continue

                    booking_id = rows[0].value
                    room_id = rows[6].value

                    if not booking_id or not isinstance(booking_id, int):
                        continue
                    # x_booking = Booking.objects.filter(id=booking_id).first()
                    print ("For booking Id: " + str(booking_id))
                    x_booking = None
                    select_query = (
                    "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id = " + str(booking_id))
                    # id -> 0,  attendee_id -> 1, check_in -> 2, check_out -> 3, room_id -> 4, broken_up -> 5
                    cursor.execute(select_query)
                    for result in cursor:
                        x_booking = result

                    booking = x_booking
                    if booking:
                        # x_room = booking.room
                        x_room = None
                        select_query = ("SELECT id, description, cost, beds, vat_id, hotel_id, room_order, keep_hotel "
                                        " FROM rooms WHERE id = " + str(booking[4]))
                        # id-> 0, description -> 1, cost -> 2, beds -> 3, vat_id -> 4, hotel_id -> 5, room_order -> 6, keep_hotel -> 7
                        cursor.execute(select_query)
                        for result in cursor:
                            x_room = result
                        room = x_room
                        # print ("room")
                        # print (room_id)
                        date_time_now_str = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                        if x_room[0] != room_id:
                            if room_id == "[REMOVE]":
                                # x_booking.delete()
                                # need to delete match_line before delete booking
                                cursor.execute("DELETE FROM match_line WHERE booking_id = " + str(booking_id))
                                cnx.commit()
                                select_query = ("DELETE FROM bookings WHERE id = " + str(booking_id))
                                cursor.execute(select_query)
                                cnx.commit()

                                update_msg.append(["Booking removed"])
                                # for temporary purpose to run render html [note: final will have no render things]
                                # booking = Booking.objects.filter(id=booking_id).first()
                                #
                                messages.append({'booking': booking[0], 'errors': erro_msg, 'msgs': update_msg})
                                continue

                            # checkin_date = datetime.strptime(str(rows[9].value),"%Y-%m-%d").date()
                            # checkout_date = datetime.strptime(str(rows[10].value),"%Y-%m-%d").date()
                            # tried using direct using string , if does't work will have to use privious one
                            checkin_date = rows[9].value
                            checkout_date = rows[10].value

                            # room_allotments = RoomAllotment.objects.filter(room_id=room_id, available_date__range=(
                            #     checkin_date, checkout_date))

                            room_allotments = []
                            select_query = "SELECT id, room_id, allotments, available_date FROM room_allotments " \
                                           " WHERE (room_id = %(p_room_id)s " \
                                           " AND available_date BETWEEN %(p_checkin_date)s AND %(p_checkout_date)s)"
                            select_param = {
                                'p_room_id': room_id,
                                'p_checkin_date': checkin_date,
                                'p_checkout_date': checkout_date
                            }

                            cursor.execute(select_query, select_param)
                            for result in cursor:
                                room_allotments.append(result)

                            is_available = False

                            if len(room_allotments) > 0:
                                for allotment in room_allotments:
                                    available = HotelLamda.get_available_allotment(allotment, room_id, cursor)
                                    if available > 0:
                                        is_available = True
                                    else:
                                        is_available = False
                                        break
                            if is_available:
                                # new_booking = Booking(attendee_id=x_booking[1], room_id=room_id,
                                #                       check_in=rows[9].value, check_out=rows[10].value,
                                #                       broken_up=x_booking[5])
                                # new_booking.save()
                                # booking = new_booking

                                insert_query = "INSERT INTO bookings(attendee_id, room_id, check_in, check_out, broken_up, created, updated) " \
                                               " VALUES (%(p_att_id)s, %(p_room_id)s, %(p_check_in)s, %(p_check_out)s, %(p_broken_up)s, %(p_created)s, %(p_updated)s)"

                                insert_param = {
                                    'p_att_id': x_booking[1],
                                    'p_room_id': room_id,
                                    'p_check_in': rows[9].value,
                                    'p_check_out': rows[10].value,
                                    'p_broken_up': x_booking[5],
                                    'p_created':date_time_now_str,
                                    'p_updated':date_time_now_str
                                }
                                cursor.execute(insert_query, insert_param)
                                cnx.commit()

                                booking_id = cursor.lastrowid

                                select_query = "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id = " + str(booking_id)
                                # id -> 0,  attendee_id -> 1, check_in -> 2, check_out -> 3, room_id -> 4, broken_up -> 5
                                cursor.execute(select_query)
                                for result in cursor:
                                    booking = result

                                # room = booking.room
                                room = None
                                select_query = "SELECT id, description, cost, beds, vat_id, hotel_id, room_order, keep_hotel " \
                                               " FROM rooms WHERE id = " + str(room_id)
                                cursor.execute(select_query)
                                for result in cursor:
                                    room = result

                                # x_booking.delete()
                                # need to delete match_line and requested_buddies before delete booking
                                cursor.execute("DELETE FROM match_line WHERE booking_id = " + str(x_booking[0]))
                                cnx.commit()
                                cursor.execute("DELETE FROM requested_buddies WHERE booking_id = " + str(x_booking[0]))
                                cnx.commit()
                                delete_query = ("DELETE FROM bookings WHERE id = " + str(x_booking[0]))
                                cursor.execute(delete_query)
                                cnx.commit()

                                update_msg.append(["Booking updated"])
                                update_flag = True
                            else:
                                update_flag = True
                                erro_msg.append("Room not available")
                                continue
                        else:
                            print('not match')
                            # if str(booking.check_in) != str(rows[9].value) or str(booking.check_out) != str(
                            #         rows[10].value):
                            if str(booking[2]) != str(rows[9].value) or str(booking[3]) != str(rows[10].value):
                                # update_flag = False
                                new_checkin_date = datetime.strptime(str(rows[9].value), "%Y-%m-%d").date()
                                new_checkout_date = datetime.strptime(str(rows[10].value), "%Y-%m-%d").date()

                                old_checkin_date = booking[2]
                                old_checkout_date = booking[3]

                                old_dates = []
                                new_dates = []

                                for single_date in HotelLamda.daterange(new_checkin_date, new_checkout_date):
                                    new_dates.append(str(single_date))
                                for single_date in HotelLamda.daterange(old_checkin_date, old_checkout_date):
                                    old_dates.append(str(single_date))

                                for dd in old_dates:
                                    if dd in new_dates:
                                        new_dates.remove(dd)

                                is_available = False
                                # print ('new_dates')
                                # print (new_dates)
                                if len(new_dates) > 0:
                                    for new_date in new_dates:
                                        # room_allotments = RoomAllotment.objects.filter(room_id=room_id, available_date=str(new_date))
                                        room_allotments = []
                                        select_query = "SELECT id, room_id, allotments, available_date FROM room_allotments WHERE room_id =" \
                                                       + str(room_id) + " AND available_date= %(p_new_date)s"
                                        cursor.execute(select_query, {'p_new_date': new_date})
                                        # print ('QQQQQQQQQQ')
                                        # print (cursor.statement)
                                        for result in cursor:
                                            # print (result)
                                            room_allotments.append(result)

                                        for allotment in room_allotments:
                                            available = HotelLamda.get_available_allotment(allotment, room_id, cursor)
                                            if available > 0:
                                                is_available = True
                                else:
                                    is_available = True

                                if is_available:
                                    # from app.views.attendee_view import AttendeeView

                                    # booking.check_in = str(rows[9].value)
                                    # booking.check_out = str(rows[10].value)
                                    # booking.save()

                                    update_query = "UPDATE bookings SET check_in = %(p_check_in)s, check_out = %(p_check_out)s " \
                                                   " WHERE id = %(p_id)s"
                                    update_param = {
                                        'p_check_in': str(rows[9].value),
                                        'p_check_out': str(rows[10].value),
                                        'p_id': booking[0]
                                    }
                                    cursor.execute(update_query, update_param)
                                    cnx.commit()

                                    # get_match = MatchLine.objects.filter(booking_id=booking.id)
                                    get_match = []
                                    select_query = "SELECT id, booking_id, match_id FROM match_line WHERE booking_id = (%(p_booking_id)s)"
                                    cursor.execute(select_query, {'p_booking_id': booking[0]})
                                    for result in cursor:
                                        get_match.append(result)

                                    booking_matches = []
                                    if get_match:
                                        # matches = MatchLine.objects.filter(match_id=get_match[0].match_id)
                                        matches = []
                                        select_query = "SELECT id, booking_id, match_id FROM match_line WHERE match_id = (%(p_match_id)s)"
                                        cursor.execute(select_query, {'p_match_id': get_match[0][2]})
                                        for result in cursor:
                                            matches.append(result)

                                        for match in matches:
                                            booking_matches.append(match[1])
                                    common_dates = HotelLamda.get_booking_common_dates(booking_matches, cursor)
                                    print ('common date')
                                    print (common_dates)
                                    if len(common_dates) == 0:
                                        # new_booking = Booking(attendee_id=booking.attendee_id, room_id=room_id,
                                        #                       check_in=rows[9].value, check_out=rows[10].value)
                                        # new_booking.save()

                                        insert_query = "INSERT INTO bookings(attendee_id, room_id, check_in, check_out, broken_up, created, updated) " \
                                                       " VALUES (%(p_att_id)s, %(p_room_id)s, %(p_check_in)s, %(p_check_out)s, 0, %(p_created)s, %(p_updated)s)"

                                        insert_param = {
                                            'p_att_id': booking[1],
                                            'p_room_id': room_id,
                                            'p_check_in': rows[9].value,
                                            'p_check_out': rows[10].value,
                                            'p_created':date_time_now_str,
                                            'p_updated':date_time_now_str
                                        }
                                        cursor.execute(insert_query, insert_param)
                                        cnx.commit()
                                        booking_id = cursor.lastrowid

                                        select_query = "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id = " + str(
                                            booking_id)
                                        # id -> 0,  attendee_id -> 1, check_in -> 2, check_out -> 3, room_id -> 4, broken_up -> 5
                                        cursor.execute(select_query)
                                        for result in cursor:
                                            booking = result

                                        print ('inserting booking for checkin-out date')

                                        # need to delete match_line and requested_buddies before delete booking
                                        cursor.execute("DELETE FROM match_line WHERE booking_id = " + str(x_booking[0]))
                                        cnx.commit()
                                        cursor.execute(
                                            "DELETE FROM requested_buddies WHERE booking_id = " + str(x_booking[0]))
                                        cnx.commit()
                                        # Booking.objects.get(id=booking.id).delete()
                                        delete_query = ("DELETE FROM bookings WHERE id = " + str(x_booking[0]))
                                        cursor.execute(delete_query)
                                        cnx.commit()

                                        update_msg.append(["Booking created"])

                                    elif len(common_dates) > 0:
                                        all_dates = []
                                        for my_date in common_dates:
                                            all_dates.append(str(my_date))
                                        end_date = max(common_dates) + timedelta(days=1)

                                        # Match.objects.filter(id=get_match[0].match_id).update(start_date=min(common_dates),
                                        #       end_date=end_date,all_dates=json.dumps(all_dates))

                                        update_query = "UPDATE matches SET start_date = %(p_start_date)s, end_date=%(p_end_date)s, " \
                                                       " all_dates = %(p_all_dates)s WHERE id = %(p_match_id)s"
                                        update_param = {
                                            'p_start_date': min(common_dates),
                                            'p_end_date': end_date,
                                            'p_all_dates': json.dumps(all_dates),
                                            'p_match_id': get_match[0][2]
                                        }
                                        cursor.execute(update_query, update_param)
                                        cnx.commit()
                                        print ('updating booking for checkin-out date')
                                        update_msg.append(["Booking updated"])
                                    else:
                                        update_msg.append(["Booking updated"])
                                    update_flag = True
                                else:
                                    update_flag = True
                                    erro_msg.append("Room not available")
                                    # print("Room not available")

                        if room[1] != rows[8].value:
                            # room.description = rows[8].value
                            # room.save()
                            update_query = "UPDATE rooms SET description= %(p_description)s WHERE id = %(p_room_id)s"
                            cursor.execute(update_query, {'p_description': rows[8].value, 'p_room_id': room[0]})
                            cnx.commit()

                            update_flag = True
                            update_msg.append(["Hotel Description Changed"])

                        # hotel = room.hotel
                        hotel = None
                        select_query = "SELECT id, name, location_id, group_id FROM hotels WHERE id = " + str(room[5])
                        cursor.execute(select_query)
                        for result in cursor:
                            hotel = result

                        if hotel[1] != rows[7].value:
                            # hotel.name = rows[7].value
                            # hotel.save()
                            update_query = "UPDATE hotels SET name = %(p_name)s WHERE id = %(p_hotel_id)s"
                            cursor.execute(update_query, {'p_name': rows[7].value, 'p_hotel_id': hotel[0]})
                            cnx.commit()

                            update_flag = True
                            update_msg.append(["Hotel name Changed"])

                        if rows[11].value == "[REMOVE]":
                            # RequestedBuddy.objects.filter(booking_id=booking.id).delete()
                            delete_query = "DELETE FROM requested_buddies WHERE booking_id = " + str(booking[0])
                            cursor.execute(delete_query)
                            cnx.commit()

                            update_msg.append(["Requested room buddy removed"])
                            update_flag = True
                        elif rows[11].value:
                            rbr_list = [x.strip() for x in rows[11].value.strip().split(',')]
                            rbr_list = list(filter(lambda lam_item: lam_item != '', rbr_list))
                            rbr_count = 0
                            old_rbr_list = []
                            select_query = " SELECT b.id, b.buddy_id, a.email FROM requested_buddies b left join " \
                                           " attendees a on b.buddy_id = a.id WHERE  b.booking_id = " + str(booking_id)
                            cursor.execute(select_query)
                            for result in cursor:
                                if result[2] in rbr_list:
                                    rbr_count += 1
                                    rbr_list.remove(result[2])
                                else:
                                    old_rbr_list.append(result)

                            if len(old_rbr_list) > 0:
                                for rbr_item in old_rbr_list:
                                    cursor.execute("DELETE FROM requested_buddies WHERE id = " + str(rbr_item[0]))
                                    cnx.commit()
                                    update_msg.append(["Requested room buddy updated"])
                                    update_flag = True

                            if rbr_count < 2:
                                for rbr_item in rbr_list:
                                    if rbr_count < 2:
                                        cursor.execute("SELECT id FROM attendees WHERE email ='" + str(rbr_item) + "'")
                                        rbr_att_id = 0
                                        for result in cursor:
                                            rbr_att_id = result[0]
                                        if rbr_att_id != 0:
                                            print ('rbr_att_id')
                                            print (rbr_att_id)
                                            insert_query = "INSERT INTO requested_buddies(requested_buddies.exists, booking_id, buddy_id, created, updated) " \
                                                           " VALUES( 1, %(p_booking_id)s, %(p_buddy_id)s, %(p_created)s, %(p_updated)s)"
                                            date_time_now_str = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                                            cursor.execute(insert_query, {'p_booking_id': booking_id, 'p_buddy_id': rbr_att_id,'p_created':date_time_now_str,'p_updated':date_time_now_str})
                                            print (cursor.statement)
                                            cnx.commit()
                                            rbr_count += 1
                                            update_msg.append(["Requested room buddy updated"])
                                        else:
                                            update_msg.append(["Requested room buddy: {} is not an user email".format(rbr_item)])
                                        update_flag = True

                        if rows[12].value and rows[12].value.strip() != None:
                            update_msg.append(HotelLamda.handle_actual_buddy(request, booking, rows[12].value, cursor, cnx))
                            update_flag = True

                        if update_flag:
                            messages.append({'booking': booking[0], 'errors': erro_msg, 'msgs': update_msg})

                    else:
                        # print(booking_id)
                        erro_msg.append("Booking not found")
                        messages.append({'booking': {'id': booking_id}, 'errors': erro_msg, 'msgs': ''})


                except Exception as e:
                    messages.append(
                        {'booking': {'id': booking_id}, 'errors': ['Exception occurs: ' + str(e)], 'msgs': ''})

        admin_id = request.session['event_auth_user']['id']
        event_id = request.session['event_auth_user']['event_id']
        insert_query = ("INSERT INTO import_change_request "
                        "(event_id, changed_data, imported_by_id, status, created_at) "
                        "VALUES (%(event_id)s, %(changed_data)s, %(imported_by_id)s, %(status)s, %(created_at)s)")

        insert_data = {
            'event_id': event_id,
            'changed_data': json.dumps(messages),
            'imported_by_id': admin_id,
            'status': 5,
            'created_at': datetime.now(),
        }
        cursor.execute(insert_query, insert_data)
        cnx.commit()

        last_import_id = cursor.lastrowid
        update_query = ("UPDATE import_change_status SET status = 5, import_change_id= " + str(
            last_import_id) + " WHERE filename = '" + filename + "'")
        cursor.execute(update_query)
        cnx.commit()

        cursor.close()
        cnx.close()

        print ('*****************messages*****************')
        print (messages)
        return

    def get_available_allotment(allotment, room_id, cursor):
        # from django.db.models.aggregates import Count
        # matched_attendee = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
        #     count_match__gt=1, match__room_id=room_id)
        matched_attendee = []
        select_query = "SELECT match_line.match_id, COUNT(match_line.match_id) AS count_match FROM match_line " \
                       " INNER JOIN matches ON ( match_line.match_id = matches.id ) WHERE matches.room_id = %(p_room_id)s " \
                       " GROUP BY match_line.match_id HAVING COUNT(match_line.match_id) > 1 ORDER BY NULL"
        select_param = {'p_room_id': room_id}
        cursor.execute(select_query, select_param)
        for result in cursor:
            matched_attendee.append(result)
        print ('matched_attendee')
        print (matched_attendee)
        # count_matched_pairs = matched_attendee.filter(match__start_date__lte=allotment.available_date,
        #                                               match__end_date__gt=allotment.available_date).count()
        count_matched_pairs = 0
        select_query = "SELECT COUNT(match_line.match_id) FROM match_line INNER JOIN matches " \
                       "ON ( match_line.match_id = matches.id ) WHERE (matches.room_id = %(p_room_id)s AND " \
                       "matches.start_date <= %(p_available_date)s  AND matches.end_date > %(p_available_date)s) " \
                       "GROUP BY match_line.match_id HAVING COUNT(match_line.match_id) > 1 ORDER BY NULL"
        select_param = {
            'p_room_id': room_id,
            'p_available_date': allotment[3]
        }
        cursor.execute(select_query, select_param)
        for result in cursor:
            count_matched_pairs += 1

        match_id = []
        if len(matched_attendee) > 0:
            for match in matched_attendee:
                match_id.append(match[0])

        # count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
        #     match_id__in=match_id, booking__check_in__lte=allotment.available_date,
        #     booking__check_out__gt=allotment.available_date).exclude(match__start_date__lte=allotment.available_date,
        #                                                              match__end_date__gt=allotment.available_date).count()
        count_matched_singles = 0

        str_match_id = str(match_id).replace('[', '').replace(']', '')
        str_match_id = str_match_id if len(str_match_id) > 0 else '0'
        select_query = "SELECT COUNT(match_line.match_id) FROM match_line INNER JOIN matches ON ( match_line.match_id = matches.id ) " \
                       " INNER JOIN bookings ON ( match_line.booking_id = bookings.id ) WHERE (bookings.check_out > %(p_available_date)s " \
                       " AND bookings.check_in <= %(p_available_date)s AND match_line.match_id IN ("+str_match_id+") " \
                       " AND NOT (matches.start_date <= %(p_available_date)s AND matches.end_date > %(p_available_date)s)) " \
                       " GROUP BY match_line.match_id ORDER BY NULL"

        cursor.execute(select_query, {'p_available_date': allotment[3]})
        for result in cursor:
            count_matched_singles += 1

        matched_booking = []
        # booking_matched = MatchLine.objects.filter(match_id__in=match_id)
        booking_matched = []
        if len(match_id)>0:
            select_query = "SELECT id, booking_id, match_id FROM match_line WHERE match_id IN (" \
                           + str_match_id + ")"
            cursor.execute(select_query)
            for result in cursor:
                matched_booking.append(result[1])

        # count_unmatched_attendee = Booking.objects.filter(room_id=room_id, check_in__lte=allotment.available_date,
        #                               check_out__gt=allotment.available_date).exclude(id__in=matched_booking).count()
        count_unmatched_attendee = 0
        if len(matched_booking) > 0:
            str_matched_booking = str(matched_booking).replace('[', '').replace(']', '')
            str_matched_booking = str_matched_booking if len(str_matched_booking) > 0 else '0'
            print ('str_matched_booking')
            print (str_matched_booking)

            select_query = "SELECT id, attendee_id, room_id, check_in, check_out, broken_up " \
                           " FROM bookings WHERE (check_in <= %(p_available_date)s AND room_id = %(p_room_id)s " \
                           " AND check_out > %(p_available_date)s AND NOT (id IN ("+str_matched_booking+")))"
            select_param = {
                'p_room_id': room_id,
                'p_available_date': allotment[3]
            }
            cursor.execute(select_query, select_param)
            # print ('here last execution')
            # print (cursor.statement)
            for result in cursor:
                count_unmatched_attendee += 1

        total = count_matched_pairs + count_matched_singles + count_unmatched_attendee
        available = allotment[2] - total
        print ('available here')
        print (available)
        return available

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def handle_actual_buddy(request, attendee_booking, actual_buddy_list, event_id, cursor, cnx=None):
        results = []
        # actual_buddy_list = actual_buddy_list.strip()
        if actual_buddy_list == "[REMOVE]":
            delete_query = "DELETE FROM match_line WHERE booking_id =" + str(attendee_booking[0])
            cursor.execute(delete_query)
            # cnx.commit()

            attendee_name = None
            select_query = "SELECT firstname, lastname FROM attendees WHERE id = " + str(attendee_booking[1])
            cursor.execute(select_query)
            for result in cursor:
                attendee_name = result
            results.append(
                "Match delete for " + attendee_name[0] + " " + attendee_name[1])
            return results

        # here 'x_result' was 'result' [ to avoid same name with cursor result ]
        x_result = {'success': False, 'message': 'Actual Buddy not updated'}

        # COMMENT START
        # actual_buddy_list = [x.strip() for x in actual_buddy_list.split(',')]
        # actual_buddy_list = list(filter(lambda abl: abl != '', actual_buddy_list))
        # COMMENT END

        select_query = ("SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id = " + str(attendee_booking))
        # id -> 0,  attendee_id -> 1, check_in -> 2, check_out -> 3, room_id -> 4, broken_up -> 5
        cursor.execute(select_query)
        attendee_booking = None
        for res in cursor:
            attendee_booking = res
        if not attendee_booking:
            return '**********Booking not found***********'

        all_pairable_bookings = [attendee_booking[0]]
        for attendee_email in actual_buddy_list:
            # attendee = Attendee.objects.filter(email=attendee_email).first()
            attendee = None
            select_query = "SELECT id, firstname, lastname FROM attendees WHERE email = '{}' AND event_id={}".format(attendee_email, event_id)
            cursor.execute(select_query)
            for result in cursor:
                print ('YYYYYYY')
                print (result)
                attendee = result

            if attendee:
                first_date = attendee_booking[2]
                last_date = attendee_booking[3]

                # my_booking = Booking.objects.filter(attendee_id=attendee.id)
                # my_booking = my_booking.filter(Q(
                #     Q(check_in__lte=first_date, check_out__gte=first_date) | Q(check_in__lte=last_date,
                #                                                                check_out__gte=last_date) | Q(
                #         check_in__gte=first_date, check_in__lte=last_date) | Q(check_out__gte=first_date,
                #                                                                check_out__lte=last_date)) & Q(
                #     room=attendee_booking.room))
                # [ here previous two query purpose cobined in next one query ]
                my_booking = []
                my_booking_id_list = []
                select_query = """SELECT id, attendee_id, room_id, check_in, check_out, broken_up FROM bookings WHERE
                                  (attendee_id = %(p_att_id)s AND ((check_in <= %(p_first_date)s AND
                                  check_out >= %(p_first_date)s) OR (check_in <= %(p_last_date)s AND
                                  check_out >= %(p_last_date)s) OR (check_in >= %(p_first_date)s AND check_in <= %(p_last_date)s)
                                  OR (check_out >= %(p_first_date)s AND check_out <= %(p_last_date)s))
                                  AND (room_id) IN (SELECT r.id FROM rooms r WHERE r.id = %(p_room_id)s))"""
                select_param = {
                    'p_att_id': attendee[0],
                    'p_first_date': first_date,
                    'p_last_date': last_date,
                    'p_room_id': attendee_booking[4]
                }
                cursor.execute(select_query, select_param)
                # print (cursor.statement)

                for result in cursor:
                    # print ('result')
                    # print (result)
                    my_booking.append(result)
                    my_booking_id_list.append(result[0])
                    all_pairable_bookings.append(result[0])

                # x_match = MatchLine.objects.filter(Q(booking_id__in=my_booking) | Q(booking_id=attendee_booking.id))
                x_match = []
                x_matchlines_id = []

                str_my_booking_id_list = str(my_booking_id_list).replace('[', '').replace(']', '')
                str_my_booking_id_list = str_my_booking_id_list if len(str_my_booking_id_list) > 0 else '0'

                select_query = "SELECT id, match_id, booking_id FROM match_line WHERE (booking_id IN " \
                               "( " + str_my_booking_id_list +" ) OR booking_id = %(p_booking_id)s)"
                cursor.execute(select_query, {'p_booking_id': attendee_booking[0]})
                # print (cursor.statement)

                for result in cursor:
                    x_match.append(result)
                    x_matchlines_id.append(result[0])

        print('len')
        print(len(all_pairable_bookings))
        if len(all_pairable_bookings) > 1:
            x_result = HotelLamda.pair_up_details(request, all_pairable_bookings, cursor, cnx)
        print(x_result)
        if x_result['success']:
            results.append(x_result['message'])
            print('x_matchlines_id')
            print(x_matchlines_id)
            if x_matchlines_id:
                # MatchLine.objects.filter(id__in=x_matchlines_id).delete()
                str_x_matchlines_id = str(x_matchlines_id).replace('[', '').replace(']', '')
                str_x_matchlines_id = str_x_matchlines_id if len(str_x_matchlines_id) > 0 else '0'
                delete_query = "DELETE FROM match_line WHERE id IN ("+str_x_matchlines_id+")"
                cursor.execute(delete_query)
                results.append(str(len(x_matchlines_id)) + " matchlines deleted.")
                # Delete Matches
                str_match_ids = [item[1] for item in x_match]
                str_match_ids = str(str_match_ids).replace('[', '').replace(']', '')
                str_match_ids = str_match_ids if len(str_match_ids) > 0 else '0'
                delete_query = "DELETE FROM matches WHERE id IN (" + str_match_ids + ")"
                cursor.execute(delete_query)
                results.append(str(len(str_match_ids)) + " matches deleted.")

            # cnx.commit()
        else:
            results.append(x_result['message'])
        return results

    @transaction.atomic
    def pair_up_details(request, booking_ids, cursor, cnx):
        # print(booking_ids)
        match_buddies = []
        response = {}
        if len(booking_ids) > 1:
            # first_booking = Booking.objects.get(pk=booking_ids[0])
            first_booking = None
            select_query = "SELECT b.id, b.attendee_id, b.check_in, b.check_out, b.room_id, b.broken_up, r.beds " \
                           " FROM bookings b inner join rooms r on b.room_id = r.id WHERE b.id = " + str(booking_ids[0])
            # id -> 0,  attendee_id -> 1, check_in -> 2, check_out -> 3, room_id -> 4, broken_up -> 5,  room.beds -> 6
            cursor.execute(select_query)
            for result in cursor:
                first_booking = result

            room_id = first_booking[4]
            # beds = first_booking.room.beds
            beds = first_booking[6]

            # bookings = Booking.objects.filter(id__in=booking_ids)
            bookings = []
            str_booking_ids = str(booking_ids).replace('[', '').replace(']', '')
            str_booking_ids = str_booking_ids if len(str_booking_ids) > 0 else '0'
            select_query = "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id IN ("+str_booking_ids+")"
            cursor.execute(select_query)
            for result in cursor:
                bookings.append(result)

            attendee_count = []
            all_pair_up_attendes = []
            for attendee_booking in bookings:
                all_pair_up_attendes.append(attendee_booking)
                if attendee_booking[1] not in attendee_count:
                    attendee_count.append(attendee_booking[1])

            if len(bookings) <= beds or len(attendee_count) <= beds:
                common_dates = HotelLamda.get_common_dates(bookings)
                # print(common_dates)
                if len(common_dates) > 0:
                    # room distribution checking
                    start_date = min(common_dates)
                    end_date = max(common_dates) + timedelta(days=1)

                    # previous_matches_room = Match.objects.filter(Q(room_id=room_id))
                    previous_matches_room = []
                    select_query = "SELECT id, start_date, end_date, room_id, all_dates FROM matches WHERE room_id = " + str(room_id)
                    cursor.execute(select_query)
                    for result in cursor:
                        previous_matches_room.append(result)

                    previous_total = len(previous_matches_room)
                    print('previous_total')
                    print(previous_total)
                    check_allotment = HotelLamda.check_allotment(request, room_id, common_dates, cursor, cnx)
                    if check_allotment:
                        all_dates = []
                        for my_date in common_dates:
                            all_dates.append(str(my_date))

                        # match = Match(room_id=room_id, start_date=start_date, end_date=end_date,
                        #               all_dates=json.dumps(all_dates))
                        # match.save()
                        insert_query = "INSERT INTO matches(room_id, start_date, end_date, all_dates) " \
                                       " VALUES (%(p_room_id)s,%(p_start_date)s,%(p_end_date)s,%(p_all_dates)s)"
                        insert_data = {
                            'p_room_id': room_id,
                            'p_start_date': start_date,
                            'p_end_date': end_date,
                            'p_all_dates': json.dumps(all_dates)
                        }
                        cursor.execute(insert_query, insert_data)
                        # cnx.commit()
                        new_match_id = cursor.lastrowid

                        date_time_now_str = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                        for booking in bookings:
                            # match_line = MatchLine(match=match, booking_id=booking.id)
                            # match_line.save()
                            insert_query = "INSERT INTO match_line(match_id,booking_id, created, updated) VALUES(%(p_match_id)s, %(p_booking_id)s, %(p_created)s, %(p_updated)s)"
                            cursor.execute(insert_query, {'p_match_id': new_match_id, 'p_booking_id': booking[0], 'p_created': date_time_now_str, 'p_updated': date_time_now_str})

                            # match_buddies.append(match_line.as_dict())
                            new_match_line_id = cursor.lastrowid
                            match_buddies.append(new_match_line_id)



                        response['success'] = True
                        response['message'] = 'Successfully paired up'

                        if len(match_buddies) > 1:
                            for match_attendee in match_buddies:
                                matchlist = match_buddies[:]
                                matchlist.remove(match_attendee)

                        context = {
                            'booking_list': all_pair_up_attendes
                        }
                        # pair_up_view = render_to_string('hotel/pair_up.html', context)
                        # response['view'] = pair_up_view
                    else:
                        response['success'] = False
                        response['message'] = 'Maximum number of paired up for this room given the time range'
                else:
                    response['success'] = False
                    response['message'] = 'No common date(s) to pair up'
            else:
                response['success'] = False
                response['message'] = 'Room capacity exceeds the selected bookings'
        else:
            response['success'] = False
            response['message'] = 'Select at least 2 attendees to pair up'
        return response

    @staticmethod
    def get_common_dates(booking_list):
        a_list = []
        all_dates = []
        attendee_dates = {}

        for booking in booking_list:
            key = 'a' + str(booking[1])
            if key not in attendee_dates:
                attendee_dates[key] = []

        for booking in booking_list:
            booking_check_in = booking[2]
            booking_check_out = booking[3]
            day_count = (booking_check_out - booking_check_in).days
            for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                all_dates.append(single_date)
                if 'a' + str(booking[1]) in attendee_dates:
                    attendee_dates['a' + str(booking[1])].append(single_date)
        for key in attendee_dates:
            a_list.append(attendee_dates[key])
        for i in range(0, len(a_list)):
            for j in range(1, len(a_list)):
                all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
        return all_dates

    def check_allotment(request, room_id, common_dates, cursor, cnx):
        check = True
        for c_dates in common_dates:
            # total_allotments = RoomAllotment.objects.filter(room_id=room_id, available_date=c_dates)
            total_allotments = []
            select_query = "SELECT id,allotments,available_date,room_id FROM room_allotments WHERE room_id=%(p_room_id)s AND available_date=%(p_c_dates)s"
            cursor.execute(select_query, {'p_room_id': room_id, 'p_c_dates': c_dates})
            for restult in cursor:
                total_allotments.append(restult)

            # matched_attendee = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
            #     count_match__gt=1, match__room_id=room_id)
            matched_attendee = []
            select_query = "SELECT match_line.match_id, COUNT(match_line.match_id) AS count_match FROM match_line " \
                           " INNER JOIN matches ON ( match_line.match_id = matches.id ) WHERE matches.room_id = %(p_room_id)s " \
                           " GROUP BY match_line.match_id HAVING COUNT(match_line.match_id) > 1 ORDER BY NULL"
            cursor.execute(select_query, {'p_room_id': room_id})
            for restult in cursor:
                matched_attendee.append(restult)

            # count_matched_pairs = matched_attendee.filter(match__start_date__lte=c_dates,
            #                                               match__end_date__gte=c_dates).count()
            count_matched_pairs = 0
            select_query = "SELECT COUNT(match_line.match_id) FROM match_line " \
                           " INNER JOIN matches ON ( match_line.match_id = matches.id ) WHERE " \
                           " (matches.room_id = %(p_room_id)s AND matches.end_date >= %(p_c_dates)s AND " \
                           " matches.start_date <= %(p_c_dates)s) GROUP BY match_line.match_id " \
                           " HAVING COUNT(match_line.match_id) > 1 ORDER BY NULL"
            cursor.execute(select_query, {'p_room_id': room_id, 'p_c_dates': c_dates})
            for restult in cursor:
                count_matched_pairs += 1

            match_id = []
            if len(matched_attendee) > 0:
                for match in matched_attendee:
                    match_id.append(match[0])

            # count_matched_singles = MatchLine.objects.values('match_id').annotate(count_match=Count('match_id')).filter(
            #     match_id__in=match_id, booking__check_in__lte=c_dates, booking__check_out__gte=c_dates).exclude(
            #     match__start_date__lte=c_dates, match__end_date__gte=c_dates).count()
            count_matched_singles = 0
            str_match_id = str(match_id).replace('[', '').replace(']', '')
            str_match_id = str_match_id if len(str_match_id) > 0 else '0'

            select_query = "SELECT COUNT(match_line.match_id) FROM match_line INNER JOIN matches ON " \
                           "( match_line.match_id = matches.id ) INNER JOIN bookings ON ( match_line.booking_id = bookings.id ) " \
                           " WHERE (match_line.match_id IN ("+str_match_id+") AND bookings.check_in <= %(p_c_dates)s " \
                           " AND bookings.check_out >= %(p_c_dates)s AND NOT (matches.start_date <= %(p_c_dates)s " \
                           " AND matches.end_date >= %(p_c_dates)s)) GROUP BY match_line.match_id ORDER BY NULL"
            cursor.execute(select_query, {'p_c_dates': c_dates})
            for restult in cursor:
                count_matched_singles += 1

            total = count_matched_pairs + count_matched_singles
            if total_allotments:
                total_remain = total_allotments[0][1] - total
                if total_remain < 1:
                    check = False
        return check

    def get_booking_common_dates(bookings, cursor):
        a_list = []
        all_dates = []
        if len(bookings) > 1:
            # booking_list = Booking.objects.filter(id__in=bookings)
            booking_list = []
            # str_booking_id_list = str(bookings).replace('[', '').replace(']', '')
            str_booking_id_list = ','.join(str(b) for b in bookings)
            str_booking_id_list = str_booking_id_list if len(str_booking_id_list) > 0 else '0'
            select_query = "SELECT id, attendee_id, check_in, check_out, room_id, broken_up FROM bookings WHERE id IN ({})".format(str_booking_id_list)
            cursor.execute(select_query)
            for result in cursor:
                booking_list.append(result)

            for booking in booking_list:
                booking_check_in = booking[2]
                booking_check_out = booking[3]
                day_count = (booking_check_out - booking_check_in).days + 1
                booking_date_list = []
                for single_date in (booking_check_in + timedelta(n) for n in range(day_count)):
                    booking_date_list.append(single_date)
                    all_dates.append(single_date)
                a_list.append(booking_date_list)

            for i in range(0, len(a_list)):
                for j in range(1, len(a_list)):
                    all_dates = set(all_dates) & set(a_list[i]) & set(a_list[j])
        return all_dates
