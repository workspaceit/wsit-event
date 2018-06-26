# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0279_notification_message_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elements',
            name='type',
            field=app.models.ElementType(default='plugin', choices=[('plugin', 'Plugin'), ('public_notification', 'Public_notification'), ('default_plugin', 'Default_plugin')], max_length=20),
        ),
    ]
