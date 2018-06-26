# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0315_auto_20170706_1028'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLanguageContents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('email_content', models.ForeignKey(to='app.EmailContents')),
                ('language', models.ForeignKey(to='app.Presets')),
            ],
            options={
                'db_table': 'email_language_contents',
            },
        ),
        migrations.CreateModel(
            name='MessageLanguageContents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('language', models.ForeignKey(to='app.Presets')),
                ('message_content', models.ForeignKey(to='app.MessageContents')),
            ],
            options={
                'db_table': 'message_language_contents',
            },
        ),
    ]
