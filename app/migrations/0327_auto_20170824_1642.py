# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0326_orderitems_item_rebate_order_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='item_rebate_order_by',
            field=models.IntegerField(default=0),
        ),
    ]
