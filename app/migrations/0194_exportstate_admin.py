# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0193_exportstate'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportstate',
            name='admin',
            field=models.ForeignKey(default=1, to='app.EventAdmin'),
            preserve_default=False,
        ),
    ]
