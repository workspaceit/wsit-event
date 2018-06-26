# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0149_auto_20160125_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='event',
            field=models.ForeignKey(default=1, to='app.Events'),
            preserve_default=False,
        ),
    ]
