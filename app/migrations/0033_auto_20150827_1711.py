# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_auto_20150826_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answers',
            name='user',
            field=models.ForeignKey(to='app.Attendee'),
        ),
        migrations.AlterField(
            model_name='seminarsusers',
            name='user',
            field=models.ForeignKey(to='app.Attendee'),
        ),
    ]
