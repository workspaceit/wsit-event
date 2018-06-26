# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0337_auto_20170913_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditorders',
            name='type',
            field=app.models.OrderItemType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate'), ('adjustment', 'Adjustment')], max_length=100),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='item_type',
            field=app.models.OrderItemType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate'), ('adjustment', 'Adjustment')], max_length=100),
        ),
        migrations.AlterField(
            model_name='orderitems',
            name='rebate_for_item_type',
            field=app.models.OrderItemType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate'), ('adjustment', 'Adjustment')], max_length=100, null=True),
        ),
    ]
