# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0377_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomallotment',
            name='cost',
            field=models.FloatField(null=True, default=0),
        ),
        migrations.AddField(
            model_name='roomallotment',
            name='vat',
            field=models.FloatField(null=True),
        ),
    ]
