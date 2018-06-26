# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0369_auto_20180314_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='deletedhistory',
            name='activity_message',
            field=models.TextField(null=True),
        ),
    ]
