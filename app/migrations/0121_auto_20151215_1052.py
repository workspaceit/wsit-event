# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0120_auto_20151211_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportrule',
            name='export_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='locations',
            name='location_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questions',
            name='question_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ruleset',
            name='rule_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='session_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='travel',
            name='travel_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
