# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0365_auto_20180201_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='bid',
            field=models.CharField(unique=True, null=True, max_length=50),
        ),
    ]
