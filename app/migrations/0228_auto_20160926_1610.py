# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0227_auto_20160926_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementdefaultlang',
            name='type',
            field=app.models.PluginType(choices=[('text', 'Text'), ('button', 'Button'), ('notification', 'Notification')], default='text', max_length=100),
        ),
    ]
