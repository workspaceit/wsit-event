# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0110_auto_20151127_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seminarsusers',
            name='status',
            field=app.models.AttendeeSessionStatus(max_length=20, default='attending', choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')]),
        ),
    ]
