# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0179_auto_20160321_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='default_answer_status',
            field=app.models.DefaultAnswerStatus(max_length=50, choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')], default='leave'),
        ),
        migrations.AlterField(
            model_name='session',
            name='default_answer_status',
            field=app.models.DefaultAnswerStatus(max_length=50, choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')], default='leave'),
        ),
        migrations.AlterField(
            model_name='travel',
            name='default_answer_status',
            field=app.models.DefaultAnswerStatus(max_length=50, choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')], default='leave'),
        ),
    ]
