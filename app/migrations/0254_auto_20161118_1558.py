# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0253_messagereceivers_push'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminarsusers',
            name='status_evalution',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='seminarsusers',
            name='status_nextup',
            field=models.BooleanField(default=False),
        ),
    ]
