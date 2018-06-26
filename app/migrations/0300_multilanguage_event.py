# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0299_multilanguage_plugindescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='multilanguage',
            name='event',
            field=models.ForeignKey(default=11, to='app.Events'),
            preserve_default=False,
        ),
    ]
