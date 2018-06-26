# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0150_pagecontent_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='is_show',
            field=models.BooleanField(default=True),
        ),
    ]
