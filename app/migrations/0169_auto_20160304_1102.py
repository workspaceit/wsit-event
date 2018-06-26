# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0168_pageimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='travel',
            name='arrival_city',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='travel',
            name='departure_city',
            field=models.CharField(default='test', max_length=255),
            preserve_default=False,
        ),
    ]
