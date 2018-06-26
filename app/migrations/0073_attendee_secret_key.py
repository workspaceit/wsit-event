# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0072_remove_attendee_secret_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='secret_key',
            field=models.CharField(unique=True, null=True, max_length=50),
        ),
    ]
