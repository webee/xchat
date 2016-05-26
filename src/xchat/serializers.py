from django.db import transaction
from rest_framework import serializers
from .models import Chat, Member, ChatTypes, ChatType, User
import xim_client


class MemberSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.user')

    class Meta:
        model = Member
        fields = ('user', 'created')


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    channel = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()
    users = serializers.ListField(required=False, write_only=True,
                                  child=serializers.CharField(allow_blank=False, max_length=32), default=[])

    class Meta:
        model = Chat
        fields = ('id', 'type', 'channel', 'users', 'title', 'owner', 'tag', 'is_deleted', 'created', 'updated')

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

        return data

    @transaction.atomic
    def create(self, validated_data):
        t = validated_data['type']
        users = validated_data['users']

        chat = None
        if t == ChatType.USER:
            # 单聊唯一
            peers = User.objects.filter(user__in=users)
            if len(peers) == 2:
                p1, p2 = peers
                chat = p1.chats.filter(type=ChatType.USER).filter(members__user=p2.user).first()

        if t == ChatType.SELF:
            # 自聊唯一
            peers = User.objects.filter(user__in=users)
            if len(peers) == 1:
                p = peers[0]
                chat = p.chats.filter(type=ChatType.SELF).first()

        if chat is not None:
            client = xim_client.get_client()
            if client.open_channel(chat.channel) is not None:
                chat.is_deleted = False
                chat.save()
            else:
                raise Exception("create channel failed")
            return chat

        client = xim_client.get_client()
        channel = client.create_channel(publishers=users, subscribers=users, tag=t)
        if channel is None:
            raise Exception("create channel failed")
        tag = validated_data.get('tag', '')
        title = validated_data.get('title', '')
        chat = Chat(type=t, channel=channel, tag=tag, title=title)
        chat.save()

        users = [User.objects.get_or_create(user=user)[0] for user in users]
        for m in users:
            Member.objects.create(chat=chat, user=m)
        return chat


class MembersSerializer(serializers.Serializer):
    users = serializers.ListField(required=False, child=serializers.CharField(allow_blank=False, max_length=32), default=[])

    def update(self, instance, validated_data):
        return self.create(validated_data)

    @transaction.atomic
    def create(self, validated_data):
        chat = validated_data['chat']
        users = validated_data['users']

        client = xim_client.get_client()
        data = client.add_channel_pub_subs(chat.channel, users, users)
        if data is not None:
            last_id = data["last_id"]
            users = [User.objects.get_or_create(user=user)[0] for user in users]
            for m in users:
                Member.objects.get_or_create(chat=chat, user=m, init_id=last_id)
            return True
        return False
