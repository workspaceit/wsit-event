# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0366_attendee_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditorders',
            name='order_number',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='creditusages',
            name='order_number',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='orders',
            name='order_number',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='payments',
            name='order_number',
            field=models.CharField(max_length=100, default=0),
        ),
    ]
