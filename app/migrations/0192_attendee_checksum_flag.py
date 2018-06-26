# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0191_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='checksum_flag',
            field=models.BooleanField(default=False),
        ),
    ]
