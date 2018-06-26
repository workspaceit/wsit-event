# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0367_auto_20180209_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='disallow_logged_in',
            field=models.BooleanField(default=False),
        ),
    ]
