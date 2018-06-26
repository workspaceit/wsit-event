# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0093_generaltag'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('session', models.ForeignKey(to='app.Session')),
                ('tag', models.ForeignKey(to='app.GeneralTag')),
            ],
            options={
                'db_table': 'seminars_has_tags',
            },
        ),
    ]
