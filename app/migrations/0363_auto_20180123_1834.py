# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0362_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='cost',
            field=models.FloatField(null=True, default=0),
        ),
        migrations.AlterField(
            model_name='room',
            name='vat',
            field=models.FloatField(null=True),
        ),
    ]
