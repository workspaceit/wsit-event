# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0372_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='booking_check_in',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='booking_check_out',
            field=models.DateField(null=True),
        ),
    ]
