# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20150819_1516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locations',
            name='contacts',
        ),
        migrations.AddField(
            model_name='locations',
            name='contacts_email',
            field=models.CharField(max_length=255, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='contacts_name',
            field=models.CharField(max_length=255, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='contacts_phone',
            field=models.CharField(max_length=255, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='contacts_web',
            field=models.CharField(max_length=255, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='map_highlight',
            field=models.CharField(max_length=255, blank=True, default=None),
        ),
    ]
