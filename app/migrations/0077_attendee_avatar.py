# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0076_auto_20150922_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='avatar',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
    ]
