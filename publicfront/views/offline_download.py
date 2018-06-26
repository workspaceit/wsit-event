from django.shortcuts import render, redirect
from django.http import HttpResponse
from app.models import Attendee, Answers, SeminarsUsers, SeminarSpeakers, Session, ActivityHistory, PageContent, \
    PagePermission, EmailTemplates, DeviceToken, Booking, TravelAttendee, Travel, Session, Hotel, Room, Group, \
    MatchLine, RequestedBuddy
from django.views.generic import TemplateView
import zipfile
import io
from boto3.session import Session as boto_session
import boto
from django.conf import settings
import os, json, re
from publicfront.views.page2 import DynamicPage
from datetime import datetime, timedelta
from django.db.models import Q

from publicfront.views.page_replace import PageReplace


class OfflineExport(TemplateView):
    def download_offline_file(request, *args, **kwargs):
        if 'uid' not in request.GET or 'deviceid' not in request.GET:
            resp = HttpResponse()
            resp.status_code = 400
            resp['message'] = 'Bad Request'
            return resp

        else:
            print('ok')
            secret_key = request.GET.get('uid')
            attendee = Attendee.objects.filter(secret_key=secret_key)
            if attendee.exists():
                device_id = request.GET.get('deviceid')
                force_download = False
                download = False
                if 'forceDownload' in request.GET:
                    force_download_value = request.GET.get('forceDownload')
                    if force_download_value == 'true':
                        force_download = True
                    elif force_download_value == 'false':
                        force_download = False

                device_info = DeviceToken.objects.filter(device_unique_id=device_id)
                if device_info.exists():
                    if device_info[0].offline_pakage_status:
                        download = True
                    elif force_download:
                        download = True
                    else:
                        download = False

                    # START
                    if download:
                        session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                               region_name='eu-west-1')
                        client = session.client('s3')

                        key = 'public/non-essential-images/EventDobby-Logo.png'
                        response = client.get_object(Bucket='event-manager2-develop', Key=key)
                        event_logo = response['Body'].read()

                        key = 'public/wsit-event-test/files/Test 7.jpg'
                        response = client.get_object(Bucket='event-manager2-develop', Key=key)
                        img1 = response['Body'].read()

                        key = 'public/wsit-event-test/files/photo-reel/14840472683166.PNG'
                        response = client.get_object(Bucket='event-manager2-develop', Key=key)
                        img2 = response['Body'].read()

                        key = 'public/wsit-event-test/compiled_css/style.css'
                        response = client.get_object(Bucket='event-manager2-develop', Key=key)
                        style = response['Body'].read()

                        pages = OfflineExport.render_static_page(request, *args, **kwargs)
                        page_contents = []

                        for page in pages:
                            template = EmailTemplates.objects.get(id=page.template_id)
                            page_content = template.content.replace('{content}', page.content)
                            page_content = page_content.replace('[[static]]public/[[event_url]]/compiled_css/',
                                                                'files/')
                            page_content = page_content.replace('[[parmanent]]non-essential-images/', 'files/')
                            page_content = page_content.replace('[[parmanent]]wsit-event-test/files/', 'files/')
                            page_content = page_content.replace('[[parmanent]]wsit-event-test/files/photo-reel/',
                                                                'files/')
                            page_content = page_content.replace('<!-- JSCRIPTS BELOW -->', """<script
                          src="https://code.jquery.com/jquery-3.1.1.min.js"
                          integrity="sha256-hVVnYaiADRTO2PzUGmuLJr8BLUSjGIZsDYGmIJLv2b8="
                          crossorigin="anonymous"></script>""")
                            page_content = page_content.replace('{menu}', """<input id="mobile-menu-trigger" type="checkbox">
                                <label id="mobile-menu-trigger-label" for="mobile-menu-trigger"></label>
                                <ul class="menu">
                                        <li >
                                                <a href="test_offline_page.html"
                                                   class="start  "
                                                   data-url="">Page 1</a>
                                        </li>
                                        >
                                        <li >
                                                <a href="test_offline_page2.html"
                                                   class="start  "
                                                   data-url="">Page 2</a>
                                        </li>

                                </ul>""")

                            page_content = PageReplace.replace_answers(request, page_content)
                            page_content = PageReplace.replace_sessions(request, page_content)
                            page_content = PageReplace.replace_travels(request, page_content)
                            page_content = PageReplace.replace_hotels(request, page_content)
                            page_content = PageReplace.replace_general_tags(request, page_content)
                            page_content = PageReplace.replace_questions_variable(request, page_content)

                            page_contents.append(page_content)

                        try:
                            s = io.BytesIO()
                            zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED)

                            zf.writestr("files/style.css", style)
                            zf.writestr("files/Test 7.jpg", img1)
                            zf.writestr("files/14840472683166.PNG", img2)
                            zf.writestr("files/EventDobby-Logo.png", event_logo)
                            zf.writestr("test_offline_page.html", page_contents[0])
                            zf.writestr("test_offline_page2.html", page_contents[1])

                            zf.close()
                            downloadCount = device_info[0].package_download_count + 1
                            DeviceToken.objects.filter(device_unique_id=device_id).update(offline_pakage_status=0,
                                                                                          package_download_count=downloadCount)
                            msg = "Offline package updated # " + str(downloadCount)
                            activity = ActivityHistory(attendee_id=attendee[0].id, activity_type="update",
                                                       category="package", event_id=attendee[0].event.id, new_value=msg)
                            activity.save()
                            resp = HttpResponse(s.getvalue(), content_type="application/x-tar-gz")
                            resp['Content-Disposition'] = 'attachment; filename=%s' % 'offline.tar.gz'
                            resp.status_code = 200
                            resp['message'] = 'Offline package downloaded successfully'
                            resp['version'] = '1.0'
                            return resp
                        except:
                            resp = HttpResponse()
                            resp.status_code = 500
                            resp['message'] = 'Something went wrong'
                            return resp

                    else:
                        resp = HttpResponse()
                        resp.status_code = 304
                        resp['message'] = 'You have already downloaded the updated package'
                        return resp
                else:
                    resp = HttpResponse()
                    resp.status_code = 404
                    resp['message'] = 'Device Not found'
                    return resp
            else:
                resp = HttpResponse()
                resp.status_code = 401
                resp['message'] = 'User not found'
                return resp

    def get_my_qr_page(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            attendee_id = request.session['event_user']['id']
            secret_key = Attendee.objects.get(pk=attendee_id).secret_key
            watching_x_men = SeminarsUsers.objects.filter(session_id=163, attendee_id=attendee_id, status='attending')

            watching = False
            if watching_x_men.exists():
                watching = True
            context = {
                'secret_key': secret_key,
                'offline': True,
                'watching': watching
            }
            my_qr_page = render(request, 'public/offline/MY_QR_CODE.html', context)
            return my_qr_page

    def get_myHotelContext(request, *args, **kwargs):

        if request.session['event_user']['attending'] == "Yes":
            attendee = request.session['event_user']['id']
            actual_flights_answers = Answers.objects.filter(user_id=attendee,
                                                            question__group__name__contains='Actual flights').order_by(
                'question__question_order')
            # if actual_flights.exists():
            actual_flights = []
            actual_hotels = []
            i = 1
            while i < 5:
                for answer in actual_flights_answers:
                    question_to_match = 'Outbound (' + str(i) + ') departure city'
                    if question_to_match == answer.question.title:
                        outbound_dep_date = outbound_dep_time = outbound_ar_city = outbound_ar_date = outbound_ar_time = \
                            outbound_booking_ref = outbound_flight_number = ''

                        outbound_dep_date_question = 'Outbound (' + str(i) + ') departure date'
                        outbound_dep_time_question = 'Outbound (' + str(i) + ') departure time'
                        outbound_ar_city_question = 'Outbound (' + str(i) + ') arrival city'
                        outbound_ar_date_question = 'Outbound (' + str(i) + ') arrival date'
                        outbound_ar_time_question = 'Outbound (' + str(i) + ') arrival time'
                        outboound_booking_ref_question = 'Outbound (' + str(i) + ') booking reference'
                        outbound_flight_number_question = 'Outbound (' + str(i) + ') flight number'

                        outbound_date_answer = actual_flights_answers.filter(
                            question__title=outbound_dep_date_question)
                        if outbound_date_answer.exists():
                            outbound_dep_date = outbound_date_answer[0].value

                        outbound_time_answer = actual_flights_answers.filter(
                            question__title=outbound_dep_time_question)
                        if outbound_time_answer.exists():
                            outbound_dep_time = outbound_time_answer[0].value

                        outbound_ar_city = actual_flights_answers.filter(question__title=outbound_ar_city_question)
                        if outbound_ar_city.exists():
                            outbound_ar_city = outbound_ar_city[0].value

                        outbound_ar_date_answer = actual_flights_answers.filter(
                            question__title=outbound_ar_date_question)
                        if outbound_ar_date_answer.exists():
                            outbound_ar_date = outbound_ar_date_answer[0].value

                        outbound_ar_time_answer = actual_flights_answers.filter(
                            question__title=outbound_ar_time_question)
                        if outbound_ar_time_answer.exists():
                            outbound_ar_time = outbound_ar_time_answer[0].value

                        outbound_booking_answer = actual_flights_answers.filter(
                            question__title=outboound_booking_ref_question)
                        if outbound_booking_answer.exists():
                            outbound_booking_ref = outbound_booking_answer[0].value

                        outbound_flight_number_answer = actual_flights_answers.filter(
                            question__title=outbound_flight_number_question)
                        if outbound_flight_number_answer.exists():
                            outbound_flight_number = outbound_flight_number_answer[0].value

                        actual_flights.append({
                            'dep_city': answer.value,
                            'dep_date': outbound_dep_date,
                            'dep_time': outbound_dep_time,
                            'ar_city': outbound_ar_city,
                            'ar_date': outbound_ar_date,
                            'ar_time': outbound_ar_time,
                            'booking_ref': outbound_booking_ref,
                            'flight_number': outbound_flight_number
                        })
                i = i + 1

            i = 1
            while i < 5:
                for answer in actual_flights_answers:
                    question_to_match_1 = 'Homebound (' + str(i) + ') departure city'
                    if question_to_match_1 == answer.question.title:
                        outbound_dep_date = outbound_dep_time = outbound_ar_city = outbound_ar_date = outbound_ar_time = \
                            outbound_booking_ref = outbound_flight_number = ''

                        outbound_dep_date_question = 'Homebound (' + str(i) + ') departure date'
                        outbound_dep_time_question = 'Homebound (' + str(i) + ') departure time'
                        outbound_ar_city_question = 'Homebound (' + str(i) + ') arrival city'
                        outbound_ar_date_question = 'Homebound (' + str(i) + ') arrival date'
                        outbound_ar_time_question = 'Homebound (' + str(i) + ') arrival time'
                        outboound_booking_ref_question = 'Homebound (' + str(i) + ') booking reference'
                        outbound_flight_number_question = 'Homebound (' + str(i) + ') flight number'

                        outbound_date_answer = actual_flights_answers.filter(
                            question__title=outbound_dep_date_question)
                        if outbound_date_answer.exists():
                            outbound_dep_date = outbound_date_answer[0].value

                        outbound_time_answer = actual_flights_answers.filter(
                            question__title=outbound_dep_time_question)
                        if outbound_time_answer.exists():
                            outbound_dep_time = outbound_time_answer[0].value

                        outbound_ar_city = actual_flights_answers.filter(question__title=outbound_ar_city_question)
                        if outbound_ar_city.exists():
                            outbound_ar_city = outbound_ar_city[0].value

                        outbound_ar_date_answer = actual_flights_answers.filter(
                            question__title=outbound_ar_date_question)
                        if outbound_ar_date_answer.exists():
                            outbound_ar_date = outbound_ar_date_answer[0].value

                        outbound_ar_time_answer = actual_flights_answers.filter(
                            question__title=outbound_ar_time_question)
                        if outbound_ar_time_answer.exists():
                            outbound_ar_time = outbound_ar_time_answer[0].value

                        outbound_booking_answer = actual_flights_answers.filter(
                            question__title=outboound_booking_ref_question)
                        if outbound_booking_answer.exists():
                            outbound_booking_ref = outbound_booking_answer[0].value

                        outbound_flight_number_answer = actual_flights_answers.filter(
                            question__title=outbound_flight_number_question)
                        if outbound_flight_number_answer.exists():
                            outbound_flight_number = outbound_flight_number_answer[0].value

                        actual_flights.append({
                            'dep_city': answer.value,
                            'dep_date': outbound_dep_date,
                            'dep_time': outbound_dep_time,
                            'ar_city': outbound_ar_city,
                            'ar_date': outbound_ar_date,
                            'ar_time': outbound_ar_time,
                            'booking_ref': outbound_booking_ref,
                            'flight_number': outbound_flight_number
                        })
                i = i + 1
            actual_hotel_answers = Answers.objects.filter(user_id=attendee,
                                                          question__group__name__contains='Actual hotel')
            hotel_name = check_in = check_out = room_buddy = ''
            has_hotel = False
            for actual_hotel_answer in actual_hotel_answers:
                if 'Hotel name' == actual_hotel_answer.question.title:
                    hotel_name = actual_hotel_answer.value
                    has_hotel = True
                elif 'Check-in' == actual_hotel_answer.question.title:
                    check_in = actual_hotel_answer.value
                elif 'Check-out' == actual_hotel_answer.question.title:
                    check_out = actual_hotel_answer.value
                elif 'Room buddy' == actual_hotel_answer.question.title:
                    room_buddy = actual_hotel_answer.value
            if has_hotel:
                actual_hotels.append({
                    'hotel_name': hotel_name,
                    'check_in': check_in,
                    'check_out': check_out,
                    'buddy': room_buddy
                })

            transfers = Answers.objects.filter(user_id=attendee,
                                               question__group__name__icontains='Transfer')

            context = {
                'actual_flights': actual_flights,
                'actual_hotels': actual_hotels,
                'transfers': transfers
            }
            my_flights_hotel = render(request, 'public/offline/My_Flights_Hotels.html', context)
            return my_flights_hotel

    def get_funky_page(request, *args, **kwargs):
        my_day_one_page = ""
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                if os.environ['ENVIRONMENT_TYPE'] == 'master':
                    question_id = 233
                elif os.environ['ENVIRONMENT_TYPE'] == 'staging':
                    question_id = 232
                elif os.environ['ENVIRONMENT_TYPE'] == 'develop':
                    question_id = 232
                else:
                    question_id = 273
                user_id = request.session['event_user']['id']
                funky_meet = Answers.objects.filter(question_id=question_id, user_id=user_id)
                funky_answer = ""
                if funky_meet.exists():
                    funky_answer = funky_meet[0].value
                context = {
                    'funky_answer': funky_answer
                }
                my_day_one_page = render(request, 'public/offline/MY_DAY_ONE_FUNKIES.html', context)
        return my_day_one_page

    def render_static_page(request, *args, **kwargs):
        pages = [DynamicPage.get_object(request, 'test-offline-page'),
                 DynamicPage.get_object(request, 'test-offline-page2')]
        return pages

    def new_download_offline_file(request, *args, **kwargs):
        try:
            if 'uid' not in request.GET or 'deviceid' not in request.GET:
                resp = HttpResponse()
                resp.status_code = 400
                resp['message'] = 'Bad Request'
                return resp

            else:
                secret_key = request.GET.get('uid')
                attendee = Attendee.objects.filter(secret_key=secret_key)
                if attendee.exists():
                    device_id = request.GET.get('deviceid')
                    force_download = False
                    download = False
                    if 'forceDownload' in request.GET:
                        force_download_value = request.GET.get('forceDownload')
                        if force_download_value == 'true':
                            force_download = True
                        elif force_download_value == 'false':
                            force_download = False

                    device_info = DeviceToken.objects.filter(device_unique_id=device_id, attendee_id=attendee[0].id)
                    if device_info.exists():
                        if device_info[0].offline_pakage_status:
                            download = True
                        elif force_download:
                            download = True
                        else:
                            download = False

                        # START
                        if download:
                            # pages = OfflineExport.render_static_page(request, *args, **kwargs)
                            url = os.getcwd() + "/publicfront/templates/public/offline_pages/"
                            index = open(url + "index.html", "r")
                            hotel = open(url + "hotel.html", "r")
                            team = open(url + "team.html", "r")
                            travel = open(url + "travel.html", "r")
                            # style = open(url+"style.css", "r").read()

                            session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                                   region_name='eu-west-1')
                            client = session.client('s3')

                            key = 'public/offline-images/agenda.png'
                            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            agenda_image = response['Body'].read()
                            key = 'public/offline-images/hotel.png'
                            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            hotel_image = response['Body'].read()
                            key = 'public/offline-images/logo.png'
                            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            logo_image = response['Body'].read()
                            key = 'public/offline-images/team.png'
                            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            team_image = response['Body'].read()
                            key = 'public/offline-images/travel.png'
                            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            travel_image = response['Body'].read()

                            key = 'public/css/temp_offline.css'
                            response = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                            style = response['Body'].read()

                            pages = [index.read(), hotel.read(), team.read(), travel.read()]
                            page_contents = []

                            for page in pages:
                                page_content = page
                                page_content = PageReplace.replace_answers(request, page_content)
                                page_content = PageReplace.replace_sessions(request, page_content)
                                page_content = PageReplace.replace_travels(request, page_content)
                                page_content = PageReplace.replace_hotels(request, page_content)
                                page_content = PageReplace.replace_general_tags(request, page_content)
                                page_content = PageReplace.replace_questions_variable(request, page_content)

                                page_contents.append(page_content)

                            try:
                                s = io.BytesIO()
                                zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED)

                                zf.writestr("img/agenda.png", agenda_image)
                                zf.writestr("img/hotel.png", hotel_image)
                                zf.writestr("img/logo.png", logo_image)
                                zf.writestr("img/team.png", team_image)
                                zf.writestr("img/travel.png", travel_image)
                                zf.writestr("style.css", style)
                                zf.writestr("index.html", page_contents[0])
                                zf.writestr("hotel.html", page_contents[1])
                                zf.writestr("team.html", page_contents[2])
                                zf.writestr("travel.html", page_contents[3])

                                zf.close()
                                downloadCount = device_info[0].package_download_count + 1
                                DeviceToken.objects.filter(device_unique_id=device_id).update(offline_pakage_status=0,
                                                                                              package_download_count=downloadCount)
                                msg = "Offline package updated # " + str(downloadCount)
                                activity = ActivityHistory(attendee_id=attendee[0].id, activity_type="update",
                                                           category="package", event_id=attendee[0].event.id,
                                                           new_value=msg)
                                activity.save()
                                resp = HttpResponse(s.getvalue(), content_type="application/x-tar-gz")
                                resp['Content-Disposition'] = 'attachment; filename=%s' % 'offline.tar.gz'
                                resp.status_code = 200
                                resp['message'] = 'Offline package downloaded successfully'
                                resp['version'] = '1.0'
                                return resp
                            except:
                                resp = HttpResponse()
                                resp.status_code = 500
                                resp['message'] = 'Something went wrong'
                                return resp

                        else:
                            resp = HttpResponse()
                            resp.status_code = 304
                            resp['message'] = 'You have already downloaded the updated package'
                            return resp

                    else:
                        resp = HttpResponse()
                        resp.status_code = 404
                        resp['message'] = 'Device Not found'
                        return resp
                else:
                    resp = HttpResponse()
                    resp.status_code = 401
                    resp['message'] = 'User not found'
                    return resp
        except Exception as e:
            print(e)
            resp = HttpResponse('Something went wrong', content_type='application/json')
            return resp

    def check_available_offline_package(request, last_package_created):
        attendee_id = request.session['event_user']['id']
        new_package = False
        if Attendee.objects.filter(updated__gt=last_package_created, id=attendee_id).exists():
            new_package = True
            return new_package
        if SeminarsUsers.objects.filter(updated__gt=last_package_created, attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if SeminarSpeakers.objects.filter(updated__gt=last_package_created, speaker_id=attendee_id).exists():
            new_package = True
            return new_package
        if TravelAttendee.objects.filter(updated__gt=last_package_created, attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if Booking.objects.filter(updated__gt=last_package_created, attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if Session.objects.filter(
                        Q(Q(seminarspeakers__speaker_id=attendee_id) | Q(seminarsusers__attendee_id=attendee_id)) & Q(
                        updated__gt=last_package_created)).exists():
            new_package = True
            return new_package
        if Travel.objects.filter(updated__gt=last_package_created, travelattendee__attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if Room.objects.filter(updated__gt=last_package_created, booking__attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if Hotel.objects.filter(updated__gt=last_package_created, room__booking__attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if Group.objects.filter(Q(updated__gt=last_package_created) & Q(Q(attendeegroups__attendee_id=attendee_id)
                                                                                | Q(
                    session__seminarspeakers__speaker_id=attendee_id)
                                                                                | Q(
                    session__seminarsusers__attendee_id=attendee_id)
                                                                                | Q(
                    hotel__room__booking__attendee_id=attendee_id)
                                                                                | Q(
                    questions__answers__user_id=attendee_id)
                                                                                | Q(
                    travel__travelattendee__attendee_id=attendee_id)
                                                                        )).exists():
            new_package = True
            return new_package
        if RequestedBuddy.objects.filter(updated__gt=last_package_created, booking__attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        if MatchLine.objects.filter(updated__gt=last_package_created, booking__attendee_id=attendee_id).exists():
            new_package = True
            return new_package
        return new_package

    def s3_offline_package(request, *args, **kwargs):
        try:
            if 'uid' not in request.GET or 'deviceid' not in request.GET:
                resp = HttpResponse()
                resp.status_code = 400
                resp['message'] = 'Bad Request'
                return resp

            else:
                secret_key = request.GET.get('uid')
                attendee = Attendee.objects.get(secret_key=secret_key)
                device_id = request.GET.get('deviceid')
                force_download = False
                download = False
                if 'forceDownload' in request.GET:
                    force_download_value = request.GET.get('forceDownload')
                    if force_download_value == 'true':
                        force_download = True
                    elif force_download_value == 'false':
                        force_download = False

                device_info = DeviceToken.objects.get(device_unique_id=device_id, attendee_id=attendee.id)
                if device_info.package_created_at:
                    if device_info.offline_pakage_status or OfflineExport.check_available_offline_package(request,
                                                                                                          device_info.package_created_at):
                        download = True
                    elif force_download:
                        download = True
                    else:
                        download = False
                else:
                    download = True

                if download:
                    event_url = attendee.event.url
                    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                    url = "public/" + event_url + "/files/offline_package"

                    html_list = []
                    css_list = []
                    js_list = []
                    image_list = []
                    others = []
                    image_formats = ['jpeg', 'jpg', 'png', 'gif', 'svg', 'bmp', 'tiff']

                    files = bucket.list(prefix=url)
                    for file in files:
                        if file.name.endswith('/'):
                            continue
                        extension = file.name.split('.')
                        extension = extension[len(extension) - 1].lower()
                        if extension in ['html', 'htm']:
                            # print('html found')
                            html_list.append(file)
                        elif extension == 'css':
                            css_list.append(file)
                        elif extension == 'js':
                            js_list.append(file)
                        elif extension in image_formats:
                            image_list.append(file)
                        else:
                            others.append(file)

                    try:
                        s = io.BytesIO()
                        zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED)
                        for html in html_list:
                            page_content = html.read().decode("utf-8")
                            page_content = OfflineExport.replace_image_src(page_content)
                            page_content = PageReplace.replace_answers(request, page_content)
                            page_content = PageReplace.replace_sessions(request, page_content)
                            page_content = PageReplace.replace_travels(request, page_content)
                            page_content = PageReplace.replace_hotels(request, page_content)
                            page_content = PageReplace.replace_general_tags(request, page_content)
                            page_content = PageReplace.replace_questions_variable(request, page_content)
                            html_name = html.name.split('/')
                            html_name = html_name[len(html_name) - 1]
                            zf.writestr(html_name, page_content)
                        for css in css_list:
                            css_name = css.name.split('/')
                            css_name = css_name[len(css_name) - 1]
                            zf.writestr(css_name, css.read())
                        for js in js_list:
                            js_name = js.name.split('/')
                            js_name = js_name[len(js_name) - 1]
                            zf.writestr(js_name, js.read())
                        for image in image_list:
                            image_name = image.name.split('/')
                            # if you change 'image/' directory then you have to change 'image/' in replace_img_src as well
                            image_name = 'image/' + image_name[len(image_name) - 1]
                            zf.writestr(image_name, image.read())

                        zf.close()
                        downloadCount = device_info.package_download_count + 1
                        versionCount = device_info.package_version + 1
                        package_created_at = datetime.now()
                        DeviceToken.objects.filter(device_unique_id=device_id).update(offline_pakage_status=0,
                                                                                      package_created_at=package_created_at,
                                                                                      package_download_count=downloadCount,
                                                                                      package_version=versionCount)
                        msg = "Offline package updated # " + str(downloadCount)
                        activity = ActivityHistory(attendee_id=attendee.id, activity_type="update",
                                                   category="package", event_id=attendee.event.id,
                                                   new_value=msg)
                        activity.save()

                        resp = HttpResponse(s.getvalue(), content_type="application/x-tar-gz")
                        resp['Content-Disposition'] = 'attachment; filename=%s' % 'offline.tar.gz'
                        resp.status_code = 200
                        resp['message'] = 'Offline package downloaded successfully'
                        resp['version'] = str(versionCount) + '.0'
                        return resp
                    except:
                        resp = HttpResponse()
                        resp.status_code = 500
                        resp['message'] = 'Something went wrong'
                        return resp
                else:
                    resp = HttpResponse()
                    resp.status_code = 304
                    resp['message'] = 'You have already downloaded the updated package'
                    return resp
        except Exception as e:
            print(e)
            resp = HttpResponse('Something went wrong', content_type='application/json')
            return resp

    def replace_image_src(page_content):
        """ this is for image src replacing method
            here we get all img tags, and replace those part with some text like 'IMAGE-TAG-RE'
            then again get only src of those tag by iterating them
            and replaced with provided src
            note: if there is any direct link as src in img tag, then it's been ignored.
         """
        regex = r"""<img.*?src.*?=.*?(\"|\').*?(\"|\')"""
        src_list = []
        result = re.finditer(regex, page_content, re.DOTALL)
        # to get all img tags
        page_content = re.sub(regex, "IMAGE-TAG-RE", page_content)

        for x in result:
            src_list.append(x.group(0))

        regex = r"""src.*?=.*?(\'|\").*?(\'|\")"""
        link_regex = r"""http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""
        i = 0
        for src in src_list:
            # to ignore direct image link
            if re.search(link_regex, src, re.M | re.I):
                i += 1
                continue
            # to get only src of the tag
            image_src = re.sub(regex, "IMAGE-SRC", src)
            somelsit = src.split('/')
            image = somelsit[len(somelsit) - 1][:-1]
            image = 'src="image/' + image + '"'
            src_list[i] = image_src.replace('IMAGE-SRC', image)
            i += 1

        i = 0
        for img_tag in src_list:
            page_content = page_content.replace('IMAGE-TAG-RE', src_list[i], 1)
            i += 1
        return page_content
