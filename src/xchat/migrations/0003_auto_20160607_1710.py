# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-07 09:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xchat', '0002_remove_member_init_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='created',
            new_name='joined',
        ),
    ]
