# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0353_auto_20171127_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='invoice_date',
            field=models.DateTimeField(null=True, default=None),
        ),
    ]
