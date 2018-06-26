# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0051_roomallotment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestedbuddy',
            name='booking',
            field=models.ForeignKey(to='app.Booking', related_name='buddies'),
        ),
    ]
