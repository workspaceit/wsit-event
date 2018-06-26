# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_attendee'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='tag',
            field=models.CharField(max_length=255, default='Early Birds'),
            preserve_default=False,
        ),
    ]
