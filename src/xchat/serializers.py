from django.db import transaction
from rest_framework import serializers
from xchat.authentication import encode_ns_user
from .models import Chat, Member, ChatTypes, ChatType


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('user', 'cur_id', 'joined', 'is_exited', 'exit_msg_id', 'dnd')


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="chat_id")
    type = serializers.CharField(allow_blank=False, max_length=10)
    tag = serializers.CharField(allow_blank=True, max_length=8)
    msg_id = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()
    users = serializers.ListField(required=False, write_only=True,
                                  child=serializers.CharField(allow_blank=False, max_length=32), default=[])

    class Meta:
        model = Chat
        fields = ('id', 'type', 'users', 'title', 'tag', 'msg_id', 'ext', 'is_deleted', 'created')

    def validate_type(self, value):
        if value not in ChatTypes:
            raise serializers.ValidationError("invalid chat type")
        return value

    def validate_users(self, value):
        users = set(value)
        return list(users)

    def validate(self, data):
        t = data['type']
        if t == ChatType.SELF and len(data['users']) != 1:
            raise serializers.ValidationError("self chat must have and only have one member")
        if t == ChatType.USER and len(data['users']) != 2:
            if len(data['users']) == 1:
                data['type'] = ChatType.SELF
            else:
                raise serializers.ValidationError("user chat must have and only have two members")
        if t == ChatType.USERS:
            if len(data['users']) < 2:
                raise serializers.ValidationError("users chat must have more than 1 members")
            elif len(data['users']) >= 100:
                raise serializers.ValidationError("users chat must have less than 100 members")
        if t == ChatType.CS and len(data['users']) != 1:
            raise serializers.ValidationError("cs chat must have and only have one member")
        if t not in [ChatType.SELF, ChatType.USER, ChatType.USERS] and data.get('tag') == "user":
            raise serializers.ValidationError("tag 'user' is reserved for user created chats")

        return data

    @transaction.atomic
    def create(self, validated_data):
        ns = validated_data['ns']
        t = validated_data['type']
        users = [encode_ns_user(ns, user) for user in validated_data['users']]

        key = None
        owner = None
        tag = validated_data.get('tag', '')
        if t == ChatType.SELF:
            # 用户建会话
            tag = 'user'
            owner = users[0]
            # 自聊唯一
            key = owner
        elif t == ChatType.USER:
            # 用户建会话
            tag = 'user'
            # 单聊唯一
            key = ','.join(sorted(users))
        elif t == ChatType.USERS:
            # 用户建会话
            tag = 'user'
        elif t == ChatType.CS:
            # TODO: 客服通过tag区别不同的客服团队
            tag = '_cs'
            owner = users[0]
            # 同一tag的user客服唯一
            key = '%s|%s' % (tag, owner)

        chat = None
        if t in [ChatType.SELF, ChatType.USER, ChatType.CS]:
            chat = Chat.objects.filter(type=t, key=key).first()

        if chat is not None:
            chat.is_deleted = False
            # update
            chat.update_members_updated(fields=['is_deleted'])
            return chat

        title = validated_data.get('title', '')
        ext = validated_data.get('ext', '')
        chat = Chat(type=t, key=key, tag=tag, title=title, ext=ext, owner=owner)
        chat.save()

        for user in users:
            member, _ = Member.objects.get_or_create(chat=chat, user=user)
        return chat


class MembersSerializer(serializers.Serializer):
    users = serializers.ListField(required=False, child=serializers.CharField(allow_blank=False, max_length=32), default=[])

    def update(self, instance, validated_data):
        return self.create(validated_data)

    @transaction.atomic
    def create(self, validated_data):
        ns = validated_data['ns']
        chat = validated_data['chat']
        users = [encode_ns_user(ns, user) for user in validated_data['users']]

        do_updated = False
        for user in users:
            member, created = Member.objects.get_or_create(chat=chat, user=user)
            if created or member.is_exited:
                do_updated = True
                member.cur_id = chat.msg_id
                member.join_msg_id = chat.msg_id
                member.is_exited = False
                member.dnd = False
                member.save()

        # update
        if do_updated:
            chat.update_members_updated()
        return True
