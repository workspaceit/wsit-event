# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0192_attendee_checksum_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='speakers',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
