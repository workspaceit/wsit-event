# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0306_tag_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='generaltag',
            name='event',
            field=models.ForeignKey(to='app.Events', default=11),
        ),
    ]
