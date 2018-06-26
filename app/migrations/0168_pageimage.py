# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0167_auto_20160225_0241'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('path', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_shown', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
                ('page', models.ForeignKey(default=None, to='app.PageContent')),
            ],
            options={
                'db_table': 'page_images',
            },
        ),
    ]
