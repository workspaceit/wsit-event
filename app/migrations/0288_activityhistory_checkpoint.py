# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0287_auto_20170420_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityhistory',
            name='checkpoint',
            field=models.ForeignKey(null=True, to='app.Checkpoint'),
        ),
    ]
