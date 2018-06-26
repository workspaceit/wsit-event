# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0363_auto_20180123_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='pay_whole_amount',
            field=models.BooleanField(default=False),
        ),
    ]
