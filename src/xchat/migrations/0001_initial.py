# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-07-17 04:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.BigIntegerField()),
                ('chat_type', models.CharField(max_length=10)),
                ('id', models.BigIntegerField()),
                ('uid', models.CharField(max_length=32)),
                ('ts', models.DateTimeField()),
                ('msg', models.TextField()),
                ('domain', models.CharField(max_length=16)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('self', '自聊'), ('user', '单聊'), ('users', '讨论组'), ('group', '群组'), ('cs', '客服'), ('room', '房间')], max_length=10)),
                ('key', models.CharField(editable=False, max_length=100, null=True, unique=True)),
                ('title', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('tag', models.CharField(blank=True, db_index=True, default='', max_length=8)),
                ('msg_id', models.BigIntegerField(default=0, editable=False)),
                ('last_msg_ts', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), editable=False)),
                ('ext', models.TextField(blank=True, default='')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('members_updated', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('owner', models.CharField(blank=True, db_index=True, default=None, max_length=32, null=True)),
            ],
            options={
                'verbose_name': 'Chat',
                'verbose_name_plural': 'Chats',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(db_index=True, max_length=32)),
                ('joined', models.DateTimeField(auto_now_add=True)),
                ('join_msg_id', models.BigIntegerField(default=0, editable=False)),
                ('cur_id', models.BigIntegerField(default=0, editable=False)),
                ('exit_msg_id', models.BigIntegerField(default=0, editable=False)),
                ('is_exited', models.BooleanField(default=False)),
                ('dnd', models.BooleanField(default=False)),
                ('label', models.TextField(blank=True, default='')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='xchat.Chat')),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('tag', models.CharField(blank=True, db_index=True, default='', max_length=8)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
            },
        ),
        migrations.CreateModel(
            name='RoomChat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.IntegerField(default=0)),
                ('chat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='xchat.Chat')),
                ('room', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='xchat.Room')),
            ],
            options={
                'verbose_name': 'RoomChat',
                'verbose_name_plural': 'RoomChats',
            },
        ),
        migrations.AlterUniqueTogether(
            name='chat',
            unique_together=set([('type', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='roomchat',
            unique_together=set([('room', 'area')]),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('chat', 'user')]),
        ),
    ]
