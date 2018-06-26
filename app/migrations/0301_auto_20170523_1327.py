# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0300_multilanguage_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plugindescription',
            name='element',
        ),
        migrations.RemoveField(
            model_name='plugindescription',
            name='language',
        ),
        migrations.RemoveField(
            model_name='plugindescription',
            name='page',
        ),
        migrations.DeleteModel(
            name='PluginDescription',
        ),
    ]
