from django.db import transaction
from rest_framework import serializers
from .models import Chat, Member, ChatTypes
import xim_client
from xim_client import types


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('user',)


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    channel = serializers.ReadOnlyField()

    class Meta:
        model = Chat
        fields = ('id', 'type', 'channel', 'title', 'owner', 'tag', 'created', 'updated')

    def validate_type(self, value):
        if value not in ChatTypes:
            raise serializers.ValidationError("invalid chat type")
        return value

    @transaction.atomic
    def create(self, validated_data):
        t = validated_data['type']
        users = validated_data['users']
        if t == "user" and len(users) != 2:
            raise Exception("user chat must have and only have two members.")
        ms = []
        for user in users:
            ms.append(types.Member(user, True, True))

        client = xim_client.get_client()
        channel = client.create_channel(ms, t)
        if channel is None:
            raise Exception("create channel failed")
        tag = validated_data.get('tag', '')
        title = validated_data.get('title', '')
        chat = Chat(type=t, channel=channel, tag=tag, title=title)
        chat.save()

        for m in users:
            Member.objects.create(chat=chat, user=m)
        return chat


class MembersSerializer(serializers.Serializer):
    members = MemberSerializer(many=True, required=False, default=[])
    users = serializers.ListField(required=False, child=serializers.CharField(allow_blank=False, max_length=32), default=[])

    def update(self, instance, validated_data):
        return self.create(validated_data)

    @transaction.atomic
    def create(self, validated_data):
        chat = validated_data['chat']
        users = validated_data['users']

        has_created = 0
        for user in users:
            _, created = Member.objects.update_or_create(chat=chat, user=user)
            has_created += 1 if created else 0
        if has_created > 0:
            chat.save()
        return has_created
