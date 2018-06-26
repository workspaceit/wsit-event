# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0181_emailtemplates_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailContents',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('subject', models.TextField()),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(to='app.Users', related_name='content_created_by')),
                ('filter', models.ForeignKey(to='app.RuleSet')),
                ('last_updated_by', models.ForeignKey(to='app.Users', related_name='content_last_updated_by')),
                ('template', models.ForeignKey(to='app.EmailTemplates')),
            ],
            options={
                'db_table': 'email_contents',
            },
        ),
    ]
