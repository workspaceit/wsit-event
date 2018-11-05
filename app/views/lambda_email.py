import boto
import boto.ses
import boto.sqs
import json
from django.conf import settings


def myfunc(event, context):
    print('----------------- Starts -----------------')
    access_key = settings.SMTP_USERNAME
    secret_key = settings.SMTP_PASSWORD
    region = settings.SES_REGION
    conn = boto.sqs.connect_to_region('eu-west-1', aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key)
    queue = conn.get_queue('test_email_queue')
    msg = queue.get_messages()

    while len(msg) > 0:
        try:
            data = json.loads(msg[0].get_body())
            mail_template_send(
                data['template'],
                data['subject'],
                data['to'],
                data['sender'],
                data['environment'],
                data['local_env']
            )
            queue.delete_message(msg[0])
        except:
            print('exception occurred')
        msg = queue.get_messages()

    print('----------------- Ends -----------------')
    return


def mail_template_send(context, subject, to, sender_mail, environment, settings_local_env):

    html_content = context

    if environment == 'master' or environment == 'staging':
        email = Mailer(subject=subject, to='support@springconf.com', from_addr = sender_mail)
        email.send(html_content, settings_local_env)
        email = Mailer(subject=subject, to=to, from_addr = sender_mail)
        email.send(html_content, settings_local_env)
    elif environment == 'develop':
        email = Mailer(subject=subject, to='workspaceinfotech@gmail.com', from_addr = sender_mail)
        # email = Mailer(subject=subject,to='joakim@springconf.com',from_addr = sender_mail)
        email.send(html_content, settings_local_env)
    else:
        email = Mailer(subject=subject,to='workspaceinfotech@gmail.com',from_addr = sender_mail)
        # email = Mailer(subject=subject, to='developerwsit@gmail.com', from_addr = sender_mail)
        email.send(html_content, settings_local_env)
        # email = Mailer(subject=subject,to='joakim@springconf.com',from_addr = sender_mail)
        # email.send(html_content, settings_local_env)


class Mailer():

    from_addr = ""
    subject = ""
    to = ""

    def __init__(self, subject, to, from_addr = 'dev@pendataasia.com'):
        self.from_addr = from_addr
        self.subject = subject
        self.to = to

        access_key = settings.SMTP_USERNAME
        secret_key = settings.SMTP_PASSWORD
        region = settings.SES_REGION

        self.conn = boto.ses.connect_to_region(
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )


    def send(self, message, local_env = False):
        # call this to send an email
        # it takes html string as a message
        from_email_address = self.from_addr
        subject = self.subject
        to = self.to
        if local_env:
            to = 'dev@pendataasia.com'
        self.conn.send_email(
            from_email_address,
            subject,
            message,
            to,
            format='html'
        )
