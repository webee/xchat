# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-16 08:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('xchat', '0011_auto_20170216_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 2, 16, 8, 36, 8, 114073, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.RunSQL("alter table xchat_member alter updated set default CURRENT_TIMESTAMP", reverse_sql=''),
    ]
