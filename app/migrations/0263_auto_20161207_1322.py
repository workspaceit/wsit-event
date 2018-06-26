# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0262_cookie_cookiepage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cookie',
            name='created',
        ),
        migrations.AddField(
            model_name='cookie',
            name='created_at',
            field=models.DateField(default='2016-12-06', auto_now_add=True),
            preserve_default=False,
        ),
    ]
