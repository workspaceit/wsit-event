from django.views import generic
from django.conf import settings
from django.template.loader import render_to_string
import boto.ses
import boto
import os


class Mailer():

    from_addr = settings.EMAIL_SENDER
    subject = ""
    to = ""

    def __init__(self, subject, to, from_addr=settings.EMAIL_SENDER):
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

    def send(self, message):
        # call this to send an email
        # it takes html string as a message
        from_email_address = self.from_addr
        subject = self.subject
        to = self.to
        if settings.LOCAL_ENV:
            to = 'workspaceinfotech@gmail.com'
        self.conn.send_email(
            from_email_address,
            subject,
            message,
            to,
            format='html'
        )

class MailHelper(generic.View):
    def mail_send(html,context,subject,to,sender_mail="mahedi@workspaceit.com"):
            html_content = render_to_string(html, context)
            # live
            if os.environ['ENVIRONMENT_TYPE'] == 'tempmaster':
                email = Mailer(subject=subject,to='workspaceinfotech@gmail.com',from_addr = sender_mail)
                email.send(html_content)
                email = Mailer(subject=subject,to=to,from_addr = "mahedi@workspaceit.com")
                email.send(html_content)
            else:
                email = Mailer(subject=subject,to='workspaceinfotech@gmail.com',from_addr = sender_mail)
                email.send(html_content)