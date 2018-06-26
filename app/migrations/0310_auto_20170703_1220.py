# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0309_registrationgroups'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationGroupOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group', models.ForeignKey(to='app.RegistrationGroups')),
            ],
            options={
                'db_table': 'registration_group_owner',
            },
        ),
        migrations.AddField(
            model_name='attendee',
            name='registration_group',
            field=models.ForeignKey(to='app.RegistrationGroups', null=True),
        ),
        migrations.AddField(
            model_name='registrationgroupowner',
            name='owner',
            field=models.ForeignKey(to='app.Attendee'),
        ),
    ]
