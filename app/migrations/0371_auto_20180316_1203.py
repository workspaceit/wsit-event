# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0370_deletedhistory_activity_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='rebate',
            field=models.ForeignKey(to='app.Rebates', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
