# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0228_auto_20160926_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementdefaultlang',
            name='type',
            field=app.models.PluginType(max_length=100, default='text', choices=[('text', 'Text'), ('item_text', 'Item Text'), ('button', 'Button'), ('notification', 'Notification')]),
        ),
    ]
