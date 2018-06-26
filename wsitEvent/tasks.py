from __future__ import absolute_import
from wsitEvent.celery import app
from app.views.mail import MailHelper


@app.task
def mail_task(args):
    MailHelper.mail_template_send(args['template'], args['subject'], args['to'], args['sender'])
    return
