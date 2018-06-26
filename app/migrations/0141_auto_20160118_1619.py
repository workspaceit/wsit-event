# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0140_pagecontent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagecontent',
            name='named_url',
        ),
        migrations.AddField(
            model_name='menuitem',
            name='content',
            field=models.ForeignKey(null=True, to='app.PageContent'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='url',
            field=models.CharField(null=True, max_length=255, unique=True),
        ),
    ]
