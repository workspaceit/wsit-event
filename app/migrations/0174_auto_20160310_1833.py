# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0173_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='default_answer',
            field=app.models.AttendeeSessionStatus(max_length=20, default='attending', choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')]),
        ),
        migrations.AlterField(
            model_name='travel',
            name='default_answer',
            field=app.models.AttendeeSessionStatus(max_length=20, default='attending', choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')]),
        ),
    ]
