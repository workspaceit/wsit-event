# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0226_auto_20160926_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='elements',
            name='event',
        ),
        migrations.AddField(
            model_name='elements',
            name='type',
            field=app.models.ElementType(default='plugin', choices=[('plugin', 'Plugin'), ('public_notification', 'Public_notification')], max_length=20),
        ),
    ]
