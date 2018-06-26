# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0145_auto_20160122_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'menu_permission',
            },
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='group',
        ),
        migrations.AddField(
            model_name='menuitem',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 25, 11, 44, 18, 274111, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='menuitem',
            name='created_by',
            field=models.ForeignKey(related_name='menu_created_by', default=1, to='app.Users'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='menuitem',
            name='last_updated_by',
            field=models.ForeignKey(related_name='menu_last_updated_by', default=1, to='app.Users'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='menuitem',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 25, 11, 44, 36, 391116, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='menupermission',
            name='menu',
            field=models.ForeignKey(to='app.MenuItem'),
        ),
    ]
