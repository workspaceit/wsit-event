# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0251_messagecontents_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagereceivershistory',
            name='receiver',
            field=models.ForeignKey(to='app.MessageReceivers'),
        ),
    ]
