# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0305_attendee_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='event',
            field=models.ForeignKey(default=10, to='app.Events'),
        ),
    ]
