# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0375_auto_20180430_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementdefaultlang',
            name='type',
            field=app.models.PluginType(default='text', choices=[('text', 'Text'), ('item_text', 'Item Text'), ('button', 'Button'), ('notification', 'Notification'), ('validation_text', 'Validation Text')], max_length=100),
        ),
    ]
