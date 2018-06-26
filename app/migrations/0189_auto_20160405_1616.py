# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0188_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='created_by',
            field=models.ForeignKey(related_name='created_by_event', to='app.Users', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='events',
            name='is_show',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='events',
            name='last_updated_by',
            field=models.ForeignKey(related_name='last_updated_by_event', to='app.Users', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='events',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 5, 10, 16, 4, 215912, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
