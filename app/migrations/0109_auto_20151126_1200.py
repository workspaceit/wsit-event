# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0108_auto_20151126_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seminarsusers',
            name='queue_order',
            field=models.IntegerField(default=1),
        ),
    ]
