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
        if t == ChatType.USERS and len(data['users']) < 2:
            raise serializers.ValidationError("users chat must have more than two members")
        if t == ChatType.CS and len(data['users']) != 1:
            raise serializers.ValidationError("cs chat must have and only have one member")

        return data

    @transaction.atomic
    def create(self, validated_data):
        ns = validated_data['ns']
        t = validated_data['type']
        users = [encode_ns_user(ns, user) for user in validated_data['users']]

        chat = None
        if t == ChatType.USER:
            # 单聊唯一
            chat = Chat.objects.filter(type=ChatType.USER).filter(members__user=users[0]).filter(members__user=users[1]).first()

        if t == ChatType.SELF:
            # 自聊唯一
            chat = Chat.objects.filter(type=ChatType.SELF).filter(members__user=users[0]).first()

        if t == ChatType.CS:
            # TODO: 客服通过tag区别不同的客服团队
            # 同一tag的user客服唯一
            chat = Chat.objects.filter(type=ChatType.CS).filter(members__user=users[0]).first()

        if chat is not None:
            chat.is_deleted = False
            # update
            chat.update_updated(fields=['is_deleted'])
            return chat

        tag = validated_data.get('tag', '')
        if t in [ChatType.SELF, ChatType.USER, ChatType.USERS]:
            # 用户建会话
            tag = 'user'
        title = validated_data.get('title', '')
        ext = validated_data.get('ext', '')
        chat = Chat(type=t, tag=tag, title=title, ext=ext)
        chat.save()

        for user in users:
            Member.objects.get_or_create(chat=chat, user=user)
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

        for user in users:
            member, _ = Member.objects.get_or_create(chat=chat, user=user)
            member.cur_id = chat.msg_id
            member.exit_msg_id = 0
            member.is_exited = False
            member.dnd = False
            member.save()
        # update
        chat.update_updated()
        return True
