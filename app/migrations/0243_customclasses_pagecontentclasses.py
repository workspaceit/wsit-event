# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0242_remove_emailcontents_filter'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomClasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('classname', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
            ],
            options={
                'db_table': 'custom_classes',
            },
        ),
        migrations.CreateModel(
            name='PageContentClasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('box_id', models.IntegerField()),
                ('classname', models.ForeignKey(to='app.CustomClasses')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'page_content_classes',
            },
        ),
    ]
