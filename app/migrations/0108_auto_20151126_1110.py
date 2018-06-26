# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0107_ruleset_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminarsusers',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='seminarsusers',
            name='queue_order',
            field=models.IntegerField(null=True),
        ),
    ]
