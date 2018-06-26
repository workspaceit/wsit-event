# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0325_auto_20170823_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='locations',
            name='show_contact_email',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locations',
            name='show_contact_name',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locations',
            name='show_contact_phone',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locations',
            name='show_contact_web',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locations',
            name='show_map_highlight',
            field=models.BooleanField(default=False),
        ),
    ]
