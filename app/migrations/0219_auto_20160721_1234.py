# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0218_auto_20160719_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElementsAnswers',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('answer', models.BooleanField(default=1)),
                ('description', models.TextField()),
                ('box_id', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users', related_name='element_answer_created_by')),
            ],
            options={
                'db_table': 'elements_answers',
            },
        ),
        migrations.CreateModel(
            name='ElementsQuestions',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users', related_name='element_question_created_by')),
            ],
            options={
                'db_table': 'elements_questions',
            },
        ),
        migrations.AddField(
            model_name='elements',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 21, 6, 34, 2, 2399, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='elements',
            name='created_by',
            field=models.ForeignKey(default=1, to='app.Users', related_name='element_created_by'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='elements',
            name='last_updated_by',
            field=models.ForeignKey(default=1, to='app.Users', related_name='element_last_updated_by'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='elements',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 21, 6, 34, 42, 802421, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='elements',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 22, 12, 32, 34, 107818)),
        ),
        migrations.AddField(
            model_name='elementsquestions',
            name='group',
            field=models.ForeignKey(to='app.Elements'),
        ),
        migrations.AddField(
            model_name='elementsquestions',
            name='last_updated_by',
            field=models.ForeignKey(to='app.Users', related_name='element_question_last_updated_by'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='element_question',
            field=models.ForeignKey(to='app.ElementsQuestions'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='last_updated_by',
            field=models.ForeignKey(to='app.Users', related_name='element_answer_last_updated_by'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
    ]
