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
                    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
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
