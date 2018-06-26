# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0096_auto_20151103_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='generaltag',
            name='category',
            field=app.models.TagType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('room', 'Room')], default='session', max_length=50),
        ),
    ]
