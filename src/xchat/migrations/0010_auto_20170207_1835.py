# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-07 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xchat', '0009_auto_20170207_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='key',
            field=models.CharField(editable=False, max_length=100, null=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='chat',
            unique_together=set([('type', 'key')]),
        ),
    ]
