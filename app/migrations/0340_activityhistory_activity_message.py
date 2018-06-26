# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0339_auto_20170915_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityhistory',
            name='activity_message',
            field=models.TextField(null=True),
        ),
    ]
