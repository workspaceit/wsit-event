# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0116_auto_20151207_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='TravelBoundRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('travel_homebound', models.ForeignKey(related_name='travel_homebound', to='app.Travel')),
                ('travel_outbound', models.ForeignKey(related_name='travel_outbound', to='app.Travel')),
            ],
            options={
                'db_table': 'travel_bound_relation',
            },
        ),
    ]
