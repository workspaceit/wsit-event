# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0354_orders_invoice_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='presets',
            name='datetime_language',
            field=models.TextField(null=True, default=None),
        ),
    ]
