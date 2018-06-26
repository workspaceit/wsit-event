# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0163_questions_actual_definition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='contact_email',
            field=models.CharField(max_length=255, default=None, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='locations',
            name='contact_name',
            field=models.CharField(max_length=255, default=None, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='locations',
            name='contact_phone',
            field=models.CharField(max_length=255, default=None, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='locations',
            name='contact_web',
            field=models.CharField(max_length=255, default=None, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='locations',
            name='map_highlight',
            field=models.CharField(max_length=255, default=None, blank=True, null=True),
        ),
    ]
