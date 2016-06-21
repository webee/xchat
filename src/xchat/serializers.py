from django.db import transaction
from rest_framework import serializers
from xchat.authentication import encode_ns_user
from .models import Chat, Member, ChatTypes, ChatType


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('user', 'cur_id', 'joined')


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="chat_id")
    msg_id = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()
    users = serializers.ListField(required=False, write_only=True,
                                  child=serializers.CharField(allow_blank=False, max_length=32), default=[])

    class Meta:
        model = Chat
        fields = ('id', 'type', 'users', 'title', 'tag', 'msg_id', 'is_deleted', 'created')

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
            raise serializers.ValidationError("user chat must have and only have two members")
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
            # 客服唯一
            chat = Chat.objects.filter(type=ChatType.CS).filter(members__user=users[0]).first()

        if chat is not None:
            chat.is_deleted = False
            chat.save()
            return chat

        tag = validated_data.get('tag', '')
        title = validated_data.get('title', '')
        chat = Chat(type=t, tag=tag, title=title)
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
            Member.objects.get_or_create(chat=chat, user=user, cur_id=chat.msg_id)
        # update
        chat.save()
        return True
