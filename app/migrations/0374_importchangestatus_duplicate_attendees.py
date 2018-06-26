# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0373_auto_20180405_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='importchangestatus',
            name='duplicate_attendees',
            field=models.TextField(null=True),
        ),
    ]
