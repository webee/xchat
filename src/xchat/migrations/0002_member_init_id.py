# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-24 11:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xchat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='init_id',
            field=models.IntegerField(default=0),
        ),
    ]
