# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0378_ruleset_matchfor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagecontents',
            name='type',
            field=app.models.MessageType(choices=[('push_or_sms', 'Push_or_Sms'), ('sms_and_push', 'Sms_and_Push'), ('sms', 'Sms'), ('push', 'Push'), ('plugin_message', 'Plugin_Message')], max_length=255),
        ),
    ]
