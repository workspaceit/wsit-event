# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0325_auto_20170823_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='item_rebate_order_by',
            field=models.IntegerField(null=True),
        ),
    ]
