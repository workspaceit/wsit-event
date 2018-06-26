# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0292_presets_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElementHtml',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('box_id', models.IntegerField()),
                ('compiled', models.TextField()),
                ('uncompiled', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('language', models.ForeignKey(to='app.Presets')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'element_html',
            },
        ),
    ]
