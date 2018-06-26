# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0293_elementhtml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementhtml',
            name='language',
            field=models.ForeignKey(to='app.Presets', null=True),
        ),
    ]
