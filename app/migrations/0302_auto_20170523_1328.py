# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0301_auto_20170523_1327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multilanguage',
            name='event',
        ),
        migrations.RemoveField(
            model_name='multilanguage',
            name='language',
        ),
        migrations.DeleteModel(
            name='MultiLanguage',
        ),
    ]
