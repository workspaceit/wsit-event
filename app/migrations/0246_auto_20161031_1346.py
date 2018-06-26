# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0245_auto_20161028_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcontents',
            name='sender_email',
            field=models.CharField(default='registration@eventdobby.com', max_length=255),
        ),
        migrations.AlterField(
            model_name='messagehistory',
            name='type',
            field=app.models.MessageHistoryType(choices=[('sms', 'SMS'), ('push', 'Push'), ('mail', 'Mail')], max_length=50),
        ),
    ]
