# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0289_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'photo_group',
            },
        ),
        migrations.AddField(
            model_name='photo',
            name='group',
            field=models.ForeignKey(to='app.PhotoGroup', null=True),
        ),
    ]
