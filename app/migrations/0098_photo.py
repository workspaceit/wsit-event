# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0097_generaltag_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('photo', models.CharField(max_length=1000)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'photos',
            },
        ),
    ]
