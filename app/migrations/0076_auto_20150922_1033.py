# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0075_session_has_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answers',
            name='value',
            field=models.TextField(),
        ),
    ]
