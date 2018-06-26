# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0332_auto_20170829_1746'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitems',
            old_name='item_rebate_order_by',
            new_name='rebate_for_item_id',
        ),
        migrations.AddField(
            model_name='orderitems',
            name='rebate_for_item_type',
            field=app.models.OrderItemType(null=True, choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate')], max_length=100),
        ),
    ]
