# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0364_room_pay_whole_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='effected_day_count',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='item_booking_id',
            field=models.IntegerField(null=True),
        ),
    ]
