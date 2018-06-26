# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0196_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportstate',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
    ]
