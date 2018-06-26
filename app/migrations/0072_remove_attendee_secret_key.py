# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0071_attendee_secret_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendee',
            name='secret_key',
        ),
    ]
