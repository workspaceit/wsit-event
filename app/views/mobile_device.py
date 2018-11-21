import os
import json
import datetime
import boto3
import botocore

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from app.models import DeviceToken, Group, Attendee
from app.snsHelper import SNSHelper
from django.contrib.auth.hashers import check_password

session = SNSHelper()


@csrf_exempt
def storeDeviceToken(request):
    json_data = {}
    json_data['error'] = True
    json_data['message'] = 'Error: There was a missing or invalid parameter in the request'
    if request.method == 'GET' and 'os' in request.GET and 'token' in request.GET and 'unique_id' in request.GET and 'secret_key' in request.GET:
        os_type = request.GET['os']
        token = request.GET['token']
        unique_device_id = request.GET['unique_id']

        attendee = Attendee.objects.get(secret_key=request.GET['secret_key'])

        if os_type == '1':
            arn = 'arn:aws:sns:eu-west-1:347024549639:app/GCM/wsit-event'
        elif os_type == '2':
            if os.environ['ENVIRONMENT_TYPE'] == 'master':
                arn = 'arn:aws:sns:eu-west-1:347024549639:app/APNS/ios-em2'
            else:
                arn = 'arn:aws:sns:eu-west-1:347024549639:app/APNS_SANDBOX/ios-em2'
        else:
            JsonResponse(json_data)

        if DeviceToken.objects.filter(device_unique_id=unique_device_id).exists():
            mobile_device = DeviceToken.objects.get(device_unique_id=unique_device_id)
            if mobile_device.token != token:
                session.deleteEnpoint(mobile_device.arn_enpoint)
                response = session.createEnpoint(arn, token, unique_device_id)
                if not response['error']:
                    mobile_device.token = token
                    mobile_device.arn_enpoint = response['endpoint']
            if mobile_device.attendee != attendee:
                mobile_device.attendee = attendee
            mobile_device.save()
        else:
            response = session.createEnpoint(arn, token, unique_device_id)
            if response['error']:
                json_data['message'] = response['message']
                return JsonResponse(json_data)

            mobile_device = DeviceToken(
                device_unique_id=unique_device_id,
                token=token,
                os_type=os_type,
                arn_enpoint=response['endpoint'],
                attendee=attendee)
            mobile_device.save()

        json_data['error'] = False
        json_data['message'] = 'Seccessful!'

    return JsonResponse(json_data)


def SendMessage(request):
    json_data = {}
    json_data['error'] = {'status': False}
    json_data['message'] = 'Seccessful!'
    mobile_devices = DeviceToken.objects.filter(is_enable=True)
    for device in mobile_devices:
        endpoint = device.arn_enpoint
        endpointAttr = session.getEndpointAttr(endpoint)

        msg = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit,\\n sed do eiusmodtempor\\n incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

        if 'attributes' in endpointAttr:
            if endpointAttr['attributes']['Enabled']:
                if device.os_type == '1':
                    session.androidMessageJSON(endpoint, msg, 'Session Before')
                elif device.os_type == '2':
                    if 'ENVIRONMENT_TYPE' in os.environ:
                        if os.environ['ENVIRONMENT_TYPE'] == 'master':
                            session.iosMessageJSON(endpoint, msg)
                        else:
                            session.iosDevMessageJSON(endpoint, msg)
            else:
                device.is_enable = False
                device.save()

    return JsonResponse(json_data)


# def getRouteUser(request, secret_key):
#     json_data = {}
#     if request.method == 'GET' and 'email' in request.GET:
#         email = request.GET['email']
#         if Attendee.objects.filter(secret_key=secret_key, email=email).exists():
#             user = Attendee.objects.get(secret_key=secret_key)
#
#             json_data['error'] = False
#             json_data['routeURL'] = user.event.url
#             json_data['push_notification_status'] = user.push_notification_status
#         else:
#             json_data['error'] = True
#             json_data['Message'] = "Secret Key Doesn't Exists"
#         return JsonResponse(json_data)
#
#     json_data['error'] = True
#     json_data['Message'] = "Invalid email!"
#     return JsonResponse(json_data)

def getRouteUser(request, secret_key):
    json_data = {}
    if request.method == 'GET' and 'email' in request.GET:
        email = request.GET['email']
        attendee_info = Attendee.objects.filter(email=email)
        if attendee_info.exists():
            check_flag = False
            for attendee in attendee_info:
                if check_password(secret_key, attendee.password):
                    check_flag = True
                    json_data['error'] = False
                    json_data['routeURL'] = attendee.event.url
                    json_data['push_notification_status'] = attendee.push_notification_status
                    json_data['secret_key'] = attendee.secret_key
                    return JsonResponse(json_data)
            if not check_flag:
                json_data['error'] = True
                json_data['Message'] = "Password Doesn't Exists"
                return JsonResponse(json_data)
        else:
            json_data['error'] = True
            json_data['Message'] = "Email Doesn't Exists"
            return JsonResponse(json_data)
    else:
        json_data['error'] = True
        json_data['Message'] = "Invalid email!"
        return JsonResponse(json_data)


def push_notification():
    next_hour = timezone.now() + datetime.timedelta(hours=1)
    next_hour_minute = timezone.now() + datetime.timedelta(hours=1, minutes=1)
    json_data = {}
    json_data['error'] = True
    json_data['message'] = 'Have something wrong!'
    groups = Group.objects.all()
    for group in groups:
        for session in group.session_set.filter(start__range=(next_hour, next_hour_minute)):
            for attendee in group.attendee_set.filter(devicetoken__isnull=False):
                for devicetoken in attendee.devicetoken_set.filter(is_enable=True):
                    endpoint = devicetoken.arn_enpoint
                    endpointAttr = session.getEndpointAttr(endpoint)

                    msg = 'Session {} will be start on {}'.format(session.name, session.start)
                    url = group.event.url

                    if 'attributes' in endpointAttr:
                        if endpointAttr['attributes']['Enabled']:
                            if devicetoken.os_type == '1':
                                session.androidMessageJSON(endpoint, msg, session.name, url)
                            elif devicetoken.os_type == '2':
                                if 'ENVIRONMENT_TYPE' in os.environ:
                                    if os.environ['ENVIRONMENT_TYPE'] == 'master':
                                        response = session.iosMessageJSON(endpoint, msg, url)
                                    else:
                                        response = session.iosDevMessageJSON(endpoint, msg, url)
                        else:
                            devicetoken.is_enable = False
                            devicetoken.save()
                    else:
                        devicetoken.is_enable = False
                        devicetoken.save()
