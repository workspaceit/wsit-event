# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0106_session_show_on_evaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleset',
            name='group',
            field=models.ForeignKey(to='app.Group', default=1),
            preserve_default=False,
        ),
    ]
