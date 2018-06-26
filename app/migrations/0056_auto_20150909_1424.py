# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0055_booking_matched'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchline',
            name='match',
            field=models.ForeignKey(to='app.Match', related_name='match_lines'),
        ),
    ]
