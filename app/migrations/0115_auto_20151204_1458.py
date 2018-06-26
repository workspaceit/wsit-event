# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0114_session_allow_overlapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='type',
            field=app.models.GroupType(max_length=50, choices=[('attendee', 'Attendee'), ('session', 'Session'), ('hotel', 'Hotel'), ('filter', 'Filter'), ('payment', 'Payment'), ('question', 'Question'), ('location', 'Location'), ('travel', 'Travel')]),
        ),
    ]
