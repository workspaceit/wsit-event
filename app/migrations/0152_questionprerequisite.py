# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0151_pagecontent_is_show'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionPreRequisite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('action', models.BooleanField(default=True)),
                ('pre_req_answer', models.ForeignKey(to='app.Option')),
                ('pre_req_question', models.ForeignKey(related_name='pre_req_question', to='app.Questions')),
                ('question', models.ForeignKey(related_name='question', to='app.Questions')),
            ],
            options={
                'db_table': 'question_pre_requisite',
            },
        ),
    ]
