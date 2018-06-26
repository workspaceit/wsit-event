# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0348_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='currency',
            field=models.CharField(null=True, max_length=32),
        ),
        migrations.AddField(
            model_name='payments',
            name='transaction',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='activityhistory',
            name='category',
            field=app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo'), ('registration_group', 'Registration_group'), ('rebate', 'Rebate'), ('order', 'Order'), ('order_item', 'Order Item'), ('credit_order', 'Credit Order'), ('credit_usage', 'Credit Usage'), ('payment', 'Payment')], max_length=50),
        ),
        migrations.AlterField(
            model_name='deletedhistory',
            name='category',
            field=app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo'), ('registration_group', 'Registration_group'), ('rebate', 'Rebate'), ('order', 'Order'), ('order_item', 'Order Item'), ('credit_order', 'Credit Order'), ('credit_usage', 'Credit Usage'), ('payment', 'Payment')], max_length=50),
        ),
    ]
