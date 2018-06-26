# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0139_auto_20160111_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('url', models.CharField(null=True, max_length=1000)),
                ('named_url', models.CharField(null=True, max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(related_name='created_by', to='app.Users')),
                ('last_updated_by', models.ForeignKey(related_name='last_updated_by', to='app.Users')),
            ],
            options={
                'db_table': 'page_contents',
            },
        ),
    ]
