# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0368_pagecontent_disallow_logged_in'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='registration_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.RegistrationGroups'),
        ),
    ]
