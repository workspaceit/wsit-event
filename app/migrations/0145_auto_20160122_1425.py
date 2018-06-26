# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0144_auto_20160121_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='events',
            name='admin',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='events',
            name='url',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
