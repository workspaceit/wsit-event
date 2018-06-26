# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0278_auto_20170214_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message_content',
            field=models.ForeignKey(to='app.MessageContents', null=True),
        ),
    ]
