# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0171_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='default_answer_status',
            field=app.models.DefaultAnswerStatus(default='set', max_length=50, choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')]),
        ),
        migrations.AddField(
            model_name='session',
            name='default_answer',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='default_answer_status',
            field=app.models.DefaultAnswerStatus(default='set', max_length=50, choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')]),
        ),
        migrations.AddField(
            model_name='travel',
            name='default_answer',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='travel',
            name='default_answer_status',
            field=app.models.DefaultAnswerStatus(default='set', max_length=50, choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')]),
        ),
    ]
