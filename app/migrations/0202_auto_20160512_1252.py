# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0201_menuitem_only_speaker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='type',
            field=app.models.GroupType(max_length=50, choices=[('attendee', 'Attendee'), ('session', 'Session'), ('hotel', 'Hotel'), ('filter', 'Filter'), ('payment', 'Payment'), ('question', 'Question'), ('location', 'Location'), ('travel', 'Travel'), ('export_filter', 'Export Filter'), ('menu', 'Menu'), ('email', 'Email')]),
        ),
    ]
