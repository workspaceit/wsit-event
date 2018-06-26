# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0179_auto_20160321_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(related_name='template_created_by', to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
                ('last_updated_by', models.ForeignKey(related_name='template_last_updated_by', to='app.Users')),
            ],
            options={
                'db_table': 'email_templates',
            },
        ),
    ]
