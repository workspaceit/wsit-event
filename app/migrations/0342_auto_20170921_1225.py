# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0341_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpermission',
            name='content',
            field=app.models.ContentType(choices=[('event', 'Event'), ('attendee', 'Attendee'), ('deleted_attendee', 'DeletedAttendee'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('location', 'Location'), ('hotel', 'Hotel'), ('page', 'Page'), ('menu', 'Menu'), ('template', 'Template'), ('css', 'Css'), ('filter', 'Filter'), ('export_filter', 'ExportFilter'), ('photo_reel', 'PhotoReel'), ('message', 'Message'), ('file_browser', 'FileBrowser'), ('checkpoints', 'Checkpoints'), ('language', 'Language'), ('economy', 'Economy'), ('setting', 'Setting'), ('assign_session', 'AssignSession'), ('assign_travel', 'AssignTravel'), ('assign_hotel', 'AssignHotel'), ('group_registration', 'GroupRegistration')], max_length=20),
        ),
    ]
