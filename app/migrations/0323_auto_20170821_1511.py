# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0322_rebates_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='contact_web',
            field=models.TextField(blank=True, null=True, default=None),
        ),
    ]
