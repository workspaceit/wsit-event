import boto3
import json
import botocore
from django.conf import settings

class SNSHelper():

    """docstring for SNSHelper"""
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='eu-west-1')
        self.sns_resource = self.session.resource('sns')
        self.sns_client = self.session.client('sns')

    def setSession(self,aws_access_key_id, secret_access_key, region='eu-west-1'):
        self.session = boto3.Session(
            aws_access_key_id = aws_access_key_id,
            aws_secret_access_key = secret_access_key,
            region_name = region)

    def listEndpoints(self, arn):
        try:
            response = self.sns_client.list_endpoints_by_platform_application(PlatformApplicationArn=arn)
            return {'error': False, 'response': response['Endpoints']}
        except botocore.exceptions.ClientError as e:
            return {'error': True, 'message': e}

    def getEndpointAttr(self, endpoint):
        try:
            response = self.sns_client.get_endpoint_attributes(EndpointArn=endpoint)
            return {'error': False, 'attributes': response['Attributes']}
        except botocore.exceptions.ClientError as e:
            return {'error': True, 'message': e}

    def createEnpoint(self, arn, token, unique_device_id):
        try:
            response = self.sns_client.create_platform_endpoint(
                PlatformApplicationArn=arn,
                Token=token,
                CustomUserData=unique_device_id
            )
            return {'error': False, 'endpoint': response['EndpointArn']}
        except botocore.exceptions.ClientError as e:
            return {'error': True, 'message': e}

    def editEnpoint(self, endpoint, token):
        try:
            self.sns_client.set_endpoint_attributes(
                EndpointArn = endpoint,
                Attributes = {
                    'Token': token,
                    'Enabled': True
                })
            return True
        except botocore.exceptions.ClientError as e:
            return False

    def deleteEnpoint(self, endpoint):
        try:
            self.sns_client.delete_endpoint(EndpointArn=endpoint)
            return True
        except botocore.exceptions.ClientError as e:
            return False

    def androidMessageJSON(self, endpoint, msg, title, url=""):
        json_msg = json.dumps({"GCM": "{ \"data\": { \"message\": \"" + msg + "\", \"url\":\"" + url + "\", \"title\": \"" + title + "\" } }"})
        return self.sendNotification(self.sns_resource.PlatformEndpoint(endpoint), json_msg)

    def iosMessageJSON(self, endpoint, msg, url=""):
        json_msg = json.dumps({"APNS": "{ \"aps\": { \"alert\": \"" + msg + "\", \"url\":\"" + url + "\" } }"})
        return self.sendNotification(self.sns_resource.PlatformEndpoint(endpoint), json_msg)

    def iosDevMessageJSON(self, endpoint, msg, url=""):
        json_msg = json.dumps({"APNS_SANDBOX": "{ \"aps\": { \"alert\": \"" + msg + "\", \"url\":\"" + url + "\" } }"})
        return self.sendNotification(self.sns_resource.PlatformEndpoint(endpoint), json_msg)

    def sendNotification(self, endpoint, json_message):
        try:
            response = endpoint.publish(
                MessageStructure= 'json',
                Message=json_message
            )
            return True
        except botocore.exceptions.ClientError as e:
            return False