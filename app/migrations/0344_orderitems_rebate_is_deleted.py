# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0343_orderitems_applied_on_open_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='rebate_is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
